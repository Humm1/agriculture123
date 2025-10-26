"""
AI Real-Time Monitoring Engine (The "Field Scout")
==================================================

This module implements AI-powered field monitoring and diagnostics:

1. **AI Diagnostic Triage & Severity Scoring:**
   - Computer vision identifies pest/disease + scores severity (5% vs 50% damage)
   - Confidence scoring determines if expert verification needed
   - Low severity → organic treatment; High severity → chemical intervention

2. **AI-Triggered Contagion Modeling:**
   - Analyzes geo-tagged reports + wind patterns + road networks
   - Identifies contagion hotspots and spread vectors
   - Enables intelligent outbreak warnings beyond simple proximity

3. **Visual Growth Log for Fertilizer Optimization:**
   - Computer vision analyzes weekly photos for NDVI proxy (color + density)
   - Provides visual nutrient diagnostics (e.g., "early yellowing = low Nitrogen")
   - Recommends fertilizer timing adjustments based on visual cues

Core Innovation:
- Severity-based triage prevents under/over-treatment
- Vector-aware contagion modeling predicts spread patterns
- Visual nutrient assessment eliminates need for expensive lab tests

Author: AgroShield AI Team
Date: October 2025
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import math


# ============================================================================
# COMPUTER VISION MODELS (SIMULATED)
# ============================================================================

def analyze_pest_disease_severity(
    image_data: bytes,
    crop: str,
    cv_confidence: Optional[float] = None,
    image_metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    AI diagnostic triage with severity scoring.
    
    Uses computer vision to:
    1. Identify pest/disease
    2. Score severity (5% vs 50% damage)
    3. Assign confidence score
    4. Determine if expert verification needed
    
    Args:
        image_data: Raw image bytes
        crop: Crop type (for context)
        cv_confidence: Override CV model confidence (for testing)
        image_metadata: Optional image metadata (resolution, lighting, etc.)
    
    Returns:
        dict: Diagnosis with severity, confidence, and triage decision
    """
    # Simulate CV analysis (in production, use TensorFlow/PyTorch model)
    cv_analysis = _simulate_cv_pest_diagnosis(crop, cv_confidence)
    
    # Analyze image quality
    image_quality = _assess_image_quality(image_data, image_metadata)
    
    # Calculate severity score
    severity_analysis = _calculate_severity_score(
        cv_analysis["damage_type"],
        cv_analysis["damage_extent_percent"],
        cv_analysis["infection_stage"]
    )
    
    # Adjust confidence based on image quality
    adjusted_confidence = _adjust_confidence_for_quality(
        cv_analysis["confidence"],
        image_quality
    )
    
    # Determine triage decision
    triage = _determine_triage_routing(
        adjusted_confidence,
        severity_analysis["severity_score"],
        image_quality
    )
    
    return {
        "pest_disease_id": cv_analysis["pest_disease_id"],
        "pest_disease_name": cv_analysis["pest_disease_name"],
        "cv_confidence": cv_analysis["confidence"],
        "adjusted_confidence": adjusted_confidence,
        "confidence_category": triage["confidence_category"],
        "damage_extent_percent": cv_analysis["damage_extent_percent"],
        "infection_stage": cv_analysis["infection_stage"],
        "severity_score": severity_analysis["severity_score"],
        "severity_category": severity_analysis["severity_category"],
        "intervention_urgency": severity_analysis["intervention_urgency"],
        "treatment_strategy": severity_analysis["treatment_strategy"],
        "image_quality": image_quality,
        "requires_expert_verification": triage["requires_expert"],
        "triage_reason": triage["reason"],
        "expert_routing": triage["expert_routing"],
        "farmer_action": triage["farmer_action"],
        "ai_reasoning": _generate_diagnostic_reasoning(
            cv_analysis, severity_analysis, triage
        )
    }


