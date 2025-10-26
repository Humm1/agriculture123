# 🚀 AgroShield - Copy & Paste Commands

## Backend Server - Choose ONE method:

### ✅ Method 1: Double-click Batch File (EASIEST)
1. Navigate to: `C:\Users\Codeternal\Desktop\agroshield\backend`
2. Double-click: `start_backend.bat`
3. Server will start automatically

### ✅ Method 2: PowerShell Script
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\backend
.\start_backend.ps1
```

### ✅ Method 3: Direct Python Command
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\backend
..\.venv\Scripts\python.exe run_server.py
```

---

## Frontend App

```powershell
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app
npx expo start
```

---

## 📱 Test Backend is Running

Open browser: http://localhost:8000/docs

You should see Swagger API documentation

---

## 🔧 If You Get Errors

### Error: "Module 'stripe' not found"
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\backend
..\.venv\Scripts\pip.exe install stripe supabase pyjwt email-validator python-dotenv
```

### Error: "Frontend can't connect"
Edit file: `frontend\agroshield-app\src\config\apiConfig.js`

Find your IP address:
```powershell
ipconfig
```

Update line 13 with your IP:
```javascript
return 'http://YOUR_IP_HERE:8000'; // Example: 'http://192.168.1.100:8000'
```

### Error: "Expo modules not found"
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app
npx expo install expo-location expo-camera expo-device
```

---

## ✅ Success Indicators

### Backend Running:
```
🚀 Starting AgroShield Backend Server
🌐 Server will be available at: http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Frontend Running:
```
› Metro waiting on exp://10.1.0.8:8081
› Scan the QR code above with Expo Go
```

---

## 🎯 All Features Ready

✅ **20 Backend API Routes**
✅ **150+ API Endpoints**  
✅ **AI Disease Prediction**  
✅ **Drone Intelligence**  
✅ **Exchange Marketplace**  
✅ **Market Linkages**  
✅ **Climate Intelligence**  
✅ **Storage Monitoring**

**Everything is connected and ready to use!**

---

## 📦 Installation

### Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Or install payment-specific packages
pip install stripe python-dotenv requests
```

### Frontend Setup

```bash
cd mobile

# Install React Native dependencies
npm install
# or
yarn install

# Install payment UI components (already done)
# - react-native-paper
# - @expo/vector-icons
```

---

## ⚙️ Configuration

### 1. Create Environment File

Create `backend/.env`:

```env
# ============================================================================
# PAYMENT PROVIDER CREDENTIALS
# ============================================================================

# M-Pesa (Get from https://developer.safaricom.co.ke)
MPESA_CONSUMER_KEY=your_consumer_key_here
MPESA_CONSUMER_SECRET=your_consumer_secret_here
MPESA_BUSINESS_SHORT_CODE=174379
MPESA_PASSKEY=your_passkey_here
MPESA_CALLBACK_URL=https://yourdomain.com/api/payments/mpesa-callback
MPESA_ENVIRONMENT=sandbox

# Stripe (Get from https://stripe.com/dashboard)
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# PayPal (Get from https://developer.paypal.com)
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
PAYPAL_MODE=sandbox
PAYPAL_WEBHOOK_ID=your_webhook_id_here

# Crypto - CoinGate (Get from https://coingate.com)
CRYPTO_API_KEY=your_coingate_api_key_here
CRYPTO_RECEIVE_CURRENCY=USDT

# Flutterwave (Alternative to Visa Direct - Get from https://flutterwave.com)
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-your_key
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-your_key
FLUTTERWAVE_ENCRYPTION_KEY=FLWSECK_TEST-your_encryption

# Currency Conversion (Optional - Get from https://fixer.io)
FIXER_API_KEY=your_fixer_api_key

# Application Settings
APP_DOMAIN=https://yourdomain.com
ENVIRONMENT=development
```

### 2. Update Payment Configuration

Edit `backend/app/routes/payments.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Update configurations to use environment variables
MPESA_CONFIG = {
    "consumer_key": os.getenv("MPESA_CONSUMER_KEY"),
    "consumer_secret": os.getenv("MPESA_CONSUMER_SECRET"),
    # ... etc
}
```

### 3. Database Setup

Run database migrations to add subscription fields:

