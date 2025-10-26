# AgroShield Frontend

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

If you encounter errors, try:
```bash
npm install --legacy-peer-deps
```

### Step 2: Start Expo Dev Server

```bash
npx expo start
```

This will open an interactive menu where you can:
- Press `a` to run on Android device/emulator
- Press `i` to run on iOS device/simulator  
- Press `w` to run in web browser
- Scan QR code with **Expo Go** app on your phone

## 📱 Expo Go App

Download Expo Go on your mobile device:
- **Android**: [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
- **iOS**: [App Store](https://apps.apple.com/app/expo-go/id982107779)

## ⚙️ Configuration

### API Base URL

Update the backend API URL in these files:
- `src/screens/FarmerMarketplace.js` (line ~10)
- `src/screens/BuyerMarketplace.js` (line ~10)

Change from:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

To your backend URL:
```javascript
const API_BASE_URL = 'http://192.168.1.100:8000';  // Your computer's IP
```

### Finding Your IP Address

**Windows**:
```bash
ipconfig
```
Look for "IPv4 Address" under your WiFi/Ethernet adapter

**macOS/Linux**:
```bash
ifconfig | grep "inet "
```

## 📂 Project Structure

```
frontend/
├── App.js                          # Main entry point
├── package.json                    # Dependencies
├── app.json                        # Expo configuration
├── babel.config.js                 # Babel configuration
└── src/
    └── screens/
        ├── FarmerMarketplace.js    # Farmer portal (1,200 lines)
        ├── BuyerMarketplace.js     # Buyer portal (1,000 lines)
        ├── StorageBLE.js           # BLE sensor monitoring
        ├── VillageGroups.js        # Community features
        ├── Notifications.js        # Notifications screen
        └── PartnerPortal.js        # Partner campaigns
```

## 🔧 Troubleshooting

### Error: "expo-cli not found"

Use `npx expo` instead of global installation:
```bash
npx expo start
```

### Error: "Unable to resolve module"

Clear cache and reinstall:
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Error: "Metro bundler failed"

Reset Metro cache:
```bash
npx expo start --clear
```

### Error: Plugin not found (expo-camera, expo-location)

These plugins are included as dependencies and will be auto-configured by Expo. Just install packages:
```bash
npm install
```

### Cannot connect to backend

1. Make sure backend is running: `http://localhost:8000/docs`
2. Use your computer's IP address (not localhost) in mobile app
3. Ensure phone and computer are on same WiFi network
4. Disable firewall temporarily to test connection

## 📦 Key Features Implemented

### 1. Farmer Marketplace (`FarmerMarketplace.js`)
- ✅ Create listings with photos (up to 5)
- ✅ View incoming buyer offers
- ✅ Accept/Counter/Decline offers
- ✅ Track contracts and payments
- ✅ Confirm delivery with photos
- ✅ View AI market insights

### 2. Buyer Marketplace (`BuyerMarketplace.js`)
- ✅ Business registration & KYB verification
- ✅ Location-based search (50/100/150km radius)
- ✅ AI supply forecasting (30/60 days)
- ✅ Make offers to farmers
- ✅ M-Pesa deposit payments
- ✅ Track orders and confirm receipt

### 3. BLE Storage Monitoring (`StorageBLE.js`)
- ✅ Scan and connect to BLE sensors
- ✅ Real-time temperature & humidity monitoring
- ✅ Crop-specific threshold alerts
- ✅ Historical data graphs
- ✅ AI spoilage predictions

## 🌐 Backend Integration

The app connects to these API endpoints:

**Marketplace (Farmer)**:
- `POST /api/marketplace/farmer/create-listing`
- `GET /api/marketplace/farmer/my-listings/{farmer_id}`
- `GET /api/marketplace/farmer/offers/{farmer_id}`
- `POST /api/marketplace/farmer/respond-to-offer`

**Marketplace (Buyer)**:
- `POST /api/marketplace/buyer/register-buyer`
- `GET /api/marketplace/buyer/search-listings`
- `GET /api/marketplace/buyer/predicted-supply`
- `POST /api/marketplace/buyer/make-offer`

**Storage**:
- `POST /api/storage/readings`
- `GET /api/storage/thresholds/{crop}`
- `GET /api/storage/alerts/{farmer_id}`

**Regional Data**:
- `GET /api/regional/comprehensive/{user_id}`
- `GET /api/regional/weather?lat=&lon=`
- `GET /api/regional/market-prices?lat=&lon=`

## 🎨 UI Components Used

- **SafeAreaView**: Safe layouts for notched devices
- **ScrollView**: Scrollable content areas
- **FlatList**: Optimized lists for large datasets
- **TouchableOpacity**: Touchable buttons
- **Modal**: Popup forms and dialogs
- **ActivityIndicator**: Loading spinners
- **Image**: Photo displays
- **Picker**: Dropdown selections
- **TextInput**: Form inputs

## 📱 Permissions Required

### Android
- Camera (crop scanning)
- Location (weather, market data)
- Bluetooth (BLE sensors)
- Storage (photo uploads)

### iOS
- Camera Usage
- Photo Library Access
- Location When In Use
- Bluetooth Always

All permissions are configured in `app.json`.

## 🚀 Deployment

### Build for Android
```bash
npx expo build:android
```

### Build for iOS
```bash
npx expo build:ios
```

### Publish Update (OTA)
```bash
npx expo publish
```

## 📖 Documentation

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [Marketplace Frontend Guide](../MARKETPLACE_FRONTEND_GUIDE.md)
- [API Reference](../API_REFERENCE.md)

## 💡 Development Tips

1. **Hot Reload**: Edit code and see changes instantly
2. **Console Logs**: Use `console.log()` for debugging
3. **React DevTools**: Install browser extension for debugging
4. **Network Inspector**: Use Expo Dev Tools to inspect API calls
5. **Performance**: Use `React.memo()` to optimize re-renders

## 🤝 Need Help?

- Check [MARKETPLACE_FRONTEND_GUIDE.md](../MARKETPLACE_FRONTEND_GUIDE.md)
- Review existing screen implementations in `src/screens/`
- Test API endpoints in Swagger UI: `http://localhost:8000/docs`
- Open an issue on GitHub

---

**Made with ❤️ for African Farmers** 🌾🇰🇪
