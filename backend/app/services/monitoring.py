"""
AI Monitoring and Metrics System
==================================

Tracks:
1. AI confidence scores across all engines
2. Prediction accuracy metrics (weather, disease, yield)
3. Practice adjustment effectiveness
4. Fertilizer savings from optimization
5. Harvest prediction accuracy
6. Farmer feedback and satisfaction

Provides dashboard API for real-time monitoring.

Author: AgroShield AI Team
Date: October 2025
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


# ============================================================================
# CONFIGURATION
# ============================================================================

MONITORING_CONFIG = {
    "metrics_storage": {
        "database_path": "data/metrics/",
        "retention_days": 365,
        "aggregation_intervals": ["hourly", "daily", "weekly", "monthly"]
    },
    "confidence_thresholds": {
        "excellent": 0.90,
        "good": 0.75,
        "acceptable": 0.65,
        "poor": 0.50
    },
    "accuracy_targets": {
        "weather_forecast": 0.85,      # 85% accuracy target
        "disease_prediction": 0.80,    # 80% accuracy target
        "yield_prediction": 0.75,      # Within 15% of actual
        "harvest_timing": 0.85         # Within ±3 days
    },
    "alert_thresholds": {
        "confidence_drop": 0.10,       # Alert if confidence drops >10%
        "accuracy_decline": 0.15,      # Alert if accuracy drops >15%
        "farmer_satisfaction": 3.0     # Alert if rating <3.0/5.0
    }
}


# In-memory metrics storage (in production, use database)
METRICS_STORE = {
    "ai_predictions": [],           # All AI predictions with outcomes
    "confidence_scores": [],        # Confidence scores over time
    "accuracy_metrics": [],         # Accuracy measurements
    "practice_adjustments": [],     # Farmer practice changes
    "fertilizer_savings": [],       # Leaching optimization savings
    "harvest_predictions": [],      # Harvest timing predictions
    "farmer_feedback": []           # Farmer ratings and comments
}


# ============================================================================
# PREDICTION TRACKING
# ============================================================================

def track_ai_prediction(
    prediction_id: str,
    engine: str,  # "brain", "advisor", "field_scout"
    prediction_type: str,  # "weather", "disease", "yield", "harvest"
    prediction_data: Dict[str, Any],
    confidence: float,
    farmer_id: str,
    field_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Track an AI prediction for later accuracy measurement.
    
    Args:
        prediction_id: Unique prediction ID
        engine: AI engine name
        prediction_type: Type of prediction
        prediction_data: Prediction details
        confidence: Confidence score (0-1)
        farmer_id: Farmer ID
        field_id: Optional field ID
    
    Returns:
        dict: Tracking confirmation
    """
    prediction_record = {
        "prediction_id": prediction_id,
        "engine": engine,
        "prediction_type": prediction_type,
        "prediction_data": prediction_data,
        "confidence": confidence,
        "farmer_id": farmer_id,
        "field_id": field_id,
        "timestamp": datetime.now().isoformat(),
        "outcome_recorded": False,
        "accuracy": None
    }
    
    METRICS_STORE["ai_predictions"].append(prediction_record)
    
    # Track confidence score
    _track_confidence_score(engine, prediction_type, confidence)
    
    return {
        "prediction_id": prediction_id,
        "tracked": True,
        "timestamp": prediction_record["timestamp"]
    }


