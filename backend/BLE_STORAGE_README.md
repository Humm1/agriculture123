# BLE Storage Monitoring Feature

## Overview
This feature enables farmers to use their phones as a **hub** to collect sensor data from low-cost Bluetooth (BLE) temperature and humidity sensors placed in storage sheds. The backend provides:

- **Crop-specific profiles** (temperature and humidity ranges)
- **Automated alerts** via SMS when conditions are unsafe
- **Localized actionable advice** (English and Swahili currently)
- **Historical data tracking** for analysis

---

## Architecture

### Backend Components

1. **Services** (`backend/app/services/`)
   - `persistence.py` – JSON-based simple storage for sensor readings, crop profiles, farmer settings, and alerts
   - `advice.py` – Evaluates sensor readings against crop profiles; formats localized messages
   - `sms_provider.py` – Abstraction for SMS sending (Twilio gateway or fallback logging)

2. **Storage Routes** (`backend/app/routes/storage.py`)
   - `/api/storage/crop_profiles` (GET/POST) – Retrieve or update crop profiles
   - `/api/storage/ble/upload` (POST) – Upload sensor readings from phone
   - `/api/storage/history` (GET) – Retrieve historical readings for a sensor
   - `/api/storage/select_crop` (POST) – Set farmer's crop selection and language
   - `/api/storage/trigger_check` (POST) – Manually trigger an alert check

---

## API Endpoints

### GET `/api/storage/crop_profiles`
Returns all crop profiles with temperature and humidity ranges.

**Response:**
```json
{
  "maize": {
    "temperature": {"min": 10, "max": 25},
    "humidity": {"min": 50, "max": 70}
  },
  "potatoes": {
    "temperature": {"min": 4, "max": 10},
    "humidity": {"min": 85, "max": 95}
  }
}
```

---

### POST `/api/storage/ble/upload`
Upload BLE sensor readings batch from the phone.

**Request Body:**
```json
{
  "farmer_id": "farmer_123",
  "sensor_id": "ble_sensor_001",
  "readings": [
    {
      "ts": "2025-10-24T12:00:00Z",
      "temperature": 30,
      "humidity": 60
    }
  ],
  "phone_number": "+254712345678",
  "crop": "maize",
  "language": "sw"
}
```

**Response:**
```json
{
  "result": {
    "level": "too_hot",
    "details": {"temp": 30, "threshold": 25}
  },
  "sms_text": "☀️ HATARI: Hifadhi ya maize ina JOTO JAA (30°C). Open vents tonight and increase airflow.",
  "sent_via_gateway": false
}
```

---

### GET `/api/storage/history?sensor_id=ble_sensor_001&limit=100`
Retrieve historical readings for a sensor.

**Response:**
```json
{
  "sensor_id": "ble_sensor_001",
  "readings": [
    {
      "ts": "2025-10-24T11:00:00Z",
      "temperature": 28,
      "humidity": 55
    }
  ]
}
```

---

### POST `/api/storage/select_crop`
Set farmer's crop selection and notification preferences.

**Form Data:**
- `farmer_id` – unique farmer identifier
- `crop` – crop name (e.g., "maize", "potatoes")
- `language` – 2-letter code ("en", "sw")
- `phone` – phone number for SMS alerts (optional)

**Response:**
```json
{
  "saved": true,
  "settings": {
    "crop": "potatoes",
    "language": "sw",
    "phone": "+254712345678"
  }
}
```

---

### POST `/api/storage/trigger_check`
Manually trigger an alert check for the latest sensor reading.

**Form Data:**
- `farmer_id`
- `sensor_id`

**Response:**
```json
{
  "level": "ok",
  "message": "✅ SAWA: Mazingira ya hifadhi ni salama kwa potatoes.",
  "sent_via_gateway": false
}
```

---

## Configuration

### SMS Provider (Twilio)
Set environment variables to enable SMS sending:

```bash
export TWILIO_ACCOUNT=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export TWILIO_TOKEN=your_auth_token
export TWILIO_FROM=+1234567890
```

If these are not set, alerts are logged to the console instead.

---

## Data Storage

All data is stored in JSON files under `backend/app/data/`:
- `sensor_readings.json` – sensor data grouped by sensor ID
- `crop_profiles.json` – crop-specific environmental ranges
- `farmer_settings.json` – farmer preferences (crop, language, phone)
- `alerts_log.json` – history of all alerts triggered

---

## Localization

Currently supports:
- **English** (`en`)
- **Swahili** (`sw`)

Messages are emoji-rich and actionable:
- ☀️ DANGER: maize store is TOO WARM (30°C). Open vents tonight and increase airflow.
- 💧 HATARI: Unyevu ni 80%. Hatari ya ukungu kwa maize. Increase airflow NOW and reduce humidity; consider drying.

To add a new language, edit `backend/app/services/advice.py` and add templates to the `TEMPLATES` dictionary.

---

## Testing

Run unit tests for the advice engine:

```bash
python backend/tests/test_advice.py
```

**Output:**
```
✅ test_evaluate_maize_ok passed
✅ test_evaluate_maize_too_hot passed
✅ test_evaluate_maize_too_humid passed
✅ test_evaluate_potatoes_ok passed
✅ test_evaluate_potatoes_too_cold passed
✅ test_format_message_en passed
✅ test_format_message_sw passed

✅ All tests passed!
```

---

## Mobile App Integration

The phone app should:

1. **Connect to BLE sensors** via Bluetooth when near storage
2. **Upload readings** to `/api/storage/ble/upload` 
3. **Display the returned `sms_text`** as a simple notification
4. **Optionally send SMS locally** if the backend returns `sent_via_gateway: false`
5. **Show history** by fetching `/api/storage/history`
6. **Let farmers select crop** via `/api/storage/select_crop`

---

## Future Enhancements

- Add more crops (rice, cassava, etc.)
- Implement PostgreSQL or SQLite for persistence
- Add user authentication and farmer accounts
- Real-time WebSocket alerts
- Advanced analytics and trend visualization
- Multi-sensor support per farmer

---

## License
This feature is part of the AgroShield project. See main README for licensing.
