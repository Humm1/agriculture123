# Digital Ocean Deployment Guide for Agropulse AI

## 🎯 Why Digital Ocean?

✅ **$200 Free Credit** for 60 days (new accounts)
✅ Simple pricing: $4-6/month after free credit
✅ Supports Docker and TensorFlow
✅ Easy to use dashboard
✅ Better for ML apps than serverless
✅ No credit card verification issues
✅ SSH access and full control

---

## 💰 Pricing

### Free Credit:
- **$200 free credit for 60 days** (sign up with referral link)
- Enough to run your app for 2 months FREE

### After Free Credit:
- **Basic Droplet**: $4/month (512MB RAM) - Too small for TensorFlow
- **Standard Droplet**: $6/month (1GB RAM) - Minimum for your app ✅
- **General Purpose**: $12/month (2GB RAM) - Recommended for TensorFlow ✅

---

## 📋 Prerequisites

### 1. Create Digital Ocean Account
- Sign up: https://m.do.co/c/yourreferralcode
- Verify email
- Add payment method (won't charge during free trial)
- Get $200 credit

### 2. Install doctl (Digital Ocean CLI)
```powershell
# Download from: https://github.com/digitalocean/doctl/releases
# Or use Chocolatey:
choco install doctl

# Verify installation
doctl version
```

---

## 🚀 Deployment Methods

## Method 1: App Platform (Easiest - Recommended)

Digital Ocean's App Platform is like Heroku - super simple!

### Features:
- ✅ Auto-deploys from GitHub
- ✅ Automatic HTTPS
- ✅ Built-in CI/CD
- ✅ Easy scaling
- ✅ No server management

### Cost:
- **Basic**: $5/month
- **Professional**: $12/month (1GB RAM + 1 vCPU) ✅ Good for TensorFlow

---

### Step-by-Step: Deploy with App Platform

#### 1. Push code to GitHub (already done ✅)

#### 2. Create App in Digital Ocean

Go to: https://cloud.digitalocean.com/apps

Click **"Create App"**

**Connect GitHub:**
- Authorize Digital Ocean
- Select repository: `Humm1/agriculture123`
- Select branch: `main`
- Auto-deploy: ✅ Yes

**Configure App:**
- **Name**: agropulse-ai
- **Region**: New York (closest to you)
- **Branch**: main
- **Source Directory**: `/backend`

**Build Settings:**
- **Type**: Web Service
- **Dockerfile Path**: `backend/Dockerfile` (we'll create this)
- **HTTP Port**: 8000
- **Run Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Environment Variables:**
Click "Edit" and add all your variables:
```
SUPABASE_URL=https://rwspbvgmmxabglptljkg.supabase.co
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_ROLE_KEY=your_key
SUPABASE_JWT_SECRET=your_secret
OPENWEATHER_API_KEY=your_key
WEATHERAPI_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+254759968865
STRIPE_SECRET_KEY=your_key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Choose Plan:**
- Select: **Professional - $12/month** (1GB RAM, good for TensorFlow)
- Or: **Basic - $5/month** (512MB RAM, remove TensorFlow)

Click **"Create Resources"**

Wait 5-10 minutes for deployment...

**Access Your App:**
- URL: `https://agropulse-ai-xxxxx.ondigitalocean.app`
- API Docs: `https://agropulse-ai-xxxxx.ondigitalocean.app/docs`

---

## Method 2: Droplet + Docker (More Control)

### Step 1: Create Droplet

Go to: https://cloud.digitalocean.com/droplets

Click **"Create Droplet"**

**Choose Image:**
- Distribution: Ubuntu 22.04 LTS

**Choose Plan:**
- **Basic**: $6/month (1GB RAM, 1 vCPU, 25GB SSD)
- **Or General Purpose**: $12/month (2GB RAM) - Better for TensorFlow ✅

**Choose Region:**
- New York 3 (closest)

**Authentication:**
- SSH Key (recommended) or Password

**Hostname:**
- `agropulse-ai-server`

Click **"Create Droplet"**

Get your Droplet IP: `xxx.xxx.xxx.xxx`

---

### Step 2: Connect to Droplet

```powershell
# SSH into your droplet
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify
docker --version
docker-compose --version
```

---

### Step 3: Deploy Your App

```bash
# On your Droplet, clone your repo
git clone https://github.com/Humm1/agriculture123.git
cd agriculture123/backend

# Create .env file with your variables
nano .env
# Paste all your environment variables, save (Ctrl+X, Y, Enter)

# Build and run with Docker
docker-compose up -d --build

# Check if running
docker ps

# View logs
docker logs backend
```

---

### Step 4: Configure Nginx (Reverse Proxy)

```bash
# Install Nginx
apt install nginx -y

# Create config
nano /etc/nginx/sites-available/agropulse

# Paste this config:
```

```nginx
server {
    listen 80;
    server_name your_droplet_ip;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/agropulse /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Your app is now live at: http://your_droplet_ip
```

---

### Step 5: Add HTTPS (Free SSL)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (requires domain name)
# If you have a domain:
certbot --nginx -d yourdomain.com

# Follow prompts, certificate auto-renews
```

---

## 🐳 Dockerfile (Required for Both Methods)

Create this file: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads storage/growth

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🐳 docker-compose.yml (Optional, for Droplet deployment)

Create: `backend/docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build: .
    container_name: agropulse-backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - WEATHERAPI_KEY=${WEATHERAPI_KEY}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./uploads:/app/uploads
      - ./storage:/app/storage
    restart: unless-stopped
```

---

## 📱 Update Frontend to Use Digital Ocean URL

After deployment, update your frontend API URL:

`frontend/agroshield-app/src/config/apiConfig.js`:

```javascript
export const getApiBaseUrl = () => {
  return __DEV__ 
    ? 'http://192.168.137.1:8000/api'  // Development
    : 'https://agropulse-ai-xxxxx.ondigitalocean.app/api';  // Production
};
```

Or if using Droplet:
```javascript
: 'http://your_droplet_ip/api';  // Droplet IP
```

---

## 🔄 Continuous Deployment

### With App Platform (Auto-deploy from GitHub):
1. Push code to GitHub
2. Digital Ocean automatically detects changes
3. Rebuilds and deploys
4. Zero downtime deployment

### With Droplet (Manual updates):
```bash
# SSH into droplet
ssh root@your_droplet_ip

# Pull latest code
cd agriculture123/backend
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## 📊 Monitoring

### App Platform:
- Built-in metrics in dashboard
- View logs in real-time
- CPU/Memory/Network usage graphs

### Droplet:
```bash
# View logs
docker logs -f backend

# Check resource usage
docker stats

# Monitor with htop
apt install htop
htop
```

---

## 💡 Recommendations

### Choose App Platform If:
- ✅ You want easy deployment
- ✅ You don't want to manage servers
- ✅ You want auto-deploy from GitHub
- ✅ You're okay with $12/month

### Choose Droplet If:
- ✅ You want more control
- ✅ You want to learn server management
- ✅ You want cheaper option ($6/month)
- ✅ You need SSH access

---

## 🎯 My Recommendation: App Platform

**Why:**
- Easiest to set up (10 minutes)
- Auto-deploys from GitHub
- Free HTTPS
- Built-in monitoring
- Scales easily
- Worth the $12/month for peace of mind

**Start with App Platform, switch to Droplet later if you want more control.**

---

## 🆘 Troubleshooting

### App Platform build failed:
- Check build logs in Digital Ocean dashboard
- Most common: TensorFlow installation timeout
  - Solution: Use smaller TensorFlow package or remove it

### Droplet app won't start:
```bash
# Check Docker logs
docker logs backend

# Restart container
docker-compose restart

# Rebuild from scratch
docker-compose down
docker system prune -a
docker-compose up -d --build
```

### Out of Memory:
- Upgrade to $12/month plan (2GB RAM)
- Or optimize TensorFlow usage
- Or use TensorFlow Lite instead

---

## 📞 Next Steps

1. **Sign up for Digital Ocean**: Get $200 free credit
2. **I'll create the Dockerfile and docker-compose.yml for you**
3. **Choose method**: App Platform (easier) or Droplet (more control)
4. **Deploy!**

Which method do you prefer? I'll create the Docker files right now!