def _simulate_cv_pest_diagnosis(crop: str, override_confidence: Optional[float]) -> Dict:
    """Simulate computer vision pest/disease diagnosis."""
    import random
    
    # Common pests by crop
    crop_pests = {
        "maize": ["fall_armyworm", "maize_streak_virus", "aphids"],
        "potato": ["late_blight", "aphids"],
        "tomato": ["late_blight", "aphids"],
        "beans": ["bean_rust", "aphids"],
        "cabbage": ["aphids"],
        "sorghum": ["fall_armyworm", "aphids"]
    }
    
    pests = crop_pests.get(crop, ["aphids"])
    pest_id = random.choice(pests)
    
    pest_names = {
        "late_blight": "Late Blight (Phytophthora infestans)",
        "fall_armyworm": "Fall Armyworm (Spodoptera frugiperda)",
        "aphids": "Aphids (Various species)",
        "bean_rust": "Bean Rust (Uromyces appendiculatus)",
        "maize_streak_virus": "Maize Streak Virus"
    }
    
    return {
        "pest_disease_id": pest_id,
        "pest_disease_name": pest_names.get(pest_id, "Unknown"),
        "confidence": override_confidence if override_confidence else random.uniform(0.65, 0.95),
        "damage_extent_percent": random.uniform(5, 60),
        "damage_type": random.choice(["leaf_damage", "stem_damage", "fruit_damage", "root_damage"]),
        "infection_stage": random.choice(["early", "moderate", "advanced"])
    }


def _assess_image_quality(image_data: bytes, metadata: Optional[Dict]) -> Dict[str, float]:
    """Assess image quality metrics."""
    import random
    
    # In production, analyze actual image properties
    # For now, simulate quality scores
    return {
        "brightness": random.uniform(0.4, 1.0),
        "sharpness": random.uniform(0.5, 1.0),
        "resolution": random.uniform(0.6, 1.0),
        "leaf_visibility": random.uniform(0.7, 1.0),
        "overall_quality": random.uniform(0.6, 0.95)
    }


def _calculate_severity_score(
    damage_type: str,
    damage_extent_percent: float,
    infection_stage: str
) -> Dict[str, Any]:
    """
    Calculate severity score and determine intervention strategy.
    
    Returns:
        dict: Severity score (0-10), category, urgency, treatment strategy
    """
    # Base score from damage extent
    base_score = (damage_extent_percent / 100) * 10
    
    # Adjust for infection stage
    stage_multipliers = {
        "early": 0.8,
        "moderate": 1.0,
        "advanced": 1.3
    }
    stage_multiplier = stage_multipliers.get(infection_stage, 1.0)
    
    # Adjust for damage type
    damage_multipliers = {
        "leaf_damage": 1.0,
        "stem_damage": 1.2,
        "fruit_damage": 1.3,
        "root_damage": 1.4
    }
    damage_multiplier = damage_multipliers.get(damage_type, 1.0)
    
    # Final severity score
    severity_score = min(base_score * stage_multiplier * damage_multiplier, 10.0)
    
    # Categorize severity
    if severity_score < 3.0:
        severity_category = "mild"
        intervention_urgency = "low"
        treatment_strategy = "organic_ipm"  # Cultural + organic methods
    elif severity_score < 5.0:
        severity_category = "moderate"
        intervention_urgency = "medium"
        treatment_strategy = "enhanced_organic"  # Biological + organic pesticides
    elif severity_score < 7.5:
        severity_category = "severe"
        intervention_urgency = "high"
        treatment_strategy = "targeted_chemical"  # Selective chemical intervention
    else:
        severity_category = "critical"
        intervention_urgency = "urgent"
        treatment_strategy = "rapid_chemical"  # Immediate broad-spectrum treatment
    
    return {
        "severity_score": round(severity_score, 2),
        "severity_category": severity_category,
        "intervention_urgency": intervention_urgency,
        "treatment_strategy": treatment_strategy,
        "damage_extent_percent": round(damage_extent_percent, 1),
        "infection_stage": infection_stage
    }


def _adjust_confidence_for_quality(
    cv_confidence: float,
    image_quality: Dict[str, float]
) -> float:
    """
    Adjust CV model confidence based on image quality.
    
    Poor image quality = lower confidence in diagnosis.
    """
    overall_quality = image_quality["overall_quality"]
    
    # Penalize confidence for poor image quality
    if overall_quality < 0.6:
        adjusted = cv_confidence * 0.75  # 25% penalty
    elif overall_quality < 0.8:
        adjusted = cv_confidence * 0.90  # 10% penalty
    else:
        adjusted = cv_confidence
    
    return round(min(adjusted, 1.0), 3)


