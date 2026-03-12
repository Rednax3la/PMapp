"""
Stripe Blueprint — handles subscription checkout, portal, webhooks, and status.
Google Pay is surfaced automatically within Stripe Checkout on supported browsers.
"""
import os
import stripe
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from db import subscriptions_col, stripe_events_col
from subscription_helpers import TIER_LIMITS, get_subscription

stripe_bp = Blueprint('stripe', __name__, url_prefix='/stripe')

# ---------------------------------------------------------------------------
# Stripe SDK configuration
# ---------------------------------------------------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PRICE_IDS = {
    "pro":        os.getenv("STRIPE_PRO_PRICE_ID", ""),
    "enterprise": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", ""),
}

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_or_create_customer(company_name: str, email: str) -> str:
    """Return an existing Stripe customer ID or create one."""
    sub = subscriptions_col.find_one({"company_name": company_name})
    if sub and sub.get("stripe_customer_id"):
        return sub["stripe_customer_id"]

    customer = stripe.Customer.create(
        email=email,
        metadata={"company_name": company_name}
    )
    subscriptions_col.update_one(
        {"company_name": company_name},
        {"$set": {"stripe_customer_id": customer.id, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return customer.id


def _upsert_subscription(company_name: str, tier: str, stripe_sub_id: str,
                         stripe_customer_id: str, status: str, period_end=None):
    """Upsert the local subscription document."""
    subscriptions_col.update_one(
        {"company_name": company_name},
        {"$set": {
            "tier": tier,
            "stripe_subscription_id": stripe_sub_id,
            "stripe_customer_id": stripe_customer_id,
            "status": status,
            "current_period_end": period_end,
            "updated_at": datetime.now(timezone.utc),
        }},
        upsert=True
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@stripe_bp.route('/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create a Stripe Checkout session for a subscription upgrade."""
    claims = get_jwt()
    company_name = claims.get("company_name")
    user_email = claims.get("sub") or ""  # identity is username/email

    data = request.json or {}
    tier = data.get("tier", "").lower()

    if tier not in PRICE_IDS:
        return jsonify({"error": "Invalid tier. Choose 'pro' or 'enterprise'."}), 400

    price_id = PRICE_IDS[tier]
    if not price_id:
        return jsonify({"error": f"Stripe Price ID for '{tier}' is not configured."}), 500

    if not stripe.api_key:
        return jsonify({"error": "Stripe is not configured on this server."}), 503

    try:
        customer_id = _get_or_create_customer(company_name, user_email)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            payment_method_types=["card"],   # Google Pay surfaces automatically in supported browsers
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{FRONTEND_URL}/subscription?success=1&tier={tier}",
            cancel_url=f"{FRONTEND_URL}/subscription?cancelled=1",
            metadata={"company_name": company_name, "tier": tier},
            allow_promotion_codes=True,
        )
        return jsonify({"checkout_url": session.url}), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 400


@stripe_bp.route('/create-portal-session', methods=['POST'])
@jwt_required()
def create_portal_session():
    """Return a Stripe Customer Portal URL for managing/cancelling subscriptions."""
    claims = get_jwt()
    company_name = claims.get("company_name")
    user_email = claims.get("sub") or ""

    if not stripe.api_key:
        return jsonify({"error": "Stripe is not configured on this server."}), 503

    try:
        customer_id = _get_or_create_customer(company_name, user_email)
        portal = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{FRONTEND_URL}/subscription",
        )
        return jsonify({"portal_url": portal.url}), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 400


@stripe_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Return the current subscription tier, status, limits, and usage."""
    claims = get_jwt()
    company_name = claims.get("company_name")

    sub = get_subscription(company_name)
    tier = sub.get("tier", "free")
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])

    # Usage stats
    from db import projects_col
    project_count = projects_col.count_documents({"company_name": company_name})

    # Count unique members across all projects
    pipeline = [
        {"$match": {"company_name": company_name}},
        {"$unwind": {"path": "$team", "preserveNullAndEmpty": False}},
        {"$group": {"_id": "$team"}},
        {"$count": "total"}
    ]
    member_result = list(projects_col.aggregate(pipeline))
    member_count = member_result[0]["total"] if member_result else 0

    period_end = sub.get("current_period_end")
    if isinstance(period_end, datetime):
        period_end = period_end.isoformat()

    return jsonify({
        "tier": tier,
        "status": sub.get("status", "active"),
        "current_period_end": period_end,
        "limits": limits,
        "usage": {
            "projects": project_count,
            "members": member_count,
        }
    }), 200


@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events. No JWT — verified via Stripe signature."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature", "")

    if WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        except stripe.error.SignatureVerificationError:
            return jsonify({"error": "Invalid signature"}), 400
    else:
        # In development without STRIPE_WEBHOOK_SECRET, parse event directly
        import json
        event = json.loads(payload)

    event_id = event.get("id", "")

    # Idempotency — skip already-processed events
    if stripe_events_col.find_one({"stripe_event_id": event_id}):
        return jsonify({"status": "already_processed"}), 200

    stripe_events_col.insert_one({
        "stripe_event_id": event_id,
        "type": event.get("type"),
        "processed_at": datetime.now(timezone.utc),
    })

    event_type = event.get("type")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        company_name = session.get("metadata", {}).get("company_name")
        tier = session.get("metadata", {}).get("tier", "pro")
        stripe_sub_id = session.get("subscription")
        stripe_customer_id = session.get("customer")

        if company_name and stripe_sub_id:
            # Fetch full subscription for period_end
            try:
                stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
                period_end = datetime.fromtimestamp(
                    stripe_sub["current_period_end"], tz=timezone.utc
                )
            except Exception:
                period_end = None

            _upsert_subscription(company_name, tier, stripe_sub_id,
                                 stripe_customer_id, "active", period_end)

    elif event_type == "customer.subscription.updated":
        stripe_sub = event["data"]["object"]
        stripe_sub_id = stripe_sub["id"]
        stripe_customer_id = stripe_sub["customer"]
        status = stripe_sub.get("status", "active")
        period_end = datetime.fromtimestamp(
            stripe_sub["current_period_end"], tz=timezone.utc
        )
        # Resolve tier from price metadata or product
        price_id = stripe_sub["items"]["data"][0]["price"]["id"] if stripe_sub["items"]["data"] else ""
        tier = "free"
        for t, pid in PRICE_IDS.items():
            if pid and pid == price_id:
                tier = t
                break

        sub_doc = subscriptions_col.find_one({"stripe_customer_id": stripe_customer_id})
        if sub_doc:
            _upsert_subscription(
                sub_doc["company_name"], tier, stripe_sub_id,
                stripe_customer_id, status, period_end
            )

    elif event_type == "customer.subscription.deleted":
        stripe_sub = event["data"]["object"]
        stripe_customer_id = stripe_sub["customer"]
        sub_doc = subscriptions_col.find_one({"stripe_customer_id": stripe_customer_id})
        if sub_doc:
            _upsert_subscription(
                sub_doc["company_name"], "free",
                None, stripe_customer_id, "cancelled", None
            )

    elif event_type == "invoice.payment_failed":
        invoice = event["data"]["object"]
        stripe_customer_id = invoice.get("customer")
        sub_doc = subscriptions_col.find_one({"stripe_customer_id": stripe_customer_id})
        if sub_doc:
            subscriptions_col.update_one(
                {"company_name": sub_doc["company_name"]},
                {"$set": {"status": "past_due", "updated_at": datetime.now(timezone.utc)}}
            )

    return jsonify({"status": "ok"}), 200
