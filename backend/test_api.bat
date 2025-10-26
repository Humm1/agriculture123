@echo off
REM Quick test script for BLE Storage API endpoints
REM Usage: Run this after starting the backend (python backend/run_dev.py)

echo.
echo ============================================
echo AgroShield BLE Storage API Quick Test
echo ============================================
echo.

SET BASE_URL=http://localhost:8000/api/storage

echo [1/5] Getting crop profiles...
curl -s %BASE_URL%/crop_profiles
echo.
echo.

echo [2/5] Selecting farmer crop (potatoes, Swahili)...
curl -s -X POST %BASE_URL%/select_crop ^
  -F "farmer_id=test_farmer" ^
  -F "crop=potatoes" ^
  -F "language=sw" ^
  -F "phone=+254712345678"
echo.
echo.

echo [3/5] Uploading BLE sensor readings (too hot scenario)...
curl -s -X POST %BASE_URL%/ble/upload ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"test_farmer\",\"sensor_id\":\"ble_test_001\",\"readings\":[{\"temperature\":30,\"humidity\":65}],\"crop\":\"maize\",\"language\":\"en\"}"
echo.
echo.

echo [4/5] Getting sensor history...
curl -s "%BASE_URL%/history?sensor_id=ble_test_001&limit=5"
echo.
echo.

echo [5/5] Manually triggering alert check...
curl -s -X POST %BASE_URL%/trigger_check ^
  -F "farmer_id=test_farmer" ^
  -F "sensor_id=ble_test_001"
echo.
echo.

echo ============================================
echo Test complete! Check output above.
echo ============================================
pause