def _determine_triage_routing(
    confidence: float,
    severity_score: float,
    image_quality: Dict[str, float]
) -> Dict[str, Any]:
    """
    Determine if case requires expert verification.
    
    Routing logic:
    - Confidence <65%: Always route to expert
    - Confidence 65-75%: Route if severity >5.0 or image quality poor
    - Confidence >75%: Proceed with AI recommendation
    """
    requires_expert = False
    reason = []
    
    # Low confidence threshold
    if confidence < 0.65:
        requires_expert = True
        reason.append("CV confidence below 65% threshold")
    
    # Medium confidence with high severity
    elif confidence < 0.75:
        if severity_score >= 5.0:
            requires_expert = True
            reason.append("Medium confidence + high severity (expert confirmation needed)")
        elif image_quality["overall_quality"] < 0.7:
            requires_expert = True
            reason.append("Medium confidence + poor image quality")
    
    # Confidence categories
    if confidence >= 0.85:
        confidence_category = "very_high"
    elif confidence >= 0.75:
        confidence_category = "high"
    elif confidence >= 0.65:
        confidence_category = "medium"
    else:
        confidence_category = "low"
    
    # Expert routing details
    if requires_expert:
        # Determine urgency based on severity
        if severity_score >= 7.5:
            urgency = "urgent"  # <2 hours
        elif severity_score >= 5.0:
            urgency = "priority"  # <24 hours
        else:
            urgency = "routine"  # <72 hours
        
        expert_routing = {
            "route_to": "extension_officer",
            "urgency": urgency,
            "estimated_response_time": _get_response_time(urgency)
        }
        
        farmer_action = "wait_for_expert" if urgency == "urgent" else "proceed_with_caution"
    else:
        expert_routing = None
        farmer_action = "proceed_with_ai_recommendation"
    
    return {
        "requires_expert": requires_expert,
        "reason": ", ".join(reason) if reason else "High confidence AI diagnosis",
        "confidence_category": confidence_category,
        "expert_routing": expert_routing,
        "farmer_action": farmer_action
    }


def _get_response_time(urgency: str) -> str:
    """Get expected expert response time."""
    response_times = {
        "urgent": "within 2 hours",
        "priority": "within 24 hours",
        "routine": "within 72 hours"
    }
    return response_times.get(urgency, "within 48 hours")


def _generate_diagnostic_reasoning(
    cv_analysis: Dict,
    severity_analysis: Dict,
    triage: Dict
) -> str:
    """Generate human-readable reasoning for diagnosis."""
    pest_name = cv_analysis["pest_disease_name"]
    confidence = cv_analysis["confidence"]
    severity = severity_analysis["severity_category"]
    treatment = severity_analysis["treatment_strategy"]
    
    reasoning = f"Identified as {pest_name} with {confidence*100:.1f}% confidence. "
    reasoning += f"Severity: {severity} ({severity_analysis['severity_score']:.1f}/10). "
    
    if triage["requires_expert"]:
        reasoning += f"Expert verification required: {triage['reason']}. "
    else:
        reasoning += f"Recommended treatment: {treatment}. "
    
    return reasoning


# ============================================================================
# AI-TRIGGERED CONTAGION MODELING
# ============================================================================

