"""
M-Pesa (Daraja API) Blueprint — Kenya payment integration.

Supports STK Push (Lipa Na M-Pesa Online) for subscription payments.
Safaricom Daraja API docs: https://developer.safaricom.co.ke/

Setup required:
1. Register at https://developer.safaricom.co.ke
2. Create a Daraja app to get consumer_key and consumer_secret
3. Go live to get production credentials
4. Set the env vars below in scheduling-api/.env
"""

import os
import base64
import requests
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from db import subscriptions_col

mpesa_bp = Blueprint('mpesa', __name__, url_prefix='/mpesa')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CONSUMER_KEY    = os.getenv('MPESA_CONSUMER_KEY', '')
CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
BUSINESS_SHORTCODE = os.getenv('MPESA_SHORTCODE', '')      # Your paybill / till number
PASSKEY         = os.getenv('MPESA_PASSKEY', '')            # From Daraja portal
CALLBACK_URL    = os.getenv('MPESA_CALLBACK_URL', '')       # Public HTTPS URL that receives payment confirmation

# Sandbox vs Production
SANDBOX = os.getenv('MPESA_SANDBOX', 'True').lower() in ('1', 'true', 'yes')
BASE_URL = 'https://sandbox.safaricom.co.ke' if SANDBOX else 'https://api.safaricom.co.ke'

# Plan prices in KES
KES_PRICES = {
    'pro':        int(os.getenv('MPESA_PRO_PRICE_KES', '3500')),       # ~KES 3,500/month
    'enterprise': int(os.getenv('MPESA_ENTERPRISE_PRICE_KES', '12000')), # ~KES 12,000/month
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _configured():
    return all([CONSUMER_KEY, CONSUMER_SECRET, BUSINESS_SHORTCODE, PASSKEY, CALLBACK_URL])


def _get_access_token() -> str:
    """Fetch a short-lived OAuth token from Safaricom."""
    credentials = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
    resp = requests.get(
        f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {credentials}"},
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def _generate_password(timestamp: str) -> str:
    """Generate the Base64-encoded M-Pesa API password."""
    raw = f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@mpesa_bp.route('/stk-push', methods=['POST'])
@jwt_required()
def stk_push():
    """
    Initiate an M-Pesa STK Push (Lipa Na M-Pesa).
    The user's phone receives a payment prompt; they enter their PIN.

    Request body:
        { "phone": "254712345678", "tier": "pro" }

    Phone must be in international format: 254XXXXXXXXX (no +, no leading 0)
    """
    if not _configured():
        return jsonify({"error": "M-Pesa is not configured on this server."}), 503

    claims = get_jwt()
    company_name = claims.get('company_name', '')

    data = request.json or {}
    phone = str(data.get('phone', '')).strip().lstrip('+')
    tier  = data.get('tier', '').lower()

    if not phone or not phone.startswith('254') or len(phone) != 12:
        return jsonify({"error": "Phone must be in format 254XXXXXXXXX (12 digits, no + prefix)"}), 400

    if tier not in KES_PRICES:
        return jsonify({"error": "Invalid tier. Choose 'pro' or 'enterprise'."}), 400

    amount = KES_PRICES[tier]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password  = _generate_password(timestamp)

    try:
        token = _get_access_token()
    except Exception as e:
        return jsonify({"error": f"M-Pesa auth failed: {str(e)}"}), 502

    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": f"ZainPM-{company_name[:12]}",
        "TransactionDesc": f"ZainPM {tier.title()} subscription"
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        result = resp.json()
    except Exception as e:
        return jsonify({"error": f"M-Pesa request failed: {str(e)}"}), 502

    if result.get('ResponseCode') != '0':
        return jsonify({
            "error": result.get('errorMessage') or result.get('ResponseDescription', 'STK push failed'),
            "raw": result
        }), 400

    # Record the pending payment
    subscriptions_col.update_one(
        {"company_name": company_name},
        {"$set": {
            "mpesa_checkout_request_id": result.get('CheckoutRequestID'),
            "mpesa_pending_tier": tier,
            "mpesa_phone": phone,
            "mpesa_initiated_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }},
        upsert=True
    )

    return jsonify({
        "message": "STK Push sent. Check your phone and enter your M-Pesa PIN.",
        "checkout_request_id": result.get('CheckoutRequestID'),
        "merchant_request_id": result.get('MerchantRequestID'),
        "amount_kes": amount,
        "tier": tier,
    }), 200


@mpesa_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    """
    Receives the payment result from Safaricom after the user completes payment.
    This URL must be publicly accessible (Safaricom's servers call it).
    Set MPESA_CALLBACK_URL to https://yourdomain.com/mpesa/callback
    """
    body = request.json or {}
    result = body.get('Body', {}).get('stkCallback', {})

    checkout_request_id = result.get('CheckoutRequestID')
    result_code = result.get('ResultCode')

    if result_code != 0:
        # Payment failed or cancelled
        subscriptions_col.update_one(
            {"mpesa_checkout_request_id": checkout_request_id},
            {"$set": {"mpesa_status": "failed", "updated_at": datetime.now(timezone.utc)}}
        )
        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

    # Payment successful — upgrade subscription
    items = {i['Name']: i.get('Value') for i in result.get('CallbackMetadata', {}).get('Item', [])}
    amount_paid = items.get('Amount', 0)
    mpesa_receipt = items.get('MpesaReceiptNumber', '')

    sub_doc = subscriptions_col.find_one({"mpesa_checkout_request_id": checkout_request_id})
    if sub_doc:
        tier = sub_doc.get('mpesa_pending_tier', 'pro')
        subscriptions_col.update_one(
            {"mpesa_checkout_request_id": checkout_request_id},
            {"$set": {
                "tier": tier,
                "status": "active",
                "mpesa_status": "paid",
                "mpesa_receipt": mpesa_receipt,
                "mpesa_amount_paid": amount_paid,
                "updated_at": datetime.now(timezone.utc),
            }}
        )

    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200


@mpesa_bp.route('/prices', methods=['GET'])
def mpesa_prices():
    """Return current KES prices for each tier (no auth required)."""
    return jsonify({
        "currency": "KES",
        "prices": KES_PRICES,
        "sandbox": SANDBOX,
    }), 200


@mpesa_bp.route('/query', methods=['POST'])
@jwt_required()
def query_status():
    """
    Query the status of an STK Push transaction.
    Request: { "checkout_request_id": "ws_CO_..." }
    """
    if not _configured():
        return jsonify({"error": "M-Pesa is not configured."}), 503

    data = request.json or {}
    checkout_request_id = data.get('checkout_request_id', '')
    if not checkout_request_id:
        return jsonify({"error": "checkout_request_id required"}), 400

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password  = _generate_password(timestamp)

    try:
        token = _get_access_token()
        resp = requests.post(
            f"{BASE_URL}/mpesa/stkpushquery/v1/query",
            json={
                "BusinessShortCode": BUSINESS_SHORTCODE,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id,
            },
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=10
        )
        return jsonify(resp.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 502
