@echo off
echo ========================================
echo Testing AgroShield Live Backend
echo URL: https://urchin-app-86rjy.ondigitalocean.app
echo ========================================
echo.

echo [1] Testing Farms Endpoint...
curl -X GET "https://urchin-app-86rjy.ondigitalocean.app/api/farms"
echo.
echo.

echo [2] Testing Weather Endpoint...
curl -X GET "https://urchin-app-86rjy.ondigitalocean.app/api/weather/forecast?lat=0&lon=0"
echo.
echo.

echo [3] Testing Crops Endpoint...
curl -X GET "https://urchin-app-86rjy.ondigitalocean.app/api/crops"
echo.
echo.

echo [4] Testing Health Check...
curl -X GET "https://urchin-app-86rjy.ondigitalocean.app/api/farms"
echo.
echo.

echo [5] Testing API Documentation...
echo Open in browser: https://urchin-app-86rjy.ondigitalocean.app/docs
echo.

pause
