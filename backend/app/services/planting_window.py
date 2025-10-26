"""
Planting Window Calculator

Determines optimal planting dates based on:
- LCRS (climate risk)
- Soil moisture conditions
- Seasonal rainfall patterns
- Crop-specific requirements

Provides late planting alerts and alternative crop suggestions.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from . import climate_persistence, lcrs_engine, advice

def get_optimal_planting_window(crop: str, location: dict, current_month: int = None) -> Dict:
    """
    Calculate optimal planting window for a crop based on location and season.
    
    Returns:
    {
        'start_date': str (ISO date),
        'end_date': str (ISO date),
        'rationale': str,
        'confidence': float (0-1)
    }
    """
    if not current_month:
        current_month = datetime.utcnow().month
    
    # Crop-specific planting windows (East Africa example)
    # In production, this would be from a database with regional variations
    crop_windows = {
        'maize': {
            'long_rains': {'start_month': 3, 'end_month': 4, 'duration_days': 45},
            'short_rains': {'start_month': 10, 'end_month': 11, 'duration_days': 30},
        },
        'potatoes': {
            'long_rains': {'start_month': 2, 'end_month': 3, 'duration_days': 30},
            'short_rains': {'start_month': 9, 'end_month': 10, 'duration_days': 30},
        },
        'beans': {
            'long_rains': {'start_month': 3, 'end_month': 4, 'duration_days': 30},
            'short_rains': {'start_month': 10, 'end_month': 11, 'duration_days': 30},
        },
        'rice': {
            'long_rains': {'start_month': 3, 'end_month': 5, 'duration_days': 60},
        },
        'cassava': {
            'year_round': {'start_month': 1, 'end_month': 12, 'duration_days': 365},
        }
    }
    
    crop_lower = crop.lower()
    if crop_lower not in crop_windows:
        # Default fallback
        return {
            'start_date': datetime.utcnow().isoformat(),
            'end_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
            'rationale': 'General planting window - consult local agronomist',
            'confidence': 0.3
        }
    
    # Find the nearest planting season
    windows = crop_windows[crop_lower]
    best_window = None
    min_distance = 12
    
    for season, window in windows.items():
        start_month = window['start_month']
        # Calculate distance to start month
        distance = (start_month - current_month) % 12
        if distance < min_distance:
            min_distance = distance
            best_window = window
            best_season = season
    
    # Calculate actual dates
    year = datetime.utcnow().year
    if best_window['start_month'] < current_month:
        year += 1  # Next year
    
    start_date = datetime(year, best_window['start_month'], 1)
    end_date = start_date + timedelta(days=best_window['duration_days'])
    
    rationale = f"Optimal for {best_season} season based on historical rainfall patterns"
    confidence = 0.8
    
    return {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'rationale': rationale,
        'confidence': confidence
    }

def check_planting_status(farmer_id: str, field_id: str, crop: str, location: dict) -> Dict:
    """
    Check if farmer is within optimal planting window, late, or early.
    
    Returns:
    {
        'status': 'optimal' | 'early' | 'late' | 'very_late',
        'days_difference': int,
        'message': str,
        'alternative_crops': [str] (if late),
        'diversification_advice': str (if applicable)
    }
    """
    optimal_window = get_optimal_planting_window(crop, location)
    now = datetime.utcnow()
    start = datetime.fromisoformat(optimal_window['start_date'])
    end = datetime.fromisoformat(optimal_window['end_date'])
    
    if start <= now <= end:
        return {
            'status': 'optimal',
            'days_difference': 0,
            'message': f"✅ IDEAL TIME: You are within the optimal planting window for {crop}. Plant now for best results!",
            'alternative_crops': [],
            'diversification_advice': None
        }
    elif now < start:
        days_early = (start - now).days
        return {
            'status': 'early',
            'days_difference': -days_early,
            'message': f"⏰ EARLY: Optimal planting starts in {days_early} days. Prepare your field and seeds.",
            'alternative_crops': [],
            'diversification_advice': None
        }
    else:
        # Late planting
        days_late = (now - end).days
        
        if days_late > 30:
            status = 'very_late'
            alternatives = get_alternative_crops(crop, days_late)
            message = f"🛑 VERY LATE: You are {days_late} days past optimal window. Strongly consider switching to fast-maturing alternatives: {', '.join(alternatives)}"
        else:
            status = 'late'
            alternatives = get_alternative_crops(crop, days_late)
            message = f"⚠️ LATE: You are {days_late} days past optimal window. Consider fast-maturing {crop} varieties or switch to: {', '.join(alternatives)}"
        
        # Check LCRS for diversification advice
        lcrs_data = lcrs_engine.calculate_lcrs(farmer_id, field_id, location)
        diversification = None
        if lcrs_data['risk_level'] in ['moderate', 'high']:
            diversification = "🌾 RISK HEDGE: Dedicate 20% of land to drought-tolerant cassava or sorghum to reduce crop failure risk."
        
        return {
            'status': status,
            'days_difference': days_late,
            'message': message,
            'alternative_crops': alternatives,
            'diversification_advice': diversification
        }

def get_alternative_crops(original_crop: str, days_late: int) -> List[str]:
    """Suggest alternative fast-maturing crops based on how late farmer is"""
    
    # Fast-maturing alternatives by original crop
    alternatives = {
        'maize': ['beans', 'cowpeas', 'amaranth'],
        'potatoes': ['sweet potatoes', 'vegetables'],
        'beans': ['green grams', 'cowpeas'],
        'rice': ['vegetables', 'beans']
    }
    
    crop_lower = original_crop.lower()
    
    if days_late > 30:
        # Very late: suggest drought-resistant options
        return ['cassava', 'sorghum', 'millet']
    elif crop_lower in alternatives:
        return alternatives[crop_lower]
    else:
        return ['beans', 'vegetables']

def generate_diversification_plan(farmer_id: str, field_id: str, location: dict, 
                                 total_area_hectares: float) -> Dict:
    """
    Generate crop diversification plan based on LCRS risk level.
    
    Returns:
    {
        'primary_crop': {'crop': str, 'percentage': float, 'area_hectares': float},
        'diversification_crops': [{'crop': str, 'percentage': float, 'area_hectares': float}],
        'rationale': str
    }
    """
    lcrs_data = lcrs_engine.calculate_lcrs(farmer_id, field_id, location)
    
    if lcrs_data['risk_level'] == 'low':
        # Low risk: 90% primary crop, 10% diversification
        return {
            'primary_crop': {'crop': 'maize', 'percentage': 90, 'area_hectares': total_area_hectares * 0.9},
            'diversification_crops': [
                {'crop': 'beans', 'percentage': 10, 'area_hectares': total_area_hectares * 0.1}
            ],
            'rationale': 'Low climate risk allows focus on primary income crop with minimal diversification.'
        }
    elif lcrs_data['risk_level'] == 'moderate':
        # Moderate risk: 70% primary, 20% drought-tolerant, 10% quick-maturing
        return {
            'primary_crop': {'crop': 'maize', 'percentage': 70, 'area_hectares': total_area_hectares * 0.7},
            'diversification_crops': [
                {'crop': 'cassava', 'percentage': 20, 'area_hectares': total_area_hectares * 0.2},
                {'crop': 'beans', 'percentage': 10, 'area_hectares': total_area_hectares * 0.1}
            ],
            'rationale': 'Moderate climate risk: hedge with 20% drought-tolerant cassava as safety net.'
        }
    else:
        # High risk: 50% primary, 30% drought-tolerant, 20% quick-maturing
        return {
            'primary_crop': {'crop': 'maize', 'percentage': 50, 'area_hectares': total_area_hectares * 0.5},
            'diversification_crops': [
                {'crop': 'cassava', 'percentage': 30, 'area_hectares': total_area_hectares * 0.3},
                {'crop': 'sorghum', 'percentage': 20, 'area_hectares': total_area_hectares * 0.2}
            ],
            'rationale': '🚨 HIGH RISK YEAR: Maximize drought-resistant crops (cassava, sorghum) to ensure food security even if rains fail.'
        }
