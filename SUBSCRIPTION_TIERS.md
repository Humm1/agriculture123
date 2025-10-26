# AgroShield Premium Features & Subscription Tiers

## 🌟 Overview

AgroShield now offers a comprehensive SaaS monetization system with **3 subscription tiers** (FREE, PRO, EXPERT) and **5 payment providers** (M-Pesa, Stripe, PayPal, Crypto, Visa).

---

## 📊 Subscription Tiers

### 🆓 FREE Tier (KES 0 / USD 0)

**Basic agricultural support for all farmers**

#### Features Included:
- ✅ **Weather & Climate**
  - Basic weather alerts
  - Standard 7-day forecast
  
- ✅ **Pest & Disease**
  - Basic pest alerts
  - Camera scan diagnosis (high confidence only - 70%+)
  - Up to 10 scans per month
  
- ✅ **Growth & Planning**
  - Basic calendar
  - Growth tracking
  
- ✅ **Market & Pricing**
  - Basic market prices
  
- ✅ **Storage & Monitoring**
  - Basic storage monitoring (daily intervals)
  - 1 storage device
  
- ✅ **Soil & Fertilizer**
  - Basic soil information
  
- ✅ **Community**
  - Village groups
  - Partner campaigns
  - Standard support

#### Limits:
- 📍 Max 2 fields
- 📸 Max 10 scans/month
- 📦 1 storage device
- 📊 Daily storage monitoring (24-hour intervals)

---

### 💼 PRO Tier (KES 250 / USD 5 per month)

**For serious farmers optimizing yields and profits**

#### Everything in FREE, plus:

- ✨ **Advanced Weather & Climate**
  - Advanced weather forecasts
  - Climate prediction models
  
- ✨ **Enhanced Diagnostics**
  - Medium confidence scans (50%+)
  - Up to 50 scans per month
  
- ✨ **Yield & Profit Forecasting** ⭐
  - AI-powered yield predictions
  - Profit forecasting with market prices
  - What-If scenario calculator (ROI analysis)
  - Investment decision support
  
- ✨ **Premium Market Intelligence** ⭐
  - Premium market access alerts
  - Regional market comparison (Nairobi, Mombasa, Kisumu)
  - Optimal sale window recommendations
  - Profit increase predictions
  
- ✨ **Advanced Growth Tracking**
  - Detailed growth analytics
  
- ✨ **Enhanced Storage**
  - Hourly monitoring (60-minute intervals)
  - Up to 3 storage devices

#### Limits:
- 📍 Max 10 fields
- 📸 Max 50 scans/month
- 📦 3 storage devices
- 📊 Hourly storage monitoring

#### Pricing:
- **Monthly:** KES 250 / USD 5
- **Annual:** KES 2,500 / USD 50 (2 months free!)

---

### 👨‍🔬 EXPERT Tier (KES 750 / USD 15 per month)

**For professional farmers & agricultural entrepreneurs**

#### Everything in PRO, plus:

- 🚀 **Priority Expert Support** ⭐
  - Human expert diagnosis
  - **Guaranteed 2-hour response time**
  - High-priority queue placement
  
- 🚀 **Advanced Diagnostics**
  - Low confidence scans (30%+)
  - Unlimited scans per month
  - **Spectral/Multi-layer Analysis** ⭐
  - Pre-symptomatic deficiency detection (14 days advance warning)
  - Subtle color variation analysis
  
- 🚀 **Custom Fertilizer Plans** ⭐
  - Stage-specific NPK blending
  - Custom soil blending recommendations
  - Certified dealer contacts
  - Organic alternatives
  
- 🚀 **High-Frequency Storage Monitoring** ⭐
  - **5-minute intervals** (288 data points/day)
  - Storage health scores
  - Trend analysis
  - **Quality Certificates** for premium buyers
  - Certificate eligibility tracking
  
- 🚀 **IoT Integration** ⭐
  - API key generation for third-party sensors
  - Webhook integration
  - Custom sensor support
  - Irrigation system integration
  - Weather station integration
  
- 🚀 **Credit & Finance**
  - **Agri-Reliability Score** (0-100)
  - Credit assessment for agricultural loans
  - Performance tracking

#### Limits:
- 📍 **Unlimited fields**
- 📸 **Unlimited scans**
- 📦 **Unlimited storage devices**
- 📊 5-minute storage monitoring

