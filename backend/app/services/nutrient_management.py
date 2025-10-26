"""
Nutrient Management System
Predicts nutrient depletion, tracks NPK levels, generates fertilizer alerts
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
NUTRIENT_TRACKING_FILE = DATA_DIR / "nutrient_tracking.json"

# Crop nutrient uptake rates (kg/hectare/day for N, P, K)
CROP_NUTRIENT_UPTAKE = {
    "maize": {
        "nitrogen_kg_per_ha_total": 120,  # Total N uptake for season
        "phosphorus_kg_per_ha_total": 30,
        "potassium_kg_per_ha_total": 100,
        "peak_uptake_stages": ["vegetative", "tasseling", "silking"],  # Highest demand
        "uptake_curve": {
            # Percentage of total uptake by growth stage
            "germination": 5,
            "emergence": 10,
            "vegetative": 40,
            "tasseling": 20,
            "silking": 15,
            "grain_fill": 8,
            "maturity": 2
        }
    },
    "beans": {
        "nitrogen_kg_per_ha_total": 40,  # Lower due to N-fixation
        "phosphorus_kg_per_ha_total": 25,
        "potassium_kg_per_ha_total": 50,
        "peak_uptake_stages": ["vegetative", "flowering"],
        "uptake_curve": {
            "germination": 5,
            "emergence": 10,
            "vegetative": 35,
            "flowering": 30,
            "pod_formation": 15,
            "pod_fill": 4,
            "maturity": 1
        }
    },
    "potatoes": {
        "nitrogen_kg_per_ha_total": 150,
        "phosphorus_kg_per_ha_total": 50,
        "potassium_kg_per_ha_total": 200,
        "peak_uptake_stages": ["vegetative", "tuber_initiation", "tuber_bulking"],
        "uptake_curve": {
            "sprouting": 5,
            "emergence": 10,
            "vegetative": 30,
            "tuber_initiation": 25,
            "tuber_bulking": 25,
            "maturity": 5
        }
    },
    "rice": {
        "nitrogen_kg_per_ha_total": 140,
        "phosphorus_kg_per_ha_total": 40,
        "potassium_kg_per_ha_total": 120,
        "peak_uptake_stages": ["tillering", "stem_elongation", "panicle_initiation"],
        "uptake_curve": {
            "germination": 3,
            "seedling": 7,
            "tillering": 30,
            "stem_elongation": 25,
            "panicle_initiation": 20,
            "flowering": 10,
            "grain_fill": 4,
            "maturity": 1
        }
    },
    "cassava": {
        "nitrogen_kg_per_ha_total": 80,
        "phosphorus_kg_per_ha_total": 30,
        "potassium_kg_per_ha_total": 150,
        "peak_uptake_stages": ["vegetative", "root_bulking"],
        "uptake_curve": {
            "establishment": 10,
            "vegetative": 40,
            "root_bulking": 45,
            "maturity": 5
        }
    }
}


def load_nutrient_tracking() -> Dict:
    """Load nutrient tracking data"""
    if NUTRIENT_TRACKING_FILE.exists():
        with open(NUTRIENT_TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_nutrient_tracking(tracking: Dict):
    """Save nutrient tracking data"""
    with open(NUTRIENT_TRACKING_FILE, 'w') as f:
        json.dump(tracking, f, indent=2)


def initialize_nutrient_tracking(
    field_id: str,
    crop: str,
    area_hectares: float,
    initial_soil_data: Dict,  # From farm_registration.add_soil_snapshot_advanced
    planting_date: str
) -> Dict:
    """
    Initialize nutrient tracking for a field
    
    Args:
        field_id: Field identifier
        crop: Crop name
        area_hectares: Field size
        initial_soil_data: Soil test results (pH, N, P, K ppm)
        planting_date: ISO format date
    
    Returns:
        Nutrient tracking record
    """
    tracking = load_nutrient_tracking()
    
    # Convert soil PPM to kg/hectare (rough conversion)
    # 1 ppm ≈ 2 kg/hectare for most soils
    initial_nitrogen_kg = initial_soil_data.get("nitrogen_ppm", 20) * 2 * area_hectares
    initial_phosphorus_kg = initial_soil_data.get("phosphorus_ppm", 15) * 2 * area_hectares
    initial_potassium_kg = initial_soil_data.get("potassium_ppm", 100) * 2 * area_hectares
    
    crop_uptake = CROP_NUTRIENT_UPTAKE.get(crop.lower(), CROP_NUTRIENT_UPTAKE["maize"])
    
    record = {
        "field_id": field_id,
        "crop": crop,
        "area_hectares": area_hectares,
        "planting_date": planting_date,
        "initialized_at": datetime.utcnow().isoformat(),
        "initial_levels": {
            "nitrogen_kg": initial_nitrogen_kg,
            "phosphorus_kg": initial_phosphorus_kg,
            "potassium_kg": initial_potassium_kg,
            "soil_ph": initial_soil_data.get("ph", 6.5)
        },
        "current_levels": {
            "nitrogen_kg": initial_nitrogen_kg,
            "phosphorus_kg": initial_phosphorus_kg,
            "potassium_kg": initial_potassium_kg,
            "last_updated": planting_date
        },
        "season_uptake_targets": {
            "nitrogen_kg": crop_uptake["nitrogen_kg_per_ha_total"] * area_hectares,
            "phosphorus_kg": crop_uptake["phosphorus_kg_per_ha_total"] * area_hectares,
            "potassium_kg": crop_uptake["potassium_kg_per_ha_total"] * area_hectares
        },
        "fertilizer_applications": [],
        "depletion_predictions": []
    }
    
    tracking[field_id] = record
    save_nutrient_tracking(tracking)
    
    return record


def predict_nutrient_depletion(
    field_id: str,
    current_date: Optional[str] = None
) -> Dict:
    """
    Predict when nutrients will reach critical levels
    
    Returns:
        Depletion predictions with days until critical and recommendations
    """
    tracking = load_nutrient_tracking()
    
    if field_id not in tracking:
        raise ValueError(f"Nutrient tracking not initialized for field {field_id}")
    
    record = tracking[field_id]
    crop = record["crop"]
    
    if current_date is None:
        current_date = datetime.utcnow().isoformat()
    
    current = datetime.fromisoformat(current_date.replace('Z', ''))
    planting = datetime.fromisoformat(record["planting_date"].replace('Z', ''))
    days_since_planting = (current - planting).days
    
    # Get current growth stage
    from .growth_model import get_current_growth_stage
    stage_info = get_current_growth_stage(crop, "short_season", record["planting_date"])
    current_stage = stage_info["current_stage"]["stage_key"] if stage_info["current_stage"] else "unknown"
    
    # Calculate nutrient consumption based on growth stage
    crop_uptake = CROP_NUTRIENT_UPTAKE.get(crop.lower(), CROP_NUTRIENT_UPTAKE["maize"])
    uptake_curve = crop_uptake["uptake_curve"]
    
    # Calculate cumulative uptake percentage up to current stage
    cumulative_uptake_percent = 0
    for stage, percent in uptake_curve.items():
        cumulative_uptake_percent += percent
        if stage == current_stage:
            break
    
    # Calculate remaining nutrients
    total_n = record["season_uptake_targets"]["nitrogen_kg"]
    total_p = record["season_uptake_targets"]["phosphorus_kg"]
    total_k = record["season_uptake_targets"]["potassium_kg"]
    
    consumed_n = total_n * (cumulative_uptake_percent / 100)
    consumed_p = total_p * (cumulative_uptake_percent / 100)
    consumed_k = total_k * (cumulative_uptake_percent / 100)
    
    # Add fertilizer applications
    for application in record["fertilizer_applications"]:
        consumed_n -= application.get("nitrogen_kg", 0)
        consumed_p -= application.get("phosphorus_kg", 0)
        consumed_k -= application.get("potassium_kg", 0)
    
    remaining_n = record["initial_levels"]["nitrogen_kg"] - consumed_n
    remaining_p = record["initial_levels"]["phosphorus_kg"] - consumed_p
    remaining_k = record["initial_levels"]["potassium_kg"] - consumed_k
    
    # Define critical thresholds (20% of season target)
    critical_n = total_n * 0.2
    critical_p = total_p * 0.2
    critical_k = total_k * 0.2
    
    # Estimate days until critical
    remaining_uptake_percent = 100 - cumulative_uptake_percent
    if remaining_uptake_percent > 0:
        days_per_percent = (stage_info["maturity_days"] - days_since_planting) / remaining_uptake_percent
    else:
        days_per_percent = 1
    
    # Calculate days until critical for each nutrient
    def days_until_critical(remaining, critical, daily_uptake_rate):
        if remaining <= critical:
            return 0
        if daily_uptake_rate <= 0:
            return 999  # Far future
        return int((remaining - critical) / daily_uptake_rate)
    
    # Estimate daily uptake (simplified)
    daily_n_uptake = total_n / stage_info["maturity_days"]
    daily_p_uptake = total_p / stage_info["maturity_days"]
    daily_k_uptake = total_k / stage_info["maturity_days"]
    
    days_until_n_critical = days_until_critical(remaining_n, critical_n, daily_n_uptake)
    days_until_p_critical = days_until_critical(remaining_p, critical_p, daily_p_uptake)
    days_until_k_critical = days_until_critical(remaining_k, critical_k, daily_k_uptake)
    
    # Generate alerts and recommendations
    alerts = []
    urgency = "low"
    
    if days_until_n_critical <= 7:
        alerts.append({
            "nutrient": "Nitrogen",
            "status": "critical",
            "days_until_critical": days_until_n_critical,
            "message": "⚠️ **NITROGEN ALERT:** Critical depletion in {} days!".format(days_until_n_critical),
            "recommendation": _get_fertilizer_recommendation("nitrogen", record["area_hectares"])
        })
        urgency = "high"
    elif days_until_n_critical <= 14:
        alerts.append({
            "nutrient": "Nitrogen",
            "status": "warning",
            "days_until_critical": days_until_n_critical,
            "message": "⚠️ **Nitrogen Warning:** Plan for top-dress in {} days".format(days_until_n_critical),
            "recommendation": _get_fertilizer_recommendation("nitrogen", record["area_hectares"])
        })
        if urgency == "low":
            urgency = "medium"
    
    if days_until_p_critical <= 14:
        alerts.append({
            "nutrient": "Phosphorus",
            "status": "warning",
            "days_until_critical": days_until_p_critical,
            "message": "📉 Phosphorus levels declining",
            "recommendation": _get_fertilizer_recommendation("phosphorus", record["area_hectares"])
        })
    
    if days_until_k_critical <= 14:
        alerts.append({
            "nutrient": "Potassium",
            "status": "warning",
            "days_until_critical": days_until_k_critical,
            "message": "📉 Potassium levels declining",
            "recommendation": _get_fertilizer_recommendation("potassium", record["area_hectares"])
        })
    
    prediction = {
        "field_id": field_id,
        "prediction_date": current_date,
        "days_since_planting": days_since_planting,
        "current_stage": current_stage,
        "nutrient_levels": {
            "nitrogen": {
                "remaining_kg": round(remaining_n, 1),
                "consumed_kg": round(consumed_n, 1),
                "days_until_critical": days_until_n_critical,
                "status": "critical" if days_until_n_critical <= 7 else "warning" if days_until_n_critical <= 14 else "adequate"
            },
            "phosphorus": {
                "remaining_kg": round(remaining_p, 1),
                "consumed_kg": round(consumed_p, 1),
                "days_until_critical": days_until_p_critical,
                "status": "critical" if days_until_p_critical <= 7 else "warning" if days_until_p_critical <= 14 else "adequate"
            },
            "potassium": {
                "remaining_kg": round(remaining_k, 1),
                "consumed_kg": round(consumed_k, 1),
                "days_until_critical": days_until_k_critical,
                "status": "critical" if days_until_k_critical <= 7 else "warning" if days_until_k_critical <= 14 else "adequate"
            }
        },
        "alerts": alerts,
        "urgency": urgency
    }
    
    # Save prediction
    record["depletion_predictions"].append(prediction)
    tracking[field_id] = record
    save_nutrient_tracking(tracking)
    
    return prediction


def _get_fertilizer_recommendation(nutrient: str, area_hectares: float) -> Dict:
    """Get fertilizer recommendations with commercial and local alternatives"""
    
    recommendations = {
        "nitrogen": {
            "commercial": [
                {
                    "product": "CAN (Calcium Ammonium Nitrate)",
                    "quantity_kg_per_ha": 50,
                    "quantity_total": round(50 * area_hectares, 1),
                    "cost_per_50kg_bag": 3500,  # KES (example price)
                    "application_method": "Broadcast or side-dress, then lightly incorporate"
                },
                {
                    "product": "Urea (46-0-0)",
                    "quantity_kg_per_ha": 30,
                    "quantity_total": round(30 * area_hectares, 1),
                    "cost_per_50kg_bag": 3000,
                    "application_method": "Side-dress 10cm from plants, water immediately"
                }
            ],
            "local_alternatives": [
                {
                    "method": "Well-Composted Manure",
                    "quantity": f"{int(5 * area_hectares)} wheelbarrows (aged 3+ months)",
                    "application": "Spread evenly and lightly incorporate",
                    "notes": "Free if you have livestock! Manure also improves soil structure."
                },
                {
                    "method": "Compost Tea",
                    "quantity": "20 liters per 100m² (spray every 2 weeks)",
                    "application": "Dilute 1:5 with water, spray on leaves and soil",
                    "notes": "Make from kitchen scraps + manure + water. Let ferment 7 days."
                },
                {
                    "method": "Green Manure (Legume Cover Crop)",
                    "quantity": "Inter-plant with beans or cowpeas",
                    "application": "Plant legumes between crop rows, cut and mulch at flowering",
                    "notes": "Legumes fix nitrogen from air. Future benefit!"
                }
            ]
        },
        "phosphorus": {
            "commercial": [
                {
                    "product": "DAP (Diammonium Phosphate 18-46-0)",
                    "quantity_kg_per_ha": 40,
                    "quantity_total": round(40 * area_hectares, 1),
                    "cost_per_50kg_bag": 4000,
                    "application_method": "Apply in bands 5cm from plants"
                },
                {
                    "product": "TSP (Triple Super Phosphate)",
                    "quantity_kg_per_ha": 30,
                    "quantity_total": round(30 * area_hectares, 1),
                    "cost_per_50kg_bag": 3800,
                    "application_method": "Incorporate into soil near root zone"
                }
            ],
            "local_alternatives": [
                {
                    "method": "Bone Meal",
                    "quantity": f"{int(2 * area_hectares)} kg",
                    "application": "Mix into soil around plants",
                    "notes": "Get from local butcher. Grind bones and age for 2 weeks."
                },
                {
                    "method": "Rock Phosphate",
                    "quantity": f"{int(3 * area_hectares)} kg",
                    "application": "Apply and incorporate into soil",
                    "notes": "Slow-release. Best applied before planting."
                }
            ]
        },
        "potassium": {
            "commercial": [
                {
                    "product": "Muriate of Potash (KCl)",
                    "quantity_kg_per_ha": 30,
                    "quantity_total": round(30 * area_hectares, 1),
                    "cost_per_50kg_bag": 3200,
                    "application_method": "Broadcast and water in"
                }
            ],
            "local_alternatives": [
                {
                    "method": "Wood Ash",
                    "quantity": f"{int(10 * area_hectares)} kg (from cooking fire)",
                    "application": "Sprinkle around plants, avoid direct contact with stems",
                    "notes": "Free! Ash from hardwood is best. Also raises pH."
                },
                {
                    "method": "Banana Peel Compost",
                    "quantity": "5-10 peels per plant",
                    "application": "Chop and bury near root zone",
                    "notes": "Banana peels are very high in potassium!"
                }
            ]
        }
    }
    
    return recommendations.get(nutrient, recommendations["nitrogen"])


def record_fertilizer_application(
    field_id: str,
    application_date: str,
    fertilizer_type: str,
    quantity_kg: float,
    nitrogen_content_percent: float = 0,
    phosphorus_content_percent: float = 0,
    potassium_content_percent: float = 0,
    notes: Optional[str] = None
) -> Dict:
    """
    Record a fertilizer application
    
    Args:
        field_id: Field identifier
        application_date: ISO format date
        fertilizer_type: Type (e.g., "CAN", "Urea", "DAP", "Manure")
        quantity_kg: Amount applied in kg
        nitrogen_content_percent: N content (e.g., 27 for CAN-27)
        phosphorus_content_percent: P content (e.g., 46 for DAP)
        potassium_content_percent: K content
        notes: Optional notes
    
    Returns:
        Application record
    """
    tracking = load_nutrient_tracking()
    
    if field_id not in tracking:
        raise ValueError(f"Nutrient tracking not initialized for field {field_id}")
    
    nitrogen_kg = quantity_kg * (nitrogen_content_percent / 100)
    phosphorus_kg = quantity_kg * (phosphorus_content_percent / 100)
    potassium_kg = quantity_kg * (potassium_content_percent / 100)
    
    application = {
        "application_date": application_date,
        "fertilizer_type": fertilizer_type,
        "quantity_kg": quantity_kg,
        "nitrogen_kg": nitrogen_kg,
        "phosphorus_kg": phosphorus_kg,
        "potassium_kg": potassium_kg,
        "notes": notes,
        "recorded_at": datetime.utcnow().isoformat()
    }
    
    tracking[field_id]["fertilizer_applications"].append(application)
    
    # Update current levels
    tracking[field_id]["current_levels"]["nitrogen_kg"] += nitrogen_kg
    tracking[field_id]["current_levels"]["phosphorus_kg"] += phosphorus_kg
    tracking[field_id]["current_levels"]["potassium_kg"] += potassium_kg
    tracking[field_id]["current_levels"]["last_updated"] = application_date
    
    save_nutrient_tracking(tracking)
    
    return application


def get_nutrient_status(field_id: str) -> Dict:
    """Get current nutrient status for a field"""
    tracking = load_nutrient_tracking()
    
    if field_id not in tracking:
        raise ValueError(f"Nutrient tracking not initialized for field {field_id}")
    
    record = tracking[field_id]
    
    # Get latest prediction
    latest_prediction = record["depletion_predictions"][-1] if record["depletion_predictions"] else None
    
    return {
        "field_id": field_id,
        "crop": record["crop"],
        "days_since_planting": (datetime.utcnow() - datetime.fromisoformat(record["planting_date"].replace('Z', ''))).days,
        "initial_levels": record["initial_levels"],
        "current_levels": record["current_levels"],
        "season_targets": record["season_uptake_targets"],
        "total_applications": len(record["fertilizer_applications"]),
        "latest_prediction": latest_prediction
    }


def calculate_budget_estimate(field_id: str, nutrient_type: str = "all") -> Dict:
    """
    Calculate budget for fertilizer needs
    
    Returns:
        Budget estimates for commercial and local alternatives
    """
    prediction = predict_nutrient_depletion(field_id)
    tracking = load_nutrient_tracking()
    record = tracking[field_id]
    area = record["area_hectares"]
    
    budget = {
        "field_id": field_id,
        "area_hectares": area,
        "commercial_options": [],
        "local_options": [],
        "total_commercial_cost_kes": 0
    }
    
    # Check which nutrients need attention
    for nutrient, data in prediction["nutrient_levels"].items():
        if data["status"] in ["critical", "warning"]:
            recommendation = _get_fertilizer_recommendation(nutrient, area)
            
            # Add commercial options
            for option in recommendation["commercial"]:
                bags_needed = option["quantity_total"] / 50  # Assuming 50kg bags
                total_cost = bags_needed * option["cost_per_50kg_bag"]
                
                budget["commercial_options"].append({
                    "nutrient": nutrient.title(),
                    "product": option["product"],
                    "quantity_kg": option["quantity_total"],
                    "bags_needed": round(bags_needed, 1),
                    "cost_per_bag_kes": option["cost_per_50kg_bag"],
                    "total_cost_kes": round(total_cost, 0)
                })
                
                budget["total_commercial_cost_kes"] += total_cost
            
            # Add local options
            for option in recommendation["local_alternatives"]:
                budget["local_options"].append({
                    "nutrient": nutrient.title(),
                    "method": option["method"],
                    "quantity": option["quantity"],
                    "application": option["application"],
                    "notes": option["notes"]
                })
    
    return budget
