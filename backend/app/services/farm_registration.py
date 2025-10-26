"""
Farm Registration and Soil Data Management
Handles field registration, GPS location, crop selection, and soil data intake

ENHANCED WITH AI:
- Micro-climate profiling from GPS coordinates
- Computer vision soil analysis
- AI-driven crop variety recommendations with risk assessment
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Import AI intelligence engine
from .ai_farm_intelligence import (
    analyze_microclimate_from_gps,
    analyze_soil_photo_with_ai,
    recommend_crop_variety_with_ai
)

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FARMS_FILE = DATA_DIR / "farms.json"
SOIL_DATA_FILE = DATA_DIR / "soil_data.json"
SOIL_PHOTOS_FILE = DATA_DIR / "soil_photos.json"


def load_farms() -> Dict:
    """Load all farm registrations"""
    if FARMS_FILE.exists():
        with open(FARMS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_farms(farms: Dict):
    """Save farm registrations"""
    with open(FARMS_FILE, 'w') as f:
        json.dump(farms, f, indent=2)


def load_soil_data() -> Dict:
    """Load all soil data"""
    if SOIL_DATA_FILE.exists():
        with open(SOIL_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_soil_data(soil_data: Dict):
    """Save soil data"""
    with open(SOIL_DATA_FILE, 'w') as f:
        json.dump(soil_data, f, indent=2)


def load_soil_photos() -> Dict:
    """Load soil photo metadata"""
    if SOIL_PHOTOS_FILE.exists():
        with open(SOIL_PHOTOS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_soil_photos(photos: Dict):
    """Save soil photo metadata"""
    with open(SOIL_PHOTOS_FILE, 'w') as f:
        json.dump(photos, f, indent=2)


def register_farm(
    farmer_id: str,
    field_name: str,
    location: Dict[str, float],  # {"latitude": -1.29, "longitude": 36.82}
    crop: str,
    variety: str,
    area_hectares: float,
    elevation: Optional[float] = None,
    enable_ai_analysis: bool = True
) -> Dict:
    """
    Register a new farm/field with GPS location and crop details
    
    ENHANCED WITH AI:
    - Automatically profiles micro-climate from GPS
    - Cross-references satellite imagery (NDVI)
    - Analyzes nearby farming groups
    - Selects optimal growth model adjustment
    
    Args:
        farmer_id: Unique farmer identifier
        field_name: Name/identifier for this field (e.g., "Plot 1", "East Field")
        location: GPS coordinates {"latitude": -1.29, "longitude": 36.82}
        crop: Main crop (e.g., "maize", "beans")
        variety: Specific variety (e.g., "H614", "KAT B1")
        area_hectares: Field size in hectares
        elevation: Optional elevation in meters (from GPS if available)
        enable_ai_analysis: Whether to run AI micro-climate profiling
    
    Returns:
        Complete farm registration record with AI insights
    """
    farms = load_farms()
    
    if farmer_id not in farms:
        farms[farmer_id] = {}
    
    field_id = f"{farmer_id}_{field_name.replace(' ', '_').lower()}"
    
    # =========================================================================
    # AI ENHANCEMENT: Micro-Climate Profiling
    # =========================================================================
    ai_microclimate = None
    if enable_ai_analysis:
        ai_microclimate = analyze_microclimate_from_gps(
            latitude=location["latitude"],
            longitude=location["longitude"],
            elevation=elevation
        )
    
    farm_record = {
        "field_id": field_id,
        "farmer_id": farmer_id,
        "field_name": field_name,
        "location": location,
        "elevation": elevation or (ai_microclimate["location"]["elevation"] if ai_microclimate else None),
        "crop": crop.lower(),
        "variety": variety,
        "area_hectares": area_hectares,
        "registered_at": datetime.utcnow().isoformat(),
        "status": "active",
        "planting_date": None,  # Set later when planting occurs
        "soil_snapshot_completed": False,
        
        # AI-powered insights
        "ai_microclimate_profile": ai_microclimate,
        "farming_zone": ai_microclimate["farming_zone"] if ai_microclimate else "unknown",
        "growth_model_adjustment": ai_microclimate["growth_model_adjustment"] if ai_microclimate else None,
        "climate_risk_factors": ai_microclimate["risk_factors"] if ai_microclimate else []
    }
    
    farms[farmer_id][field_id] = farm_record
    save_farms(farms)
    
    # Generate AI registration report
    if ai_microclimate:
        report = _generate_ai_registration_report(farm_record, ai_microclimate)
        farm_record["ai_registration_report"] = report
    
    return farm_record


def _generate_ai_registration_report(farm: Dict, ai_profile: Dict) -> Dict:
    """Generate farmer-friendly AI registration report"""
    return {
        "summary": f"Your farm in {ai_profile['farming_zone'].replace('_', ' ').title()} zone",
        "location_insights": [
            f"📍 Elevation: {ai_profile['location']['elevation']}m",
            f"🌡️ Temperature range: {ai_profile['climate_factors']['typical_temp_range'][0]}-{ai_profile['climate_factors']['typical_temp_range'][1]}°C",
            f"💧 Rainfall: {ai_profile['climate_factors']['estimated_annual_rainfall'][0]}-{ai_profile['climate_factors']['estimated_annual_rainfall'][1]}mm/year"
        ],
        "satellite_analysis": {
            "vegetation_health": ai_profile["satellite_analysis"]["ndvi_health_category"],
            "note": ai_profile["satellite_analysis"]["vegetation_status"]
        },
        "community_context": ai_profile["community_insights"]["message"],
        "growth_model_note": ai_profile["growth_model_adjustment"]["explanation"],
        "risk_warnings": [r["risk"] + " (" + r["severity"] + ")" for r in ai_profile["risk_factors"]],
        "recommended_crops": ai_profile["recommended_crops"]
    }


def add_soil_snapshot_simple(
    field_id: str,
    soil_photo_wet_url: str,
    soil_photo_dry_url: str,
    estimated_texture: Optional[str] = None,
    estimated_type: Optional[str] = None,
    enable_ai_analysis: bool = True
) -> Dict:
    """
    Add simple soil snapshot with photo URLs
    
    ENHANCED WITH AI:
    - Computer vision analyzes soil color, texture, moisture
    - Generates Initial Fertility Score
    - Suggests 2 most probable soil types
    - Provides visual nutrient deficiency indicators
    
    Args:
        field_id: Field identifier
        soil_photo_wet_url: URL/path to wet soil photo
        soil_photo_dry_url: URL/path to dry soil photo
        estimated_texture: Optional texture estimate (e.g., "sandy", "loamy", "clay")
        estimated_type: Optional type estimate (e.g., "Red Clay", "Black Cotton")
    
    Returns:
        Soil snapshot record
    """
    photos = load_soil_photos()
    
    # =========================================================================
    # AI ENHANCEMENT: Computer Vision Soil Analysis
    # =========================================================================
    ai_soil_analysis = None
    if enable_ai_analysis:
        # Get farm location for geological context
        farm = get_farm_by_field_id(field_id)
        if farm and "location" in farm:
            ai_soil_analysis = analyze_soil_photo_with_ai(
                image_url=soil_photo_wet_url,  # Use wet photo for analysis
                gps_location=farm["location"],
                moisture_condition="wet"
            )
    
    snapshot = {
        "field_id": field_id,
        "method": "photo_simple",
        "wet_photo_url": soil_photo_wet_url,
        "dry_photo_url": soil_photo_dry_url,
        "estimated_texture": estimated_texture or "unknown",
        "estimated_type": estimated_type or "unknown",
        "captured_at": datetime.utcnow().isoformat(),
        "quality_score": calculate_photo_quality_score(estimated_texture, estimated_type),
        
        # AI-powered insights
        "ai_soil_analysis": ai_soil_analysis
    }
    
    # If AI analysis available, populate probable soil types
    if ai_soil_analysis:
        snapshot["ai_fertility_score"] = ai_soil_analysis["fertility_assessment"]["overall_score"]
        snapshot["ai_fertility_rating"] = ai_soil_analysis["fertility_assessment"]["rating"]
        snapshot["ai_probable_types"] = [
            pt["type"] for pt in ai_soil_analysis["probable_soil_types"]
        ]
        snapshot["ai_recommendations"] = ai_soil_analysis["recommendations"]
    
    if field_id not in photos:
        photos[field_id] = []
    photos[field_id].append(snapshot)
    save_soil_photos(photos)
    
    # Update farm record
    _update_soil_snapshot_status(field_id, True)
    
    return snapshot


def add_soil_snapshot_advanced(
    field_id: str,
    ph: float,
    nitrogen_ppm: float,
    phosphorus_ppm: float,
    potassium_ppm: float,
    organic_matter_percent: Optional[float] = None,
    data_source: str = "manual"  # "manual", "ble_sensor", "lab_test"
) -> Dict:
    """
    Add advanced soil snapshot with NPK values
    
    Args:
        field_id: Field identifier
        ph: Soil pH (typically 4.5 - 8.5)
        nitrogen_ppm: Nitrogen in parts per million
        phosphorus_ppm: Phosphorus in parts per million
        potassium_ppm: Potassium in parts per million
        organic_matter_percent: Optional organic matter percentage
        data_source: How data was obtained
    
    Returns:
        Soil snapshot record with recommendations
    """
    soil_data = load_soil_data()
    
    snapshot = {
        "field_id": field_id,
        "method": "advanced_npk",
        "data_source": data_source,
        "ph": ph,
        "nitrogen_ppm": nitrogen_ppm,
        "phosphorus_ppm": phosphorus_ppm,
        "potassium_ppm": potassium_ppm,
        "organic_matter_percent": organic_matter_percent,
        "captured_at": datetime.utcnow().isoformat(),
        "quality_score": 100,  # Advanced data is always high quality
        "recommendations": generate_soil_recommendations(ph, nitrogen_ppm, phosphorus_ppm, potassium_ppm)
    }
    
    if field_id not in soil_data:
        soil_data[field_id] = []
    soil_data[field_id].append(snapshot)
    save_soil_data(soil_data)
    
    # Update farm record
    _update_soil_snapshot_status(field_id, True)
    
    return snapshot


def get_latest_soil_snapshot(field_id: str) -> Optional[Dict]:
    """Get the most recent soil snapshot for a field"""
    # Check advanced data first
    soil_data = load_soil_data()
    if field_id in soil_data and soil_data[field_id]:
        return soil_data[field_id][-1]
    
    # Fall back to photo data
    photos = load_soil_photos()
    if field_id in photos and photos[field_id]:
        return photos[field_id][-1]
    
    return None


def calculate_photo_quality_score(texture: Optional[str], soil_type: Optional[str]) -> int:
    """
    Calculate quality score for photo-based soil estimation
    
    Returns:
        Quality score 0-100 (lower = less reliable)
    """
    score = 50  # Base score for photo analysis
    
    if texture and texture != "unknown":
        score += 20
    if soil_type and soil_type != "unknown":
        score += 30
    
    return score


def generate_soil_recommendations(
    ph: float,
    nitrogen_ppm: float,
    phosphorus_ppm: float,
    potassium_ppm: float
) -> Dict:
    """
    Generate soil amendment recommendations based on NPK values
    
    Returns:
        Dictionary with recommendations and urgency levels
    """
    recommendations = {
        "ph_status": "optimal",
        "nitrogen_status": "optimal",
        "phosphorus_status": "optimal",
        "potassium_status": "optimal",
        "amendments_needed": [],
        "urgency": "low"
    }
    
    # pH recommendations (optimal range 6.0-7.5 for most crops)
    if ph < 5.5:
        recommendations["ph_status"] = "too_acidic"
        recommendations["amendments_needed"].append({
            "issue": "Soil too acidic",
            "recommendation": "Apply agricultural lime (2-4 tons/hectare)",
            "local_alternative": "Wood ash or crushed eggshells",
            "urgency": "high"
        })
        recommendations["urgency"] = "high"
    elif ph > 8.0:
        recommendations["ph_status"] = "too_alkaline"
        recommendations["amendments_needed"].append({
            "issue": "Soil too alkaline",
            "recommendation": "Apply sulfur or organic matter",
            "local_alternative": "Compost or coffee grounds",
            "urgency": "medium"
        })
        if recommendations["urgency"] == "low":
            recommendations["urgency"] = "medium"
    
    # Nitrogen recommendations (optimal > 30 ppm)
    if nitrogen_ppm < 20:
        recommendations["nitrogen_status"] = "deficient"
        recommendations["amendments_needed"].append({
            "issue": "Nitrogen deficiency",
            "recommendation": "Apply CAN (50-100 kg/hectare) or Urea",
            "local_alternative": "Well-composted manure (5-10 tons/hectare) or legume intercropping",
            "urgency": "high"
        })
        recommendations["urgency"] = "high"
    elif nitrogen_ppm < 30:
        recommendations["nitrogen_status"] = "low"
        recommendations["amendments_needed"].append({
            "issue": "Low nitrogen",
            "recommendation": "Plan for top-dress application",
            "local_alternative": "Green manure or compost tea",
            "urgency": "medium"
        })
        if recommendations["urgency"] == "low":
            recommendations["urgency"] = "medium"
    
    # Phosphorus recommendations (optimal > 15 ppm)
    if phosphorus_ppm < 10:
        recommendations["phosphorus_status"] = "deficient"
        recommendations["amendments_needed"].append({
            "issue": "Phosphorus deficiency",
            "recommendation": "Apply DAP or TSP (30-50 kg/hectare)",
            "local_alternative": "Bone meal or rock phosphate",
            "urgency": "high"
        })
        recommendations["urgency"] = "high"
    
    # Potassium recommendations (optimal > 100 ppm)
    if potassium_ppm < 80:
        recommendations["potassium_status"] = "deficient"
        recommendations["amendments_needed"].append({
            "issue": "Potassium deficiency",
            "recommendation": "Apply Muriate of Potash (20-40 kg/hectare)",
            "local_alternative": "Wood ash or banana peels compost",
            "urgency": "medium"
        })
        if recommendations["urgency"] == "low":
            recommendations["urgency"] = "medium"
    
    return recommendations


def get_farm_by_field_id(field_id: str) -> Optional[Dict]:
    """Get farm record by field ID"""
    farms = load_farms()
    for farmer_id, fields in farms.items():
        if field_id in fields:
            return fields[field_id]
    return None


def get_farmer_farms(farmer_id: str) -> Dict:
    """Get all farms for a farmer"""
    farms = load_farms()
    return farms.get(farmer_id, {})


def update_planting_date(field_id: str, planting_date: str) -> Dict:
    """Update planting date for a field (triggers calendar generation)"""
    farms = load_farms()
    
    for farmer_id, fields in farms.items():
        if field_id in fields:
            fields[field_id]["planting_date"] = planting_date
            fields[field_id]["planting_updated_at"] = datetime.utcnow().isoformat()
            save_farms(farms)
            return fields[field_id]
    
    raise ValueError(f"Field {field_id} not found")


def _update_soil_snapshot_status(field_id: str, completed: bool):
    """Internal helper to update soil snapshot completion status"""
    farms = load_farms()
    
    for farmer_id, fields in farms.items():
        if field_id in fields:
            fields[field_id]["soil_snapshot_completed"] = completed
            save_farms(farms)
            return


def estimate_soil_type_from_photo(texture: str) -> str:
    """
    Estimate soil type from texture analysis
    
    This is a simplified estimation. In production, this would use
    ML image analysis or actual soil classification.
    """
    texture_map = {
        "sandy": "Sandy Loam",
        "loamy": "Loam",
        "clay": "Clay Loam",
        "red_clay": "Red Clay",
        "black_cotton": "Black Cotton Soil",
        "volcanic": "Volcanic Ash Soil"
    }
    
    return texture_map.get(texture.lower(), "Unknown Soil Type")


def calculate_field_distance(loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
    """
    Calculate distance between two GPS coordinates in kilometers
    Uses Haversine formula
    
    Args:
        loc1: {"latitude": x, "longitude": y}
        loc2: {"latitude": x, "longitude": y}
    
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in kilometers
    
    lat1 = radians(loc1["latitude"])
    lon1 = radians(loc1["longitude"])
    lat2 = radians(loc2["latitude"])
    lon2 = radians(loc2["longitude"])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def get_nearby_farms(location: Dict[str, float], radius_km: float = 5.0) -> List[Dict]:
    """
    Get all farms within a specified radius
    Used for community alerts (pest/disease outbreaks)
    
    Args:
        location: Center point {"latitude": x, "longitude": y}
        radius_km: Search radius in kilometers (default 5km)
    
    Returns:
        List of farms within radius
    """
    farms = load_farms()
    nearby = []
    
    for farmer_id, fields in farms.items():
        for field_id, farm in fields.items():
            distance = calculate_field_distance(location, farm["location"])
            if distance <= radius_km:
                nearby.append({
                    **farm,
                    "distance_km": round(distance, 2)
                })
    
    return sorted(nearby, key=lambda x: x["distance_km"])


