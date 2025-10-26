# 📱 Mobile App Integration Guide - BLE Storage Monitoring

## Overview
This guide shows how to integrate the phone-as-hub BLE storage monitoring feature into the AgroShield mobile app.

---

## Architecture Flow

```
[BLE Sensor] ──Bluetooth──> [Phone App] ──HTTP──> [Backend API]
                                 ↓
                         [Local Storage]
                                 ↓
                         [SMS Fallback]
```

---

## Implementation Steps

### 1️⃣ Install BLE Library

For React Native:
```bash
npm install react-native-ble-plx
```

For Flutter:
```bash
flutter pub add flutter_blue_plus
```

---

### 2️⃣ Scan & Connect to BLE Sensors

#### React Native Example:
```javascript
import { BleManager } from 'react-native-ble-plx';

const manager = new BleManager();

// Scan for sensors
manager.startDeviceScan(null, null, (error, device) => {
  if (error) {
    console.error(error);
    return;
  }
  
  // Filter for your sensor (e.g., by name or service UUID)
  if (device.name && device.name.includes('TempHumidity')) {
    manager.stopDeviceScan();
    connectToSensor(device);
  }
});

// Connect and read data
async function connectToSensor(device) {
  const connected = await device.connect();
  await connected.discoverAllServicesAndCharacteristics();
  
  // Read temperature & humidity characteristics
  const tempChar = await connected.readCharacteristicForService(
    'temp-service-uuid',
    'temp-characteristic-uuid'
  );
  
  const humChar = await connected.readCharacteristicForService(
    'humidity-service-uuid',
    'humidity-characteristic-uuid'
  );
  
  const temperature = decodeTemperature(tempChar.value);
  const humidity = decodeHumidity(humChar.value);
  
  // Store reading for batch upload
  storeReading({ temperature, humidity, ts: new Date().toISOString() });
}
```

---

### 3️⃣ Batch Upload Readings to Backend

Upload sensor data when:
- Farmer manually refreshes
- App moves to background
- Every N minutes (configurable)

```javascript
async function uploadReadings(farmerId, sensorId, readings) {
  const payload = {
    farmer_id: farmerId,
    sensor_id: sensorId,
    readings: readings, // Array of {ts, temperature, humidity}
    phone_number: '+254712345678', // Optional: for SMS alerts
    crop: 'maize', // From farmer settings
    language: 'sw' // From farmer settings or device locale
  };
  
  const response = await fetch('http://YOUR_BACKEND/api/storage/ble/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  
  // Show alert message to farmer
  if (result.sms_text) {
    showNotification(result.sms_text);
  }
  
  // If backend didn't send SMS (no Twilio configured), send locally
  if (!result.sent_via_gateway && payload.phone_number) {
    sendSMSLocally(payload.phone_number, result.sms_text);
  }
  
  return result;
}
```

---

### 4️⃣ Show Alert Notifications

Display emoji-rich alerts to farmer:

```javascript
function showNotification(message) {
  // Use push notification or in-app alert
  Alert.alert('Storage Alert', message, [
    { text: 'OK', style: 'default' }
  ]);
  
  // Or local push notification
  PushNotification.localNotification({
    title: '🚨 Storage Alert',
    message: message,
    playSound: true,
    soundName: 'default'
  });
}
```

---

### 5️⃣ Let Farmer Select Crop

Simple dropdown to set crop and language:

```javascript
async function saveFarmerCrop(farmerId, crop, language, phone) {
  const formData = new FormData();
  formData.append('farmer_id', farmerId);
  formData.append('crop', crop);
  formData.append('language', language);
  formData.append('phone', phone);
  
  const response = await fetch('http://YOUR_BACKEND/api/storage/select_crop', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// UI Example (React Native)
<Picker
  selectedValue={selectedCrop}
  onValueChange={(crop) => {
    setSelectedCrop(crop);
    saveFarmerCrop(farmerId, crop, language, phone);
  }}
>
  <Picker.Item label="Maize" value="maize" />
  <Picker.Item label="Potatoes" value="potatoes" />
  <Picker.Item label="Rice" value="rice" />
  <Picker.Item label="Cassava" value="cassava" />
  <Picker.Item label="Beans" value="beans" />
  <Picker.Item label="Onions" value="onions" />
</Picker>
```

---

### 6️⃣ Display History & Trends

Fetch and visualize sensor history:

```javascript
async function fetchHistory(sensorId, limit = 100) {
  const response = await fetch(
    `http://YOUR_BACKEND/api/storage/history?sensor_id=${sensorId}&limit=${limit}`
  );
  const data = await response.json();
  return data.readings;
}

// Example: Use react-native-chart-kit for visualization
import { LineChart } from 'react-native-chart-kit';

