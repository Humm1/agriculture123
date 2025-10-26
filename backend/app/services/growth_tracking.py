"""
Photo-Driven Growth Tracking Portal
Weekly photo uploads, health score visualization, and growth progress monitoring
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .growth_model import calculate_optimal_growth_curve, get_current_growth_stage

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
GROWTH_PHOTOS_FILE = DATA_DIR / "growth_photos.json"
HEALTH_SCORES_FILE = DATA_DIR / "health_scores.json"


def load_growth_photos() -> Dict:
    """Load all growth tracking photos"""
    if GROWTH_PHOTOS_FILE.exists():
        with open(GROWTH_PHOTOS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_growth_photos(photos: Dict):
    """Save growth tracking photos"""
    with open(GROWTH_PHOTOS_FILE, 'w') as f:
        json.dump(photos, f, indent=2)


def load_health_scores() -> Dict:
    """Load all health score records"""
    if HEALTH_SCORES_FILE.exists():
        with open(HEALTH_SCORES_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_health_scores(scores: Dict):
    """Save health score records"""
    with open(HEALTH_SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=2)


def upload_growth_photo(
    field_id: str,
    photo_url: str,
    photo_type: str,  # "overview" or "closeup"
    notes: Optional[str] = None,
    manual_health_score: Optional[int] = None
) -> Dict:
    """
    Upload a growth tracking photo
    
    Args:
        field_id: Field identifier
        photo_url: URL/path to uploaded photo
        photo_type: Type of photo (overview/closeup)
        notes: Optional farmer notes
        manual_health_score: Optional manual health assessment (1-10)
    
    Returns:
        Photo record with auto-generated health score
    """
    photos = load_growth_photos()
    
    if field_id not in photos:
        photos[field_id] = []
    
    # Calculate health score (in production, this would use ML/AI)
    health_score = manual_health_score if manual_health_score else _estimate_health_score_from_photo(photo_url)
    
    photo_record = {
        "photo_id": f"{field_id}_photo_{len(photos[field_id]) + 1}",
        "field_id": field_id,
        "photo_url": photo_url,
        "photo_type": photo_type,
        "uploaded_at": datetime.utcnow().isoformat(),
        "notes": notes,
        "health_score": health_score,
        "analysis_method": "manual" if manual_health_score else "auto"
    }
    
    photos[field_id].append(photo_record)
    save_growth_photos(photos)
    
    # Update health score history
    _record_health_score(field_id, health_score, photo_record["photo_id"])
    
    return photo_record


def _estimate_health_score_from_photo(photo_url: str) -> int:
    """
    Estimate health score from photo
    
    In production, this would use ML/AI image analysis:
    - Leaf color (green = healthy, yellow/brown = stressed)
    - Leaf density (full canopy = high score)
    - Visible pests/diseases (reduces score)
    - Plant vigor (height, thickness of stem)
    
    For now, returns a placeholder score
    """
    # Placeholder: In real implementation, call ML model
    # For demo, return random-ish score based on timestamp
    timestamp_hash = hash(photo_url + str(datetime.utcnow().timestamp()))
    return (timestamp_hash % 4) + 6  # Returns 6-9 (simulates healthy plants)


def _record_health_score(field_id: str, score: int, photo_id: Optional[str] = None):
    """Record health score in time series"""
    scores = load_health_scores()
    
    if field_id not in scores:
        scores[field_id] = []
    
    scores[field_id].append({
        "timestamp": datetime.utcnow().isoformat(),
        "health_score": score,
        "photo_id": photo_id
    })
    
    save_health_scores(scores)


def get_growth_status_graph(
    field_id: str,
    crop: str,
    variety: str,
    planting_date: str
) -> Dict:
    """
    Generate growth status graph comparing actual vs optimal health
    
    Returns:
        Graph data with optimal curve and actual health scores
    """
    # Get optimal growth curve
    from .farm_registration import get_farm_by_field_id
    farm = get_farm_by_field_id(field_id)
    
    if not farm:
        raise ValueError(f"Farm not found for field {field_id}")
    
    planting = datetime.fromisoformat(planting_date.replace('Z', ''))
    days_since_planting = (datetime.utcnow() - planting).days
    
    # Get crop model
    from .growth_model import get_crop_model
    model = get_crop_model(crop, variety)
    maturity_days = model["maturity_days"]
    
    # Generate optimal curve
    optimal_curve = calculate_optimal_growth_curve(crop, variety, maturity_days)
    
    # Get actual health scores
    scores = load_health_scores()
    actual_scores = []
    
    if field_id in scores:
        for score_record in scores[field_id]:
            score_date = datetime.fromisoformat(score_record["timestamp"].replace('Z', ''))
            days_after_planting = (score_date - planting).days
            
            actual_scores.append({
                "day": days_after_planting,
                "health_score": score_record["health_score"],
                "timestamp": score_record["timestamp"],
                "photo_id": score_record.get("photo_id")
            })
    
    # Calculate current status
    current_stage = get_current_growth_stage(crop, variety, planting_date)
    
    # Get expected health score for today
    expected_today = next(
        (point["optimal_health_score"] for point in optimal_curve 
         if abs(point["day"] - days_since_planting) <= 3),
        7.0
    )
    
    # Get actual health score for today (or most recent)
    actual_today = actual_scores[-1]["health_score"] if actual_scores else None
    
    # Calculate health status
    if actual_today:
        variance = actual_today - expected_today
        if variance >= 0:
            status = "above_optimal"
            message = f"✅ Plant health is excellent! ({actual_today}/10)"
        elif variance >= -1:
            status = "on_track"
            message = f"🌱 Growth is on track ({actual_today}/10)"
        elif variance >= -2:
            status = "below_optimal"
            message = f"⚠️ Health slightly below optimal ({actual_today}/10). Monitor closely."
        else:
            status = "concerning"
            message = f"🚨 Health significantly below optimal ({actual_today}/10). Action needed!"
    else:
        status = "no_data"
        message = "📸 Upload your first photo to track growth!"
    
    return {
        "field_id": field_id,
        "days_since_planting": days_since_planting,
        "overall_progress_percent": current_stage["overall_progress_percent"],
        "current_stage": current_stage["current_stage"],
        "optimal_curve": optimal_curve,
        "actual_scores": actual_scores,
        "current_status": {
            "status": status,
            "message": message,
            "expected_health_score": expected_today,
            "actual_health_score": actual_today,
            "variance": actual_today - expected_today if actual_today else None
        },
        "recommendations": _generate_growth_recommendations(status, actual_today, expected_today)
    }


def _generate_growth_recommendations(
    status: str,
    actual_score: Optional[int],
    expected_score: float
) -> List[str]:
    """Generate recommendations based on growth status"""
    
    if status == "no_data":
        return [
            "Take your first weekly photo to start tracking",
            "Capture both overview and close-up of leaves",
            "Add notes about any concerns or observations"
        ]
    
    if status == "above_optimal" or status == "on_track":
        return [
            "Continue current practices - excellent work!",
            "Maintain regular weeding schedule",
            "Monitor for any changes in coming week"
        ]
    
    if status == "below_optimal":
        return [
            "Check for pest damage on leaves",
            "Ensure adequate water supply (soil should be moist)",
            "Consider light fertilizer application if last was >2 weeks ago",
            "Remove any weeds competing for nutrients"
        ]
    
    if status == "concerning":
        return [
            "🚨 URGENT: Inspect plants for pests or diseases",
            "Use AgroShield pest scan feature immediately",
            "Check soil moisture - may need irrigation",
            "Review fertilizer application schedule",
            "Consult extension officer if problem unclear"
        ]
    
    return ["Continue monitoring growth regularly"]


def get_photo_history(field_id: str, limit: Optional[int] = None) -> List[Dict]:
    """Get photo history for a field"""
    photos = load_growth_photos()
    
    if field_id not in photos:
        return []
    
    photo_list = photos[field_id]
    
    if limit:
        photo_list = photo_list[-limit:]  # Get most recent
    
    return photo_list


def get_next_photo_prompt(field_id: str, planting_date: str) -> Optional[Dict]:
    """Get the next scheduled photo prompt"""
    from .calendar_generator import get_calendar
    
    calendar = get_calendar(field_id)
    if not calendar or "photo_schedule" not in calendar:
        return None
    
    now = datetime.utcnow()
    
    # Find next pending photo
    for photo_prompt in calendar["photo_schedule"]:
        if photo_prompt["status"] == "pending":
            due_date = datetime.fromisoformat(photo_prompt["due_date"].replace('Z', ''))
            days_until_due = (due_date - now).days
            
            if days_until_due <= 7:  # Within a week
                return {
                    **photo_prompt,
                    "days_until_due": days_until_due,
                    "is_overdue": days_until_due < 0
                }
    
    return None


def mark_photo_prompt_completed(field_id: str, photo_number: int, photo_url: str):
    """Mark a photo prompt as completed"""
    from .calendar_generator import load_calendars, save_calendars
    
    calendars = load_calendars()
    
    if field_id not in calendars or not calendars[field_id]:
        raise ValueError(f"No calendar found for field {field_id}")
    
    calendar = calendars[field_id][-1]
    
    for prompt in calendar["photo_schedule"]:
        if prompt["photo_number"] == photo_number:
            prompt["status"] = "completed"
            prompt["photo_url"] = photo_url
            break
    
    save_calendars(calendars)


def calculate_photo_compliance_rate(field_id: str) -> Dict:
    """Calculate how many photos were taken on schedule"""
    from .calendar_generator import get_calendar
    
    calendar = get_calendar(field_id)
    if not calendar or "photo_schedule" not in calendar:
        return {"compliance_rate": 0, "completed": 0, "total": 0}
    
    now = datetime.utcnow()
    
    # Only count prompts that are due
    due_prompts = [p for p in calendar["photo_schedule"] 
                   if datetime.fromisoformat(p["due_date"].replace('Z', '')) <= now]
    
    completed = sum(1 for p in due_prompts if p["status"] == "completed")
    total = len(due_prompts)
    
    return {
        "compliance_rate": round((completed / total) * 100, 1) if total > 0 else 0,
        "completed": completed,
        "total": total,
        "total_scheduled": len(calendar["photo_schedule"])
    }


def analyze_health_trend(field_id: str, days: int = 30) -> Dict:
    """
    Analyze health score trend over specified period
    
    Returns:
        Trend analysis with direction and rate of change
    """
    scores = load_health_scores()
    
    if field_id not in scores or len(scores[field_id]) < 2:
        return {
            "trend": "insufficient_data",
            "direction": "unknown",
            "rate_of_change": 0,
            "message": "Upload more photos to analyze trends"
        }
    
    # Get scores from specified period
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    recent_scores = [
        s for s in scores[field_id]
        if datetime.fromisoformat(s["timestamp"].replace('Z', '')) >= cutoff_date
    ]
    
    if len(recent_scores) < 2:
        return {
            "trend": "insufficient_data",
            "direction": "unknown",
            "rate_of_change": 0,
            "message": "Upload more photos to analyze trends"
        }
    
    # Calculate trend
    first_score = recent_scores[0]["health_score"]
    last_score = recent_scores[-1]["health_score"]
    avg_score = sum(s["health_score"] for s in recent_scores) / len(recent_scores)
    
    change = last_score - first_score
    rate_of_change = change / len(recent_scores)  # Average change per data point
    
    if change > 1:
        direction = "improving"
        message = f"📈 Health is improving! (+{change} points over {days} days)"
    elif change < -1:
        direction = "declining"
        message = f"📉 Health is declining. ({change} points over {days} days) - Take action!"
    else:
        direction = "stable"
        message = f"➡️ Health is stable. (±{abs(change)} points over {days} days)"
    
    return {
        "trend": direction,
        "direction": direction,
        "rate_of_change": round(rate_of_change, 2),
        "first_score": first_score,
        "last_score": last_score,
        "average_score": round(avg_score, 1),
        "total_change": change,
        "days_analyzed": days,
        "data_points": len(recent_scores),
        "message": message
    }


def compare_with_community(
    field_id: str,
    crop: str,
    current_health_score: int
) -> Dict:
    """
    Compare field's health score with community average for same crop
    
    Returns:
        Comparison with percentile ranking
    """
    # Get all farms with same crop
    from .farm_registration import load_farms
    farms = load_farms()
    
    same_crop_scores = []
    
    for farmer_id, fields in farms.items():
        for fid, farm in fields.items():
            if farm["crop"] == crop.lower() and fid != field_id:
                # Get latest health score for this field
                scores = load_health_scores()
                if fid in scores and scores[fid]:
                    latest_score = scores[fid][-1]["health_score"]
                    same_crop_scores.append(latest_score)
    
    if not same_crop_scores:
        return {
            "community_average": None,
            "your_score": current_health_score,
            "percentile": None,
            "message": "Not enough community data yet for comparison"
        }
    
    community_avg = sum(same_crop_scores) / len(same_crop_scores)
    
    # Calculate percentile
    better_than = sum(1 for s in same_crop_scores if current_health_score > s)
    percentile = (better_than / len(same_crop_scores)) * 100
    
    if percentile >= 75:
        message = f"🏆 Excellent! Your crop is healthier than {int(percentile)}% of community"
    elif percentile >= 50:
        message = f"👍 Good! Your crop is above average ({int(percentile)} percentile)"
    elif percentile >= 25:
        message = f"📊 Average performance ({int(percentile)} percentile). Room for improvement"
    else:
        message = f"⚠️ Below community average. Consider consulting top performers"
    
    return {
        "community_average": round(community_avg, 1),
        "your_score": current_health_score,
        "percentile": int(percentile),
        "total_farms_compared": len(same_crop_scores),
        "message": message
    }
