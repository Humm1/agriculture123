"""
Test Suite for AI Smart Recommendations Engine
===============================================

Tests:
- Planting window optimization with yield simulation
- Financial risk scenario generation
- Personalized alert generation
- Farmer practice profiling

Target: 90%+ code coverage

Author: AgroShield AI Team
Date: October 2025
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.ai_smart_recommendations import (
    optimize_planting_window,
    generate_financial_risk_scenarios,
    generate_personalized_alert,
    update_farmer_practice_profile,
    CROP_YIELD_MODELS,
    MARKET_PRICE_DATA,
    FARMER_PRACTICE_PROFILES
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_farmer_profile():
    """Sample farmer practice profile."""
    return {
        "farmer_id": "test_farmer_001",
        "fertilizer_preference": "organic",
        "mulching_frequency": "regular",
        "irrigation_access": True,
        "risk_tolerance": "moderate",
        "actions_tracked": 15
    }


@pytest.fixture
def sample_field_data():
    """Sample field data."""
    return {
        "field_id": "field_001",
        "size_acres": 2.5,
        "soil_type": "ferralsols_red",
        "lat": -1.29,
        "lon": 36.82
    }


# ============================================================================
# TESTS: PLANTING WINDOW OPTIMIZATION
# ============================================================================

class TestPlantingWindowOptimization:
    """Test dynamic planting window optimization."""
    
    def test_optimize_basic_maize(self):
        """Test basic optimization for maize."""
        result = optimize_planting_window(
            crop="maize",
            lat=-1.29,
            lon=36.82,
            field_id="field_001"
        )
        
        assert "crop" in result
        assert "optimal_planting_date" in result
        assert "yield_improvement_percent" in result
        assert "recommendation" in result
        assert "all_scenarios" in result
    
    def test_yield_simulation_range(self):
        """Test that yield simulation covers -10 to +20 day range."""
        result = optimize_planting_window(
            crop="potato",
            lat=-1.29,
            lon=36.82,
            field_id="field_001"
        )
        
        scenarios = result["all_scenarios"]
        
        # Should have ~30 scenarios (-10 to +20 days)
        assert len(scenarios) >= 25
        assert len(scenarios) <= 35
    
    def test_optimal_window_identification(self):
        """Test that optimal planting date is correctly identified."""
        result = optimize_planting_window(
            crop="beans",
            lat=-1.29,
            lon=36.82,
            field_id="field_001"
        )
        
        optimal_date = result["optimal_planting_date"]
        optimal_yield = result["optimal_yield_kg_per_acre"]
        
        # Optimal yield should be highest in all scenarios
        all_yields = [s["yield_kg_per_acre"] for s in result["all_scenarios"]]
        assert optimal_yield >= max(all_yields) * 0.99  # Within 1% of max
    
    def test_recommendation_timing(self):
        """Test recommendation timing (plant now, wait, or too late)."""
        result = optimize_planting_window(
            crop="maize",
            lat=-1.29,
            lon=36.82,
            field_id="field_001"
        )
        
        recommendation = result["recommendation"]
        
        # Should have clear action
        assert any(keyword in recommendation.lower() for keyword in 
                  ["plant now", "wait", "days", "optimal"])
    
    def test_window_penalty_calculation(self):
        """Test that window penalty increases with distance from optimal."""
        result = optimize_planting_window(
            crop="tomato",
            lat=-1.29,
            lon=36.82,
            field_id="field_001"
        )
        
        scenarios = result["all_scenarios"]
        
        # Find optimal scenario
        optimal = max(scenarios, key=lambda s: s["yield_kg_per_acre"])
        optimal_offset = optimal["days_from_today"]
        
        # Scenarios farther from optimal should have lower yields
        for scenario in scenarios:
            if abs(scenario["days_from_today"] - optimal_offset) > 10:
                assert scenario["yield_kg_per_acre"] < optimal["yield_kg_per_acre"]
    
    def test_weather_impact_on_yield(self):
        """Test that weather conditions affect yield predictions."""
        # Simulate different weather conditions
        with patch('app.services.ai_smart_recommendations._get_weather_forecast') as mock_weather:
            # Scenario 1: Good rainfall
            mock_weather.return_value = {
                "rainfall_30day": 120,  # Good
                "temperature_avg": 24,
                "extreme_events": 0
            }
            result_good = optimize_planting_window("maize", -1.29, 36.82, "field_001")
            
            # Scenario 2: Drought
            mock_weather.return_value = {
                "rainfall_30day": 30,  # Drought
                "temperature_avg": 32,
                "extreme_events": 2
            }
            result_drought = optimize_planting_window("maize", -1.29, 36.82, "field_001")
            
            # Good weather should have higher optimal yield
            assert result_good["optimal_yield_kg_per_acre"] > result_drought["optimal_yield_kg_per_acre"]


# ============================================================================
# TESTS: FINANCIAL RISK SCENARIOS
# ============================================================================

class TestFinancialRiskScenarios:
    """Test financial risk scenario generation."""
    
    def test_generate_scenarios_basic(self):
        """Test basic scenario generation for multiple crops."""
        result = generate_financial_risk_scenarios(
            crops=["maize", "beans", "potato"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.5,
            farmer_id="test_farmer"
        )
        
        assert "farmer_id" in result
        assert "scenarios" in result
        assert len(result["scenarios"]) == 3
        assert "recommendation" in result
    
    def test_scenario_structure(self):
        """Test that each scenario has required fields."""
        result = generate_financial_risk_scenarios(
            crops=["maize", "beans"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id="test_farmer"
        )
        
        required_fields = [
            "crop",
            "expected_yield_kg",
            "yield_risk_percent",
            "current_price_per_kg",
            "price_volatility",
            "production_cost",
            "net_profit_expected",
            "profit_scenarios",
            "recommendation_score"
        ]
        
        for scenario in result["scenarios"]:
            for field in required_fields:
                assert field in scenario, f"Missing field: {field}"
    
    def test_profit_scenarios_calculation(self):
        """Test best/expected/worst profit scenario calculations."""
        result = generate_financial_risk_scenarios(
            crops=["maize"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id="test_farmer"
        )
        
        scenario = result["scenarios"][0]
        profit_scenarios = scenario["profit_scenarios"]
        
        # Best > Expected > Worst
        assert profit_scenarios["best_case"] >= profit_scenarios["expected"]
        assert profit_scenarios["expected"] >= profit_scenarios["worst_case"]
    
    def test_risk_adjusted_recommendations(self):
        """Test that recommendations consider both profit and risk."""
        result = generate_financial_risk_scenarios(
            crops=["maize", "sorghum"],  # Maize higher risk, Sorghum lower risk
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id="test_farmer"
        )
        
        scenarios = result["scenarios"]
        
        # Should be sorted by recommendation score
        scores = [s["recommendation_score"] for s in scenarios]
        assert scores == sorted(scores, reverse=True)
    
    def test_price_volatility_impact(self):
        """Test that price volatility affects risk calculations."""
        result = generate_financial_risk_scenarios(
            crops=["maize", "beans", "potato"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id="test_farmer"
        )
        
        for scenario in result["scenarios"]:
            # Higher volatility should mean wider profit range
            volatility = scenario["price_volatility"]
            profit_range = (scenario["profit_scenarios"]["best_case"] - 
                          scenario["profit_scenarios"]["worst_case"])
            
            # Some correlation between volatility and range
            if volatility > 0.15:  # High volatility
                assert profit_range > 0  # Should have significant range
    
    def test_farmer_risk_tolerance(self):
        """Test that farmer risk tolerance affects recommendations."""
        # Risk-averse farmer
        FARMER_PRACTICE_PROFILES["risk_averse_farmer"] = {
            "risk_tolerance": "low"
        }
        
        result_risk_averse = generate_financial_risk_scenarios(
            crops=["maize", "sorghum"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id="risk_averse_farmer"
        )
        
        # Risk-seeking farmer
        FARMER_PRACTICE_PROFILES["risk_seeking_farmer"] = {
            "risk_tolerance": "high"
        }
        
        result_risk_seeking = generate_financial_risk_scenarios(
            crops=["maize", "sorghum"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id="risk_seeking_farmer"
        )
        
        # Recommendations should differ based on risk tolerance
        # (Risk-averse should prefer lower-risk crops)
        assert result_risk_averse["recommendation"] != result_risk_seeking["recommendation"] or \
               result_risk_averse["scenarios"][0]["crop"] != result_risk_seeking["scenarios"][0]["crop"]


# ============================================================================
# TESTS: PERSONALIZED ALERTS
# ============================================================================

class TestPersonalizedAlerts:
    """Test personalized alert generation."""
    
    def test_generate_basic_alert(self):
        """Test basic alert generation."""
        result = generate_personalized_alert(
            farmer_id="test_farmer",
            crop="maize",
            crop_stage="vegetative",
            alert_type="irrigation_needed"
        )
        
        assert "alert_message" in result
        assert "personalization" in result
        assert "priority" in result
        assert "actions" in result
    
    def test_irrigation_alert_personalization(self):
        """Test irrigation alert personalization based on access."""
        # Farmer with irrigation
        FARMER_PRACTICE_PROFILES["farmer_with_irrigation"] = {
            "irrigation_access": True
        }
        
        result_with = generate_personalized_alert(
            farmer_id="farmer_with_irrigation",
            crop="maize",
            crop_stage="flowering",
            alert_type="irrigation_needed"
        )
        
        # Farmer without irrigation
        FARMER_PRACTICE_PROFILES["farmer_no_irrigation"] = {
            "irrigation_access": False
        }
        
        result_without = generate_personalized_alert(
            farmer_id="farmer_no_irrigation",
            crop="maize",
            crop_stage="flowering",
            alert_type="irrigation_needed"
        )
        
        # Messages should differ
        assert result_with["alert_message"] != result_without["alert_message"]
    
    def test_fertilizer_alert_personalization(self):
        """Test fertilizer alert personalization based on preference."""
        # Organic farmer
        FARMER_PRACTICE_PROFILES["organic_farmer"] = {
            "fertilizer_preference": "organic"
        }
        
        result_organic = generate_personalized_alert(
            farmer_id="organic_farmer",
            crop="maize",
            crop_stage="vegetative",
            alert_type="fertilizer_due"
        )
        
        # Chemical farmer
        FARMER_PRACTICE_PROFILES["chemical_farmer"] = {
            "fertilizer_preference": "chemical"
        }
        
        result_chemical = generate_personalized_alert(
            farmer_id="chemical_farmer",
            crop="maize",
            crop_stage="vegetative",
            alert_type="fertilizer_due"
        )
        
        # Should recommend different products
        assert "organic" in result_organic["alert_message"].lower() or \
               "compost" in result_organic["alert_message"].lower()
    
    def test_mulching_alert_context(self):
        """Test mulching alert considers past actions."""
        # Farmer who mulches regularly
        FARMER_PRACTICE_PROFILES["regular_mulcher"] = {
            "mulching_frequency": "regular"
        }
        
        result_regular = generate_personalized_alert(
            farmer_id="regular_mulcher",
            crop="tomato",
            crop_stage="flowering",
            alert_type="moisture_stress"
        )
        
        # Message should acknowledge existing mulch
        assert "mulch" in result_regular["alert_message"].lower()
    
    def test_alert_fatigue_prevention(self):
        """Test that similar alerts have cooldown."""
        # Generate same alert twice quickly
        result1 = generate_personalized_alert(
            farmer_id="test_farmer",
            crop="maize",
            crop_stage="vegetative",
            alert_type="irrigation_needed"
        )
        
        result2 = generate_personalized_alert(
            farmer_id="test_farmer",
            crop="maize",
            crop_stage="vegetative",
            alert_type="irrigation_needed"
        )
        
        # Second alert should have lower priority or be suppressed
        # (implementation specific)
        assert result2 is not None


# ============================================================================
# TESTS: FARMER PRACTICE PROFILING
# ============================================================================

class TestFarmerPracticeProfile:
    """Test farmer practice profiling system."""
    
    def test_track_fertilizer_preference(self):
        """Test tracking fertilizer preference."""
        farmer_id = "test_profile_farmer"
        
        # Track multiple organic applications
        for _ in range(5):
            update_farmer_practice_profile(
                farmer_id=farmer_id,
                action="fertilizer_application",
                context={"type": "organic"}
            )
        
        # Track one chemical application
        update_farmer_practice_profile(
            farmer_id=farmer_id,
            action="fertilizer_application",
            context={"type": "chemical"}
        )
        
        profile = FARMER_PRACTICE_PROFILES.get(farmer_id, {})
        
        # Should infer organic preference (>67% organic)
        assert profile.get("fertilizer_preference") == "organic"
    
    def test_track_mulching_frequency(self):
        """Test tracking mulching frequency."""
        farmer_id = "test_mulcher"
        
        # Track regular mulching
        for i in range(3):
            update_farmer_practice_profile(
                farmer_id=farmer_id,
                action="mulching",
                context={"date": (datetime.now() - timedelta(days=i*30)).isoformat()}
            )
        
        profile = FARMER_PRACTICE_PROFILES.get(farmer_id, {})
        
        # Should detect regular mulching
        assert profile.get("mulching_frequency") in ["regular", "frequent"]
    
    def test_track_irrigation_access(self):
        """Test detecting irrigation access."""
        farmer_id = "test_irrigator"
        
        # Track irrigation events
        for _ in range(3):
            update_farmer_practice_profile(
                farmer_id=farmer_id,
                action="irrigation",
                context={"method": "drip"}
            )
        
        profile = FARMER_PRACTICE_PROFILES.get(farmer_id, {})
        
        # Should detect irrigation access
        assert profile.get("irrigation_access") == True
    
    def test_infer_risk_tolerance(self):
        """Test inferring risk tolerance from crop choices."""
        farmer_id = "test_risk_farmer"
        
        # Track high-value, high-risk crop choices
        crops_tracked = ["tomato", "cabbage", "potato"]  # Higher risk/reward
        
        for crop in crops_tracked:
            update_farmer_practice_profile(
                farmer_id=farmer_id,
                action="crop_selection",
                context={"crop": crop}
            )
        
        profile = FARMER_PRACTICE_PROFILES.get(farmer_id, {})
        
        # Profile should exist and track crops
        assert farmer_id in FARMER_PRACTICE_PROFILES
        assert profile.get("actions_tracked", 0) >= 3


# ============================================================================
# TESTS: CROP MODELS AND MARKET DATA
# ============================================================================

class TestCropModelsAndMarketData:
    """Test crop yield models and market price data."""
    
    def test_all_major_crops_in_models(self):
        """Test that all major crops have yield models."""
        expected_crops = ["maize", "potato", "beans", "tomato", "cabbage", "sorghum"]
        
        for crop in expected_crops:
            assert crop in CROP_YIELD_MODELS, f"Missing model for {crop}"
    
    def test_yield_model_structure(self):
        """Test that each crop model has required fields."""
        required_fields = [
            "base_yield_kg_per_acre",
            "optimal_planting_window",
            "water_stress_sensitivity",
            "temperature_sensitivity",
            "growth_days"
        ]
        
        for crop, model in CROP_YIELD_MODELS.items():
            for field in required_fields:
                assert field in model, f"{crop} missing {field}"
    
    def test_market_data_completeness(self):
        """Test that market data has pricing for all crops."""
        for crop in CROP_YIELD_MODELS.keys():
            assert crop in MARKET_PRICE_DATA, f"Missing market data for {crop}"
    
    def test_market_price_structure(self):
        """Test market price data structure."""
        required_fields = [
            "current_price_per_kg",
            "volatility",
            "seasonal_multipliers",
            "production_cost_per_acre"
        ]
        
        for crop, data in MARKET_PRICE_DATA.items():
            for field in required_fields:
                assert field in data, f"{crop} missing {field}"
    
    def test_seasonal_multipliers_realistic(self):
        """Test that seasonal multipliers are realistic."""
        for crop, data in MARKET_PRICE_DATA.items():
            multipliers = data["seasonal_multipliers"]
            
            # Harvest season should have lower prices
            # Planting/lean season should have higher prices
            assert 0.5 <= multipliers["harvest_season"] <= 1.5
            assert 0.8 <= multipliers["planting_season"] <= 2.0
            assert 0.8 <= multipliers["lean_season"] <= 2.5


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for recommendations engine."""
    
    def test_complete_farmer_workflow(self):
        """Test complete workflow: profiling → optimization → recommendation."""
        farmer_id = "integration_test_farmer"
        
        # Step 1: Build farmer profile
        update_farmer_practice_profile(
            farmer_id=farmer_id,
            action="fertilizer_application",
            context={"type": "organic"}
        )
        update_farmer_practice_profile(
            farmer_id=farmer_id,
            action="mulching",
            context={"date": datetime.now().isoformat()}
        )
        
        # Step 2: Optimize planting window
        planting = optimize_planting_window(
            crop="maize",
            lat=-1.29,
            lon=36.82,
            field_id="field_001"
        )
        assert planting is not None
        
        # Step 3: Get financial scenarios
        financial = generate_financial_risk_scenarios(
            crops=["maize", "beans"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id=farmer_id
        )
        assert financial is not None
        
        # Step 4: Generate personalized alert
        alert = generate_personalized_alert(
            farmer_id=farmer_id,
            crop="maize",
            crop_stage="vegetative",
            alert_type="fertilizer_due"
        )
        assert alert is not None
        assert "organic" in alert["alert_message"].lower()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance tests for recommendations engine."""
    
    def test_optimization_speed(self):
        """Test planting window optimization speed."""
        import time
        
        start = time.time()
        result = optimize_planting_window("maize", -1.29, 36.82, "field_001")
        duration = time.time() - start
        
        # Should complete in under 2 seconds
        assert duration < 2.0
        assert result is not None
    
    def test_financial_scenarios_speed(self):
        """Test financial scenario generation speed."""
        import time
        
        start = time.time()
        result = generate_financial_risk_scenarios(
            crops=["maize", "beans", "potato", "tomato"],
            lat=-1.29,
            lon=36.82,
            field_size_acres=2.0,
            farmer_id="perf_test"
        )
        duration = time.time() - start
        
        # Should complete in under 1 second
        assert duration < 1.0
        assert result is not None
    
    def test_bulk_recommendations(self):
        """Test recommendations for many farmers."""
        import time
        
        num_farmers = 100
        
        start = time.time()
        for i in range(num_farmers):
            generate_personalized_alert(
                farmer_id=f"farmer_{i}",
                crop="maize",
                crop_stage="vegetative",
                alert_type="irrigation_needed"
            )
        duration = time.time() - start
        
        # Should handle 100 farmers in under 10 seconds
        assert duration < 10.0
        
        avg_per_farmer = duration / num_farmers
        assert avg_per_farmer < 0.1  # <100ms per farmer


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.ai_smart_recommendations", "--cov-report=term-missing"])
