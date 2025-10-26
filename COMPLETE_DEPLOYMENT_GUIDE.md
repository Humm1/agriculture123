# 🚀 Deploy Agropulse AI - Backend + Frontend (Web + Mobile)

## Complete Deployment Guide for Vercel

---

## 📦 What We're Deploying:

1. **Backend API** → `https://agropulse-ai.vercel.app/api`
2. **Web App** → `https://agropulse-ai-web.vercel.app`
3. **Mobile App** → APK/IPA for Android/iOS devices

---

## Part 1: Deploy Backend to Vercel

### Step 1: Deploy Backend

```powershell
# Navigate to project root
cd C:\Users\Codeternal\Desktop\agroshield

# Login to Vercel
vercel login

# Deploy backend to production
vercel --prod

# When prompted:
# ? What's your project's name? agropulse-ai
# ? In which directory is your code? ./
```

### Step 2: Add Backend Environment Variables

```powershell
# Add all environment variables
vercel env add SUPABASE_URL production
vercel env add SUPABASE_ANON_KEY production
vercel env add SUPABASE_SERVICE_ROLE_KEY production
vercel env add STRIPE_SECRET_KEY production
vercel env add SECRET_KEY production
vercel env add DEBUG production

# Redeploy after adding variables
vercel --prod
```

**Backend URL:** `https://agropulse-ai.vercel.app`

**Test it:** `https://agropulse-ai.vercel.app/docs`

---

## Part 2: Deploy Web Frontend to Vercel

### Step 1: Build Web Version

```powershell
# Navigate to frontend
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app

# Test web build locally first
npm run build:web

# You should see "dist" folder created
```

### Step 2: Deploy Web Frontend

```powershell
# Still in frontend/agroshield-app directory
vercel --prod

# When prompted:
# ? Set up and deploy? Y
# ? Which scope? [Your Account]
# ? Link to existing project? N
# ? What's your project's name? agropulse-ai-web
# ? In which directory is your code? ./
# ? Want to override the settings? N
```

**Web App URL:** `https://agropulse-ai-web.vercel.app`

---

## Part 3: Build Mobile App (APK/IPA)

### For Android:

```powershell
# Navigate to frontend
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app

# Install EAS CLI (if not installed)
npm install -g eas-cli

# Login to Expo
eas login

# Configure EAS Build
eas build:configure

# Build Android APK (Preview build - no Play Store needed)
eas build --platform android --profile preview

# Wait for build to complete (5-10 minutes)
# Download APK from the link provided
```

### For iOS (requires Mac or EAS Build):

```powershell
# Build iOS app
eas build --platform ios --profile preview
```

---

## 📱 URL Configuration Summary

Your app now has 3 deployment targets:

### 1. Backend API (FastAPI)
- **URL:** `https://agropulse-ai.vercel.app`
- **API Docs:** `https://agropulse-ai.vercel.app/docs`
- **Used by:** Both web and mobile apps

### 2. Web App (React Native Web)
- **URL:** `https://agropulse-ai-web.vercel.app`
- **Access:** Any web browser
- **Features:** Full app in browser

### 3. Mobile App (React Native)
- **Development:** Local Expo Go app
- **Production:** APK/IPA installed on device
- **Connects to:** Vercel backend API

---

## 🔧 Update Frontend Configuration

Your `apiConfig.js` is already set up correctly:

```javascript
export const getApiBaseUrl = () => {
  return __DEV__ 
    ? 'http://192.168.137.1:8000/api'  // Development - Local
    : 'https://agropulse-ai.vercel.app/api';  // Production - Vercel
};
```

**Development mode:**
- Web: `npm run web` → connects to local backend
- Mobile: Expo Go → connects to local backend

**Production mode:**
- Web: `https://agropulse-ai-web.vercel.app` → connects to Vercel backend
- Mobile: APK → connects to Vercel backend

---

## 🎯 Quick Deploy Commands

### Deploy Backend:
```powershell
cd C:\Users\Codeternal\Desktop\agroshield
vercel --prod
```

### Deploy Web Frontend:
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app
npm run build:web
vercel --prod
```

### Build Mobile APK:
```powershell
cd C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app
eas build --platform android --profile preview
```

---

## 🌐 Access Your Deployments

### Backend API:
- Production: `https://agropulse-ai.vercel.app`
- Docs: `https://agropulse-ai.vercel.app/docs`

### Web App:
- Production: `https://agropulse-ai-web.vercel.app`
- Can be accessed from any browser

