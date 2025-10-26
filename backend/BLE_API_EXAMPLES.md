# Example Test Payloads for BLE Storage API

## 1. Upload BLE Sensor Readings

**POST** `http://localhost:8000/api/storage/ble/upload`

```json
{
  "farmer_id": "farmer_001",
  "sensor_id": "ble_sensor_maize_001",
  "readings": [
    {
      "ts": "2025-10-24T10:00:00Z",
      "temperature": 22,
      "humidity": 60
    },
    {
      "ts": "2025-10-24T11:00:00Z",
      "temperature": 30,
      "humidity": 65
    }
  ],
  "phone_number": "+254712345678",
  "crop": "maize",
  "language": "en"
}
```

**Expected Response:**
```json
{
  "result": {
    "level": "too_hot",
    "details": {
      "temp": 30,
      "threshold": 25
    }
  },
  "sms_text": "☀️ DANGER: maize store is TOO WARM (30°C). Open vents tonight and increase airflow.",
  "sent_via_gateway": false
}
```

---

## 2. Get Crop Profiles

**GET** `http://localhost:8000/api/storage/crop_profiles`

**Expected Response:**
```json
{
  "maize": {
    "temperature": {
      "min": 10,
      "max": 25
    },
    "humidity": {
      "min": 50,
      "max": 70
    }
  },
  "potatoes": {
    "temperature": {
      "min": 4,
      "max": 10
    },
    "humidity": {
      "min": 85,
      "max": 95
    }
  }
}
```

---

## 3. Select Farmer's Crop

**POST** `http://localhost:8000/api/storage/select_crop`

**Form Data:**
- `farmer_id=farmer_001`
- `crop=potatoes`
- `language=sw`
- `phone=+254712345678`

**Expected Response:**
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

## 4. Get Sensor History

**GET** `http://localhost:8000/api/storage/history?sensor_id=ble_sensor_maize_001&limit=10`

**Expected Response:**
```json
{
  "sensor_id": "ble_sensor_maize_001",
  "readings": [
    {
      "ts": "2025-10-24T10:00:00Z",
      "temperature": 22,
      "humidity": 60
    },
    {
      "ts": "2025-10-24T11:00:00Z",
      "temperature": 30,
      "humidity": 65
    }
  ]
}
```

---

## 5. Manually Trigger Alert Check

**POST** `http://localhost:8000/api/storage/trigger_check`

**Form Data:**
- `farmer_id=farmer_001`
- `sensor_id=ble_sensor_maize_001`

**Expected Response:**
```json
{
  "level": "too_hot",
  "message": "☀️ DANGER: maize store is TOO WARM (30°C). Open vents tonight and increase airflow.",
  "sent_via_gateway": false
}
```

---

## Testing with curl (Windows cmd)

### Upload BLE Readings
```cmd
curl -X POST http://localhost:8000/api/storage/ble/upload ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"sensor_id\":\"ble_sensor_maize_001\",\"readings\":[{\"temperature\":30,\"humidity\":65}],\"phone_number\":\"+254712345678\",\"crop\":\"maize\",\"language\":\"en\"}"
```

### Get Crop Profiles
```cmd
curl http://localhost:8000/api/storage/crop_profiles
```

### Get History
```cmd
curl "http://localhost:8000/api/storage/history?sensor_id=ble_sensor_maize_001&limit=10"
```

### Select Crop
```cmd
curl -X POST http://localhost:8000/api/storage/select_crop ^
  -F "farmer_id=farmer_001" ^
  -F "crop=potatoes" ^
  -F "language=sw" ^
  -F "phone=+254712345678"
```

### Trigger Alert Check
```cmd
curl -X POST http://localhost:8000/api/storage/trigger_check ^
  -F "farmer_id=farmer_001" ^
  -F "sensor_id=ble_sensor_maize_001"
```

---

## Notes
- Replace `localhost:8000` with your server URL if deployed
- For Twilio SMS to work, set environment variables: `TWILIO_ACCOUNT`, `TWILIO_TOKEN`, `TWILIO_FROM`
- Without Twilio config, alerts are logged to console
