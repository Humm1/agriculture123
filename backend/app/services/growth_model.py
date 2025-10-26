"""
Scientific Growth Model Engine
Provides crop-specific growth stages, development timelines, and phenological data
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Growth models for major crops
# All timings are in days after planting (DAP)
CROP_GROWTH_MODELS = {
    "maize": {
        "varieties": {
            "h614": {
                "name": "H614 (Hybrid)",
                "maturity_days": 120,
                "stages": {
                    "germination": {"start": 0, "end": 7, "name": "Germination"},
                    "emergence": {"start": 7, "end": 14, "name": "Emergence"},
                    "vegetative": {"start": 14, "end": 55, "name": "Vegetative Growth"},
                    "tasseling": {"start": 55, "end": 65, "name": "Tasseling"},
                    "silking": {"start": 60, "end": 70, "name": "Silking"},
                    "grain_fill": {"start": 70, "end": 100, "name": "Grain Filling"},
                    "maturity": {"start": 100, "end": 120, "name": "Physiological Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 20,
                    "second_weeding": 40,
                    "first_top_dress": 30,
                    "second_top_dress": 55,
                    "pest_scouting_start": 14,
                    "disease_monitoring_start": 21
                },
                "water_requirements": {
                    "total_mm": 500,
                    "critical_stages": ["silking", "grain_fill"]
                }
            },
            "short_season": {
                "name": "Short Season Variety",
                "maturity_days": 90,
                "stages": {
                    "germination": {"start": 0, "end": 6, "name": "Germination"},
                    "emergence": {"start": 6, "end": 12, "name": "Emergence"},
                    "vegetative": {"start": 12, "end": 45, "name": "Vegetative Growth"},
                    "tasseling": {"start": 45, "end": 52, "name": "Tasseling"},
                    "silking": {"start": 48, "end": 55, "name": "Silking"},
                    "grain_fill": {"start": 55, "end": 75, "name": "Grain Filling"},
                    "maturity": {"start": 75, "end": 90, "name": "Physiological Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 18,
                    "second_weeding": 35,
                    "first_top_dress": 25,
                    "second_top_dress": 45,
                    "pest_scouting_start": 12,
                    "disease_monitoring_start": 18
                },
                "water_requirements": {
                    "total_mm": 450,
                    "critical_stages": ["silking", "grain_fill"]
                }
            },
            "long_season": {
                "name": "Long Season Variety",
                "maturity_days": 150,
                "stages": {
                    "germination": {"start": 0, "end": 8, "name": "Germination"},
                    "emergence": {"start": 8, "end": 16, "name": "Emergence"},
                    "vegetative": {"start": 16, "end": 70, "name": "Vegetative Growth"},
                    "tasseling": {"start": 70, "end": 80, "name": "Tasseling"},
                    "silking": {"start": 75, "end": 85, "name": "Silking"},
                    "grain_fill": {"start": 85, "end": 130, "name": "Grain Filling"},
                    "maturity": {"start": 130, "end": 150, "name": "Physiological Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 22,
                    "second_weeding": 45,
                    "third_weeding": 70,
                    "first_top_dress": 35,
                    "second_top_dress": 65,
                    "pest_scouting_start": 16,
                    "disease_monitoring_start": 24
                },
                "water_requirements": {
                    "total_mm": 600,
                    "critical_stages": ["silking", "grain_fill"]
                }
            }
        },
        "default_variety": "short_season"
    },
    "beans": {
        "varieties": {
            "kat_b1": {
                "name": "KAT B1 (Bush Bean)",
                "maturity_days": 75,
                "stages": {
                    "germination": {"start": 0, "end": 5, "name": "Germination"},
                    "emergence": {"start": 5, "end": 10, "name": "Emergence"},
                    "vegetative": {"start": 10, "end": 35, "name": "Vegetative Growth"},
                    "flowering": {"start": 35, "end": 50, "name": "Flowering"},
                    "pod_formation": {"start": 45, "end": 60, "name": "Pod Formation"},
                    "pod_fill": {"start": 55, "end": 70, "name": "Pod Filling"},
                    "maturity": {"start": 70, "end": 75, "name": "Harvest Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 14,
                    "second_weeding": 30,
                    "fertilizer_application": 14,
                    "pest_scouting_start": 10,
                    "disease_monitoring_start": 15
                },
                "water_requirements": {
                    "total_mm": 350,
                    "critical_stages": ["flowering", "pod_fill"]
                }
            },
            "climbing": {
                "name": "Climbing Variety",
                "maturity_days": 90,
                "stages": {
                    "germination": {"start": 0, "end": 6, "name": "Germination"},
                    "emergence": {"start": 6, "end": 12, "name": "Emergence"},
                    "vegetative": {"start": 12, "end": 45, "name": "Vegetative & Climbing"},
                    "flowering": {"start": 45, "end": 60, "name": "Flowering"},
                    "pod_formation": {"start": 55, "end": 70, "name": "Pod Formation"},
                    "pod_fill": {"start": 65, "end": 85, "name": "Pod Filling"},
                    "maturity": {"start": 85, "end": 90, "name": "Harvest Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 16,
                    "second_weeding": 35,
                    "staking": 21,
                    "fertilizer_application": 16,
                    "pest_scouting_start": 12,
                    "disease_monitoring_start": 18
                },
                "water_requirements": {
                    "total_mm": 400,
                    "critical_stages": ["flowering", "pod_fill"]
                }
            }
        },
        "default_variety": "kat_b1"
    },
    "potatoes": {
        "varieties": {
            "shangi": {
                "name": "Shangi",
                "maturity_days": 90,
                "stages": {
                    "sprouting": {"start": 0, "end": 14, "name": "Sprouting"},
                    "emergence": {"start": 14, "end": 21, "name": "Emergence"},
                    "vegetative": {"start": 21, "end": 45, "name": "Vegetative Growth"},
                    "tuber_initiation": {"start": 35, "end": 50, "name": "Tuber Initiation"},
                    "tuber_bulking": {"start": 50, "end": 80, "name": "Tuber Bulking"},
                    "maturity": {"start": 80, "end": 90, "name": "Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 25,
                    "second_weeding": 45,
                    "first_earthing_up": 30,
                    "second_earthing_up": 50,
                    "first_top_dress": 21,
                    "second_top_dress": 42,
                    "blight_monitoring_start": 28
                },
                "water_requirements": {
                    "total_mm": 500,
                    "critical_stages": ["tuber_initiation", "tuber_bulking"]
                }
            },
            "dutch_robjin": {
                "name": "Dutch Robjin",
                "maturity_days": 105,
                "stages": {
                    "sprouting": {"start": 0, "end": 16, "name": "Sprouting"},
                    "emergence": {"start": 16, "end": 24, "name": "Emergence"},
                    "vegetative": {"start": 24, "end": 50, "name": "Vegetative Growth"},
                    "tuber_initiation": {"start": 40, "end": 55, "name": "Tuber Initiation"},
                    "tuber_bulking": {"start": 55, "end": 95, "name": "Tuber Bulking"},
                    "maturity": {"start": 95, "end": 105, "name": "Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 28,
                    "second_weeding": 50,
                    "first_earthing_up": 35,
                    "second_earthing_up": 55,
                    "first_top_dress": 24,
                    "second_top_dress": 45,
                    "blight_monitoring_start": 30
                },
                "water_requirements": {
                    "total_mm": 550,
                    "critical_stages": ["tuber_initiation", "tuber_bulking"]
                }
            }
        },
        "default_variety": "shangi"
    },
    "rice": {
        "varieties": {
            "basmati": {
                "name": "Basmati 370",
                "maturity_days": 120,
                "stages": {
                    "germination": {"start": 0, "end": 10, "name": "Germination"},
                    "seedling": {"start": 10, "end": 25, "name": "Seedling Stage"},
                    "tillering": {"start": 25, "end": 55, "name": "Tillering"},
                    "stem_elongation": {"start": 55, "end": 75, "name": "Stem Elongation"},
                    "panicle_initiation": {"start": 70, "end": 85, "name": "Panicle Initiation"},
                    "flowering": {"start": 85, "end": 95, "name": "Flowering"},
                    "grain_fill": {"start": 95, "end": 115, "name": "Grain Filling"},
                    "maturity": {"start": 115, "end": 120, "name": "Maturity"}
                },
                "critical_practices": {
                    "transplanting": 21,
                    "first_weeding": 35,
                    "second_weeding": 55,
                    "first_top_dress": 28,
                    "second_top_dress": 60,
                    "water_management_critical": 70
                },
                "water_requirements": {
                    "total_mm": 1200,
                    "critical_stages": ["tillering", "flowering"]
                }
            }
        },
        "default_variety": "basmati"
    },
    "cassava": {
        "varieties": {
            "tmse_419": {
                "name": "TMSE 419",
                "maturity_days": 365,
                "stages": {
                    "establishment": {"start": 0, "end": 30, "name": "Establishment"},
                    "vegetative": {"start": 30, "end": 180, "name": "Vegetative Growth"},
                    "root_bulking": {"start": 180, "end": 330, "name": "Root Bulking"},
                    "maturity": {"start": 330, "end": 365, "name": "Harvest Maturity"}
                },
                "critical_practices": {
                    "first_weeding": 30,
                    "second_weeding": 60,
                    "third_weeding": 120,
                    "fertilizer_application": 30,
                    "pest_monitoring_start": 45
                },
                "water_requirements": {
                    "total_mm": 1000,
                    "critical_stages": ["establishment", "root_bulking"]
                }
            }
        },
        "default_variety": "tmse_419"
    }
}


def get_crop_model(crop: str, variety: Optional[str] = None) -> Dict:
    """
    Get growth model for a specific crop and variety
    
    Args:
        crop: Crop name (e.g., "maize", "beans")
        variety: Specific variety (optional, uses default if not provided)
    
    Returns:
        Complete growth model dictionary
    """
    crop = crop.lower()
    if crop not in CROP_GROWTH_MODELS:
        raise ValueError(f"Crop '{crop}' not found in growth models")
    
    crop_data = CROP_GROWTH_MODELS[crop]
    
    if variety is None:
        variety = crop_data["default_variety"]
    else:
        variety = variety.lower()
    
    if variety not in crop_data["varieties"]:
        raise ValueError(f"Variety '{variety}' not found for crop '{crop}'")
    
    return crop_data["varieties"][variety]


def get_current_growth_stage(
    crop: str,
    variety: str,
    planting_date: str
) -> Dict:
    """
    Determine current growth stage based on planting date
    
    Args:
        crop: Crop name
        variety: Variety name
        planting_date: ISO format date string (e.g., "2025-10-24")
    
    Returns:
        Dictionary with current stage info and days after planting
    """
    model = get_crop_model(crop, variety)
    planting = datetime.fromisoformat(planting_date.replace('Z', ''))
    now = datetime.utcnow()
    
    days_after_planting = (now - planting).days
    
    # Find current stage
    current_stage = None
    for stage_key, stage_data in model["stages"].items():
        if stage_data["start"] <= days_after_planting <= stage_data["end"]:
            current_stage = {
                "stage_key": stage_key,
                "stage_name": stage_data["name"],
                "stage_start": stage_data["start"],
                "stage_end": stage_data["end"],
                "days_in_stage": days_after_planting - stage_data["start"],
                "days_remaining_in_stage": stage_data["end"] - days_after_planting,
                "progress_percent": int(((days_after_planting - stage_data["start"]) / 
                                        (stage_data["end"] - stage_data["start"])) * 100)
            }
            break
    
    # If past maturity
    if days_after_planting > model["maturity_days"]:
        current_stage = {
            "stage_key": "overdue",
            "stage_name": "Past Maturity (Harvest Overdue)",
            "stage_start": model["maturity_days"],
            "stage_end": model["maturity_days"],
            "days_in_stage": days_after_planting - model["maturity_days"],
            "days_remaining_in_stage": 0,
            "progress_percent": 100
        }
    
    return {
        "days_after_planting": days_after_planting,
        "current_stage": current_stage,
        "planting_date": planting_date,
        "crop": crop,
        "variety": variety,
        "maturity_days": model["maturity_days"],
        "overall_progress_percent": min(int((days_after_planting / model["maturity_days"]) * 100), 100)
    }


def get_upcoming_practices(
    crop: str,
    variety: str,
    planting_date: str,
    days_lookahead: int = 14
) -> List[Dict]:
    """
    Get upcoming critical farm practices
    
    Args:
        crop: Crop name
        variety: Variety name
        planting_date: ISO format date string
        days_lookahead: Number of days to look ahead (default 14)
    
    Returns:
        List of upcoming practices with due dates
    """
    model = get_crop_model(crop, variety)
    planting = datetime.fromisoformat(planting_date.replace('Z', ''))
    now = datetime.utcnow()
    
    days_after_planting = (now - planting).days
    
    upcoming = []
    
    for practice_name, practice_day in model["critical_practices"].items():
        days_until_due = practice_day - days_after_planting
        
        # Include if within lookahead window or overdue (but not too far overdue)
        if -7 <= days_until_due <= days_lookahead:
            due_date = planting + timedelta(days=practice_day)
            
            status = "upcoming"
            if days_until_due < 0:
                status = "overdue"
            elif days_until_due == 0:
                status = "due_today"
            elif days_until_due <= 3:
                status = "due_soon"
            
            upcoming.append({
                "practice_name": practice_name.replace('_', ' ').title(),
                "practice_key": practice_name,
                "days_after_planting": practice_day,
                "due_date": due_date.isoformat(),
                "days_until_due": days_until_due,
                "status": status,
                "urgency": "high" if days_until_due <= 2 else "medium" if days_until_due <= 7 else "low"
            })
    
    return sorted(upcoming, key=lambda x: x["days_until_due"])


def calculate_optimal_growth_curve(
    crop: str,
    variety: str,
    maturity_days: int
) -> List[Dict]:
    """
    Generate optimal health score curve for the crop
    Used for comparing actual growth photos against expected progress
    
    Returns:
        List of datapoints: [{"day": 0, "optimal_health_score": 5}, ...]
    """
    model = get_crop_model(crop, variety)
    
    curve = []
    
    # Generate curve with key inflection points based on growth stages
    stages = model["stages"]
    
    for day in range(0, maturity_days + 1, 7):  # Weekly datapoints
        # Calculate expected health score based on stage
        health_score = 5.0  # Base score
        
        for stage_data in stages.values():
            if stage_data["start"] <= day <= stage_data["end"]:
                # Health peaks during vegetative/reproductive stages
                if "vegetative" in stage_data["name"].lower():
                    health_score = 7.0 + (day - stage_data["start"]) / (stage_data["end"] - stage_data["start"]) * 2
                elif "flowering" in stage_data["name"].lower() or "silking" in stage_data["name"].lower():
                    health_score = 9.0
                elif "fill" in stage_data["name"].lower():
                    health_score = 8.5
                elif "maturity" in stage_data["name"].lower():
                    health_score = 7.0 - (day - stage_data["start"]) / (stage_data["end"] - stage_data["start"]) * 2
                else:
                    health_score = 6.0
                break
        
        curve.append({
            "day": day,
            "optimal_health_score": round(min(health_score, 10.0), 1)
        })
    
    return curve


def get_water_requirements_by_stage(
    crop: str,
    variety: str,
    current_day: int
) -> Dict:
    """
    Get water requirements for current growth stage
    
    Returns:
        Water requirements and criticality
    """
    model = get_crop_model(crop, variety)
    water_req = model["water_requirements"]
    
    # Determine current stage
    current_stage_key = None
    for stage_key, stage_data in model["stages"].items():
        if stage_data["start"] <= current_day <= stage_data["end"]:
            current_stage_key = stage_key
            break
    
    is_critical = current_stage_key in water_req["critical_stages"]
    
    # Calculate weekly water requirement
    daily_mm = water_req["total_mm"] / model["maturity_days"]
    weekly_mm = daily_mm * 7
    
    return {
        "total_season_mm": water_req["total_mm"],
        "daily_mm": round(daily_mm, 1),
        "weekly_mm": round(weekly_mm, 1),
        "current_stage": current_stage_key,
        "is_critical_stage": is_critical,
        "critical_stages": water_req["critical_stages"],
        "stress_impact": "HIGH - Critical for yield" if is_critical else "MEDIUM - Manageable deficit"
    }


def get_all_crops() -> List[str]:
    """Get list of all available crops"""
    return list(CROP_GROWTH_MODELS.keys())


def get_crop_varieties(crop: str) -> List[Dict]:
    """Get all varieties for a crop"""
    crop = crop.lower()
    if crop not in CROP_GROWTH_MODELS:
        return []
    
    varieties = []
    for variety_key, variety_data in CROP_GROWTH_MODELS[crop]["varieties"].items():
        varieties.append({
            "key": variety_key,
            "name": variety_data["name"],
            "maturity_days": variety_data["maturity_days"]
        })
    
    return varieties
