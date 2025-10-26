@echo off
REM AgroShield Climate Engine API Test Script
REM Run this after starting the backend (python backend/run_dev.py)

echo.
echo ============================================
echo AgroShield Climate Engine API Test
echo ============================================
echo.

SET BASE=http://localhost:8000/api/climate
SET FARMER=demo_farmer
SET FIELD=demo_field
SET LAT=-1.2921
SET LON=36.8219

echo [1/8] Submitting soil report (damp)...
curl -s -X POST %BASE%/soil_report ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"moisture_level\":\"damp\"}"
echo.
echo.

echo [2/8] Submitting rain report (moderate)...
curl -s -X POST %BASE%/rain_report ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"%FARMER%\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"amount\":\"moderate\"}"
echo.
echo.

echo [3/8] Calculating LCRS (3-month forecast)...
curl -s -X POST %BASE%/lcrs/calculate ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"forecast_months\":3}"
echo.
echo.

echo [4/8] Checking planting status for maize...
curl -s -X POST %BASE%/planting/check_status ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"crop\":\"maize\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%}}"
echo.
echo.

echo [5/8] Recording planting (maize, short_season, 2.5 ha)...
curl -s -X POST %BASE%/planting/record ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"crop\":\"maize\",\"planting_date\":\"2025-10-24T00:00:00\",\"variety\":\"short_season\",\"area_hectares\":2.5}"
echo.
echo.

echo [6/8] Getting crop diversification plan (5 ha total)...
curl -s -X POST %BASE%/diversification/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"total_area_hectares\":5.0}"
echo.
echo.

echo [7/8] Generating harvest prediction...
curl -s -X POST %BASE%/harvest/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"planting_date\":\"2025-10-24T00:00:00\",\"crop\":\"maize\",\"variety\":\"short_season\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"language\":\"en\"}"
echo.
echo.

echo [8/8] Getting farmer dashboard...
curl -s "%BASE%/dashboard/%FARMER%?field_id=%FIELD%"
echo.
echo.

echo ============================================
echo Test complete! Check output above.
echo ============================================
pause
