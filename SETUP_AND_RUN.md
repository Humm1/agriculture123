# AgroShield - Complete Setup & Run Guide

## 🚀 Quick Start Commands

### Backend Server

**From the backend directory:**

```powershell
# Navigate to backend
cd C:\Users\Codeternal\Desktop\agroshield\backend

# Start the server using the startup script
..\..venv\Scripts\python.exe run_server.py
```

**Alternative method:**
```powershell
# From backend directory
cd C:\Users\Codeternal\Desktop\agroshield\backend

# Run uvicorn directly
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend App

```powershell
# Navigate to frontend
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app

# Start Expo
npx expo start

# Or start with cache clear
npx expo start -c
```

---

## 📋 Complete Setup Instructions

### 1. Backend Setup

#### Install Python Dependencies
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\backend
..\.venv\Scripts\pip.exe install -r requirements.txt
```

#### Verify Installation
```powershell
..\.venv\Scripts\python.exe -c "from app.main import app; print('✓ Backend ready')"
```

#### Start Backend
```powershell
..\.venv\Scripts\python.exe run_server.py
```

**Expected Output:**
```
======================================================================
🚀 Starting AgroShield Backend Server
======================================================================
📍 Backend Location: C:\Users\Codeternal\Desktop\agroshield\backend
🌐 Server will be available at: http://localhost:8000
📚 API Documentation: http://localhost:8000/docs
======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Frontend Setup

#### Install Dependencies
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app
npm install
```

#### Install Expo Modules
```powershell
npx expo install expo-location expo-camera expo-device
```

#### Configure API URL

Edit `src/config/apiConfig.js` and update the IP address:

```javascript
const getBackendUrl = () => {
  if (__DEV__) {
    return 'http://YOUR_COMPUTER_IP:8000'; // Replace with your IP
  }
  // ...
};
```

**Find your IP address:**
```powershell
ipconfig
# Look for "IPv4 Address" under your network adapter
```

#### Start Frontend
```powershell
npx expo start
```

---

## 🔗 API Endpoints Available

### Disease Prediction & AI Intelligence
- `POST /api/ai/predict/disease-risk` - Predict disease risk
- `POST /api/ai/predict/integrated-intelligence` - Generate intelligence report
- `GET /api/ai/predict/actions/{farm_id}` - Get action recommendations
- `GET /api/ai/predict/disease-risk/{farm_id}` - Get disease history
- `GET /api/ai/predict/integrated-intelligence/{farm_id}` - Get intelligence report

### Drone Intelligence
- `POST /api/drone/plan-flight` - Plan drone flight
- `POST /api/drone/upload-images` - Upload drone images
- `POST /api/drone/analysis/multispectral` - NDVI analysis
- `POST /api/drone/analysis/3d-reconstruction` - 3D farm modeling
- `POST /api/drone/prediction/yield` - Yield prediction
- `POST /api/drone/harvest/calculate-optimal-window` - Optimal harvest timing
- `POST /api/drone/marketplace/create-aggregation-bundle` - Farmer aggregation
- `POST /api/drone/marketplace/create-pre-harvest-listing` - Pre-harvest sales
- `POST /api/drone/harvest/trigger-alert` - Harvest alerts
- `GET /api/drone/flights/{farm_id}` - Get flight history
- `GET /api/drone/harvest/farmer-alerts/{farmer_id}` - Get harvest alerts

### Exchange Marketplace
- `GET /api/exchange/assets` - List assets
- `POST /api/exchange/assets/create` - Create asset listing
- `GET /api/exchange/assets/{id}` - Asset details
- `POST /api/exchange/assets/{id}/verify` - AI verification
- `POST /api/exchange/orders/create` - Create order
- `GET /api/exchange/orders` - List orders
- `POST /api/exchange/escrow/initiate` - Start escrow
- `POST /api/exchange/escrow/{id}/release` - Release payment
- `POST /api/exchange/escrow/{id}/dispute` - Open dispute
- `GET /api/exchange/disputes` - List disputes

### Market Linkages
- `POST /api/market-linkages/price/fair-price` - Get fair price
- `GET /api/market-linkages/price/trends` - Price trends
- `POST /api/market-linkages/logistics/calculate` - Calculate logistics
- `POST /api/market-linkages/logistics/book` - Book transport
- `POST /api/market-linkages/logistics/pool` - Pool shipments
- `POST /api/market-linkages/liquidity/create-pool` - Create liquidity pool
- `POST /api/market-linkages/liquidity/join-pool` - Join pool
- `GET /api/market-linkages/liquidity/pools` - List pools

### Farms & Growth
- `GET /api/farms` - List farms
- `POST /api/farms` - Create farm
- `GET /api/farms/{id}` - Farm details
- `POST /api/growth/add` - Add growth record
- `GET /api/growth/records` - Growth history

### Storage Monitoring
- `GET /api/storage/conditions` - Current conditions
- `POST /api/storage/add-reading` - Add sensor reading
- `GET /api/storage/alerts` - Storage alerts
- `GET /api/storage/history/{storage_id}` - History

