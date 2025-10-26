# 📦 Frontend Migration Guide
## Transferring Files from `frontend/` to `agroshield-app/`

This guide shows exactly which files to copy from your existing `frontend/` directory into the fresh Expo `agroshield-app/` project to make it fully functional on both web and mobile.

---

## 📋 Files to Transfer

### ✅ **1. Configuration Files**

| Source | Destination | Purpose |
|--------|-------------|---------|
| `frontend/app.json` | `agroshield-app/app.json` | **REPLACE** - Expo config with web support |
| `frontend/package.json` | `agroshield-app/package.json` | **MERGE** - Dependencies list |
| `frontend/babel.config.js` | `agroshield-app/babel.config.js` | **REPLACE** - Babel configuration |
| `frontend/metro.config.js` | `agroshield-app/metro.config.js` | **COPY** - Metro bundler config |
| `frontend/webpack.config.js` | `agroshield-app/webpack.config.js` | **COPY** - Web bundler config |
| `frontend/index.html` | `agroshield-app/index.html` | **COPY** - Web entry point |

### ✅ **2. Main App File**

| Source | Destination | Purpose |
|--------|-------------|---------|
| `frontend/App.js` | `agroshield-app/App.js` | **REPLACE** - Main component with web responsiveness |

### ✅ **3. Screen Files (Core Features)**

Create directory: `agroshield-app/src/screens/`

| Source | Destination | Lines | Features |
|--------|-------------|-------|----------|
| `frontend/src/screens/FarmerMarketplace.js` | `agroshield-app/src/screens/FarmerMarketplace.js` | 1,200 | Farmer selling portal |
| `frontend/src/screens/BuyerMarketplace.js` | `agroshield-app/src/screens/BuyerMarketplace.js` | 1,000 | Buyer sourcing portal |

### ✅ **4. Additional Screens (From Mobile App)**

If these exist in `mobile/src/screens/`, copy them:

| Source | Destination | Purpose |
|--------|-------------|---------|
| `mobile/src/screens/StorageBLE.js` | `agroshield-app/src/screens/StorageBLE.js` | BLE sensor monitoring |
| `mobile/src/screens/VillageGroups.js` | `agroshield-app/src/screens/VillageGroups.js` | Community groups |
| `mobile/src/screens/Notifications.js` | `agroshield-app/src/screens/Notifications.js` | Notifications |
| `mobile/src/screens/PartnerPortal.js` | `agroshield-app/src/screens/PartnerPortal.js` | Partner campaigns |
| `mobile/src/screens/PartnerCampaigns.js` | `agroshield-app/src/screens/PartnerCampaigns.js` | Campaign listings |

### ✅ **5. Navigation (Optional - Recommended)**

If you want full navigation from the mobile app:

```
mobile/src/navigation/  →  agroshield-app/src/navigation/
├── AppNavigator.js         # Root navigator
├── MainTabNavigator.js     # Bottom tabs
├── HomeStack.js            # Home navigation
├── FarmStack.js            # Farm management
├── GroupsStack.js          # Village groups
├── CampaignsStack.js       # Partner portal
└── ProfileStack.js         # Profile section
```

### ✅ **6. Services & API (Recommended)**

```
mobile/src/services/  →  agroshield-app/src/services/
└── api.js                  # Complete API client (all endpoints)
```

### ✅ **7. Context & State Management**

```
mobile/src/context/  →  agroshield-app/src/context/
└── AuthContext.js          # Authentication state
```

### ✅ **8. Theme & Design System**

```
mobile/src/theme/  →  agroshield-app/src/theme/
└── theme.js                # Colors, spacing, typography
```

### ✅ **9. Assets (Optional)**

```
frontend/assets/  →  agroshield-app/assets/
├── icon.png                # App icon
├── splash.png              # Splash screen
├── adaptive-icon.png       # Android adaptive icon
└── favicon.png             # Web favicon
```

---

## 🚀 Step-by-Step Migration Process

### **Step 1: Install Dependencies**

```bash
cd agroshield-app
npm install --legacy-peer-deps
```

### **Step 2: Copy Configuration Files**

```bash
# Windows PowerShell
cd c:\Users\Codeternal\Desktop\agroshield

# Copy config files
copy frontend\app.json agroshield-app\app.json
copy frontend\babel.config.js agroshield-app\babel.config.js
copy frontend\metro.config.js agroshield-app\metro.config.js
copy frontend\webpack.config.js agroshield-app\webpack.config.js
copy frontend\index.html agroshield-app\index.html
```

### **Step 3: Merge package.json**

Open `agroshield-app/package.json` and add these dependencies:

```json
{
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.72.6",
    "react-dom": "18.2.0",
    "react-native-web": "~0.19.6",
    "expo": "~49.0.15",
    "expo-status-bar": "~1.6.0",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "react-native-screens": "~3.24.0",
    "react-native-safe-area-context": "4.6.3",
    "axios": "^1.5.1",
    "@react-native-async-storage/async-storage": "1.18.2",
    "expo-camera": "~13.4.4",
    "expo-image-picker": "~14.3.2",
    "expo-document-picker": "~11.5.4",
    "expo-location": "~16.1.0",
    "@react-native-picker/picker": "^2.5.1",
    "react-native-maps": "1.7.1",
    "react-native-ble-manager": "^11.5.3",
    "react-native-ble-plx": "^3.1.2"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@expo/webpack-config": "^19.0.0"
  }
}
```

Then run:
```bash
npm install --legacy-peer-deps
```