def analyze_contagion_patterns(
    pest_disease_id: str,
    recent_reports: List[Dict],
    wind_data: Optional[Dict] = None,
    road_network: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    AI-triggered contagion modeling using geo-tagged reports + environmental vectors.
    
    Analyzes:
    1. Spatial clustering of reports
    2. Wind direction and speed (airborne spread)
    3. Road networks (human-mediated spread)
    
    Args:
        pest_disease_id: Pest/disease identifier
        recent_reports: List of recent geo-tagged reports (last 30 days)
        wind_data: Wind direction and speed data
        road_network: Road network data (for human-mediated spread analysis)
    
    Returns:
        dict: Contagion analysis with spread vectors and hotspots
    """
    if len(recent_reports) < 3:
        return {
            "contagion_detected": False,
            "reason": "Insufficient reports for contagion analysis (minimum 3 required)"
        }
    
    # Simulate wind data if not provided
    if wind_data is None:
        wind_data = _simulate_wind_data()
    
    # Identify spatial clusters
    clusters = _identify_spatial_clusters(recent_reports)
    
    # Analyze spread vectors
    spread_vectors = _analyze_spread_vectors(
        recent_reports, wind_data, road_network
    )
    
    # Detect contagion hotspots
    hotspots = _detect_contagion_hotspots(clusters, spread_vectors)
    
    # Classify contagion type
    contagion_type = _classify_contagion_type(spread_vectors, hotspots)
    
    return {
        "contagion_detected": len(hotspots) > 0,
        "contagion_type": contagion_type,
        "hotspots": hotspots,
        "spread_vectors": spread_vectors,
        "total_reports": len(recent_reports),
        "report_date_range": {
            "earliest": min(r["date"] for r in recent_reports),
            "latest": max(r["date"] for r in recent_reports)
        },
        "spread_rate_km_per_day": _calculate_spread_rate(recent_reports),
        "affected_area_km2": _calculate_affected_area(recent_reports),
        "predicted_spread_direction": spread_vectors.get("dominant_vector", "unknown"),
        "recommended_alert_zones": _generate_alert_zones(hotspots, spread_vectors),
        "ai_reasoning": _generate_contagion_reasoning(contagion_type, spread_vectors)
    }


def _identify_spatial_clusters(reports: List[Dict]) -> List[Dict]:
    """Identify spatial clusters of pest/disease reports."""
    # Simplified clustering: Group reports within 5km radius
    clusters = []
    processed = set()
    
    for i, report in enumerate(reports):
        if i in processed:
            continue
        
        cluster = [report]
        processed.add(i)
        
        for j, other_report in enumerate(reports):
            if j in processed:
                continue
            
            distance = _calculate_distance(
                report["lat"], report["lon"],
                other_report["lat"], other_report["lon"]
            )
            
            if distance <= 5.0:  # 5km radius
                cluster.append(other_report)
                processed.add(j)
        
        if len(cluster) >= 2:  # Minimum 2 reports for a cluster
            # Calculate cluster centroid
            centroid_lat = sum(r["lat"] for r in cluster) / len(cluster)
            centroid_lon = sum(r["lon"] for r in cluster) / len(cluster)
            
            clusters.append({
                "centroid": {"lat": centroid_lat, "lon": centroid_lon},
                "report_count": len(cluster),
                "reports": cluster,
                "radius_km": _calculate_cluster_radius(cluster, centroid_lat, centroid_lon)
            })
    
    return clusters


def _analyze_spread_vectors(
    reports: List[Dict],
    wind_data: Dict,
    road_network: Optional[List[Dict]]
) -> Dict[str, Any]:
    """
    Analyze spread vectors (wind, roads, etc.).
    
    Returns:
        dict: Spread vector analysis
    """
    # Sort reports by date
    sorted_reports = sorted(reports, key=lambda r: r["date"])
    
    # Analyze temporal spread pattern
    spread_directions = []
    
    for i in range(len(sorted_reports) - 1):
        earlier = sorted_reports[i]
        later = sorted_reports[i + 1]
        
        # Calculate direction of spread
        bearing = _calculate_bearing(
            earlier["lat"], earlier["lon"],
            later["lat"], later["lon"]
        )
        
        distance = _calculate_distance(
            earlier["lat"], earlier["lon"],
            later["lat"], later["lon"]
        )
        
        days_diff = (datetime.fromisoformat(later["date"]) - 
                    datetime.fromisoformat(earlier["date"])).days
        
        if days_diff > 0:
            spread_directions.append({
                "bearing": bearing,
                "distance_km": distance,
                "days": days_diff,
                "speed_km_per_day": distance / days_diff
            })
    
    if not spread_directions:
        return {"dominant_vector": "unknown", "vector_type": "unknown"}
    
    # Calculate dominant spread direction
    avg_bearing = sum(s["bearing"] for s in spread_directions) / len(spread_directions)
    avg_speed = sum(s["speed_km_per_day"] for s in spread_directions) / len(spread_directions)
    
    # Check if spread aligns with wind direction
    wind_direction = wind_data.get("direction_degrees", 0)
    wind_speed_kmh = wind_data.get("speed_kmh", 0)
    
    bearing_diff = abs(avg_bearing - wind_direction)
    wind_aligned = bearing_diff < 45 or bearing_diff > 315  # Within 45 degrees
    
    # Determine vector type
    if wind_aligned and wind_speed_kmh >= 10:
        vector_type = "wind_driven"
        vector_name = f"Wind-driven ({_bearing_to_direction(wind_direction)})"
    elif road_network and _is_road_aligned(spread_directions, road_network):
        vector_type = "road_network"
        vector_name = "Human-mediated (road network)"
    else:
        vector_type = "natural_diffusion"
        vector_name = "Natural diffusion"
    
    return {
        "dominant_vector": vector_name,
        "vector_type": vector_type,
        "dominant_bearing": round(avg_bearing, 1),
        "avg_spread_speed_km_per_day": round(avg_speed, 2),
        "wind_alignment": "aligned" if wind_aligned else "not_aligned",
        "wind_data": wind_data
    }


def _detect_contagion_hotspots(
    clusters: List[Dict],
    spread_vectors: Dict
) -> List[Dict]:
    """Identify contagion hotspots requiring urgent action."""
    hotspots = []
    
    for cluster in clusters:
        # Hotspot criteria:
        # 1. ≥5 reports in cluster
        # 2. High report density (>1 report per km²)
        
        if cluster["report_count"] >= 5:
            area = math.pi * (cluster["radius_km"] ** 2)
            density = cluster["report_count"] / area if area > 0 else 0
            
            if density >= 1.0:
                hotspots.append({
                    "location": cluster["centroid"],
                    "report_count": cluster["report_count"],
                    "radius_km": round(cluster["radius_km"], 2),
                    "density_reports_per_km2": round(density, 2),
                    "severity": "high" if density >= 2.0 else "moderate",
                    "recommended_action": _get_hotspot_action(density)
                })
    
    return hotspots


def _classify_contagion_type(
    spread_vectors: Dict,
    hotspots: List[Dict]
) -> str:
    """Classify type of contagion (e.g., invasive pest, localized outbreak)."""
    if not hotspots:
        return "sporadic_occurrence"
    
    vector_type = spread_vectors.get("vector_type", "unknown")
    avg_speed = spread_vectors.get("avg_spread_speed_km_per_day", 0)
    
    if vector_type == "wind_driven" and avg_speed > 2.0:
        return "rapid_airborne_spread"
    elif vector_type == "road_network":
        return "human_mediated_spread"
    elif len(hotspots) >= 2:
        return "multiple_outbreak_sources"
    else:
        return "localized_outbreak"


def _generate_alert_zones(
    hotspots: List[Dict],
    spread_vectors: Dict
) -> List[Dict]:
    """Generate recommended alert zones based on contagion analysis."""
    alert_zones = []
    
    for hotspot in hotspots:
        # Base alert radius
        base_radius = hotspot["radius_km"] + 5  # +5km buffer
        
        # Expand radius based on spread speed
        avg_speed = spread_vectors.get("avg_spread_speed_km_per_day", 0)
        if avg_speed > 2.0:
            base_radius += 5  # Fast spread = larger alert zone
        
        alert_zones.append({
            "center": hotspot["location"],
            "radius_km": round(base_radius, 1),
            "severity": hotspot["severity"],
            "message": _format_alert_message(hotspot, spread_vectors)
        })
    
    return alert_zones


def _format_alert_message(hotspot: Dict, spread_vectors: Dict) -> str:
    """Format alert message for hotspot."""
    vector = spread_vectors.get("dominant_vector", "unknown")
    
    if spread_vectors.get("vector_type") == "wind_driven":
        return f"🐛 **OUTBREAK WARNING:** Pest spread accelerating {vector}. Clean tools and clothing before entering your field."
    elif spread_vectors.get("vector_type") == "road_network":
        return f"🐛 **OUTBREAK WARNING:** Pest spread along main road. Disinfect equipment and avoid transporting plant material."
    else:
        return f"🐛 **OUTBREAK WARNING:** Localized outbreak detected. Inspect crops daily and report immediately."


def _generate_contagion_reasoning(contagion_type: str, spread_vectors: Dict) -> str:
    """Generate human-readable reasoning for contagion analysis."""
    vector = spread_vectors.get("dominant_vector", "unknown")
    speed = spread_vectors.get("avg_spread_speed_km_per_day", 0)
    
    reasoning = f"Contagion type: {contagion_type.replace('_', ' ')}. "
    reasoning += f"Primary spread vector: {vector}. "
    reasoning += f"Spread rate: {speed:.1f} km/day. "
    
    return reasoning


# ============================================================================
# VISUAL GROWTH LOG FOR FERTILIZER OPTIMIZATION
# ============================================================================

def analyze_growth_photos_for_nutrients(
    farmer_id: str,
    crop: str,
    photo_history: List[Dict]
) -> Dict[str, Any]:
    """
    Computer vision analysis of weekly growth photos for nutrient diagnostics.
    
    Analyzes NDVI proxy (color + foliage density) to detect nutrient deficiencies.
    
    Args:
        farmer_id: Farmer identifier
        crop: Crop type
        photo_history: List of photo records with dates and image data
    
    Returns:
        dict: Visual nutrient assessment with fertilizer timing recommendations
    """
    if len(photo_history) < 2:
        return {
            "status": "insufficient_data",
            "message": "Need at least 2 weeks of photos for trend analysis"
        }
    
    # Analyze each photo for visual indicators
    photo_analyses = []
    
    for photo in photo_history:
        visual_analysis = _analyze_photo_visual_indicators(
            photo.get("image_data"),
            crop
        )
        
        photo_analyses.append({
            "date": photo["date"],
            "days_since_planting": photo.get("days_since_planting", 0),
            "ndvi_proxy": visual_analysis["ndvi_proxy"],
            "leaf_color_score": visual_analysis["leaf_color_score"],
            "foliage_density": visual_analysis["foliage_density"],
            "growth_stage": photo.get("growth_stage", "unknown"),
            "indicators": visual_analysis["indicators"]
        })
    
    # Analyze trends over time
    trend_analysis = _analyze_growth_trends(photo_analyses)
    
    # Detect nutrient deficiencies
    nutrient_diagnosis = _diagnose_nutrient_deficiencies(
        photo_analyses[-1],  # Most recent photo
        trend_analysis
    )
    
    # Generate fertilizer recommendations
    fertilizer_recommendations = _generate_fertilizer_timing_recommendations(
        nutrient_diagnosis,
        photo_analyses[-1]["days_since_planting"],
        crop
    )
    
    return {
        "farmer_id": farmer_id,
        "crop": crop,
        "analysis_date": datetime.now().isoformat(),
        "photos_analyzed": len(photo_analyses),
        "current_status": photo_analyses[-1],
        "trend_analysis": trend_analysis,
        "nutrient_diagnosis": nutrient_diagnosis,
        "fertilizer_recommendations": fertilizer_recommendations,
        "visual_diagnostics_summary": _generate_visual_summary(
            nutrient_diagnosis, trend_analysis
        )
    }


def _analyze_photo_visual_indicators(image_data: bytes, crop: str) -> Dict[str, Any]:
    """
    Analyze photo for visual health indicators (NDVI proxy).
    
    In production, use computer vision model to extract:
    - Leaf color (greenness)
    - Foliage density
    - Plant vigor
    """
    import random
    
    # Simulate CV analysis
    # In production, analyze actual image pixels
    
    # NDVI proxy (0-1, where 1 = healthy dense green vegetation)
    ndvi_proxy = random.uniform(0.4, 0.9)
    
    # Leaf color score (0-1, where 1 = deep green)
    leaf_color_score = random.uniform(0.5, 0.95)
    
    # Foliage density (0-1, where 1 = full canopy coverage)
    foliage_density = random.uniform(0.3, 0.9)
    
    # Visual indicators
    indicators = []
    
    if leaf_color_score < 0.6:
        indicators.append("yellowing_leaves")
    if foliage_density < 0.5:
        indicators.append("sparse_foliage")
    if ndvi_proxy < 0.5:
        indicators.append("poor_vigor")
    
    return {
        "ndvi_proxy": round(ndvi_proxy, 3),
        "leaf_color_score": round(leaf_color_score, 3),
        "foliage_density": round(foliage_density, 3),
        "indicators": indicators
    }


def _analyze_growth_trends(photo_analyses: List[Dict]) -> Dict[str, Any]:
    """Analyze trends in visual indicators over time."""
    if len(photo_analyses) < 2:
        return {"status": "insufficient_data"}
    
    # Calculate changes in NDVI proxy
    ndvi_values = [p["ndvi_proxy"] for p in photo_analyses]
    color_values = [p["leaf_color_score"] for p in photo_analyses]
    
    # Recent trend (last 2-3 photos)
    recent_ndvi = ndvi_values[-3:] if len(ndvi_values) >= 3 else ndvi_values
    
    if len(recent_ndvi) >= 2:
        ndvi_change = recent_ndvi[-1] - recent_ndvi[0]
        
        if ndvi_change > 0.1:
            trend = "improving"
        elif ndvi_change < -0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "unknown"
    
    return {
        "overall_trend": trend,
        "ndvi_change": round(ndvi_change, 3) if len(recent_ndvi) >= 2 else 0,
        "current_ndvi": round(ndvi_values[-1], 3),
        "avg_leaf_color": round(sum(color_values) / len(color_values), 3),
        "weeks_tracked": len(photo_analyses)
    }


def _diagnose_nutrient_deficiencies(
    current_status: Dict,
    trend_analysis: Dict
) -> Dict[str, Any]:
    """Diagnose nutrient deficiencies from visual indicators."""
    deficiencies = []
    
    # Nitrogen deficiency: Yellowing leaves + declining NDVI
    if ("yellowing_leaves" in current_status["indicators"] or 
        current_status["leaf_color_score"] < 0.65):
        
        if trend_analysis.get("overall_trend") == "declining":
            deficiencies.append({
                "nutrient": "Nitrogen",
                "confidence": 0.85,
                "symptoms": ["Yellowing leaves (chlorosis)", "Poor vigor", "Declining NDVI"],
                "severity": "moderate" if current_status["leaf_color_score"] < 0.55 else "mild"
            })
    
    # Phosphorus deficiency: Purple tint (can't detect from simplified model)
    # Potassium deficiency: Brown leaf edges (can't detect from simplified model)
    
    if not deficiencies:
        return {
            "deficiencies_detected": False,
            "status": "healthy",
            "message": "No nutrient deficiencies detected from visual analysis"
        }
    
    return {
        "deficiencies_detected": True,
        "deficiencies": deficiencies,
        "primary_deficiency": deficiencies[0]["nutrient"]
    }


def _generate_fertilizer_timing_recommendations(
    nutrient_diagnosis: Dict,
    days_since_planting: int,
    crop: str
) -> Dict[str, Any]:
    """Generate fertilizer timing recommendations based on visual diagnostics."""
    if not nutrient_diagnosis.get("deficiencies_detected"):
        return {
            "action": "maintain_current_schedule",
            "message": "Continue with planned fertilizer schedule"
        }
    
    primary_deficiency = nutrient_diagnosis["deficiencies"][0]
    nutrient = primary_deficiency["nutrient"]
    severity = primary_deficiency["severity"]
    
    # Determine adjustment to fertilizer schedule
    if severity == "moderate":
        adjustment = "advance_by_5_days"
        message = f"🌱 **URGENT NUTRIENT ALERT:** Your {crop} leaves are showing early yellowing (low {nutrient}). Pull forward your next fertilizer session by 5 days. Apply NOW."
    else:
        adjustment = "advance_by_2_days"
        message = f"🌱 **Nutrient Alert:** Mild {nutrient} deficiency detected. Advance next fertilizer application by 2 days."
    
    # Recommended fertilizer types
    if nutrient == "Nitrogen":
        fertilizer_options = [
            {"type": "organic", "product": "Composted manure", "rate": "2 tons/acre"},
            {"type": "organic", "product": "Chicken manure tea (foliar)", "rate": "Spray every 7 days"},
            {"type": "chemical", "product": "CAN (Calcium Ammonium Nitrate)", "rate": "50 kg/acre"}
        ]
    elif nutrient == "Phosphorus":
        fertilizer_options = [
            {"type": "organic", "product": "Bone meal", "rate": "100 kg/acre"},
            {"type": "chemical", "product": "DAP (Diammonium Phosphate)", "rate": "50 kg/acre"}
        ]
    elif nutrient == "Potassium":
        fertilizer_options = [
            {"type": "organic", "product": "Wood ash", "rate": "200 kg/acre"},
            {"type": "chemical", "product": "Muriate of Potash", "rate": "50 kg/acre"}
        ]
    else:
        fertilizer_options = []
    
    return {
        "action": adjustment,
        "message": message,
        "deficient_nutrient": nutrient,
        "severity": severity,
        "recommended_products": fertilizer_options,
        "application_timing": "immediate" if severity == "moderate" else "within_3_days"
    }


def _generate_visual_summary(
    nutrient_diagnosis: Dict,
    trend_analysis: Dict
) -> str:
    """Generate human-readable visual diagnostics summary."""
    if not nutrient_diagnosis.get("deficiencies_detected"):
        return f"✅ Healthy crop. NDVI trend: {trend_analysis.get('overall_trend', 'unknown')}. Continue current management."
    
    primary = nutrient_diagnosis["deficiencies"][0]
    symptoms = ", ".join(primary["symptoms"])
    
    summary = f"⚠️ {primary['nutrient']} deficiency detected ({primary['severity']}). "
    summary += f"Symptoms: {symptoms}. "
    summary += f"NDVI trend: {trend_analysis.get('overall_trend', 'unknown')}. "
    summary += "Action required: Advance fertilizer application."
    
    return summary


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates (Haversine formula)."""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def _calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing (direction) from point 1 to point 2."""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
    
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def _bearing_to_direction(bearing: float) -> str:
    """Convert bearing to compass direction."""
    directions = ["North", "NE", "East", "SE", "South", "SW", "West", "NW"]
    index = round(bearing / 45) % 8
    return directions[index]


def _calculate_cluster_radius(cluster: List[Dict], centroid_lat: float, centroid_lon: float) -> float:
    """Calculate radius of cluster from centroid."""
    max_distance = 0
    for report in cluster:
        distance = _calculate_distance(
            centroid_lat, centroid_lon,
            report["lat"], report["lon"]
        )
        max_distance = max(max_distance, distance)
    return max_distance


def _calculate_spread_rate(reports: List[Dict]) -> float:
    """Calculate average spread rate from reports."""
    if len(reports) < 2:
        return 0.0
    
    sorted_reports = sorted(reports, key=lambda r: r["date"])
    
    earliest = sorted_reports[0]
    latest = sorted_reports[-1]
    
    distance = _calculate_distance(
        earliest["lat"], earliest["lon"],
        latest["lat"], latest["lon"]
    )
    
    days = (datetime.fromisoformat(latest["date"]) - 
            datetime.fromisoformat(earliest["date"])).days
    
    return round(distance / days, 2) if days > 0 else 0.0


def _calculate_affected_area(reports: List[Dict]) -> float:
    """Calculate affected area from bounding box of reports."""
    if len(reports) < 2:
        return 0.0
    
    lats = [r["lat"] for r in reports]
    lons = [r["lon"] for r in reports]
    
    # Calculate bounding box
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    # Calculate area (approximate)
    height = _calculate_distance(min_lat, min_lon, max_lat, min_lon)
    width = _calculate_distance(min_lat, min_lon, min_lat, max_lon)
    
    return round(height * width, 2)


def _simulate_wind_data() -> Dict:
    """Simulate wind data (replace with real weather API in production)."""
    import random
    return {
        "direction_degrees": random.uniform(0, 360),
        "speed_kmh": random.uniform(5, 25),
        "source": "simulated"
    }


def _is_road_aligned(spread_directions: List[Dict], road_network: List[Dict]) -> bool:
    """Check if spread pattern aligns with road network."""
    # Simplified: Assume road alignment if spread speed > 5 km/day
    # In production, analyze actual road network geometry
    avg_speed = sum(s["speed_km_per_day"] for s in spread_directions) / len(spread_directions)
    return avg_speed > 5.0


def _get_hotspot_action(density: float) -> str:
    """Get recommended action for hotspot based on density."""
    if density >= 2.0:
        return "Emergency mass treatment campaign + quarantine zone establishment"
    else:
        return "Intensive monitoring + coordinated treatment within 5km radius"


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "analyze_pest_disease_severity",
    "analyze_contagion_patterns",
    "analyze_growth_photos_for_nutrients"
]
