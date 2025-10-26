# BLE Storage Monitoring - System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGROSHIELD BLE STORAGE SYSTEM                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   FARMER SETUP   │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Place BLE Sensor in Storage Shed                                        │
│     ┌─────────────┐                                                         │
│     │  🌡️💧 BLE   │  Measures:                                              │
│     │   SENSOR    │  - Temperature                                          │
│     │ (Battery)   │  - Humidity                                             │
│     └─────────────┘  - Every 15 minutes                                     │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         │ Bluetooth Low Energy (BLE)
         │ Range: ~10-50 meters
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Phone App Connects (When Farmer is Nearby)                              │
│     ┌──────────────────┐                                                    │
│     │   📱 PHONE APP   │  Actions:                                          │
│     │   (BLE Client)   │  - Scan for sensor                                 │
│     │                  │  - Connect via Bluetooth                           │
│     │  ┌────────────┐  │  - Download readings                               │
│     │  │ Local DB   │  │  - Batch store locally                             │
│     │  └────────────┘  │                                                    │
│     └──────────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         │ HTTPS/Internet
         │ POST /api/storage/ble/upload
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Backend API Processes Data                                              │
│     ┌──────────────────────────────────────────────────────────────┐       │
│     │  FastAPI Backend                                             │       │
│     │                                                               │       │
│     │  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │       │
│     │  │ persistence  │───▶│   advice     │───▶│ sms_provider  │  │       │
│     │  │    .py       │    │    .py       │    │     .py       │  │       │
│     │  └──────────────┘    └──────────────┘    └───────────────┘  │       │
│     │         │                    │                     │         │       │
│     │         ▼                    ▼                     ▼         │       │
│     │  Store readings      Evaluate vs.         Send SMS via      │       │
│     │  to JSON files       crop profile         Twilio or log     │       │
│     └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         │ Returns: {sms_text, level, sent_via_gateway}
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Alert Delivery (Multi-Channel)                                          │
│                                                                              │
│  ┌──────────────────┐           ┌──────────────────┐                       │
│  │  📲 In-App        │           │  📩 SMS          │                       │
│  │  Notification     │           │  (Twilio/Local)  │                       │
│  │                   │           │                  │                       │
│  │  ☀️ DANGER:       │           │  To: +254712...  │                       │
│  │  Maize store is   │           │  Msg: ☀️ DANGER  │                       │
│  │  TOO WARM (30°C)  │           │  Maize store...  │                       │
│  │                   │           │                  │                       │
│  │  [View Details]   │           │  [Open App]      │                       │
│  └──────────────────┘           └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Farmer Takes Action                                                     │
│                                                                              │
│  Based on advice:                                                           │
│  ✅ Open vents to cool storage                                              │
│  ✅ Increase airflow                                                        │
│  ✅ Check for mold/pests                                                    │
│  ✅ Consider moving crops                                                   │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                             CROP PROFILE SYSTEM
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  Crop Profiles Database                                                     │
│                                                                              │
│  ┌────────────┬──────────────────┬────────────────────┐                    │
│  │ Crop       │ Temperature (°C) │ Humidity (%)       │                    │
│  ├────────────┼──────────────────┼────────────────────┤                    │
│  │ Maize      │ 10 - 25          │ 50 - 70            │                    │
│  │ Potatoes   │ 4 - 10           │ 85 - 95            │                    │
│  │ Rice       │ 12 - 18          │ 60 - 70            │                    │
│  │ Cassava    │ 0 - 5            │ 85 - 90            │                    │
│  │ Beans      │ 10 - 20          │ 50 - 65            │                    │
│  │ Onions     │ 0 - 4            │ 65 - 70            │                    │
│  └────────────┴──────────────────┴────────────────────┘                    │
│                                                                              │
│  Retrieved via: GET /api/storage/crop_profiles                              │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                          ALERT EVALUATION LOGIC
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  Sensor Reading: {temp: 30°C, humidity: 65%}                                │
│  Crop: Maize                                                                │
│  Profile: {temp_max: 25°C, humidity_max: 70%}                               │
│                                                                              │
│  Evaluation:                                                                │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │  if temp > temp_max:                                         │          │
│  │      level = "too_hot" ✅ MATCHED (30 > 25)                  │          │
│  │      advice = "Open vents tonight and increase airflow"      │          │
│  │                                                               │          │
│  │  elif temp < temp_min:                                       │          │
│  │      level = "too_cold"                                      │          │
│  │                                                               │          │
│  │  elif humidity > humidity_max:                               │          │
│  │      level = "too_humid"                                     │          │
│  │                                                               │          │
│  │  else:                                                        │          │
│  │      level = "ok"                                            │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  Result: level = "too_hot"                                                  │
│  Message (English): "☀️ DANGER: maize store is TOO WARM (30°C).             │
│                      Open vents tonight and increase airflow."              │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                         LOCALIZATION EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  English (en)                                                                │
│  ☀️ DANGER: maize store is TOO WARM (30°C).                                 │
│     Open vents tonight and increase airflow.                                │
│                                                                              │
│  Swahili (sw)                                                                │
│  ☀️ HATARI: Hifadhi ya maize ina JOTO JAA (30°C).                           │
│     Open vents tonight and increase airflow.                                │
│                                                                              │
│  💧 DANGER: Humidity is 80%. High risk of mold on your maize.               │
│     Increase airflow NOW and reduce humidity; consider drying.              │
│                                                                              │
│  💧 HATARI: Unyevu ni 80%. Hatari ya ukungu kwa maize.                      │
│     Increase airflow NOW and reduce humidity; consider drying.              │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                              DATA PERSISTENCE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  backend/app/data/                                                          │
│                                                                              │
│  ├── sensor_readings.json                                                   │
│  │   {                                                                      │
│  │     "ble_sensor_001": [                                                  │
│  │       {"ts": "2025-10-24T10:00:00Z", "temp": 22, "hum": 60},            │
│  │       {"ts": "2025-10-24T11:00:00Z", "temp": 30, "hum": 65}             │
│  │     ]                                                                    │
│  │   }                                                                      │
│  │                                                                           │
│  ├── crop_profiles.json                                                     │
│  │   {                                                                      │
│  │     "maize": {"temperature": {"min": 10, "max": 25}, ...}               │
│  │   }                                                                      │
│  │                                                                           │
│  ├── farmer_settings.json                                                   │
│  │   {                                                                      │
│  │     "farmer_001": {"crop": "potatoes", "language": "sw", "phone": ...}  │
│  │   }                                                                      │
│  │                                                                           │
│  └── alerts_log.json                                                        │
│      [                                                                       │
│        {"farmer_id": "farmer_001", "level": "too_hot", "ts": "...", ...}   │
│      ]                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                           API ENDPOINTS SUMMARY
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  GET  /api/storage/crop_profiles                                            │
│       → Returns all crop profiles                                           │
│                                                                              │
│  POST /api/storage/crop_profiles                                            │
│       → Updates crop profiles (admin only)                                  │
│                                                                              │
│  POST /api/storage/ble/upload                                               │
│       → Upload BLE sensor readings batch                                    │
│       → Returns alert message and level                                     │
│                                                                              │
│  GET  /api/storage/history?sensor_id=xxx&limit=100                          │
│       → Returns historical readings for sensor                              │
│                                                                              │
│  POST /api/storage/select_crop                                              │
│       → Set farmer's crop, language, phone preferences                      │
│                                                                              │
│  POST /api/storage/trigger_check                                            │
│       → Manually trigger alert evaluation                                   │
└─────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                            DEPLOYMENT CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  Backend Setup:                                                              │
│  ☐ Install dependencies: pip install -r backend/requirements.txt            │
│  ☐ Configure Twilio (optional): export TWILIO_ACCOUNT=...                   │
│  ☐ Start server: python backend/run_dev.py                                  │
│  ☐ Test API: http://localhost:8000/docs                                     │
│                                                                              │
│  Mobile App Setup:                                                           │
│  ☐ Install BLE library (react-native-ble-plx or flutter_blue_plus)          │
│  ☐ Implement sensor scanning & reading                                      │
│  ☐ Add batch upload to /api/storage/ble/upload                              │
│  ☐ Display alert notifications                                              │
│  ☐ Add crop selection UI                                                    │
│  ☐ Show history charts                                                      │
│                                                                              │
│  Testing:                                                                    │
│  ☐ Run unit tests: python backend/tests/test_advice.py                      │
│  ☐ Test API endpoints: backend/test_api.bat                                 │
│  ☐ Test BLE connection with real sensor                                     │
│  ☐ Verify SMS delivery (or logging)                                         │
│  ☐ Test localization (English & Swahili)                                    │
└─────────────────────────────────────────────────────────────────────────────┘

```