### Location & Climate
- `POST /api/location/update` - Update location
- `GET /api/location/climate-profile` - Climate profile
- `GET /api/location/nearby-farmers` - Nearby farmers
- `GET /api/climate/forecast` - Weather forecast
- `GET /api/climate/risk-score` - Climate risk

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - User profile

### Partners & Groups
- `GET /api/partners` - List partners
- `POST /api/partners/help-request` - Request help
- `GET /api/groups` - List groups
- `POST /api/groups` - Create group

---

## 🧪 Testing the Integration

### 1. Test Backend Health
```powershell
curl http://localhost:8000/docs
```

### 2. Test AI Prediction Endpoint
```powershell
curl -X POST http://localhost:8000/api/ai/predict/disease-risk -H "Content-Type: application/json" -d '{
  "farm_id": "F001",
  "crop_type": "Maize",
  "field_area_hectares": 2.0,
  "current_temperature_c": 28,
  "current_humidity_percentage": 75,
  "current_rainfall_mm_last_week": 30,
  "five_day_forecast": [],
  "soil_moisture_percentage": 45,
  "soil_temperature_c": 25,
  "soil_ph": 6.5,
  "soil_npk": {"nitrogen": 25, "phosphorus": 15, "potassium": 20},
  "days_since_planting": 30,
  "growth_stage": "vegetative",
  "days_to_harvest": 60
}'
```

### 3. Test Drone Intelligence
```powershell
curl -X POST http://localhost:8000/api/drone/plan-flight -H "Content-Type: application/json" -d '{
  "farm_id": "F001",
  "field_area_hectares": 2.0,
  "flight_altitude_m": 50,
  "image_overlap_percentage": 70
}'
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Issue:** Module 'app' not found
```
ModuleNotFoundError: No module named 'app'
```

**Solution:** Make sure you're in the backend directory:
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\backend
..\.venv\Scripts\python.exe run_server.py
```

---

**Issue:** Missing dependencies
```
ModuleNotFoundError: No module named 'stripe'
```

**Solution:** Install dependencies:
```powershell
..\.venv\Scripts\pip.exe install stripe supabase pyjwt email-validator python-dotenv
```

---

### Frontend Connection Issues

**Issue:** Network request failed

**Solution:** Update IP address in `src/config/apiConfig.js`:
```javascript
// For physical device, use your computer's IP
return 'http://192.168.1.XXX:8000'; // Replace XXX

// For Android Emulator
return 'http://10.0.2.2:8000';

// For iOS Simulator
return 'http://localhost:8000';
```

---

**Issue:** Expo modules not found

**Solution:**
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app
npx expo install expo-location expo-camera expo-device
npx expo start -c
```

---

## 📱 Running on Devices

### Android Emulator
1. Start Android Emulator
2. Backend URL: `http://10.0.2.2:8000`
3. Run: `npx expo start` → Press `a`

### iOS Simulator
1. Start iOS Simulator
2. Backend URL: `http://localhost:8000`
3. Run: `npx expo start` → Press `i`

### Physical Device
1. Connect to same WiFi as development computer
2. Find computer's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
3. Update `src/config/apiConfig.js` with IP address
4. Scan QR code with Expo Go app

---

## 🎯 Key Features Connected

### ✅ Disease Prediction System
- Real-time disease risk assessment
- Weather-based predictions
- Treatment recommendations
- Financial impact analysis

### ✅ Drone Intelligence
- Flight path planning
- NDVI multispectral analysis
- 3D farm reconstruction
- Yield predictions
- Optimal harvest windows
- Farmer aggregation marketplace
- Pre-harvest sales listings

### ✅ Exchange Marketplace
- AI-verified asset listings
- Escrow transactions
- Fraud prevention system
- Dispute resolution
- Payment finality

### ✅ Market Linkages
- Fair price discovery
- Smart logistics routing
- Community liquidity pools
- Bulk transport optimization

### ✅ Climate Intelligence
- GPS-based micro-climate profiling
- LCRS (Localized Climate Risk Score)
- 5-day weather forecasts
- Crop vulnerability assessment

---

## 📊 Monitoring

### Backend Logs
Watch the terminal where backend is running for request logs

### Frontend Logs
```powershell
# In Expo terminal, press 'j' to open debugger
# Or use React Native Debugger
```

### API Documentation
Visit: http://localhost:8000/docs

Interactive Swagger UI with all endpoints documented

---

## 🔐 Environment Variables (Optional)

Create `.env` file in backend directory:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Other
SECRET_KEY=your-secret-key
DEBUG=True
```

---

## 🎉 Success Indicators

### Backend Running Successfully
```
✓ Backend imports successful!
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Frontend Running Successfully
```
› Metro waiting on exp://10.1.0.8:8081
› Web is waiting on http://localhost:8081
› Using Expo Go
```

### API Connection Working
- No "Network Request Failed" errors in app
- Data loads in screens
- Image uploads work
- Forms submit successfully

---

## 📞 Support

If you encounter issues:
1. Check this README
2. Review terminal logs
3. Test API endpoints at http://localhost:8000/docs
4. Verify IP address configuration
5. Ensure backend is running before starting frontend

---

**Last Updated:** October 25, 2025