#### Pricing:
- **Monthly:** KES 750 / USD 15
- **Annual:** KES 7,500 / USD 150 (2 months free!)

---

## 💰 Pay-Per-Service Options

For farmers who don't need a full subscription:

### 1. Expert Diagnosis (KES 50 / USD 1)
- One photo forwarded to human expert
- Professional diagnosis within 48 hours
- Valid for 48 hours

### 2. Custom Fertilizer Plan (KES 50 / USD 1)
- One custom soil blending plan
- Stage-specific recommendations
- Valid for 7 days

### 3. IoT Integration Setup (KES 100 / USD 2)
- API key for third-party sensors
- 30-day integration access
- Documentation included

### 4. Storage Certificate (KES 75 / USD 1.50)
- Quality certification document
- QR code verification
- Single certificate generation

---

## 💳 Payment Methods

### 🇰🇪 Kenya
- **M-Pesa** (Recommended) - Mobile money, instant
- **Visa/Mastercard** via Flutterwave
- **Crypto** (BTC, ETH, USDT, USDC)

### 🌍 International
- **Stripe** - Credit/debit cards
- **PayPal** - Global payment system
- **Crypto** - Bitcoin, Ethereum, stablecoins

---

## 🎯 Feature Comparison Table

| Feature | FREE | PRO | EXPERT |
|---------|------|-----|--------|
| **Weather Alerts** | Basic | Advanced | Advanced |
| **Climate Prediction** | ❌ | ✅ | ✅ |
| **Pest Scanning** | 10/month | 50/month | Unlimited |
| **Scan Confidence** | 70%+ | 50%+ | 30%+ |
| **Yield Forecasting** | ❌ | ✅ | ✅ |
| **What-If Scenarios** | ❌ | ✅ | ✅ |
| **Market Alerts** | Basic | Premium | Premium |
| **Regional Comparison** | ❌ | ✅ | ✅ |
| **Expert Diagnosis** | Pay-per-use | Pay-per-use | ✅ Included |
| **Priority Response** | ❌ | ❌ | ✅ 2hr |
| **Spectral Analysis** | ❌ | ❌ | ✅ |
| **Pre-symptom Detection** | ❌ | ❌ | ✅ 14 days |
| **Custom Fertilizer** | ❌ | ❌ | ✅ |
| **Storage Monitoring** | Daily | Hourly | 5-min |
| **Storage Certificates** | ❌ | ❌ | ✅ |
| **IoT Integration** | ❌ | ❌ | ✅ |
| **Agri-Credit Score** | ❌ | ❌ | ✅ |
| **Max Fields** | 2 | 10 | Unlimited |
| **Storage Devices** | 1 | 3 | Unlimited |

---

## 🔧 Technical Implementation

### Backend Routes Created:

1. **`/api/payments`** - Multi-provider payment processing
   - POST `/subscribe` - Create subscription
   - POST `/pay-per-service` - One-time purchases
   - POST `/check-feature-access` - Verify feature access
   - GET `/user-features/{user_id}` - Get user's available features
   - POST `/mpesa-callback` - M-Pesa webhook
   - POST `/stripe-webhook` - Stripe webhook
   - POST `/crypto-callback` - Crypto webhook

2. **`/api/premium`** - Premium feature endpoints
   - POST `/yield-forecast` - AI yield prediction (PRO+)
   - POST `/what-if-scenario` - ROI calculator (PRO+)
   - GET `/premium-market-alerts/{crop}` - Market intelligence (PRO+)
   - POST `/priority-expert-triage` - Expert support (EXPERT)
   - POST `/spectral-analysis` - Pre-symptom detection (EXPERT)
   - POST `/custom-fertilizer-plan` - Custom blending (EXPERT)
   - GET `/storage-monitoring/{device_id}` - Storage data (All tiers)
   - POST `/storage-certificate` - Quality certificate (EXPERT)
   - POST `/iot-api-key` - API key generation (EXPERT)

### Feature Guard Middleware:

```python
# Enforce feature access
@require_feature("yield_forecasting")
async def get_forecast(user_id: str):
    ...

# Enforce subscription tier
@require_tier("PRO")
async def pro_feature(user_id: str):
    ...

# Enforce usage limits
@check_limit("max_scans_per_month")
async def scan_plant(user_id: str):
    ...
```

### Frontend Screens Created:

1. **SubscriptionScreen.js** - Tier selection & payment
2. **TransactionsScreen.js** - Payment history
3. **YieldForecastScreen.js** - Forecasting & What-If calculator
4. **MarketAlertsScreen.js** - Premium market intelligence

---

## 🚀 Getting Started

### For Users:

1. **Download AgroShield** app
2. **Register** with phone number
3. Start with **FREE tier** - no payment required
4. **Upgrade** when you need more features:
   - Tap "Subscription" in menu
   - Choose PRO or EXPERT
   - Select payment method
   - Complete payment

### For Developers:

1. **Configure payment providers** (see `PAYMENT_SETUP_GUIDE.py`)
2. **Set environment variables** in `.env` file
3. **Test with sandbox credentials**
4. **Deploy with HTTPS** (required for webhooks)
5. **Move to production** keys when ready

---

## 📈 Pricing Strategy

### Why These Prices?

- **FREE Tier:** Acquire users, build trust
- **PRO Tier (KES 250):** ~$5 USD/month - affordable for smallholder farmers
- **EXPERT Tier (KES 750):** ~$15 USD/month - commercial farmers & co-ops

### Annual Discount:
- Pay for 10 months, get 12 months (17% off)
- Encourages longer commitment
- Improves cash flow predictability

### Regional Pricing:
- **Kenya:** Priced in KES (local currency)
- **International:** Priced in USD
- Automatic currency conversion

---

## 🎓 Use Cases

### FREE Tier:
- **Beginner farmers** learning digital agriculture
- **Smallholders** with 1-2 fields
- **Testing** the platform before committing

### PRO Tier:
- **Commercial farmers** with 3-10 fields
- **Farmers** optimizing yields and profits
- **Market-savvy farmers** timing sales for max profit

### EXPERT Tier:
- **Agricultural entrepreneurs** with large operations
- **Cooperatives** managing multiple farmers
- **Export farmers** requiring quality certificates
- **Tech-savvy farmers** integrating IoT sensors

---

## 🔐 Security & Compliance

- ✅ PCI DSS compliant (card payments via Stripe/PayPal)
- ✅ Webhook signature verification
- ✅ HTTPS-only payment endpoints
- ✅ No card details stored locally
- ✅ Transaction logging for audit trail
- ✅ Rate limiting on payment endpoints

---

## 📞 Support

### Payment Issues:
- **M-Pesa:** Contact Safaricom support
- **Stripe/PayPal:** Email support@agroshield.com
- **Crypto:** Check transaction on blockchain explorer

### Feature Access Issues:
- Check subscription status in app
- Verify payment completion
- Contact support@agroshield.com

### Upgrades & Downgrades:
- Upgrade anytime - takes effect immediately
- Downgrade at end of billing period
- Refunds not available for partial months

---

## 🔄 Subscription Lifecycle

1. **Free Trial:** Start with FREE tier (no card required)
2. **Upgrade:** Choose PRO or EXPERT, complete payment
3. **Active:** Full feature access until expiry
4. **Renewal:** Auto-renew or manual renewal
5. **Expiry Warning:** SMS reminder 3 days before expiry
6. **Expired:** Downgrade to FREE tier
7. **Reactivation:** Pay to restore premium features

---

## 📊 Agri-Reliability Score (EXPERT Only)

A credit score for agricultural loans, calculated from:

- **Successful Harvests (30%):** Completed growing seasons
- **AI Recommendations (25%):** Following AgroShield advice
- **Timely Actions (20%):** Pest control, fertilizer application
- **Community Engagement (15%):** Sharing feedback, helping others
- **Account Age (10%):** Months using AgroShield

**Score Range:** 0-100
- **80-100:** Excellent (eligible for premium loans)
- **60-79:** Good (standard loan terms)
- **40-59:** Fair (higher interest rates)
- **0-39:** Poor (loan approval unlikely)

---

## 🌱 Roadmap

### Coming Soon:
- [ ] Mobile banking integration (Equity, KCB)
- [ ] USSD payment option (*384*96#)
- [ ] Cooperative/group subscriptions (bulk pricing)
- [ ] Partner financing (buy-now-pay-later)
- [ ] Input credit integration (fertilizer on credit)

---

## 📄 License

Copyright © 2025 AgroShield. All rights reserved.

---

**Made with 💚 for African farmers**