### **Step 4: Copy Main App File**

```bash
copy frontend\App.js agroshield-app\App.js
```

### **Step 5: Copy Screen Files**

```bash
# Create src/screens directory
mkdir agroshield-app\src
mkdir agroshield-app\src\screens

# Copy marketplace screens
copy frontend\src\screens\FarmerMarketplace.js agroshield-app\src\screens\FarmerMarketplace.js
copy frontend\src\screens\BuyerMarketplace.js agroshield-app\src\screens\BuyerMarketplace.js
```

### **Step 6: Copy Additional Screens (If Available)**

Check if these exist in `mobile/src/screens/` and copy them:

```bash
# Check if mobile directory exists
dir mobile\src\screens

# Copy if they exist
copy mobile\src\screens\StorageBLE.js agroshield-app\src\screens\
copy mobile\src\screens\VillageGroups.js agroshield-app\src\screens\
copy mobile\src\screens\Notifications.js agroshield-app\src\screens\
copy mobile\src\screens\PartnerPortal.js agroshield-app\src\screens\
copy mobile\src\screens\PartnerCampaigns.js agroshield-app\src\screens\
```

### **Step 7: Copy Services (API Client)**

```bash
mkdir agroshield-app\src\services
copy mobile\src\services\api.js agroshield-app\src\services\api.js
```

### **Step 8: Copy Theme**

```bash
mkdir agroshield-app\src\theme
copy mobile\src\theme\theme.js agroshield-app\src\theme\theme.js
```

### **Step 9: Copy Context (Auth)**

```bash
mkdir agroshield-app\src\context
copy mobile\src\context\AuthContext.js agroshield-app\src\context\AuthContext.js
```

### **Step 10: Copy Navigation (Optional)**

```bash
mkdir agroshield-app\src\navigation
xcopy mobile\src\navigation\*.js agroshield-app\src\navigation\ /Y
```

---

## 🔧 Post-Migration Configuration

### 1. **Update API URLs**

Open each screen file and update `API_BASE_URL`:

```javascript
// Change from localhost to your computer's IP for mobile testing
const API_BASE_URL = 'http://192.168.1.100:8000';  // Replace with your IP
```

Find your IP:
```bash
# Windows
ipconfig

# Look for IPv4 Address
```

### 2. **Test on Mobile**

```bash
cd agroshield-app
npx expo start

# Scan QR code with Expo Go app
# Or press 'a' for Android, 'i' for iOS
```

### 3. **Test on Web**

```bash
npx expo start --web

# Opens at http://localhost:19006
```

---

## ✅ Verification Checklist

After migration, verify:

- [ ] App runs on mobile (Expo Go)
- [ ] App runs on web browser
- [ ] FarmerMarketplace screen loads
- [ ] BuyerMarketplace screen loads
- [ ] API calls work (update API_BASE_URL first)
- [ ] Navigation between screens works (if using navigation)
- [ ] Images and assets load correctly
- [ ] Responsive design works on web (max-width: 1200px)

---

## 📱 What Works on Each Platform

| Feature | Mobile | Web | Notes |
|---------|--------|-----|-------|
| UI/UX | ✅ | ✅ | Responsive design |
| API Calls | ✅ | ✅ | Update API_BASE_URL |
| Camera | ✅ | ⚠️ | Limited web support |
| Image Picker | ✅ | ✅ | Works on both |
| Location | ✅ | ✅ | Requires permissions |
| BLE Sensors | ✅ | ❌ | Mobile only |
| Maps | ✅ | ✅ | Works on both |
| Async Storage | ✅ | ✅ | localStorage on web |
| Push Notifications | ✅ | ⚠️ | Limited web support |

---

## 🎯 Minimal Migration (Quick Start)

If you just want the core marketplace functionality:

**Copy only these files:**

1. `app.json` (config)
2. `package.json` (dependencies)
3. `App.js` (main component)
4. `webpack.config.js` (web support)
5. `src/screens/FarmerMarketplace.js` (farmer portal)
6. `src/screens/BuyerMarketplace.js` (buyer portal)

**Install dependencies:**
```bash
npm install --legacy-peer-deps
```

**Run:**
```bash
npx expo start --web  # Web
npx expo start        # Mobile
```

---

## 🔍 Troubleshooting

### Issue: "Module not found"
**Solution**: Make sure all imported files are copied. Check import paths in screen files.

### Issue: "Expo web not working"
**Solution**: Ensure these are installed:
```bash
npm install react-dom react-native-web @expo/webpack-config --legacy-peer-deps
```

### Issue: "API calls failing"
**Solution**: Update `API_BASE_URL` in screen files to your backend URL.

### Issue: "BLE not working on web"
**Solution**: BLE is mobile-only. Show appropriate message on web platform.

---

## 📚 Related Documentation

- [MARKETPLACE_FRONTEND_GUIDE.md](MARKETPLACE_FRONTEND_GUIDE.md) - Complete API integration
- [frontend/README.md](frontend/README.md) - Frontend setup guide
- [mobile/MOBILE_APP_GUIDE.md](mobile/MOBILE_APP_GUIDE.md) - Mobile app architecture

---

## 🎉 Result

After migration, you'll have:

✅ **Single codebase** for mobile (iOS/Android) and web
✅ **All marketplace features** working on both platforms
✅ **Responsive design** that adapts to screen size
✅ **Shared components** between platforms
✅ **Easy deployment** via Expo

Run `npx expo start` and choose your platform! 🚀📱🌐
