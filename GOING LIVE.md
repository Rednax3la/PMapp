# ZainPM — Going Live Checklist

This document walks you through everything you need to do before ZainPM is ready for real users and investors. Work through each section in order.

---

## 1. Get Your Domain and Hosting

**Choose a hosting provider.** Good options for Kenya-based startups:

| Provider | Notes |
|---|---|
| **Railway.app** | Easiest — deploys from GitHub in minutes, free tier available |
| **Render.com** | Good free tier for backend, cheap paid plans |
| **DigitalOcean** | More control, ~$6/month droplet. Popular with Kenyan devs |
| **AWS / GCP** | Enterprise-grade — overkill for early stage |

**Get a domain.** Register via [Namecheap](https://namecheap.com), [GoDaddy Kenya](https://godaddy.com), or [Kenya Network Information Centre (KENIC)](https://kenic.or.ke) if you want a `.co.ke` domain.

**Set up SSL.** All providers above give you free SSL via Let's Encrypt. Your app **requires HTTPS** for cookies and M-Pesa callbacks to work.

---

## 2. Secure Your Environment Variables

### Backend (`scheduling-api/.env`)

Before going live, replace every placeholder:

```bash
# Generate a real JWT secret (run this in your terminal):
python -c "import secrets; print(secrets.token_hex(64))"
```

| Variable | What to set |
|---|---|
| `JWT_SECRET_KEY` | The 64-char random string from the command above |
| `JWT_COOKIE_SECURE` | `True` (you will have HTTPS) |
| `JWT_COOKIE_SAMESITE` | `None` (required for cross-origin cookies in production) |
| `FRONTEND_URL` | `https://yourdomain.com` |
| `MONGO_USERNAME` | Your Atlas username |
| `MONGO_PASSWORD` | Your Atlas password |
| `STRIPE_SECRET_KEY` | Your Stripe **live** secret key (starts with `sk_live_`) |
| `STRIPE_WEBHOOK_SECRET` | From Stripe dashboard → Webhooks (after you add the endpoint) |
| `STRIPE_PRO_PRICE_ID` | Price ID from your Stripe product (see Section 4) |
| `STRIPE_ENTERPRISE_PRICE_ID` | Price ID from your Stripe product (see Section 4) |
| `MPESA_SANDBOX` | `False` |
| `MPESA_CONSUMER_KEY` | From Safaricom Daraja portal (see Section 5) |
| `MPESA_CONSUMER_SECRET` | From Safaricom Daraja portal |
| `MPESA_SHORTCODE` | Your Safaricom paybill/till number |
| `MPESA_PASSKEY` | From Daraja portal, under your app |
| `MPESA_CALLBACK_URL` | `https://yourdomain.com/mpesa/callback` |

### Frontend (`Frontend/website/.env.production`)

```
VUE_APP_API_URL=/api
VUE_APP_STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_key
```

---

## 3. MongoDB Atlas — Production Setup

1. Log in at [cloud.mongodb.com](https://cloud.mongodb.com)
2. **Network Access** → Add IP Address → Allow access from anywhere (`0.0.0.0/0`) — or whitelist your server's specific IP for better security
3. **Database Access** → Make sure your user has `readWriteAnyDatabase` role
4. **Backups** → Enable continuous backup on your cluster (M10 or above)
5. **Indexes** — Already created automatically when the app starts

> **Important:** The free M0 cluster has a 512 MB storage limit. For a production app with paying customers, upgrade to at least M10 ($57/month).

---

## 4. Stripe Setup (Card / Google Pay payments)

### Create your products

1. Go to [dashboard.stripe.com/products](https://dashboard.stripe.com/products)
2. Create **two products**:

   - **ZainPM Pro** — Price: $29.00/month (recurring), copy the Price ID (`price_xxx`)
   - **ZainPM Enterprise** — Price: $99.00/month (recurring), copy the Price ID (`price_xxx`)

3. Paste the Price IDs into your backend `.env`:
   ```
   STRIPE_PRO_PRICE_ID=price_xxx
   STRIPE_ENTERPRISE_PRICE_ID=price_xxx
   ```

### Set up the webhook

1. Go to [dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. URL: `https://yourdomain.com/stripe/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Copy the **Signing secret** → paste into `STRIPE_WEBHOOK_SECRET`

### Enable Google Pay

Google Pay works **automatically** within Stripe Checkout — no additional setup needed. Users on Android/Chrome will see the Google Pay button appear.

### Test before going live

Use Stripe's test card: `4242 4242 4242 4242` (any future expiry, any CVC).

---

## 5. M-Pesa / Daraja API Setup (Kenya Payments)

### Step 1 — Get Daraja credentials

1. Go to [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create an account and verify it
3. Create a new app
4. Note your **Consumer Key** and **Consumer Secret**
5. Under your app, find the **Lipa Na M-Pesa Online Passkey** (sandbox passkey is provided automatically; production passkey comes after going live)

### Step 2 — Get a Paybill / Till Number

- If your company is registered, apply for a **Safaricom Paybill number** via [Safaricom Business](https://www.safaricom.co.ke/business)
- Alternatively, use a **Till Number** (Buy Goods) for small businesses
- This becomes your `MPESA_SHORTCODE`

### Step 3 — Go live with Daraja

1. In the Daraja portal, click **Go Live** on your app
2. Safaricom reviews your app (takes 1–5 business days)
3. You'll receive production credentials: Consumer Key, Consumer Secret, and Passkey
4. Update your `.env` with the production values and set `MPESA_SANDBOX=False`

### Step 4 — Set the callback URL

The `MPESA_CALLBACK_URL` must be a **public HTTPS URL**. Safaricom's servers will call it after payment. Set it to: `https://yourdomain.com/mpesa/callback`

For local development/testing, use [ngrok](https://ngrok.com):
```bash
ngrok http 5001
# Copy the HTTPS URL → https://abc123.ngrok.io/mpesa/callback
```

### Step 5 — Test M-Pesa

In sandbox mode, use the test credentials from the Daraja portal. The sandbox simulates STK Push without real money.

---

## 6. Deploy with Docker

### On your server (e.g. DigitalOcean Droplet):

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone your repo
git clone https://github.com/yourusername/PMapp.git
cd PMapp

# Create your production .env files (copy and fill in from Section 2)
nano scheduling-api/.env
nano Frontend/website/.env.production

# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

Your app will be running at:
- Frontend: `http://yourserverip:80`
- Backend API: `http://yourserverip:5001` (proxied via nginx as `/api`)

### Point your domain to the server

In your domain registrar's DNS settings, add an **A record**:
```
Type: A
Name: @  (or www)
Value: <your server IP address>
TTL: 3600
```

---

## 7. Pre-Launch Testing Checklist

Run through these manually before inviting any users:

### Authentication
- [ ] Register a new company (admin account)
- [ ] Login → lands on Admin Dashboard
- [ ] Register a member (second email, same company — or invite via project team)
- [ ] Login as member → lands on Member Dashboard
- [ ] Logout works, session is cleared

### Core Features
- [ ] Create a project (check subscription limit at 4th project on Free tier)
- [ ] Create tasks within a project
- [ ] Assign a member to a task
- [ ] Update task progress from Member Dashboard
- [ ] Gantt chart loads real project data
- [ ] Timetable loads real project data
- [ ] Reports page shows live stats
- [ ] CSV export downloads correctly
- [ ] Members page shows actual team members
- [ ] Settings page loads and saves profile

### Payments
- [ ] Stripe checkout opens with Stripe test card `4242 4242 4242 4242`
- [ ] After successful payment, subscription tier updates in the app
- [ ] Google Pay button appears in Stripe checkout (test on Chrome Android or Chrome desktop with a saved card)
- [ ] M-Pesa STK Push modal opens, phone number validation works
- [ ] (In Daraja sandbox) STK Push is received on the test phone

### Security
- [ ] Unauthenticated user redirected to `/auth`
- [ ] Member cannot navigate to `/` (admin dashboard)
- [ ] Admin cannot navigate to `/member-dashboard`
- [ ] JWT cookie is `HttpOnly` (verify in browser DevTools → Application → Cookies)

---

## 8. Legal & Compliance (Kenya)

### Kenya Data Protection Act 2019

Your app collects user emails and project data. You are legally required to:

1. **Privacy Policy** — Write one that explains:
   - What data you collect (email, company name, project/task data)
   - Why you collect it (to provide the service)
   - Who you share it with (MongoDB Atlas — US servers, Stripe — US, Safaricom — Kenya)
   - How users can request data deletion

2. **Terms of Service** — Standard SaaS terms covering:
   - Acceptable use
   - Subscription and payment terms
   - Data ownership (their data remains theirs)
   - Service availability / uptime SLA

3. **Data residency** — If customers ask, MongoDB Atlas can be configured to store data in specific regions. Currently your cluster is likely in US East. This may matter for enterprise clients.

4. **Register your company** — To use Safaricom Paybill and receive payments legally, you need a registered business entity in Kenya (sole proprietorship or limited company). Register at the [Business Registration Service](https://www.businessregistration.go.ke).

### VAT

If your annual turnover exceeds KES 5 million, you are required to register for VAT with KRA. At that point, add 16% VAT to your KES prices.

---

## 9. Investor Pitch Readiness

These are the things investors will look for:

### Numbers to track from day one
- Monthly Recurring Revenue (MRR)
- Number of paying customers
- Free → Paid conversion rate
- Monthly Active Users (MAU)
- Churn rate

### Recommended tools
- **Analytics**: Add [Mixpanel](https://mixpanel.com) or [PostHog](https://posthog.com) (PostHog is open-source and free) to track feature usage
- **Error monitoring**: Add [Sentry](https://sentry.io) (free tier) — add `pip install sentry-sdk` to backend and the JS SDK to frontend
- **Uptime monitoring**: [UptimeRobot](https://uptimerobot.com) is free and pings your site every 5 minutes

### What makes ZainPM Kenya-market-differentiated
- M-Pesa payments (most Kenyan businesses don't have credit cards)
- Africa/Nairobi default timezone
- KES pricing displayed alongside USD
- Built locally — faster support response than international alternatives

---

## 10. Quick Reference — Key URLs After Launch

| Page | URL |
|---|---|
| Frontend | `https://yourdomain.com` |
| Admin Dashboard | `https://yourdomain.com/` |
| Member Dashboard | `https://yourdomain.com/member-dashboard` |
| Subscription Page | `https://yourdomain.com/subscription` |
| Stripe Webhook | `https://yourdomain.com/stripe/webhook` |
| M-Pesa Callback | `https://yourdomain.com/mpesa/callback` |
| API Health Check | `https://yourdomain.com/api/auth/validate` |

---

## 11. Ongoing Maintenance

- **Rotate JWT_SECRET_KEY** every 6 months (forces all users to re-login)
- **Renew Daraja credentials** if Safaricom requires it
- **Keep dependencies updated**: run `pip install -r requirements.txt --upgrade` and `npm update` quarterly
- **Monitor MongoDB storage** — upgrade your Atlas cluster before hitting limits
- **Back up** your MongoDB Atlas cluster before any major code changes

---

*Last updated: March 2026 — ZainPM v1.0*
