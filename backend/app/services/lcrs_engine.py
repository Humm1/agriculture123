"""
LCRS (Localized Climate Risk Score) Calculation Engine

Combines:
- Official meteorological data (rainfall patterns, temperature trends)
- Crowdsourced rain reports from local farmers
- Soil Moisture Index from farmer reports
- Historical climate patterns

Output: Risk score (0-100) where:
- 0-30: Low risk (favorable conditions)
- 31-60: Moderate risk (normal variability)
- 61-100: High risk (drought/flood likely)
"""
from datetime import datetime, timedelta
from typing import Dict, List
from . import climate_persistence

def calculate_crowdsourced_rain_factor(location: dict, days: int = 7) -> float:
    """
    Analyze recent crowdsourced rain reports to estimate rainfall adequacy.
    Returns 0-1 where 1 = adequate rain, 0 = drought conditions
    """
    reports = climate_persistence.get_rain_reports(days=days, location=location)
    
    if not reports:
        return 0.5  # neutral if no data
    
    # Weight recent reports more heavily
    total_weight = 0
    weighted_sum = 0
    
    for r in reports:
        # Convert amount to numeric score
        amount_scores = {
            'none': 0,
            'light': 0.3,
            'moderate': 0.7,
            'heavy': 1.0
        }
        score = amount_scores.get(r['amount'], 0.5)
        
        # Time decay: recent reports weighted more
        days_ago = (datetime.utcnow() - datetime.fromisoformat(r['ts'])).days
        weight = max(0.1, 1.0 - (days_ago / days))
        
        weighted_sum += score * weight
        total_weight += weight
    
    return weighted_sum / total_weight if total_weight > 0 else 0.5

def calculate_soil_moisture_factor(farmer_id: str, field_id: str) -> float:
    """
    Get soil moisture index from farmer's latest report.
    Returns 0-1 where 1 = optimal moisture, 0 = very dry/saturated
    """
    report = climate_persistence.get_latest_soil_report(farmer_id, field_id)
    
    if not report:
        return 0.5  # neutral if no data
    
    smi = climate_persistence.calculate_soil_moisture_index(report['moisture_level'])
    
    # Optimal soil moisture is around 60% (damp)
    # Convert to risk factor: distance from optimal
    optimal = 60
    deviation = abs(smi - optimal) / optimal
    
    # Convert deviation to favorable factor (1 = optimal, 0 = extreme)
    return max(0, 1 - deviation)

def estimate_weather_forecast_risk(month_offset: int = 0) -> float:
    """
    Estimate weather risk for a future month (0 = current month, 1 = next month, etc.)
    In production, this would integrate with national meteorological API.
    
    For demo, uses simplified seasonal patterns for East Africa:
    - March-May: Long rains (low risk)
    - June-September: Dry season (moderate-high risk)
    - October-December: Short rains (low-moderate risk)
    - January-February: Dry season (high risk)
    """
    target_month = (datetime.utcnow().month + month_offset) % 12
    if target_month == 0:
        target_month = 12
    
    # Seasonal risk scores for East Africa (simplified)
    seasonal_risk = {
        1: 0.8,   # Jan: Dry, high risk
        2: 0.8,   # Feb: Dry, high risk
        3: 0.3,   # Mar: Long rains start
        4: 0.2,   # Apr: Long rains peak
        5: 0.3,   # May: Long rains end
        6: 0.6,   # Jun: Dry season
        7: 0.7,   # Jul: Dry season
        8: 0.7,   # Aug: Dry season
        9: 0.6,   # Sep: Dry season end
        10: 0.4,  # Oct: Short rains start
        11: 0.3,  # Nov: Short rains
        12: 0.4,  # Dec: Short rains end
    }
    
    return seasonal_risk.get(target_month, 0.5)

def calculate_lcrs(farmer_id: str, field_id: str, location: dict, 
                  forecast_months: int = 3) -> Dict:
    """
    Calculate Localized Climate Risk Score (LCRS) for the next N months.
    
    Returns:
    {
        'score': float (0-100),
        'risk_level': 'low' | 'moderate' | 'high',
        'factors': {
            'rain_adequacy': float,
            'soil_moisture': float,
            'seasonal_forecast': float,
            'drought_risk': float,
            'flood_risk': float
        },
        'recommendations': [str],
        'valid_until': str (ISO date)
    }
    """
    # 1. Crowdsourced rain factor (recent 14 days)
    rain_factor = calculate_crowdsourced_rain_factor(location, days=14)
    
    # 2. Soil moisture factor
    soil_factor = calculate_soil_moisture_factor(farmer_id, field_id)
    
    # 3. Seasonal forecast (average over next N months)
    forecast_risks = [estimate_weather_forecast_risk(i) for i in range(forecast_months)]
    avg_forecast_risk = sum(forecast_risks) / len(forecast_risks)
    
    # 4. Drought risk (low rain + low soil moisture + high forecast risk)
    drought_risk = (1 - rain_factor) * 0.3 + (1 - soil_factor) * 0.3 + avg_forecast_risk * 0.4
    
    # 5. Flood risk (high rain + high soil moisture)
    # Get actual soil moisture value, not optimal factor
    soil_report = climate_persistence.get_latest_soil_report(farmer_id, field_id)
    soil_saturation = 0.5
    if soil_report:
        smi = climate_persistence.calculate_soil_moisture_index(soil_report['moisture_level'])
        soil_saturation = smi / 100.0
    
    flood_risk = rain_factor * 0.5 + soil_saturation * 0.5 if soil_saturation > 0.7 else 0.1
    
    # 6. Overall LCRS (weighted combination)
    # Higher score = higher risk
    lcrs = (
        drought_risk * 0.6 +      # Drought is primary concern
        flood_risk * 0.2 +        # Flood less common but serious
        avg_forecast_risk * 0.2   # General seasonal risk
    ) * 100
    
    # Determine risk level
    if lcrs < 30:
        risk_level = 'low'
    elif lcrs < 60:
        risk_level = 'moderate'
    else:
        risk_level = 'high'
    
    # Generate recommendations
    recommendations = []
    if drought_risk > 0.6:
        recommendations.append('High drought risk: Consider drought-resistant crop varieties')
        recommendations.append('Implement water conservation measures')
    if flood_risk > 0.6:
        recommendations.append('High flood risk: Ensure proper drainage in fields')
        recommendations.append('Consider raised bed planting')
    if soil_factor < 0.4:
        recommendations.append('Soil moisture suboptimal: Check irrigation or drainage needs')
    
    # Crop diversification advice for high risk
    if lcrs > 60:
        recommendations.append('DIVERSIFICATION: Allocate 20% of land to drought-tolerant cash crop (cassava, sorghum)')
    
    valid_until = (datetime.utcnow() + timedelta(days=forecast_months * 30)).isoformat()
    
    return {
        'score': round(lcrs, 1),
        'risk_level': risk_level,
        'factors': {
            'rain_adequacy': round(rain_factor, 2),
            'soil_moisture': round(soil_factor, 2),
            'seasonal_forecast': round(avg_forecast_risk, 2),
            'drought_risk': round(drought_risk, 2),
            'flood_risk': round(flood_risk, 2)
        },
        'recommendations': recommendations,
        'valid_until': valid_until
    }
