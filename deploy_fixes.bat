@echo off
echo ========================================
echo DEPLOYING FIXES TO DIGITALOCEAN
echo ========================================

cd /d "C:\Users\Codeternal\Desktop\agroshield"

echo.
echo Step 1: Adding all changes...
git add .

echo.
echo Step 2: Committing changes...
git commit -m "Fix: Remove ai_analysis column from plot_images query and fix Budget Calculator"

echo.
echo Step 3: Pushing to GitHub (will trigger DigitalOcean deployment)...
git push origin main

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Wait 2-3 minutes for DigitalOcean to rebuild and deploy.
echo Then refresh your app to see the fixes.
echo.
pause
