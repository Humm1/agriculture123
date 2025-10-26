# ============================================================================
# AGROSHIELD PAYMENT INTEGRATION CONFIGURATION
# Multi-Provider Payment Setup Guide
# ============================================================================

"""
This guide helps you set up payment integrations with:
1. M-Pesa (Kenya mobile money)
2. Stripe (Global cards & wallets)
3. PayPal (Global payment system)
4. Crypto (Bitcoin, Ethereum, USDT, USDC)
5. Visa Direct (Visa card processing)

Follow the steps below to configure each provider.
"""

# ============================================================================
# 1. M-PESA CONFIGURATION (SAFARICOM - KENYA)
# ============================================================================

"""
SETUP STEPS:
1. Go to: https://developer.safaricom.co.ke
2. Create account and verify
3. Create a new app
4. Get credentials:
   - Consumer Key
   - Consumer Secret
   - Business Short Code (PayBill or Till Number)
   - Passkey (for STK Push)
5. Set callback URL (must be HTTPS and publicly accessible)
6. Start with Sandbox, move to Production when ready

SANDBOX TEST CREDENTIALS:
- Consumer Key: (get from portal)
- Consumer Secret: (get from portal)
- Short Code: 174379 (default sandbox)
- Passkey: (get from portal)
- Test Phone: 254708374149 (always successful)

Update in: backend/app/routes/payments.py
"""

MPESA_CONFIG = {
    "consumer_key": "YOUR_MPESA_CONSUMER_KEY",
    "consumer_secret": "YOUR_MPESA_CONSUMER_SECRET",
    "business_short_code": "174379",  # Your PayBill/Till
    "passkey": "YOUR_MPESA_PASSKEY",
    "callback_url": "https://yourdomain.com/api/payments/mpesa-callback",
    "environment": "sandbox"  # or "production"
}


# ============================================================================
# 2. STRIPE CONFIGURATION (GLOBAL PAYMENTS)
# ============================================================================

"""
SETUP STEPS:
1. Go to: https://stripe.com
2. Create account
3. Get API keys from Dashboard > Developers > API keys
4. Set up webhooks:
   - Go to Dashboard > Developers > Webhooks
   - Add endpoint: https://yourdomain.com/api/payments/stripe-webhook
   - Select events: payment_intent.succeeded, customer.subscription.created
5. Get webhook signing secret

TEST MODE:
- Use test API keys (starts with sk_test_)
- Test card: 4242 4242 4242 4242
- Any future expiry, any CVC

CURRENCIES SUPPORTED:
- USD, EUR, GBP, KES, and 135+ more

PRICING:
- 2.9% + $0.30 per transaction (US)
- Check your region's pricing

Update in: backend/app/routes/payments.py
"""

STRIPE_CONFIG = {
    "secret_key": "sk_test_YOUR_STRIPE_SECRET_KEY",
    "publishable_key": "pk_test_YOUR_STRIPE_PUBLISHABLE_KEY",
    "webhook_secret": "whsec_YOUR_WEBHOOK_SECRET"
}

# Frontend (mobile): Add Stripe publishable key
STRIPE_PUBLISHABLE_KEY = "pk_test_YOUR_KEY"


# ============================================================================
# 3. PAYPAL CONFIGURATION (GLOBAL PAYMENTS)
# ============================================================================

"""
SETUP STEPS:
1. Go to: https://developer.paypal.com
2. Create account (or login with existing PayPal)
3. Create app in Dashboard
4. Get credentials:
   - Client ID
   - Client Secret
5. Set up webhooks:
   - Add webhook URL: https://yourdomain.com/api/payments/paypal-webhook
   - Select events: PAYMENT.CAPTURE.COMPLETED, PAYMENT.SALE.COMPLETED

SANDBOX TESTING:
- Use sandbox credentials
- Create test accounts in PayPal Sandbox
- Test buyer: Email from sandbox accounts
- Test seller: Your business sandbox account

CURRENCIES SUPPORTED:
- USD, EUR, GBP, and 25+ currencies

PRICING:
- 2.9% + fixed fee per transaction (varies by country)
- International: +1.5% cross-border fee

Update in: backend/app/routes/payments.py
"""

PAYPAL_CONFIG = {
    "client_id": "YOUR_PAYPAL_CLIENT_ID",
    "client_secret": "YOUR_PAYPAL_CLIENT_SECRET",
    "mode": "sandbox",  # or "live"
    "webhook_id": "YOUR_WEBHOOK_ID"
}


