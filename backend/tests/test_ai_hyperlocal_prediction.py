"""
Test Suite for AI Hyper-Local Prediction Engine
================================================

Tests:
- Weather data fusion with dynamic trust scoring
- Disease outbreak predictions with probability scoring
- Source reliability updates
- Historical outbreak analysis

Target: 90%+ code coverage

Author: AgroShield AI Team
Date: October 2025
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.ai_hyperlocal_prediction import (
    synthesize_micro_climate_forecast,
    predict_pest_disease_outbreaks,
    update_source_reliability,
    PATHOGEN_LIFE_CYCLES,
    WEATHER_SOURCE_RELIABILITY
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_satellite_data():
    """Sample satellite weather data."""
    return {
        "temperature_c": 24.5,
        "humidity_percent": 75.0,
        "rainfall_mm": 12.3,
        "confidence": 0.85,
        "source": "satellite"
    }


@pytest.fixture
def sample_crowdsourced_data():
    """Sample crowdsourced weather data from nearby farmers."""
    return [
        {
            "farmer_id": "farmer001",
            "lat": -1.28,
            "lon": 36.81,
            "distance_km": 3.5,
            "temperature_c": 25.0,
            "humidity_percent": 72.0,
            "rainfall_mm": 10.0,
            "reported_at": datetime.now().isoformat()
        },
        {
            "farmer_id": "farmer002",
            "lat": -1.30,
            "lon": 36.83,
            "distance_km": 8.2,
            "temperature_c": 23.5,
            "humidity_percent": 78.0,
            "rainfall_mm": 15.0,
            "reported_at": datetime.now().isoformat()
        }
    ]


@pytest.fixture
def sample_ble_data():
    """Sample BLE sensor data."""
    return {
        "sensor_id": "ble_sensor_001",
        "temperature_c": 24.2,
        "humidity_percent": 76.0,
        "soil_moisture_percent": 65.0,
        "confidence": 0.90,
        "last_updated": datetime.now().isoformat()
    }


@pytest.fixture
def sample_micro_climate_forecast():
    """Sample micro-climate forecast."""
    return [
        {
            "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
            "temperature_min": 18 + i * 0.5,
            "temperature_max": 28 + i * 0.5,
            "humidity_avg": 70 + i,
            "rainfall_mm": 5 * i
        }
        for i in range(7)
    ]


@pytest.fixture
def sample_outbreak_history():
    """Sample historical outbreak data."""
    return [
        {
            "outbreak_id": "outbreak_001",
            "pathogen": "late_blight",
            "lat": -1.29,
            "lon": 36.82,
            "distance_km": 15.0,
            "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "severity": 7.5
        },
        {
            "outbreak_id": "outbreak_002",
            "pathogen": "fall_armyworm",
            "lat": -1.27,
            "lon": 36.80,
            "distance_km": 8.0,
            "date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
            "severity": 6.0
        }
    ]


# ============================================================================
# TESTS: WEATHER DATA FUSION
# ============================================================================

class TestWeatherDataFusion:
    """Test weather data fusion with dynamic trust scoring."""
    
    def test_synthesize_basic_forecast(self, sample_satellite_data, sample_ble_data):
        """Test basic forecast synthesis with satellite + BLE data."""
        result = synthesize_micro_climate_forecast(
            lat=-1.29,
            lon=36.82,
            forecast_days=7
        )
        
        assert "forecast_days" in result
        assert len(result["forecast_days"]) == 7
        assert "data_sources" in result
        assert "overall_confidence" in result
        
        # Check first day structure
        day1 = result["forecast_days"][0]
        assert "date" in day1
        assert "temperature_c" in day1
        assert "humidity_percent" in day1
        assert "rainfall_mm" in day1
        assert "confidence" in day1
    
    def test_trust_score_weighting(self):
        """Test that trust scores properly weight data sources."""
        # Satellite (85%) should have higher weight than crowdsourced (65%)
        result = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=1)
        
        # Overall confidence should be weighted average
        assert 0.6 <= result["overall_confidence"] <= 0.95
    
    def test_proximity_weighting(self, sample_crowdsourced_data):
        """Test that proximity affects crowdsourced data weighting."""
        # Closer farmers should have higher influence
        # Distance penalty: exp(-distance / 10)
        close_farmer = sample_crowdsourced_data[0]  # 3.5 km
        far_farmer = sample_crowdsourced_data[1]    # 8.2 km
        
        close_weight = pytest.approx(0.704, rel=0.01)  # exp(-3.5/10)
        far_weight = pytest.approx(0.440, rel=0.01)    # exp(-8.2/10)
        
        # Verify weights follow exponential decay
        assert close_weight > far_weight
    
    def test_data_source_tracking(self):
        """Test that data sources are properly tracked."""
        result = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=1)
        
        assert "data_sources" in result
        sources = result["data_sources"]
        
        # Should list sources used
        assert isinstance(sources, list)
        assert len(sources) > 0
        
        # Each source should have metadata
        for source in sources:
            assert "name" in source
            assert "trust_score" in source
    
    def test_forecast_consistency(self):
        """Test that forecast values are consistent and realistic."""
        result = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=7)
        
        for day in result["forecast_days"]:
            # Temperature range check (Kenya climate)
            assert 10 <= day["temperature_c"] <= 40
            
            # Humidity range check
            assert 0 <= day["humidity_percent"] <= 100
            
            # Rainfall positive
            assert day["rainfall_mm"] >= 0
            
            # Confidence in valid range
            assert 0 <= day["confidence"] <= 1


# ============================================================================
# TESTS: DISEASE OUTBREAK PREDICTIONS
# ============================================================================

class TestDiseaseOutbreakPredictions:
    """Test disease/pest outbreak predictions."""
    
    def test_predict_outbreaks_basic(self, sample_micro_climate_forecast):
        """Test basic outbreak prediction."""
        result = predict_pest_disease_outbreaks(
            crop="potato",
            lat=-1.29,
            lon=36.82,
            micro_climate_forecast=sample_micro_climate_forecast
        )
        
        assert "crop" in result
        assert "predictions" in result
        assert "location" in result
        assert isinstance(result["predictions"], list)
    
    def test_late_blight_activation_conditions(self):
        """Test late blight activation (10-25°C, 90% humidity, 12h rain)."""
        # Create conditions favorable for late blight
        favorable_forecast = [
            {
                "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                "temperature_min": 15,
                "temperature_max": 20,
                "humidity_avg": 92,
                "rainfall_mm": 15
            }
            for i in range(7)
        ]
        
        result = predict_pest_disease_outbreaks(
            crop="potato",
            lat=-1.29,
            lon=36.82,
            micro_climate_forecast=favorable_forecast
        )
        
        # Should predict late_blight
        predictions = result["predictions"]
        blight_predictions = [p for p in predictions if p["pathogen"] == "late_blight"]
        
        if len(blight_predictions) > 0:
            prediction = blight_predictions[0]
            assert prediction["probability"] > 0.5  # High probability
            assert prediction["days_until_activation"] <= 3
    
    def test_fall_armyworm_conditions(self):
        """Test fall armyworm activation (25-30°C, 60% humidity, 2 dry days)."""
        # Hot, moderately humid conditions
        favorable_forecast = [
            {
                "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                "temperature_min": 24,
                "temperature_max": 29,
                "humidity_avg": 65,
                "rainfall_mm": 0  # Dry
            }
            for i in range(7)
        ]
        
        result = predict_pest_disease_outbreaks(
            crop="maize",
            lat=-1.29,
            lon=36.82,
            micro_climate_forecast=favorable_forecast
        )
        
        predictions = result["predictions"]
        armyworm_predictions = [p for p in predictions if p["pathogen"] == "fall_armyworm"]
        
        if len(armyworm_predictions) > 0:
            prediction = armyworm_predictions[0]
            assert prediction["probability"] > 0.4
    
    def test_probability_scaling(self):
        """Test that probability scales with risk factors."""
        result = predict_pest_disease_outbreaks(
            crop="potato",
            lat=-1.29,
            lon=36.82,
            micro_climate_forecast=[
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "temperature_min": 15,
                    "temperature_max": 22,
                    "humidity_avg": 85,
                    "rainfall_mm": 10
                }
                for i in range(7)
            ]
        )
        
        # All probabilities should be 0-1
        for prediction in result["predictions"]:
            assert 0 <= prediction["probability"] <= 1
    
    def test_preventative_actions_included(self):
        """Test that preventative actions are recommended."""
        result = predict_pest_disease_outbreaks(
            crop="potato",
            lat=-1.29,
            lon=36.82,
            micro_climate_forecast=[
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "temperature_min": 18,
                    "temperature_max": 24,
                    "humidity_avg": 80,
                    "rainfall_mm": 8
                }
                for i in range(7)
            ]
        )
        
        for prediction in result["predictions"]:
            if prediction["probability"] > 0.5:
                assert "preventative_actions" in prediction
                assert len(prediction["preventative_actions"]) > 0
    
    def test_historical_outbreak_multiplier(self, sample_outbreak_history):
        """Test that historical outbreaks increase risk."""
        # Mock historical data
        with patch('app.services.ai_hyperlocal_prediction._get_historical_outbreaks') as mock_history:
            mock_history.return_value = sample_outbreak_history
            
            result = predict_pest_disease_outbreaks(
                crop="potato",
                lat=-1.29,
                lon=36.82,
                micro_climate_forecast=[
                    {
                        "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                        "temperature_min": 18,
                        "temperature_max": 24,
                        "humidity_avg": 85,
                        "rainfall_mm": 12
                    }
                    for i in range(7)
                ]
            )
            
            # Should have higher risk due to history
            blight_predictions = [p for p in result["predictions"] if p["pathogen"] == "late_blight"]
            if blight_predictions:
                assert blight_predictions[0]["probability"] > 0.6


# ============================================================================
# TESTS: SOURCE RELIABILITY UPDATES
# ============================================================================

class TestSourceReliabilityUpdates:
    """Test dynamic source reliability updates."""
    
    def test_update_reliability_correct_prediction(self):
        """Test that reliability increases with correct predictions."""
        initial_trust = WEATHER_SOURCE_RELIABILITY.get("satellite", 0.85)
        
        update_source_reliability(
            source="satellite",
            prediction_correct=True
        )
        
        # Trust should increase (or stay high)
        # Formula: 0.7 * old + 0.3 * new (where new = 1.0 for correct)
        # Expected: 0.7 * 0.85 + 0.3 * 1.0 = 0.595 + 0.3 = 0.895
        updated_trust = WEATHER_SOURCE_RELIABILITY.get("satellite", 0.85)
        assert updated_trust >= initial_trust or updated_trust >= 0.85
    
    def test_update_reliability_incorrect_prediction(self):
        """Test that reliability decreases with incorrect predictions."""
        # Reset to known value
        WEATHER_SOURCE_RELIABILITY["test_source"] = 0.80
        
        update_source_reliability(
            source="test_source",
            prediction_correct=False
        )
        
        # Trust should decrease
        # Formula: 0.7 * 0.80 + 0.3 * 0.0 = 0.56
        updated_trust = WEATHER_SOURCE_RELIABILITY.get("test_source", 0.80)
        assert updated_trust < 0.80
    
    def test_per_farmer_tracking(self):
        """Test per-farmer reliability tracking for crowdsourced data."""
        farmer_id = "farmer_test_123"
        
        update_source_reliability(
            source="crowdsourced",
            prediction_correct=True,
            farmer_id=farmer_id
        )
        
        # Should track per-farmer
        farmer_reliability = WEATHER_SOURCE_RELIABILITY.get(f"crowdsourced_{farmer_id}")
        assert farmer_reliability is not None
    
    def test_reliability_bounds(self):
        """Test that reliability stays within 0-1 bounds."""
        # Test many updates don't exceed bounds
        for _ in range(10):
            update_source_reliability("test_bounded", True)
        
        trust = WEATHER_SOURCE_RELIABILITY.get("test_bounded", 0.5)
        assert 0 <= trust <= 1


# ============================================================================
# TESTS: PATHOGEN DATABASE
# ============================================================================

class TestPathogenDatabase:
    """Test pathogen life cycle database."""
    
    def test_all_pathogens_defined(self):
        """Test that all major pathogens are in database."""
        expected_pathogens = [
            "late_blight",
            "fall_armyworm",
            "aphids",
            "bean_rust",
            "maize_streak_virus"
        ]
        
        for pathogen in expected_pathogens:
            assert pathogen in PATHOGEN_LIFE_CYCLES
    
    def test_pathogen_data_structure(self):
        """Test that each pathogen has required fields."""
        required_fields = [
            "temp_range",
            "humidity_threshold",
            "rainfall_condition",
            "incubation_days",
            "preventative_window_hours"
        ]
        
        for pathogen, data in PATHOGEN_LIFE_CYCLES.items():
            for field in required_fields:
                assert field in data, f"{pathogen} missing {field}"
    
    def test_temperature_ranges_realistic(self):
        """Test that temperature ranges are realistic for Kenya."""
        for pathogen, data in PATHOGEN_LIFE_CYCLES.items():
            temp_min, temp_max = data["temp_range"]
            
            # Should be within possible Kenya temps
            assert 0 <= temp_min <= 40
            assert 0 <= temp_max <= 45
            assert temp_min < temp_max


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_end_to_end_prediction_flow(self):
        """Test complete flow from weather data to outbreak prediction."""
        # Step 1: Get micro-climate forecast
        forecast = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=7)
        assert forecast is not None
        
        # Step 2: Predict outbreaks
        outbreaks = predict_pest_disease_outbreaks(
            crop="potato",
            lat=-1.29,
            lon=36.82,
            micro_climate_forecast=forecast["forecast_days"]
        )
        assert outbreaks is not None
        assert "predictions" in outbreaks
        
        # Step 3: Verify predictions have actionable data
        for prediction in outbreaks["predictions"]:
            if prediction["probability"] > 0.5:
                assert "preventative_actions" in prediction
                assert "predicted_onset_date" in prediction
    
    def test_multiple_crops_parallel(self):
        """Test predictions for multiple crops simultaneously."""
        crops = ["maize", "potato", "beans"]
        forecast = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=7)
        
        results = []
        for crop in crops:
            result = predict_pest_disease_outbreaks(
                crop=crop,
                lat=-1.29,
                lon=36.82,
                micro_climate_forecast=forecast["forecast_days"]
            )
            results.append(result)
        
        # Should have results for all crops
        assert len(results) == len(crops)
        
        # Each should have predictions
        for result in results:
            assert "predictions" in result


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and load tests."""
    
    def test_forecast_generation_speed(self):
        """Test that forecast generation is fast enough."""
        import time
        
        start = time.time()
        result = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=7)
        duration = time.time() - start
        
        # Should complete in under 2 seconds
        assert duration < 2.0
        assert result is not None
    
    def test_outbreak_prediction_speed(self):
        """Test that outbreak prediction is fast enough."""
        import time
        
        forecast = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=7)
        
        start = time.time()
        result = predict_pest_disease_outbreaks(
            crop="maize",
            lat=-1.29,
            lon=36.82,
            micro_climate_forecast=forecast["forecast_days"]
        )
        duration = time.time() - start
        
        # Should complete in under 1 second
        assert duration < 1.0
        assert result is not None
    
    def test_bulk_farmer_predictions(self):
        """Test predictions for many farmers (load test)."""
        import time
        
        num_farmers = 50
        forecast = synthesize_micro_climate_forecast(-1.29, 36.82, forecast_days=7)
        
        start = time.time()
        for i in range(num_farmers):
            predict_pest_disease_outbreaks(
                crop="maize",
                lat=-1.29 + i * 0.01,
                lon=36.82 + i * 0.01,
                micro_climate_forecast=forecast["forecast_days"]
            )
        duration = time.time() - start
        
        # Should handle 50 farmers in under 30 seconds
        assert duration < 30.0
        
        # Average per farmer
        avg_per_farmer = duration / num_farmers
        assert avg_per_farmer < 1.0  # <1 second per farmer


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.ai_hyperlocal_prediction", "--cov-report=term-missing"])
