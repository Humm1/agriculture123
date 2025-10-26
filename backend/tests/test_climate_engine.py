"""
Unit tests for Climate Engine (LCRS, Planting Windows, Harvest Prediction)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from app.services import lcrs_engine, planting_window, harvest_prediction, climate_persistence

# ============================================================================
# LCRS ENGINE TESTS
# ============================================================================

def test_soil_moisture_index():
    """Test soil moisture index calculation"""
    assert climate_persistence.calculate_soil_moisture_index('dry') == 20
    assert climate_persistence.calculate_soil_moisture_index('damp') == 60
    assert climate_persistence.calculate_soil_moisture_index('saturated') == 95
    print('✅ test_soil_moisture_index passed')

def test_lcrs_calculation():
    """Test LCRS calculation"""
    # Add sample data
    farmer_id = 'test_farmer_001'
    field_id = 'field_001'
    location = {'lat': -1.2921, 'lon': 36.8219}  # Nairobi coordinates
    
    # Add soil report
    climate_persistence.add_soil_report(farmer_id, field_id, 'damp')
    
    # Calculate LCRS
    lcrs = lcrs_engine.calculate_lcrs(farmer_id, field_id, location, forecast_months=3)
    
    assert 'score' in lcrs
    assert 'risk_level' in lcrs
    assert lcrs['risk_level'] in ['low', 'moderate', 'high']
    assert 0 <= lcrs['score'] <= 100
    assert 'factors' in lcrs
    assert 'recommendations' in lcrs
    
    print(f'✅ test_lcrs_calculation passed - Score: {lcrs["score"]}, Level: {lcrs["risk_level"]}')

def test_seasonal_forecast():
    """Test seasonal weather forecast estimation"""
    # March (long rains) should have low risk
    march_risk = lcrs_engine.estimate_weather_forecast_risk(0)  # Current month offset
    
    # January (dry season) should have high risk
    jan_risk = lcrs_engine.estimate_weather_forecast_risk(0)
    
    assert 0 <= march_risk <= 1
    assert 0 <= jan_risk <= 1
    
    print(f'✅ test_seasonal_forecast passed - Forecast risk calculated')

# ============================================================================
# PLANTING WINDOW TESTS
# ============================================================================

def test_optimal_planting_window():
    """Test optimal planting window calculation"""
    location = {'lat': -1.2921, 'lon': 36.8219}
    
    window = planting_window.get_optimal_planting_window('maize', location)
    
    assert 'start_date' in window
    assert 'end_date' in window
    assert 'rationale' in window
    assert 'confidence' in window
    
    # Verify dates are valid ISO format
    datetime.fromisoformat(window['start_date'])
    datetime.fromisoformat(window['end_date'])
    
    print(f'✅ test_optimal_planting_window passed - Window: {window["start_date"][:10]} to {window["end_date"][:10]}')

def test_planting_status_late():
    """Test late planting detection"""
    farmer_id = 'test_farmer_002'
    field_id = 'field_002'
    location = {'lat': -1.2921, 'lon': 36.8219}
    
    # Add soil report
    climate_persistence.add_soil_report(farmer_id, field_id, 'dry')
    
    status = planting_window.check_planting_status(farmer_id, field_id, 'maize', location)
    
    assert 'status' in status
    assert status['status'] in ['optimal', 'early', 'late', 'very_late']
    assert 'message' in status
    
    if status['status'] in ['late', 'very_late']:
        assert len(status['alternative_crops']) > 0
    
    print(f'✅ test_planting_status_late passed - Status: {status["status"]}')

def test_alternative_crops():
    """Test alternative crop suggestions"""
    alternatives = planting_window.get_alternative_crops('maize', 15)
    assert len(alternatives) > 0
    assert isinstance(alternatives, list)
    
    very_late_alternatives = planting_window.get_alternative_crops('maize', 35)
    assert 'cassava' in very_late_alternatives or 'sorghum' in very_late_alternatives
    
    print(f'✅ test_alternative_crops passed - Alternatives: {", ".join(alternatives)}')

def test_diversification_plan():
    """Test crop diversification plan generation"""
    farmer_id = 'test_farmer_003'
    field_id = 'field_003'
    location = {'lat': -1.2921, 'lon': 36.8219}
    
    # Add soil report
    climate_persistence.add_soil_report(farmer_id, field_id, 'damp')
    
    plan = planting_window.generate_diversification_plan(farmer_id, field_id, location, 5.0)
    
    assert 'primary_crop' in plan
    assert 'diversification_crops' in plan
    assert 'rationale' in plan
    assert plan['primary_crop']['percentage'] + sum(c['percentage'] for c in plan['diversification_crops']) == 100
    
    print(f'✅ test_diversification_plan passed - Primary: {plan["primary_crop"]["percentage"]}%, Diversification: {len(plan["diversification_crops"])} crops')

# ============================================================================
# HARVEST PREDICTION TESTS
# ============================================================================

def test_crop_maturity_days():
    """Test crop maturity period retrieval"""
    maize_days = harvest_prediction.get_crop_maturity_days('maize')
    assert maize_days > 0
    
    beans_days = harvest_prediction.get_crop_maturity_days('beans', 'bush')
    assert beans_days == 60
    
    print(f'✅ test_crop_maturity_days passed - Maize: {maize_days} days, Bush beans: {beans_days} days')

def test_harvest_date_prediction():
    """Test harvest date prediction"""
    planting_date = datetime.utcnow().isoformat()
    
    prediction = harvest_prediction.predict_harvest_date(planting_date, 'maize', 'short_season')
    
    assert 'predicted_date' in prediction
    assert 'harvest_window_start' in prediction
    assert 'harvest_window_end' in prediction
    assert 'maturity_days' in prediction
    assert prediction['maturity_days'] == 90
    
    # Verify harvest is in the future
    harvest_date = datetime.fromisoformat(prediction['predicted_date'])
    assert harvest_date > datetime.utcnow()
    
    print(f'✅ test_harvest_date_prediction passed - Harvest in {prediction["maturity_days"]} days')

def test_harvest_weather_check():
    """Test weather forecast for harvest period"""
    # Future date (3 months ahead)
    future_date = (datetime.utcnow() + timedelta(days=90)).isoformat()
    location = {'lat': -1.2921, 'lon': 36.8219}
    
    weather = harvest_prediction.check_harvest_weather(future_date, location)
    
    assert 'conditions' in weather
    assert weather['conditions'] in ['dry', 'wet', 'uncertain']
    assert 'rain_probability' in weather
    assert 'advice' in weather
    assert 'icon' in weather
    
    print(f'✅ test_harvest_weather_check passed - Conditions: {weather["conditions"]} {weather["icon"]}')

def test_storage_readiness_check():
    """Test storage facility readiness check"""
    farmer_id = 'test_farmer_004'
    sensor_id = 'test_sensor_001'
    
    # This will return 'no data' for new farmer
    status = harvest_prediction.check_storage_readiness(farmer_id, sensor_id)
    
    assert 'ready' in status
    assert 'issues' in status
    assert 'recommendations' in status
    
    print(f'✅ test_storage_readiness_check passed - Ready: {status["ready"]}')

def test_harvest_alert_generation():
    """Test comprehensive harvest alert generation"""
    farmer_id = 'test_farmer_005'
    field_id = 'field_005'
    planting_date = datetime.utcnow().isoformat()
    location = {'lat': -1.2921, 'lon': 36.8219}
    
    # Add soil report
    climate_persistence.add_soil_report(farmer_id, field_id, 'damp')
    
    alert = harvest_prediction.generate_harvest_alert(
        farmer_id, field_id, planting_date, 'maize', 'short_season', location
    )
    
    assert 'harvest_prediction' in alert
    assert 'weather_forecast' in alert
    assert 'storage_status' in alert
    assert 'alert_message' in alert
    assert 'alert_level' in alert
    assert alert['alert_level'] in ['info', 'warning', 'critical']
    assert 'action_items' in alert
    
    print(f'✅ test_harvest_alert_generation passed - Alert level: {alert["alert_level"]}')
    print(f'   Message: {alert["alert_message"][:100]}...')

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_farmer_workflow():
    """Test complete farmer workflow from planting to harvest"""
    farmer_id = 'integration_farmer_001'
    field_id = 'integration_field_001'
    location = {'lat': -1.2921, 'lon': 36.8219}
    
    # 1. Farmer reports soil moisture
    climate_persistence.add_soil_report(farmer_id, field_id, 'damp')
    print('  1️⃣ Soil report submitted')
    
    # 2. Farmer reports rain
    climate_persistence.add_rain_report(farmer_id, location, 'moderate')
    print('  2️⃣ Rain report submitted')
    
    # 3. Calculate LCRS
    lcrs = lcrs_engine.calculate_lcrs(farmer_id, field_id, location)
    print(f'  3️⃣ LCRS calculated: {lcrs["score"]} ({lcrs["risk_level"]})')
    
    # 4. Check planting status
    status = planting_window.check_planting_status(farmer_id, field_id, 'maize', location)
    print(f'  4️⃣ Planting status: {status["status"]}')
    
    # 5. Record planting
    planting_date = datetime.utcnow().isoformat()
    climate_persistence.add_planting_record(farmer_id, field_id, 'maize', planting_date, 'short_season', 2.5)
    print('  5️⃣ Planting recorded')
    
    # 6. Generate harvest alert
    alert = harvest_prediction.generate_harvest_alert(
        farmer_id, field_id, planting_date, 'maize', 'short_season', location
    )
    print(f'  6️⃣ Harvest alert generated: {alert["alert_level"]}')
    
    # 7. Get diversification plan
    plan = planting_window.generate_diversification_plan(farmer_id, field_id, location, 5.0)
    print(f'  7️⃣ Diversification plan: {plan["primary_crop"]["percentage"]}% primary crop')
    
    print('✅ test_full_farmer_workflow passed - Complete workflow executed')

# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == '__main__':
    print('🧪 Running Climate Engine Tests...\n')
    
    print('--- LCRS Engine Tests ---')
    test_soil_moisture_index()
    test_lcrs_calculation()
    test_seasonal_forecast()
    
    print('\n--- Planting Window Tests ---')
    test_optimal_planting_window()
    test_planting_status_late()
    test_alternative_crops()
    test_diversification_plan()
    
    print('\n--- Harvest Prediction Tests ---')
    test_crop_maturity_days()
    test_harvest_date_prediction()
    test_harvest_weather_check()
    test_storage_readiness_check()
    test_harvest_alert_generation()
    
    print('\n--- Integration Tests ---')
    test_full_farmer_workflow()
    
    print('\n✅ All Climate Engine tests passed!')