# ============================================================================
# 4. CRYPTO CONFIGURATION (COINGATE OR COINBASE COMMERCE)
# ============================================================================

"""
OPTION A: COINGATE (Recommended for African markets)
SETUP STEPS:
1. Go to: https://coingate.com
2. Create merchant account
3. Get API credentials from Settings > API
4. Set callback URL: https://yourdomain.com/api/payments/crypto-callback
5. Choose receive currency (USD, EUR, BTC, etc.)

SUPPORTED CRYPTOCURRENCIES:
- Bitcoin (BTC)
- Ethereum (ETH)
- Tether (USDT)
- USD Coin (USDC)
- 70+ other cryptocurrencies

PRICING:
- 1% processing fee
- Instant conversion to fiat or stable coins

TEST MODE:
- CoinGate provides sandbox environment
- Use test API key

OPTION B: COINBASE COMMERCE
1. Go to: https://commerce.coinbase.com
2. Create account
3. Get API key
4. Similar setup to CoinGate

Update in: backend/app/routes/payments.py
"""

CRYPTO_CONFIG = {
    "api_key": "YOUR_COINGATE_API_KEY",
    "api_url": "https://api.coingate.com/v2",
    "callback_url": "https://yourdomain.com/api/payments/crypto-callback",
    "receive_currency": "USDT",  # Stable coin recommended
    "accepted_currencies": ["BTC", "ETH", "USDT", "USDC"]
}


# ============================================================================
# 5. VISA DIRECT CONFIGURATION (CARD PROCESSING)
# ============================================================================

"""
SETUP STEPS:
1. Apply for Visa Direct through payment processor:
   - Flutterwave (Africa): https://flutterwave.com
   - Paystack (Africa): https://paystack.com
   - Or direct through Visa: https://developer.visa.com

2. For Flutterwave/Paystack (Easier for African markets):
   - Create account
   - Complete KYC verification
   - Get API keys
   - Enable card payments
   - Lower fees than direct Visa

3. For Direct Visa (Enterprise):
   - Apply at developer.visa.com
   - Complete merchant verification
   - Get API credentials
   - Requires business verification

RECOMMENDED: Use Flutterwave or Paystack
They handle Visa/Mastercard and provide easier integration

FLUTTERWAVE SETUP:
1. Go to: https://dashboard.flutterwave.com
2. Create account
3. Get API keys (public and secret)
4. Enable card payments
5. Set webhook URL

PRICING:
- Flutterwave: 3.8% per transaction (Kenya)
- Paystack: 3.9% + KES 50 per transaction
- Direct Visa: Negotiated rates

Update in: backend/app/routes/payments.py
"""

# For Flutterwave (Recommended)
FLUTTERWAVE_CONFIG = {
    "public_key": "FLWPUBK_TEST-YOUR_KEY",
    "secret_key": "FLWSECK_TEST-YOUR_KEY",
    "encryption_key": "FLWSECK_TEST-YOUR_ENCRYPTION_KEY",
    "webhook_secret": "YOUR_WEBHOOK_SECRET"
}

# For Direct Visa
VISA_CONFIG = {
    "merchant_id": "YOUR_VISA_MERCHANT_ID",
    "api_key": "YOUR_VISA_API_KEY",
    "api_url": "https://sandbox.api.visa.com",
    "webhook_secret": "YOUR_VISA_WEBHOOK_SECRET"
}


# ============================================================================
# CURRENCY CONVERSION
# ============================================================================

"""
Since you have multiple currencies, use a conversion service:

OPTION 1: Fixer.io (Recommended)
1. Go to: https://fixer.io
2. Create free account (1000 requests/month free)
3. Get API key
4. Use for real-time KES/USD conversion

OPTION 2: ExchangeRate-API
1. Go to: https://www.exchangerate-api.com
2. Free tier: 1500 requests/month
3. Get API key
"""

CURRENCY_API_CONFIG = {
    "provider": "fixer",  # or "exchangerate-api"
    "api_key": "YOUR_FIXER_API_KEY",
    "base_currency": "USD",
    "target_currencies": ["KES", "USD", "EUR", "GBP"]
}


# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