function StorageHistoryChart({ readings }) {
  const temps = readings.map(r => r.temperature);
  const labels = readings.map(r => new Date(r.ts).getHours() + 'h');
  
  return (
    <LineChart
      data={{
        labels: labels,
        datasets: [{ data: temps }]
      }}
      width={screenWidth - 32}
      height={220}
      chartConfig={{
        backgroundColor: '#1cc910',
        backgroundGradientFrom: '#eff3ff',
        backgroundGradientTo: '#efefef',
        decimalPlaces: 1,
        color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`
      }}
    />
  );
}
```

---

### 7️⃣ SMS Fallback (Local)

If backend SMS fails, send locally:

```javascript
import { SMS } from 'expo';

async function sendSMSLocally(phoneNumber, message) {
  const isAvailable = await SMS.isAvailableAsync();
  if (isAvailable) {
    const { result } = await SMS.sendSMSAsync(
      [phoneNumber],
      message
    );
    console.log('SMS sent:', result);
  }
}
```

---

## UI/UX Best Practices

### 1. **Simple Setup Flow**
```
[Step 1: Scan for Sensor] → [Step 2: Select Crop] → [Step 3: Done!]
```

### 2. **Clear Status Indicators**
- 🟢 **Green**: Conditions OK
- 🟡 **Yellow**: Warning (near threshold)
- 🔴 **Red**: Danger (threshold exceeded)

### 3. **Actionable Advice**
Show advice prominently with emoji icons:
```
☀️ TOO HOT
Your maize store is 30°C (safe max: 25°C)

What to do:
✅ Open vents tonight
✅ Increase airflow
```

### 4. **Offline Support**
- Cache crop profiles locally
- Store readings and sync when online
- Show last known status even offline

### 5. **Simple Language**
- Use local language (Swahili, English, etc.)
- Avoid technical jargon
- Use large, readable fonts

---

## Sample Screen Layout

```
┌─────────────────────────────────┐
│  📦 Maize Storage               │
├─────────────────────────────────┤
│                                 │
│  🌡️  Temperature: 30°C          │
│      [▓▓▓▓▓▓▓▓▓▓░░] TOO HOT!    │
│                                 │
│  💧  Humidity: 65%              │
│      [▓▓▓▓▓░░░░░░░] OK          │
│                                 │
│  ⚠️  WARNING                    │
│  Your maize store is TOO WARM   │
│  Open vents tonight!            │
│                                 │
│  [View History] [Refresh Data]  │
│                                 │
└─────────────────────────────────┘
```

---

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/storage/crop_profiles` | GET | Get all crop profiles |
| `/api/storage/ble/upload` | POST | Upload sensor readings |
| `/api/storage/history` | GET | Get sensor history |
| `/api/storage/select_crop` | POST | Set farmer's crop |
| `/api/storage/trigger_check` | POST | Manual alert check |

---

## Testing Checklist

- [ ] BLE sensor scan & connect works
- [ ] Temperature & humidity read correctly
- [ ] Batch upload to backend succeeds
- [ ] Alert notifications display properly
- [ ] Crop selection saves and persists
- [ ] History chart renders correctly
- [ ] SMS fallback works offline
- [ ] UI is readable in sunlight (high contrast)
- [ ] Works on low-end Android devices (< 2GB RAM)
- [ ] Handles poor network connectivity gracefully

---

## Recommended BLE Sensors

### Budget Options ($25-40):
- **Xiaomi Mi Temperature and Humidity Monitor 2** (~$10)
  - Good for basic monitoring
  - Limited range (~10m)
  
- **Govee H5075** (~$25)
  - Longer battery life
  - Better range (~50m)
  
- **SwitchBot Meter Plus** (~$30)
  - Large display
  - Cloud sync option

### Professional Options ($50-100):
- **Ruuvi Tag Pro** (~$50)
  - Industrial-grade
  - Weatherproof
  - Long battery (5+ years)

---

## Security Considerations

1. **Validate Sensor Data**
   - Reject impossible values (e.g., temp > 100°C)
   - Rate-limit uploads to prevent abuse

2. **Authenticate Farmers**
   - Use JWT tokens for API requests
   - Store farmer_id securely

3. **Encrypt Sensitive Data**
   - Use HTTPS for all API calls
   - Don't store phone numbers in plain text

---

## Performance Tips

1. **Batch Readings**
   - Don't upload every reading individually
   - Batch 10-50 readings per upload

2. **Background Sync**
   - Use background tasks to sync when app is closed
   - React Native: `react-native-background-task`

3. **Local Caching**
   - Cache crop profiles locally
   - Only fetch when needed

4. **Optimize Charts**
   - Downsample data for charts (e.g., 1 point per hour)
   - Use virtualization for long lists

---

## Support & Resources

- **API Docs**: http://YOUR_BACKEND/docs
- **Backend README**: `backend/BLE_STORAGE_README.md`
- **API Examples**: `backend/BLE_API_EXAMPLES.md`
- **Test Script**: `backend/test_api.bat`

---

## Questions?

Contact the backend team or check the implementation summary:
- `backend/IMPLEMENTATION_SUMMARY.md`

---

**Happy coding! 🚀**