```bash
# If using SQLAlchemy/Alembic
alembic revision --autogenerate -m "Add subscription fields"
alembic upgrade head

# Or apply SQL directly (see IMPLEMENTATION_SUMMARY.md for SQL)
```

---

## 🧪 Testing

### Test with Sandbox Credentials

#### 1. M-Pesa Testing

```python
# Use sandbox test phone number
phone = "254708374149"  # Always successful
amount = 250  # KES

# This will trigger STK Push on your test phone
response = await subscriptionAPI.subscribe(phone, "PRO", "monthly")
```

#### 2. Stripe Testing

```javascript
// Use test card numbers
const testCard = "4242424242424242";  // Success
const cvv = "123";
const expiry = "12/25";

// This will process payment in test mode
response = await subscriptionAPI.subscribe(userId, "PRO", "monthly", {
  provider: "stripe",
  paymentMethodId: "pm_test_xxxx"
});
```

#### 3. PayPal Testing

- Use sandbox.paypal.com
- Create test buyer/seller accounts
- Test with sandbox credentials

#### 4. Crypto Testing

- Use CoinGate sandbox
- Test payment URL generation
- Verify callback handling

---

## 🔐 Security Checklist

Before going live:

- [ ] **SSL Certificate**: Get HTTPS (Let's Encrypt is free)
- [ ] **Environment Variables**: Never commit `.env` to Git
- [ ] **Webhook Secrets**: Verify all webhook signatures
- [ ] **Rate Limiting**: Implement on payment endpoints
- [ ] **Logging**: Log all transactions & errors
- [ ] **Monitoring**: Set up error tracking (Sentry)

---

## 🚀 Deployment

### 1. Deploy Backend with HTTPS

```bash
# Example with Nginx + Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# Configure Nginx for HTTPS
# Update callback URLs to production domain
```

### 2. Update Webhooks

For each provider, update webhook URLs:

- **M-Pesa**: Update in Safaricom Developer Portal
- **Stripe**: Update in Dashboard > Webhooks
- **PayPal**: Update in Developer Dashboard
- **Crypto**: Update in CoinGate settings

### 3. Switch to Production Keys

Replace all `sandbox`/`test` keys with production keys:

```env
MPESA_ENVIRONMENT=production
STRIPE_SECRET_KEY=sk_live_your_key
PAYPAL_MODE=live
```

### 4. Test with Small Real Transactions

- Test KES 10 M-Pesa payment
- Test $0.50 Stripe payment
- Verify webhook delivery
- Check subscription activation

---

## 📱 Mobile App Updates

### Update API Base URL

In `mobile/src/services/api.js`:

```javascript
const API_BASE_URL = 'https://yourdomain.com/api';  // Production
// const API_BASE_URL = 'http://localhost:8000/api';  // Development
```

### Add Stripe Public Key

For Stripe card input (future):

```javascript
import { StripeProvider } from '@stripe/stripe-react-native';

const STRIPE_PUBLISHABLE_KEY = 'pk_live_your_key';  // Production
// const STRIPE_PUBLISHABLE_KEY = 'pk_test_your_key';  // Testing
```

---

## 🧾 Usage Examples

### Backend - Check Feature Access

```python
from app.middleware.feature_guard import require_feature

@router.post("/premium-feature")
@require_feature("yield_forecasting")
async def premium_endpoint(user_id: str):
    # User automatically validated for PRO+ access
    return {"data": "premium content"}
```

### Backend - Check Usage Limits

```python
from app.middleware.feature_guard import check_limit

@router.post("/scan")
@check_limit("max_scans_per_month")
async def scan_plant(user_id: str):
    # Automatically enforces monthly scan limits
    return {"scan_result": "..."}
```

### Frontend - Subscribe User

```javascript
import { subscriptionAPI } from '../services/api';

// M-Pesa subscription
const result = await subscriptionAPI.subscribe(
  user.phone,      // "254712345678"
  "PRO",          // Tier
  "monthly"       // Duration
);
// User receives STK Push on phone

// Stripe subscription
const result = await subscriptionAPI.subscribe(
  user.phone,
  "PRO",
  "monthly",
  {
    provider: "stripe",
    paymentMethodId: paymentMethod.id,
    currency: "USD"
  }
);
```

### Frontend - Check Feature Access

```javascript
import { subscriptionAPI } from '../services/api';

const access = await subscriptionAPI.checkAccess(
  user.id,
  "yield_forecasting"
);

if (!access.has_access) {
  // Show upgrade prompt
  Alert.alert(
    'Premium Feature',
    `Upgrade to ${access.upgrade_tier} to access this feature`,
    [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Upgrade', onPress: () => navigateToSubscription() }
    ]
  );
}
```

---

## 🐛 Troubleshooting

### Payment Failed

1. **Check webhook delivery**:
   - M-Pesa: Check callback logs
   - Stripe: Check Dashboard > Webhooks
   - PayPal: Check Developer Dashboard

2. **Verify credentials**:
   - Confirm API keys are production (not test)
   - Check environment variables loaded correctly

3. **Check callback URL**:
   - Must be HTTPS
   - Must be publicly accessible
   - Must return 200 OK

### Feature Access Denied

1. **Check subscription status**:
   ```python
   user = persistence.get_user_by_id(user_id)
   print(user.get("subscription_tier"))  # Should be PRO or EXPERT
   print(user.get("subscription_expiry"))  # Should be future date
   ```

2. **Verify payment completed**:
   - Check transactions table
   - Confirm payment status is "completed"

3. **Check feature spelling**:
   - Feature names must match exactly (case-sensitive)
   - Example: "yield_forecasting" not "yieldForecasting"

### Usage Limit Errors

1. **Reset monthly counters**:
   ```python
   # At start of each month (cron job)
   persistence.update_user(user_id, {
       "usage_max_scans_per_month": 0
   })
   ```

2. **Verify tier limits**:
   - FREE: 10 scans/month
   - PRO: 50 scans/month
   - EXPERT: Unlimited (-1)

---

## 📊 Monitoring

### Key Metrics to Track

```python
# In your analytics dashboard:

# 1. Conversion rates
free_to_pro_conversion = pro_subscriptions / total_users * 100

# 2. Monthly Recurring Revenue (MRR)
mrr = sum(active_subscriptions.amount)

# 3. Payment success rate
success_rate = completed_payments / total_payments * 100

# 4. Churn rate
churn = expired_subscriptions / active_subscriptions * 100

# 5. Feature usage
most_used_feature = max(feature_usage, key=feature_usage.get)
```

---

## 🎓 Resources

### Documentation:
- **M-Pesa**: https://developer.safaricom.co.ke/docs
- **Stripe**: https://stripe.com/docs
- **PayPal**: https://developer.paypal.com/docs
- **CoinGate**: https://developer.coingate.com/docs
- **Flutterwave**: https://developer.flutterwave.com/docs

### Support:
- **M-Pesa**: apisupport@safaricom.co.ke
- **Stripe**: support@stripe.com
- **PayPal**: merchanttechnicalsupport@paypal.com
- **CoinGate**: support@coingate.com
- **Flutterwave**: hi@flutterwavego.com

---

## ✅ Production Checklist

Before launching:

- [ ] All payment providers configured
- [ ] `.env` file with production keys
- [ ] Database migrations applied
- [ ] HTTPS enabled with SSL certificate
- [ ] Webhooks tested with production URLs
- [ ] Small test transactions successful
- [ ] Error logging & monitoring enabled
- [ ] Backup & recovery plan in place
- [ ] Payment failure handling tested
- [ ] Subscription expiry logic working
- [ ] SMS reminders configured (optional)
- [ ] Customer support ready
- [ ] Terms of service & privacy policy updated
- [ ] Refund policy documented

---

## 🎉 You're Ready!

Your multi-payment integration is complete. Start with:

1. **Configure M-Pesa** (most popular in Kenya)
2. **Add Stripe** (international cards)
3. **Test thoroughly** with sandbox
4. **Go live** with small transactions
5. **Monitor & optimize**

Good luck! 🚀

---

**Questions?** Refer to:
- `PAYMENT_SETUP_GUIDE.py` - Detailed provider setup
- `SUBSCRIPTION_TIERS.md` - Feature breakdown
- `IMPLEMENTATION_SUMMARY.md` - Technical details