"""
BEFORE GOING LIVE:

1. SSL/HTTPS Setup:
   - All payment webhooks MUST use HTTPS
   - Get SSL certificate (Let's Encrypt is free)
   - Use domain with SSL (not IP address)

2. Environment Variables:
   - NEVER commit API keys to Git
   - Use environment variables (.env file)
   - Add .env to .gitignore

3. Webhook URL Requirements:
   - Must be publicly accessible (not localhost)
   - Must return 200 OK quickly
   - Handle requests asynchronously

4. Testing Checklist:
   ✅ M-Pesa: Test with sandbox phone number
   ✅ Stripe: Test with 4242... card
   ✅ PayPal: Test with sandbox account
   ✅ Crypto: Test with sandbox API
   ✅ Webhooks: Test callback handling

5. Security:
   ✅ Verify webhook signatures
   ✅ Use HTTPS only
   ✅ Rate limit payment endpoints
   ✅ Log all transactions
   ✅ Store payment IDs, not card details

6. Move to Production:
   - Switch from sandbox to production keys
   - Update callback URLs to production domain
   - Test with small real transactions first
   - Monitor error logs

7. Compliance:
   - PCI DSS compliance (for card payments)
   - Data protection regulations (GDPR if EU customers)
   - Local payment regulations (Kenya: CBK guidelines)
"""


# ============================================================================
# EXAMPLE .env FILE
# ============================================================================

"""
Create a file named `.env` in backend directory:

# M-Pesa
MPESA_CONSUMER_KEY=your_key_here
MPESA_CONSUMER_SECRET=your_secret_here
MPESA_BUSINESS_SHORT_CODE=174379
MPESA_PASSKEY=your_passkey_here
MPESA_CALLBACK_URL=https://yourdomain.com/api/payments/mpesa-callback
MPESA_ENVIRONMENT=sandbox

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# PayPal
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
PAYPAL_MODE=sandbox
PAYPAL_WEBHOOK_ID=your_webhook_id_here

# Crypto
CRYPTO_API_KEY=your_coingate_key_here
CRYPTO_RECEIVE_CURRENCY=USDT

# Flutterwave (instead of direct Visa)
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-your_key
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-your_key
FLUTTERWAVE_ENCRYPTION_KEY=FLWSECK_TEST-your_encryption

# Currency Conversion
FIXER_API_KEY=your_fixer_api_key

# Application
APP_DOMAIN=https://yourdomain.com
ENVIRONMENT=development
"""


# ============================================================================
# LOADING ENVIRONMENT VARIABLES IN CODE
# ============================================================================

"""
Install python-dotenv:
    pip install python-dotenv

Then in backend/app/routes/payments.py, add at the top:

from dotenv import load_dotenv
import os

load_dotenv()

MPESA_CONFIG = {
    "consumer_key": os.getenv("MPESA_CONSUMER_KEY"),
    "consumer_secret": os.getenv("MPESA_CONSUMER_SECRET"),
    "business_short_code": os.getenv("MPESA_BUSINESS_SHORT_CODE"),
    "passkey": os.getenv("MPESA_PASSKEY"),
    "callback_url": os.getenv("MPESA_CALLBACK_URL"),
    "environment": os.getenv("MPESA_ENVIRONMENT", "sandbox")
}

# Similar for other providers...
"""


# ============================================================================
# SUPPORT CONTACTS
# ============================================================================

"""
M-Pesa Support:
- Email: apisupport@safaricom.co.ke
- Portal: https://developer.safaricom.co.ke

Stripe Support:
- Email: support@stripe.com
- Docs: https://stripe.com/docs

PayPal Support:
- Developer forum: https://www.paypal-community.com
- Email: merchanttechnicalsupport@paypal.com

CoinGate Support:
- Email: support@coingate.com
- Live chat on website

Flutterwave Support:
- Email: hi@flutterwavego.com
- Slack: Join their developer Slack
"""


# ============================================================================
# PRICING SUMMARY (As of 2025)
# ============================================================================

"""
M-Pesa:
- B2C: 1.5% of transaction value
- C2B: Negotiable with Safaricom
- Monthly fees may apply

Stripe:
- Standard: 2.9% + $0.30 per transaction
- International cards: +1.5%
- Currency conversion: +1%

PayPal:
- Standard: 2.9% + fixed fee
- International: +1.5%
- Currency conversion: ~3%

Crypto (CoinGate):
- 1% processing fee
- No chargeback fees
- Instant settlement

Flutterwave:
- Kenya cards: 3.8%
- International cards: 3.8% + $0.25
- Mobile money: 1.4%

RECOMMENDATION FOR AGROSHIELD:
1. M-Pesa: Primary for Kenyan users (most popular)
2. Stripe: International users + credit cards
3. Crypto: Tech-savvy users + remittances
4. PayPal: Backup option for international

Start with M-Pesa + Stripe, add others based on demand.
"""