def get_ai_variety_recommendation(
    field_id: str,
    crop: str,
    selected_variety: str,
    lcrs_score: float
) -> Dict:
    """
    Get AI-powered crop variety recommendation with risk assessment
    
    Analyzes farmer's selected variety against:
    - LCRS (climate risk score)
    - Soil fertility from AI analysis
    - Farming zone suitability
    - Historical success rates
    
    Args:
        field_id: Field identifier
        crop: Selected crop
        selected_variety: Farmer's chosen variety
        lcrs_score: Long-term climate risk score (0-10, higher = more risk)
    
    Returns:
        Risk assessment and optimized alternative if needed
    """
    # Get farm data
    farm = get_farm_by_field_id(field_id)
    if not farm:
        return {"error": "Farm not found"}
    
    # Get soil fertility from AI analysis
    photos = load_soil_photos()
    soil_fertility_score = 6.0  # Default medium
    
    if field_id in photos and len(photos[field_id]) > 0:
        latest_snapshot = photos[field_id][-1]
        if "ai_fertility_score" in latest_snapshot:
            soil_fertility_score = latest_snapshot["ai_fertility_score"]
    
    # Get farming zone and elevation
    farming_zone = farm.get("farming_zone", "highland_moderate")
    elevation = farm.get("elevation", 1500)
    
    # Call AI recommendation engine
    recommendation = recommend_crop_variety_with_ai(
        crop=crop,
        selected_variety=selected_variety,
        lcrs_score=lcrs_score,
        soil_fertility_score=soil_fertility_score,
        farming_zone=farming_zone,
        elevation=elevation
    )
    
    return recommendation
