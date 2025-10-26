# 🚀 Vercel Deployment Guide - Agropulse AI

## Deploy FastAPI Backend to Vercel (100% FREE - No Credit Card!)

---

## Why Vercel?

✅ **Completely FREE** - No payment verification required  
✅ **Automatic HTTPS** - Free SSL certificates  
✅ **Global CDN** - Fast performance worldwide  
✅ **Auto-deploy** - GitHub integration  
✅ **Never sleeps** - Always online  
✅ **Serverless** - Scales automatically  

---

## Quick Deploy (5 Minutes)

### Step 1: Install Vercel CLI

```powershell
# Install Vercel CLI globally
npm install -g vercel

# Verify installation
vercel --version
```

---

### Step 2: Create Vercel Configuration

Create `vercel.json` in **project root**:

```json
{
  "version": 2,
  "name": "agropulse-ai",
  "builds": [
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.11"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/app/main.py"
    },
    {
      "src": "/docs",
      "dest": "backend/app/main.py"
    },
    {
      "src": "/openapi.json",
      "dest": "backend/app/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "backend/app/main.py"
    }
  ]
}
```

---

### Step 3: Verify Backend Structure

Make sure your `backend/app/main.py` exports the FastAPI app:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Agropulse AI API",
    description="AI-Powered Agricultural Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your routes here...
# Include all route files

# This is important for Vercel serverless
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Step 4: Ensure requirements.txt is in Backend Directory

```powershell
# Verify requirements.txt exists in backend directory
dir backend\requirements.txt

# Should show the file with all your dependencies:
# - fastapi
# - uvicorn
# - pydantic
# - supabase
# - stripe
# - etc.
```

---

### Step 5: Deploy to Vercel

```powershell
# Navigate to project root
cd C:\Users\Codeternal\Desktop\agroshield

# Login to Vercel (opens browser)
vercel login

# Deploy (first time)
vercel

# Follow the prompts:
# ? Set up and deploy "agroshield"? Y
# ? Which scope? [Your Account]
# ? Link to existing project? N
# ? What's your project's name? agropulse-ai
# ? In which directory is your code? ./
# ? Want to override settings? N

# This creates a preview deployment
```

---

### Step 6: Add Environment Variables

```powershell
# Add all your environment variables
vercel env add SUPABASE_URL
# Enter: https://your-project.supabase.co

vercel env add SUPABASE_ANON_KEY
# Paste your anon key

vercel env add SUPABASE_SERVICE_ROLE_KEY
# Paste your service role key

vercel env add STRIPE_SECRET_KEY
# Paste your Stripe key (or leave empty for testing)

vercel env add SECRET_KEY
# Enter a random secret key (e.g., use Python to generate)

vercel env add DEBUG
# Enter: False

# Verify all variables are set
vercel env ls
```

---

### Step 7: Deploy to Production

```powershell
# Deploy to production
vercel --prod

# ✅ Your API will be live at:
# https://agropulse-ai.vercel.app
# or
# https://agropulse-ai-yourusername.vercel.app
```

---

## Update Frontend to Use Vercel URL

After deployment, update your frontend configuration:

**Edit:** `frontend/agroshield-app/src/config/apiConfig.js`

```javascript
// API Base URL - Configure based on environment
export const getApiBaseUrl = () => {
  // Check environment variable first
  if (process.env.API_BASE_URL) {
    return process.env.API_BASE_URL;
  }

  // Use Vercel production URL or local network for development
  return __DEV__ 
    ? 'http://192.168.137.1:8000/api'  // Development - Local network
    : 'https://agropulse-ai.vercel.app/api';  // Production - Vercel
};
```

---

## Alternative: Deploy via GitHub (Recommended)

### Step 1: Push to GitHub

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Vercel deployment"

# Create GitHub repository at: https://github.com/new

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/agropulse-ai.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Connect GitHub to Vercel