### Mobile App:
- Download APK from EAS Build
- Install on Android device
- Or use Expo Go for development

---

## 📊 Vercel Dashboard

Monitor all deployments at: https://vercel.com/dashboard

You'll have 2 projects:
1. **agropulse-ai** (Backend)
2. **agropulse-ai-web** (Frontend)

---

## 🔄 Automatic Deployments

### Connect to GitHub:

1. Go to: https://vercel.com/dashboard
2. Select project → Settings → Git
3. Connect your GitHub repo: `Humm1/agriculture123`
4. Enable auto-deploy

Now every push to GitHub automatically deploys! 🎉

### Separate Repositories (Optional):

For better organization, you could:
- Backend: `https://github.com/Humm1/agropulse-backend`
- Frontend: `https://github.com/Humm1/agropulse-frontend`

---

## 🧪 Testing Your Deployment

### Test Backend:
```powershell
# Test health endpoint
curl https://agropulse-ai.vercel.app/api/farms

# Test AI prediction
curl -X POST https://agropulse-ai.vercel.app/api/ai/predict/disease-risk ^
  -H "Content-Type: application/json" ^
  -d "{\"temperature\":28,\"humidity\":75}"
```

### Test Web App:
Open browser: `https://agropulse-ai-web.vercel.app`

### Test Mobile App:
1. Install APK on Android device
2. Open app
3. Should connect to Vercel backend automatically

---

## 📱 Distribution Options

### Web App:
- Share URL: `https://agropulse-ai-web.vercel.app`
- Users access directly in browser
- No installation needed

### Mobile App:

**Option 1: Direct APK Distribution**
- Share APK file directly
- Users enable "Install from unknown sources"
- Install APK

**Option 2: Google Play Store**
```powershell
# Build production AAB for Play Store
eas build --platform android --profile production

# Upload AAB to Play Console
```

**Option 3: Apple App Store**
```powershell
# Build iOS app
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

---

## 🎨 Custom Domains (Optional)

### Add Custom Domain:

1. **Buy domain:** e.g., `agropulseai.com`

2. **Add to Vercel:**
```powershell
# For backend
vercel domains add api.agropulseai.com

# For web app
vercel domains add app.agropulseai.com
```

3. **Update DNS:**
- Type: CNAME
- Name: api / app
- Value: cname.vercel-dns.com

4. **Update frontend config:**
```javascript
return __DEV__ 
  ? 'http://192.168.137.1:8000/api'
  : 'https://api.agropulseai.com/api';
```

---

## 💰 Cost Breakdown

### Vercel Free Tier:
- ✅ **2 projects** (backend + frontend)
- ✅ **100GB bandwidth/month**
- ✅ **Unlimited deployments**
- ✅ **HTTPS certificates**
- ✅ **Global CDN**
- **Cost:** $0/month

### EAS Build Free Tier:
- ✅ **Free builds** with some wait time
- ✅ **Unlimited projects**
- **Cost:** $0/month

### Optional Paid Services:
- Play Store: $25 one-time
- App Store: $99/year
- Custom domain: $10-15/year

**Total Free Cost:** $0 🎉

---

## 🚨 Troubleshooting

### Web Build Fails:

```powershell
# Clear cache and rebuild
cd frontend\agroshield-app
rm -rf dist node_modules
npm install
npm run build:web
```

### Backend Deploy Fails:

```powershell
# Check vercel.json exists in root
dir vercel.json

# Check requirements.txt in backend
dir backend\requirements.txt
```

### Mobile App Can't Connect:

```javascript
// Check API config
// Make sure production URL is correct
console.log('API Base:', getApiBaseUrl());
```

---

## ✅ Success Checklist

### Backend:
- [ ] Deployed to Vercel
- [ ] Environment variables set
- [ ] `/docs` endpoint accessible
- [ ] API endpoints working

### Web Frontend:
- [ ] Built successfully (`npm run build:web`)
- [ ] Deployed to Vercel
- [ ] Can access in browser
- [ ] Connects to backend API

### Mobile App:
- [ ] APK built with EAS
- [ ] Installed on Android device
- [ ] Connects to backend API
- [ ] All features working

---

## 🎉 You're Live!

Your app is now deployed in 3 ways:

1. **Backend API:** `https://agropulse-ai.vercel.app`
2. **Web App:** `https://agropulse-ai-web.vercel.app`
3. **Mobile App:** APK for Android devices

Share your app with farmers worldwide! 🌾🚀