def record_prediction_outcome(
    prediction_id: str,
    actual_outcome: Any,
    outcome_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Record the actual outcome of a prediction for accuracy measurement.
    
    Args:
        prediction_id: Prediction ID to update
        actual_outcome: Actual observed outcome
        outcome_date: Date outcome was observed
    
    Returns:
        dict: Accuracy calculation result
    """
    # Find prediction
    prediction = None
    for pred in METRICS_STORE["ai_predictions"]:
        if pred["prediction_id"] == prediction_id:
            prediction = pred
            break
    
    if not prediction:
        return {"error": "Prediction not found", "prediction_id": prediction_id}
    
    # Calculate accuracy based on prediction type
    accuracy = _calculate_accuracy(
        prediction["prediction_type"],
        prediction["prediction_data"],
        actual_outcome
    )
    
    # Update prediction record
    prediction["outcome_recorded"] = True
    prediction["actual_outcome"] = actual_outcome
    prediction["accuracy"] = accuracy
    prediction["outcome_date"] = outcome_date or datetime.now().isoformat()
    
    # Track accuracy metric
    _track_accuracy_metric(
        prediction["engine"],
        prediction["prediction_type"],
        accuracy,
        prediction["confidence"]
    )
    
    return {
        "prediction_id": prediction_id,
        "accuracy": accuracy,
        "accuracy_category": _categorize_accuracy(accuracy),
        "met_target": accuracy >= MONITORING_CONFIG["accuracy_targets"].get(
            prediction["prediction_type"], 0.75
        )
    }


def _calculate_accuracy(
    prediction_type: str,
    prediction_data: Dict,
    actual_outcome: Any
) -> float:
    """Calculate accuracy based on prediction type."""
    
    if prediction_type == "weather":
        # Weather accuracy: percentage of correct forecasts
        predicted_temp = prediction_data.get("temperature_c", 0)
        actual_temp = actual_outcome.get("temperature_c", 0)
        
        # Accuracy = 1 - (|predicted - actual| / threshold)
        temp_diff = abs(predicted_temp - actual_temp)
        temp_accuracy = max(0, 1 - (temp_diff / 5.0))  # ±5°C threshold
        
        predicted_rain = prediction_data.get("rainfall_mm", 0)
        actual_rain = actual_outcome.get("rainfall_mm", 0)
        
        # Rainfall accuracy (more lenient for small amounts)
        if actual_rain < 1 and predicted_rain < 5:
            rain_accuracy = 1.0
        else:
            rain_diff = abs(predicted_rain - actual_rain)
            rain_accuracy = max(0, 1 - (rain_diff / max(actual_rain, 10)))
        
        return (temp_accuracy + rain_accuracy) / 2
    
    elif prediction_type == "disease":
        # Disease prediction: did outbreak occur within predicted timeframe?
        predicted_outbreak = prediction_data.get("probability", 0) > 0.5
        actual_outbreak = actual_outcome.get("outbreak_occurred", False)
        
        if predicted_outbreak == actual_outbreak:
            return 1.0  # Correct prediction
        else:
            return 0.0  # Incorrect prediction
    
    elif prediction_type == "yield":
        # Yield prediction: percentage error
        predicted_yield = prediction_data.get("yield_kg_per_acre", 0)
        actual_yield = actual_outcome.get("yield_kg_per_acre", 0)
        
        if actual_yield == 0:
            return 0.0
        
        percentage_error = abs(predicted_yield - actual_yield) / actual_yield
        
        # Accuracy = 1 - percentage error (capped at 0)
        return max(0, 1 - percentage_error)
    
    elif prediction_type == "harvest":
        # Harvest timing: days difference
        from datetime import datetime
        
        predicted_date = datetime.fromisoformat(prediction_data.get("harvest_date"))
        actual_date = datetime.fromisoformat(actual_outcome.get("harvest_date"))
        
        days_diff = abs((predicted_date - actual_date).days)
        
        # Within 3 days = 100%, 7 days = 70%, 14 days = 40%
        if days_diff <= 3:
            return 1.0
        elif days_diff <= 7:
            return 0.7
        elif days_diff <= 14:
            return 0.4
        else:
            return 0.2
    
    else:
        return 0.0


def _categorize_accuracy(accuracy: float) -> str:
    """Categorize accuracy level."""
    if accuracy >= 0.90:
        return "excellent"
    elif accuracy >= 0.75:
        return "good"
    elif accuracy >= 0.60:
        return "acceptable"
    else:
        return "poor"


# ============================================================================
# CONFIDENCE SCORE TRACKING
# ============================================================================

def _track_confidence_score(engine: str, prediction_type: str, confidence: float):
    """Track confidence score for trend analysis."""
    METRICS_STORE["confidence_scores"].append({
        "engine": engine,
        "prediction_type": prediction_type,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat()
    })


def get_confidence_trends(
    engine: Optional[str] = None,
    prediction_type: Optional[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get confidence score trends over time.
    
    Args:
        engine: Optional engine filter
        prediction_type: Optional prediction type filter
        days: Number of days to analyze
    
    Returns:
        dict: Confidence trends and statistics
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter confidence scores
    filtered_scores = []
    for score in METRICS_STORE["confidence_scores"]:
        score_date = datetime.fromisoformat(score["timestamp"])
        
        if score_date < cutoff_date:
            continue
        
        if engine and score["engine"] != engine:
            continue
        
        if prediction_type and score["prediction_type"] != prediction_type:
            continue
        
        filtered_scores.append(score)
    
    if not filtered_scores:
        return {
            "period_days": days,
            "total_predictions": 0,
            "message": "No data available for specified period"
        }
    
    # Calculate statistics
    confidences = [s["confidence"] for s in filtered_scores]
    
    return {
        "period_days": days,
        "total_predictions": len(filtered_scores),
        "confidence_stats": {
            "mean": round(statistics.mean(confidences), 3),
            "median": round(statistics.median(confidences), 3),
            "min": round(min(confidences), 3),
            "max": round(max(confidences), 3),
            "std_dev": round(statistics.stdev(confidences), 3) if len(confidences) > 1 else 0
        },
        "distribution": {
            "excellent": len([c for c in confidences if c >= 0.90]),
            "good": len([c for c in confidences if 0.75 <= c < 0.90]),
            "acceptable": len([c for c in confidences if 0.65 <= c < 0.75]),
            "poor": len([c for c in confidences if c < 0.65])
        },
        "trend": _calculate_trend(filtered_scores),
        "filters": {"engine": engine, "prediction_type": prediction_type}
    }


def _calculate_trend(scores: List[Dict]) -> str:
    """Calculate confidence trend (improving, stable, declining)."""
    if len(scores) < 10:
        return "insufficient_data"
    
    # Compare first half vs second half
    midpoint = len(scores) // 2
    first_half_avg = statistics.mean([s["confidence"] for s in scores[:midpoint]])
    second_half_avg = statistics.mean([s["confidence"] for s in scores[midpoint:]])
    
    diff = second_half_avg - first_half_avg
    
    if diff > 0.05:
        return "improving"
    elif diff < -0.05:
        return "declining"
    else:
        return "stable"


# ============================================================================
# ACCURACY METRICS TRACKING
# ============================================================================

def _track_accuracy_metric(
    engine: str,
    prediction_type: str,
    accuracy: float,
    confidence: float
):
    """Track accuracy metric for analysis."""
    METRICS_STORE["accuracy_metrics"].append({
        "engine": engine,
        "prediction_type": prediction_type,
        "accuracy": accuracy,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat()
    })


def get_accuracy_report(
    engine: Optional[str] = None,
    prediction_type: Optional[str] = None,
    days: int = 90
) -> Dict[str, Any]:
    """
    Get comprehensive accuracy report.
    
    Args:
        engine: Optional engine filter
        prediction_type: Optional prediction type filter
        days: Number of days to analyze
    
    Returns:
        dict: Accuracy report with comparisons to targets
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter metrics
    filtered_metrics = []
    for metric in METRICS_STORE["accuracy_metrics"]:
        metric_date = datetime.fromisoformat(metric["timestamp"])
        
        if metric_date < cutoff_date:
            continue
        
        if engine and metric["engine"] != engine:
            continue
        
        if prediction_type and metric["prediction_type"] != prediction_type:
            continue
        
        filtered_metrics.append(metric)
    
    if not filtered_metrics:
        return {
            "period_days": days,
            "total_measurements": 0,
            "message": "No accuracy data available"
        }
    
    # Calculate statistics
    accuracies = [m["accuracy"] for m in filtered_metrics]
    
    # Get target for comparison
    target = MONITORING_CONFIG["accuracy_targets"].get(
        prediction_type if prediction_type else "weather_forecast",
        0.75
    )
    
    avg_accuracy = statistics.mean(accuracies)
    
    return {
        "period_days": days,
        "total_measurements": len(filtered_metrics),
        "accuracy_stats": {
            "mean": round(avg_accuracy, 3),
            "median": round(statistics.median(accuracies), 3),
            "min": round(min(accuracies), 3),
            "max": round(max(accuracies), 3),
            "std_dev": round(statistics.stdev(accuracies), 3) if len(accuracies) > 1 else 0
        },
        "target_comparison": {
            "target": target,
            "actual": round(avg_accuracy, 3),
            "difference": round(avg_accuracy - target, 3),
            "meeting_target": avg_accuracy >= target
        },
        "confidence_correlation": _analyze_confidence_accuracy_correlation(filtered_metrics),
        "filters": {"engine": engine, "prediction_type": prediction_type}
    }


def _analyze_confidence_accuracy_correlation(metrics: List[Dict]) -> Dict[str, Any]:
    """Analyze correlation between confidence and accuracy."""
    if len(metrics) < 10:
        return {"correlation": "insufficient_data"}
    
    # Group by confidence levels
    high_conf = [m for m in metrics if m["confidence"] >= 0.75]
    low_conf = [m for m in metrics if m["confidence"] < 0.75]
    
    if not high_conf or not low_conf:
        return {"correlation": "insufficient_variation"}
    
    high_conf_accuracy = statistics.mean([m["accuracy"] for m in high_conf])
    low_conf_accuracy = statistics.mean([m["accuracy"] for m in low_conf])
    
    return {
        "high_confidence_avg": round(high_conf_accuracy, 3),
        "low_confidence_avg": round(low_conf_accuracy, 3),
        "difference": round(high_conf_accuracy - low_conf_accuracy, 3),
        "correlation": "positive" if high_conf_accuracy > low_conf_accuracy else "negative"
    }


# ============================================================================
# PRACTICE ADJUSTMENT TRACKING
# ============================================================================

def track_practice_adjustment(
    farmer_id: str,
    field_id: str,
    recommendation_id: str,
    recommended_action: str,
    actual_action: str,
    outcome: Optional[str] = None
) -> Dict[str, Any]:
    """
    Track whether farmer followed AI recommendations and outcomes.
    
    Args:
        farmer_id: Farmer ID
        field_id: Field ID
        recommendation_id: Recommendation ID
        recommended_action: What AI recommended
        actual_action: What farmer actually did
        outcome: Optional outcome description
    
    Returns:
        dict: Tracking confirmation
    """
    adjustment = {
        "farmer_id": farmer_id,
        "field_id": field_id,
        "recommendation_id": recommendation_id,
        "recommended_action": recommended_action,
        "actual_action": actual_action,
        "followed_recommendation": recommended_action.lower() == actual_action.lower(),
        "outcome": outcome,
        "timestamp": datetime.now().isoformat()
    }
    
    METRICS_STORE["practice_adjustments"].append(adjustment)
    
    return {
        "adjustment_id": recommendation_id,
        "tracked": True,
        "followed": adjustment["followed_recommendation"]
    }


def get_adoption_rate(days: int = 30) -> Dict[str, Any]:
    """
    Calculate AI recommendation adoption rate.
    
    Args:
        days: Number of days to analyze
    
    Returns:
        dict: Adoption statistics
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_adjustments = [
        adj for adj in METRICS_STORE["practice_adjustments"]
        if datetime.fromisoformat(adj["timestamp"]) >= cutoff_date
    ]
    
    if not recent_adjustments:
        return {
            "period_days": days,
            "total_recommendations": 0,
            "message": "No practice adjustment data available"
        }
    
    total = len(recent_adjustments)
    followed = len([adj for adj in recent_adjustments if adj["followed_recommendation"]])
    
    return {
        "period_days": days,
        "total_recommendations": total,
        "followed_recommendations": followed,
        "adoption_rate": round(followed / total, 3) if total > 0 else 0,
        "adoption_rate_percent": round((followed / total) * 100, 1) if total > 0 else 0
    }


# ============================================================================
# FERTILIZER SAVINGS TRACKING
# ============================================================================

def track_fertilizer_savings(
    farmer_id: str,
    field_id: str,
    crop: str,
    traditional_amount_kg: float,
    optimized_amount_kg: float,
    cost_per_kg: float,
    leaching_prevented_percent: float
) -> Dict[str, Any]:
    """
    Track fertilizer savings from AI optimization.
    
    Args:
        farmer_id: Farmer ID
        field_id: Field ID
        crop: Crop type
        traditional_amount_kg: Traditional fertilizer amount
        optimized_amount_kg: AI-optimized amount
        cost_per_kg: Fertilizer cost per kg
        leaching_prevented_percent: Estimated leaching prevention
    
    Returns:
        dict: Savings calculation
    """
    amount_saved_kg = traditional_amount_kg - optimized_amount_kg
    cost_saved = amount_saved_kg * cost_per_kg
    
    savings = {
        "farmer_id": farmer_id,
        "field_id": field_id,
        "crop": crop,
        "traditional_amount_kg": traditional_amount_kg,
        "optimized_amount_kg": optimized_amount_kg,
        "amount_saved_kg": amount_saved_kg,
        "cost_per_kg": cost_per_kg,
        "cost_saved": cost_saved,
        "leaching_prevented_percent": leaching_prevented_percent,
        "timestamp": datetime.now().isoformat()
    }
    
    METRICS_STORE["fertilizer_savings"].append(savings)
    
    return {
        "savings_id": len(METRICS_STORE["fertilizer_savings"]),
        "amount_saved_kg": round(amount_saved_kg, 2),
        "cost_saved": round(cost_saved, 2),
        "savings_percent": round((amount_saved_kg / traditional_amount_kg) * 100, 1) if traditional_amount_kg > 0 else 0
    }


def get_fertilizer_savings_report(days: int = 90) -> Dict[str, Any]:
    """
    Get comprehensive fertilizer savings report.
    
    Args:
        days: Number of days to analyze
    
    Returns:
        dict: Savings report
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_savings = [
        s for s in METRICS_STORE["fertilizer_savings"]
        if datetime.fromisoformat(s["timestamp"]) >= cutoff_date
    ]
    
    if not recent_savings:
        return {
            "period_days": days,
            "total_optimizations": 0,
            "message": "No fertilizer savings data available"
        }
    
    total_kg_saved = sum(s["amount_saved_kg"] for s in recent_savings)
    total_cost_saved = sum(s["cost_saved"] for s in recent_savings)
    avg_leaching_prevented = statistics.mean([s["leaching_prevented_percent"] for s in recent_savings])
    
    return {
        "period_days": days,
        "total_optimizations": len(recent_savings),
        "total_fertilizer_saved_kg": round(total_kg_saved, 2),
        "total_cost_saved": round(total_cost_saved, 2),
        "avg_cost_saved_per_farmer": round(total_cost_saved / len(recent_savings), 2),
        "avg_leaching_prevented_percent": round(avg_leaching_prevented, 1),
        "environmental_impact": {
            "nitrogen_runoff_prevented_kg": round(total_kg_saved * 0.15, 2),  # Assume 15% N content
            "water_pollution_reduction": "significant"
        }
    }


# ============================================================================
# HARVEST PREDICTION TRACKING
# ============================================================================

def track_harvest_prediction(
    farmer_id: str,
    field_id: str,
    crop: str,
    predicted_date: str,
    predicted_yield_kg: float,
    confidence: float
) -> str:
    """
    Track harvest prediction for later accuracy measurement.
    
    Args:
        farmer_id: Farmer ID
        field_id: Field ID
        crop: Crop type
        predicted_date: Predicted harvest date (ISO format)
        predicted_yield_kg: Predicted yield
        confidence: Prediction confidence
    
    Returns:
        str: Prediction ID
    """
    prediction_id = f"harvest_{farmer_id}_{field_id}_{datetime.now().timestamp()}"
    
    prediction = {
        "prediction_id": prediction_id,
        "farmer_id": farmer_id,
        "field_id": field_id,
        "crop": crop,
        "predicted_date": predicted_date,
        "predicted_yield_kg": predicted_yield_kg,
        "confidence": confidence,
        "created_at": datetime.now().isoformat(),
        "outcome_recorded": False
    }
    
    METRICS_STORE["harvest_predictions"].append(prediction)
    
    return prediction_id


def record_actual_harvest(
    prediction_id: str,
    actual_date: str,
    actual_yield_kg: float
) -> Dict[str, Any]:
    """
    Record actual harvest for accuracy measurement.
    
    Args:
        prediction_id: Prediction ID
        actual_date: Actual harvest date
        actual_yield_kg: Actual yield
    
    Returns:
        dict: Accuracy calculation
    """
    # Find prediction
    prediction = None
    for pred in METRICS_STORE["harvest_predictions"]:
        if pred["prediction_id"] == prediction_id:
            prediction = pred
            break
    
    if not prediction:
        return {"error": "Prediction not found"}
    
    # Calculate date accuracy
    from datetime import datetime
    predicted_date = datetime.fromisoformat(prediction["predicted_date"])
    actual_date_dt = datetime.fromisoformat(actual_date)
    
    days_diff = abs((predicted_date - actual_date_dt).days)
    
    if days_diff <= 3:
        date_accuracy = 1.0
    elif days_diff <= 7:
        date_accuracy = 0.7
    elif days_diff <= 14:
        date_accuracy = 0.4
    else:
        date_accuracy = 0.2
    
    # Calculate yield accuracy
    predicted_yield = prediction["predicted_yield_kg"]
    
    if actual_yield_kg > 0:
        yield_error_percent = abs(predicted_yield - actual_yield_kg) / actual_yield_kg
        yield_accuracy = max(0, 1 - yield_error_percent)
    else:
        yield_accuracy = 0.0
    
    # Overall accuracy
    overall_accuracy = (date_accuracy + yield_accuracy) / 2
    
    # Update prediction
    prediction["outcome_recorded"] = True
    prediction["actual_date"] = actual_date
    prediction["actual_yield_kg"] = actual_yield_kg
    prediction["days_difference"] = days_diff
    prediction["date_accuracy"] = date_accuracy
    prediction["yield_accuracy"] = yield_accuracy
    prediction["overall_accuracy"] = overall_accuracy
    
    return {
        "prediction_id": prediction_id,
        "date_accuracy": round(date_accuracy, 3),
        "days_difference": days_diff,
        "yield_accuracy": round(yield_accuracy, 3),
        "yield_error_percent": round(yield_error_percent * 100, 1) if actual_yield_kg > 0 else 0,
        "overall_accuracy": round(overall_accuracy, 3),
        "accuracy_category": _categorize_accuracy(overall_accuracy)
    }


# ============================================================================
# FARMER FEEDBACK COLLECTION
# ============================================================================

def collect_farmer_feedback(
    farmer_id: str,
    feature: str,  # "weather", "recommendations", "pest_detection", etc.
    rating: float,  # 1-5 scale
    comment: Optional[str] = None,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Collect farmer feedback on AI features.
    
    Args:
        farmer_id: Farmer ID
        feature: Feature being rated
        rating: Rating (1-5)
        comment: Optional comment
        context: Optional context data
    
    Returns:
        dict: Feedback ID
    """
    feedback = {
        "feedback_id": f"feedback_{len(METRICS_STORE['farmer_feedback'])}",
        "farmer_id": farmer_id,
        "feature": feature,
        "rating": rating,
        "comment": comment,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }
    
    METRICS_STORE["farmer_feedback"].append(feedback)
    
    # Check if rating below threshold (trigger alert)
    if rating < MONITORING_CONFIG["alert_thresholds"]["farmer_satisfaction"]:
        _trigger_satisfaction_alert(farmer_id, feature, rating, comment)
    
    return {
        "feedback_id": feedback["feedback_id"],
        "received": True,
        "timestamp": feedback["timestamp"]
    }


def get_farmer_satisfaction_report(days: int = 30) -> Dict[str, Any]:
    """
    Get farmer satisfaction report.
    
    Args:
        days: Number of days to analyze
    
    Returns:
        dict: Satisfaction metrics
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_feedback = [
        f for f in METRICS_STORE["farmer_feedback"]
        if datetime.fromisoformat(f["timestamp"]) >= cutoff_date
    ]
    
    if not recent_feedback:
        return {
            "period_days": days,
            "total_responses": 0,
            "message": "No feedback data available"
        }
    
    ratings = [f["rating"] for f in recent_feedback]
    
    # Group by feature
    by_feature = defaultdict(list)
    for f in recent_feedback:
        by_feature[f["feature"]].append(f["rating"])
    
    feature_ratings = {
        feature: {
            "avg_rating": round(statistics.mean(ratings_list), 2),
            "total_responses": len(ratings_list)
        }
        for feature, ratings_list in by_feature.items()
    }
    
    return {
        "period_days": days,
        "total_responses": len(recent_feedback),
        "overall_rating": round(statistics.mean(ratings), 2),
        "rating_distribution": {
            "5_star": len([r for r in ratings if r >= 4.5]),
            "4_star": len([r for r in ratings if 3.5 <= r < 4.5]),
            "3_star": len([r for r in ratings if 2.5 <= r < 3.5]),
            "2_star": len([r for r in ratings if 1.5 <= r < 2.5]),
            "1_star": len([r for r in ratings if r < 1.5])
        },
        "by_feature": feature_ratings,
        "satisfaction_level": _categorize_satisfaction(statistics.mean(ratings))
    }


def _categorize_satisfaction(rating: float) -> str:
    """Categorize satisfaction level."""
    if rating >= 4.5:
        return "excellent"
    elif rating >= 3.5:
        return "good"
    elif rating >= 2.5:
        return "acceptable"
    else:
        return "poor"


def _trigger_satisfaction_alert(farmer_id: str, feature: str, rating: float, comment: Optional[str]):
    """Trigger alert for low satisfaction."""
    print(f"⚠️ LOW SATISFACTION ALERT: Farmer {farmer_id} rated {feature} as {rating}/5")
    if comment:
        print(f"   Comment: {comment}")
    
    # In production, send to monitoring dashboard/Slack/email


# ============================================================================
# DASHBOARD API
# ============================================================================

def get_dashboard_summary() -> Dict[str, Any]:
    """
    Get comprehensive dashboard summary of all metrics.
    
    Returns:
        dict: Complete monitoring dashboard data
    """
    return {
        "generated_at": datetime.now().isoformat(),
        "confidence_trends": get_confidence_trends(days=30),
        "accuracy_report": get_accuracy_report(days=90),
        "adoption_rate": get_adoption_rate(days=30),
        "fertilizer_savings": get_fertilizer_savings_report(days=90),
        "farmer_satisfaction": get_farmer_satisfaction_report(days=30),
        "system_health": _get_system_health(),
        "alerts": _get_active_alerts()
    }


def _get_system_health() -> Dict[str, str]:
    """Get overall system health status."""
    # Check recent accuracy
    accuracy = get_accuracy_report(days=7)
    confidence = get_confidence_trends(days=7)
    satisfaction = get_farmer_satisfaction_report(days=7)
    
    health = {
        "overall": "healthy",
        "accuracy": "good",
        "confidence": "good",
        "satisfaction": "good"
    }
    
    # Check thresholds
    if accuracy.get("total_measurements", 0) > 0:
        if accuracy["accuracy_stats"]["mean"] < 0.70:
            health["accuracy"] = "warning"
            health["overall"] = "degraded"
    
    if confidence.get("total_predictions", 0) > 0:
        if confidence["confidence_stats"]["mean"] < 0.65:
            health["confidence"] = "warning"
            health["overall"] = "degraded"
    
    if satisfaction.get("total_responses", 0) > 0:
        if satisfaction["overall_rating"] < 3.0:
            health["satisfaction"] = "warning"
            health["overall"] = "degraded"
    
    return health


def _get_active_alerts() -> List[Dict[str, Any]]:
    """Get list of active system alerts."""
    alerts = []
    
    # Check for confidence drops
    confidence = get_confidence_trends(days=7)
    if confidence.get("trend") == "declining":
        alerts.append({
            "type": "confidence_decline",
            "severity": "warning",
            "message": "AI confidence scores declining over past 7 days",
            "action": "Review recent predictions and data quality"
        })
    
    # Check for accuracy issues
    accuracy = get_accuracy_report(days=7)
    if accuracy.get("total_measurements", 0) > 0:
        if not accuracy["target_comparison"]["meeting_target"]:
            alerts.append({
                "type": "accuracy_below_target",
                "severity": "warning",
                "message": f"Accuracy ({accuracy['accuracy_stats']['mean']:.2f}) below target ({accuracy['target_comparison']['target']:.2f})",
                "action": "Review model parameters and training data"
            })
    
    # Check for low satisfaction
    satisfaction = get_farmer_satisfaction_report(days=7)
    if satisfaction.get("total_responses", 0) > 0:
        if satisfaction["overall_rating"] < 3.0:
            alerts.append({
                "type": "low_satisfaction",
                "severity": "critical",
                "message": f"Low farmer satisfaction: {satisfaction['overall_rating']:.1f}/5.0",
                "action": "Review farmer feedback and improve features"
            })
    
    return alerts


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "track_ai_prediction",
    "record_prediction_outcome",
    "get_confidence_trends",
    "get_accuracy_report",
    "track_practice_adjustment",
    "get_adoption_rate",
    "track_fertilizer_savings",
    "get_fertilizer_savings_report",
    "track_harvest_prediction",
    "record_actual_harvest",
    "collect_farmer_feedback",
    "get_farmer_satisfaction_report",
    "get_dashboard_summary",
    "MONITORING_CONFIG"
]


if __name__ == "__main__":
    # Example usage
    print("AI Monitoring System")
    print("=" * 60)
    print("\nExample Dashboard Summary:")
    print(json.dumps(get_dashboard_summary(), indent=2))