1. Go to: **https://vercel.com/new**
2. Click **"Import Git Repository"**
3. Select your GitHub repository: `agropulse-ai`
4. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: *(leave empty)*
   - **Output Directory**: *(leave empty)*
   - **Install Command**: *(leave empty)*
5. Click **"Deploy"**

### Step 3: Add Environment Variables in Dashboard

1. After import, go to your project dashboard
2. Click **Settings** → **Environment Variables**
3. Add all variables:
   - `SUPABASE_URL` = `https://your-project.supabase.co`
   - `SUPABASE_ANON_KEY` = `your-anon-key`
   - `SUPABASE_SERVICE_ROLE_KEY` = `your-service-role-key`
   - `STRIPE_SECRET_KEY` = `sk_test_your_key`
   - `SECRET_KEY` = `random-secret-key`
   - `DEBUG` = `False`
4. Select **Production**, **Preview**, and **Development** for each variable
5. Click **"Save"**

### Step 4: Redeploy

1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest deployment
3. ✅ Your app will be live!

---

## Test Your Deployment

### Access API Documentation

```
https://agropulse-ai.vercel.app/docs
```

You should see the FastAPI interactive documentation (Swagger UI).

### Test Endpoints

```powershell
# Test health endpoint
curl https://agropulse-ai.vercel.app/api/farms

# Test AI prediction
curl -X POST https://agropulse-ai.vercel.app/api/ai/predict/disease-risk ^
  -H "Content-Type: application/json" ^
  -d "{\"temperature\":28,\"humidity\":75}"
```

---

## Vercel CLI Commands

```powershell
# Deploy preview (staging)
vercel

# Deploy production
vercel --prod

# View deployments
vercel ls

# View logs (real-time)
vercel logs

# View environment variables
vercel env ls

# Pull environment variables to local .env
vercel env pull

# Remove deployment
vercel remove [deployment-url]

# Open project in browser
vercel open

# View project info
vercel inspect [deployment-url]
```

---

## Automatic Deployments from GitHub

Once connected to GitHub, every push automatically deploys:

- **`main` branch** → Production (https://agropulse-ai.vercel.app)
- **Other branches** → Preview URLs (https://agropulse-ai-git-branch.vercel.app)

### Example Workflow:

```powershell
# Make changes
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin main

# ✅ Vercel automatically deploys to production!
# Check deployment at: https://vercel.com/dashboard
```

---

## Project Structure for Vercel

```
agroshield/
├── vercel.json              # ← Vercel configuration
├── .gitignore               # ← Git ignore file
├── backend/
│   ├── requirements.txt     # ← Python dependencies (REQUIRED)
│   ├── app/
│   │   ├── main.py          # ← FastAPI app (must export 'app')
│   │   ├── routes/          # ← All API routes
│   │   │   ├── farms.py
│   │   │   ├── predict.py
│   │   │   ├── ai_prediction.py
│   │   │   ├── drone_intelligence.py
│   │   │   └── ... (all other routes)
│   │   └── services/        # ← Business logic
│   └── uploads/             # ← User uploads (gitignored)
└── frontend/
    └── agroshield-app/
        ├── src/
        │   └── config/
        │       └── apiConfig.js  # ← Update with Vercel URL
        └── package.json
```

---

## Troubleshooting

### Build Fails: "Could not find requirements.txt"

```powershell
# Make sure requirements.txt is in backend directory
dir backend\requirements.txt

# If missing, it should contain all dependencies
# Verify it includes:
# - fastapi
# - uvicorn[standard]
# - pydantic
# - supabase
# - stripe
# - etc.
```

### Build Fails: "Module 'app' has no attribute 'app'"

Make sure `backend/app/main.py` exports `app` at module level:

```python
from fastapi import FastAPI

app = FastAPI()  # ← This must be at module level

# All routes and middleware here...

# This is fine at the bottom:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Import Errors: "No module named 'X'"

```powershell
# Make sure ALL dependencies are in backend/requirements.txt
# Common missing packages:
# - python-multipart (for file uploads)
# - email-validator (for Pydantic email validation)
# - pyjwt (for JWT tokens)
```

### Timeout Errors: "Function execution timeout"

Update `vercel.json` to increase timeout:

```json
{
  "version": 2,
  "functions": {
    "backend/app/main.py": {
      "maxDuration": 30
    }
  }
}
```

### Environment Variables Not Working

```powershell
# Make sure variables are set for all environments
vercel env add VARIABLE_NAME production
vercel env add VARIABLE_NAME preview
vercel env add VARIABLE_NAME development

# Pull and verify
vercel env pull
# Check .env.local file that was created

# Redeploy
vercel --prod
```

### CORS Issues

Make sure CORS is properly configured in `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Vercel Free Tier Limits

✅ **Unlimited deployments**  
✅ **100GB bandwidth/month** (more than enough!)  
✅ **100 hours serverless execution/month**  
✅ **Unlimited team members**  
✅ **Automatic HTTPS**  
✅ **Global CDN**  
✅ **DDoS protection**  

**Note:** Serverless functions have a 10-second execution limit per request on free tier.

---

## Monitor Your Deployment

### Vercel Dashboard

Visit: https://vercel.com/dashboard

You can see:
- **Deployments** - All your deployments and their status
- **Analytics** - Bandwidth usage, requests, errors
- **Logs** - Real-time function logs
- **Domains** - Manage custom domains

### Real-time Logs

```powershell
# View logs in real-time
vercel logs --follow

# View logs for specific deployment
vercel logs [deployment-url]

# Filter logs by function
vercel logs --filter "backend/app/main.py"
```

---

## Custom Domain (Optional)

### Add Your Domain

1. **Buy a domain** (e.g., from Namecheap, GoDaddy)

2. **Add domain in Vercel**:
```powershell
vercel domains add agropulseai.com
vercel domains add www.agropulseai.com
```

3. **Update DNS records** (in your domain registrar):
```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

4. **Wait for DNS propagation** (5-30 minutes)

5. **Vercel automatically provisions SSL certificate** ✅

---

## Scale Your App

### Upgrade Plans (if needed)

- **Hobby (Free)**: Perfect for development and small apps
- **Pro ($20/month)**: 
  - 1TB bandwidth
  - 1000 hours serverless execution
  - 60-second function timeout
  - Team collaboration
- **Enterprise**: Custom pricing for large-scale apps

**Start with free tier** - it's more than enough for most apps! 🎉

---

## Success Checklist

- [ ] Vercel CLI installed (`npm install -g vercel`)
- [ ] `vercel.json` created in root
- [ ] `requirements.txt` exists in `backend/` directory
- [ ] FastAPI app exports `app` at module level
- [ ] Logged in to Vercel (`vercel login`)
- [ ] Deployed to production (`vercel --prod`)
- [ ] Environment variables set (`vercel env add`)
- [ ] API accessible at `/docs` endpoint
- [ ] Frontend updated with Vercel URL
- [ ] GitHub auto-deploy configured (optional)

---

## Quick Deploy Commands

```powershell
# One-time setup
npm install -g vercel
vercel login

# Deploy preview
vercel

# Add environment variables
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add STRIPE_SECRET_KEY
vercel env add SECRET_KEY
vercel env add DEBUG

# Deploy to production
vercel --prod

# View your app
vercel open
```

---

## Support & Resources

- **Vercel Documentation**: https://vercel.com/docs
- **FastAPI on Vercel**: https://vercel.com/guides/deploying-fastapi-with-vercel
- **Vercel Community**: https://github.com/vercel/vercel/discussions
- **Vercel Discord**: https://vercel.com/discord

---

**🚀 Deploy now!**

```powershell
vercel login
vercel --prod
```

Your API will be live in under 2 minutes! ✨
