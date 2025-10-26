"""
Enhanced Pest and Disease Alert System with IPM Focus
Features:
- Integrated Pest Management (IPM) - Cultural/Biological/Organic FIRST
- Geo-tagging with GPS coordinates for precision tracking
- Preventative weather-based alerts (LCRS integration)
- Efficacy feedback loop for continuous improvement
- Expert triage system for low-confidence diagnoses
- Pretrained AI model integration (PlantVillage, TensorFlow Hub)
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
PEST_REPORTS_FILE = DATA_DIR / "pest_reports.json"
DISEASE_REPORTS_FILE = DATA_DIR / "disease_reports.json"
PEST_LIBRARY_FILE = DATA_DIR / "pest_disease_library.json"
TREATMENT_FEEDBACK_FILE = DATA_DIR / "treatment_feedback.json"
EXPERT_TRIAGE_QUEUE_FILE = DATA_DIR / "expert_triage_queue.json"
PREVENTATIVE_ALERTS_FILE = DATA_DIR / "preventative_alerts.json"

# AI Model Configuration
AI_MODEL_CONFIG = {
    "primary_model": "plantvillage_mobilenet_v2",
    "fallback_model": "tfhub_plant_disease_classifier",
    "confidence_threshold_auto": 0.75,  # Auto-apply advice
    "confidence_threshold_triage": 0.50,  # Send to expert if below
    "supported_crops": ["maize", "beans", "potatoes", "rice", "cassava", "tomato", "wheat"]
}


def load_pest_reports() -> Dict:
    """Load all pest reports"""
    if PEST_REPORTS_FILE.exists():
        with open(PEST_REPORTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_pest_reports(reports: Dict):
    """Save pest reports"""
    with open(PEST_REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=2)


def load_disease_reports() -> Dict:
    """Load all disease reports"""
    if DISEASE_REPORTS_FILE.exists():
        with open(DISEASE_REPORTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_disease_reports(reports: Dict):
    """Save disease reports"""
    with open(DISEASE_REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=2)


def load_treatment_feedback() -> Dict:
    """Load treatment efficacy feedback"""
    if TREATMENT_FEEDBACK_FILE.exists():
        with open(TREATMENT_FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_treatment_feedback(feedback: Dict):
    """Save treatment efficacy feedback"""
    with open(TREATMENT_FEEDBACK_FILE, 'w') as f:
        json.dump(feedback, f, indent=2)


def load_expert_triage_queue() -> List:
    """Load expert triage queue"""
    if EXPERT_TRIAGE_QUEUE_FILE.exists():
        with open(EXPERT_TRIAGE_QUEUE_FILE, 'r') as f:
            return json.load(f)
    return []


def save_expert_triage_queue(queue: List):
    """Save expert triage queue"""
    with open(EXPERT_TRIAGE_QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)


def load_preventative_alerts() -> Dict:
    """Load preventative alert history"""
    if PREVENTATIVE_ALERTS_FILE.exists():
        with open(PREVENTATIVE_ALERTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_preventative_alerts(alerts: Dict):
    """Save preventative alert history"""
    with open(PREVENTATIVE_ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)


def _call_ai_model(image_url: str, crop: str, symptoms_description: Optional[str]) -> Dict:
    """
    Call pretrained AI model for pest/disease identification
    
    Supports multiple pretrained models:
    1. PlantVillage MobileNetV2 (TensorFlow Hub)
    2. Plant Disease Classifier (Custom TensorFlow model)
    3. PlantDoc (ResNet-based)
    
    In production, this would:
    - Load image from URL
    - Preprocess for model input (224x224, normalize)
    - Run inference through model
    - Post-process predictions
    
    API Integration Example:
    ```python
    import tensorflow as tf
    import tensorflow_hub as hub
    
    # Load model from TensorFlow Hub
    model_url = "https://tfhub.dev/google/cropnet/classifier/cassava_disease_V1/2"
    model = hub.load(model_url)
    
    # Preprocess image
    img = tf.keras.preprocessing.image.load_img(image_url, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) / 255.0
    
    # Predict
    predictions = model(img_array)
    ```
    
    For now, returns structured placeholder ready for model integration
    """
    
    # PRODUCTION INTEGRATION POINTS:
    # 
    # Option 1: TensorFlow Hub PlantVillage Model
    # URL: https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/classification/5
    # Classes: 38 plant disease categories
    # 
    # Option 2: Custom PlantVillage Model (Kaggle dataset)
    # GitHub: https://github.com/spMohanty/PlantVillage-Dataset
    # Classes: Tomato, Potato, Corn diseases (14 classes each)
    # 
    # Option 3: Roboflow Plant Disease API
    # API: https://api.roboflow.com/plant-disease-detection
    # 
    # Option 4: Google Cloud Vision AI + Custom Model
    # API: https://cloud.google.com/vision/docs/drag-and-drop
    
    # For now, simulate AI response
    return _simulate_pest_disease_diagnosis(crop, symptoms_description)


def _queue_for_expert_triage(report: Dict):
    """
    Queue low-confidence diagnosis for expert review
    
    In production, this would:
    - Send push notification to verified extension officers
    - Create ticket in expert dashboard
    - Send SMS/email alert to local agricultural officer
    """
    queue = load_expert_triage_queue()
    
    triage_ticket = {
        "ticket_id": f"TRIAGE_{report['report_id']}",
        "report_id": report['report_id'],
        "farmer_id": report['farmer_id'],
        "field_id": report['field_id'],
        "crop": report['crop'],
        "image_url": report['image_url'],
        "gps_location": report['gps_location'],
        "symptoms_description": report['symptoms_description'],
        "ai_diagnosis": report['diagnosis'],
        "ai_confidence": report['diagnosis']['confidence'],
        "queued_at": datetime.utcnow().isoformat(),
        "status": "pending",  # pending, assigned, resolved
        "assigned_expert": None,
        "expert_response": None,
        "priority": "high" if report['diagnosis']['severity'] == "high" else "medium"
    }
    
    queue.append(triage_ticket)
    save_expert_triage_queue(queue)
    
    # TODO: Send notification to extension officers
    # _notify_extension_officers(triage_ticket)


def scan_plant_image(
    field_id: str,
    farmer_id: str,
    image_url: str,
    crop: str,
    gps_latitude: float,
    gps_longitude: float,
    symptoms_description: Optional[str] = None,
    use_ai_model: bool = True
) -> Dict:
    """
    Enhanced plant image scan with IPM focus, geo-tagging, and AI integration
    
    Args:
        field_id: Field identifier
        farmer_id: Farmer identifier
        image_url: URL/path to uploaded image
        crop: Crop type
        gps_latitude: Exact GPS latitude of scan location
        gps_longitude: Exact GPS longitude of scan location
        symptoms_description: Optional text description of symptoms
        use_ai_model: Whether to call AI model (True) or simulate (False for testing)
    
    Returns:
        Diagnosis with IPM-focused recommendations and geo-tag
    """
    # Geo-tag for precision tracking
    gps_location = {
        "latitude": gps_latitude,
        "longitude": gps_longitude,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Call AI model for diagnosis
    if use_ai_model:
        diagnosis = _call_ai_model(image_url, crop, symptoms_description)
    else:
        # Fallback to simulation for testing
        diagnosis = _simulate_pest_disease_diagnosis(crop, symptoms_description)
    
    # Create report
    report_id = f"{field_id}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Determine status based on confidence
    if diagnosis["confidence"] >= AI_MODEL_CONFIG["confidence_threshold_auto"]:
        status = "confirmed"
        action_required = "apply_treatment"
    elif diagnosis["confidence"] >= AI_MODEL_CONFIG["confidence_threshold_triage"]:
        status = "needs_verification"
        action_required = "monitor_and_rescan"
    else:
        status = "expert_triage_required"
        action_required = "await_expert_review"
    
    report = {
        "report_id": report_id,
        "field_id": field_id,
        "farmer_id": farmer_id,
        "crop": crop,
        "image_url": image_url,
        "gps_location": gps_location,  # GEO-TAGGING
        "symptoms_description": symptoms_description,
        "scan_timestamp": datetime.utcnow().isoformat(),
        "diagnosis": diagnosis,
        "status": status,
        "action_required": action_required,
        "community_alert_sent": False,
        "efficacy_feedback": None,  # For feedback loop
        "expert_review": None  # For expert triage
    }
    
    # Send to expert triage if confidence is low
    if status == "expert_triage_required":
        _queue_for_expert_triage(report)
    
    # Save report
    if diagnosis["type"] == "pest":
        reports = load_pest_reports()
        if field_id not in reports:
            reports[field_id] = []
        reports[field_id].append(report)
        save_pest_reports(reports)
    else:
        reports = load_disease_reports()
        if field_id not in reports:
            reports[field_id] = []
        reports[field_id].append(report)
        save_disease_reports(reports)
    
    return report


def _simulate_pest_disease_diagnosis(crop: str, symptoms: Optional[str]) -> Dict:
    """
    Simulate AI diagnosis (placeholder for ML model)
    
    In production, this would be replaced with actual ML inference
    """
    # Common pests/diseases by crop
    common_issues = {
        "maize": [
            {
                "name": "Fall Armyworm",
                "type": "pest",
                "confidence": 0.85,
                "description": "Caterpillar pest that feeds on leaves, creating characteristic 'window pane' damage"
            },
            {
                "name": "Maize Streak Virus",
                "type": "disease",
                "confidence": 0.75,
                "description": "Viral disease causing yellow streaks on leaves"
            },
            {
                "name": "Stem Borer",
                "type": "pest",
                "confidence": 0.70,
                "description": "Larva bores into maize stem, causing wilting and breakage"
            }
        ],
        "beans": [
            {
                "name": "Bean Fly",
                "type": "pest",
                "confidence": 0.80,
                "description": "Larvae mine through leaves, creating winding trails"
            },
            {
                "name": "Angular Leaf Spot",
                "type": "disease",
                "confidence": 0.75,
                "description": "Fungal disease causing angular brown lesions on leaves"
            }
        ],
        "potatoes": [
            {
                "name": "Late Blight",
                "type": "disease",
                "confidence": 0.90,
                "description": "Devastating fungal disease causing brown lesions on leaves and tubers"
            },
            {
                "name": "Potato Tuber Moth",
                "type": "pest",
                "confidence": 0.75,
                "description": "Moth larvae tunnel into tubers, causing storage losses"
            }
        ]
    }
    
    # Select diagnosis (in real system, ML model would do this)
    crop_issues = common_issues.get(crop.lower(), common_issues["maize"])
    diagnosis_data = crop_issues[0]  # Just use first for simulation
    
    # Get remedies
    remedies = _get_pest_disease_remedies(diagnosis_data["name"], crop)
    
    return {
        "identified_issue": diagnosis_data["name"],
        "type": diagnosis_data["type"],
        "confidence": diagnosis_data["confidence"],
        "description": diagnosis_data["description"],
        "severity": "high" if diagnosis_data["confidence"] >= 0.8 else "medium",
        "remedies": remedies
    }


def _get_pest_disease_remedies(issue_name: str, crop: str) -> Dict:
    """
    Get IPM-focused treatment recommendations
    
    PRIORITY ORDER (Integrated Pest Management):
    1. CULTURAL controls (hand-picking, sanitation, crop rotation)
    2. BIOLOGICAL controls (beneficial insects, natural predators)
    3. ORGANIC treatments (neem, garlic, ash, botanical extracts)
    4. CHEMICAL controls (ONLY if organic fails after 3-7 days)
    
    This approach reduces costs, protects environment, and builds sustainable farming
    """
    
    remedy_library = {
        "Fall Armyworm": {
            "ipm_approach": "Cultural → Biological → Organic → Chemical (last resort)",
            "immediate_actions": [
                "🔍 Scout field daily, especially early morning",
                "✋ Hand-pick and destroy visible caterpillars",
                "🥚 Look for egg masses on leaf undersides, crush them"
            ],
            "step_1_cultural": [
                {
                    "method": "Hand-Picking & Destruction",
                    "timing": "Start IMMEDIATELY",
                    "frequency": "Daily for 5 days",
                    "effectiveness": "70-80% for small infestations",
                    "cost": "FREE (labor only)",
                    "notes": "Most effective in early morning when caterpillars are visible"
                },
                {
                    "method": "Field Sanitation",
                    "timing": "Start today",
                    "action": "Remove and burn all crop residues after harvest",
                    "effectiveness": "Prevents next generation",
                    "cost": "FREE"
                }
            ],
            "step_2_biological": [
                {
                    "method": "Beneficial Insects (Natural Predators)",
                    "organisms": "Ladybugs, lacewings, parasitic wasps",
                    "action": "Avoid broad-spectrum insecticides to protect these helpers",
                    "effectiveness": "Provides long-term control",
                    "cost": "FREE (conserve existing population)"
                },
                {
                    "method": "Biopesticide - Bacillus thuringiensis (Bt)",
                    "product": "Dipel or Thuricide (organic certified)",
                    "dosage": "10g per 20L water",
                    "application": "Spray in evening (Bt degrades in sunlight)",
                    "effectiveness": "80-90% on young larvae",
                    "cost": "~600 KES per 100g",
                    "notes": "Safe for humans, animals, and beneficial insects"
                }
            ],
            "step_3_organic": [
                {
                    "method": "Neem Extract Spray (ORGANIC)",
                    "preparation": "Crush 1kg neem seeds, soak in 10L water overnight",
                    "application": "Strain and spray on plants (focus on whorls)",
                    "frequency": "Every 5 days until control achieved",
                    "effectiveness": "70-85% on young larvae",
                    "timing": "Apply if cultural methods insufficient after 3 days",
                    "cost": "~200 KES per treatment (if buying neem seeds)",
                    "monitor": "Check results after 3 days. If no improvement, proceed to Step 4"
                },
                {
                    "method": "Ash + Soap Solution (ORGANIC)",
                    "preparation": "Mix 2 cups wood ash + 1 bar soap (grated) in 10L water",
                    "application": "Spray entire plant, especially leaf whorls",
                    "frequency": "Twice per week",
                    "effectiveness": "60-70%",
                    "cost": "Nearly free (use cooking fire ash)",
                    "monitor": "Observe for 5 days"
                },
                {
                    "method": "Tephrosia vogelii Extract (ORGANIC)",
                    "preparation": "Crush 1kg leaves, soak in 5L water for 24hrs",
                    "application": "Dilute 1:5 and spray",
                    "frequency": "Every week",
                    "effectiveness": "75-80%",
                    "cost": "Free if plant is available locally",
                    "caution": "Toxic to fish - avoid near water"
                }
            ],
            "step_4_chemical": [
                {
                    "use_only_if": "⚠️ Organic methods fail after 7 days OR infestation exceeds 30% of plants",
                    "warning": "Chemical pesticides are LAST RESORT. High cost, environmental harm, resistance risk."
                },
                {
                    "product": "Tracer 480 SC (Spinosad - Bio-pesticide)",
                    "dosage": "50ml per 20L water",
                    "cost": "~800 KES per 100ml bottle",
                    "application": "Spray thoroughly, targeting whorls",
                    "effectiveness": "90-95%",
                    "notes": "Bio-pesticide, safer for beneficials. TRY THIS BEFORE synthetic"
                },
                {
                    "product": "Belt 480 SC (Flubendiamide - SYNTHETIC)",
                    "dosage": "20ml per 20L water",
                    "cost": "~1200 KES per 100ml",
                    "application": "Spray at early infestation",
                    "effectiveness": "95%+",
                    "notes": "Very effective but expensive. ABSOLUTE LAST RESORT",
                    "resistance_warning": "Rotate with other chemicals to prevent resistance"
                }
            ],
            "prevention": [
                "Plant early to avoid peak pest pressure",
                "Intercrop with desmodium (push-pull system)",
                "Use pheromone traps to monitor and reduce populations",
                "Destroy crop residues after harvest"
            ]
        },
        "Late Blight": {
            "immediate_actions": [
                "🚨 URGENT: Remove and BURN infected plants immediately",
                "💧 Stop overhead watering (use drip if possible)",
                "🌬️ Improve air circulation between plants"
            ],
            "local_remedies": [
                {
                    "method": "Copper-based Home Spray",
                    "preparation": "Mix copper sulfate (1 tablespoon) + lime (2 tablespoons) in 10L water",
                    "application": "Spray all plants thoroughly (bottom and top of leaves)",
                    "frequency": "Every 7-10 days, or after rain",
                    "cost": "~300 KES for season supply"
                },
                {
                    "method": "Garlic + Chili Extract",
                    "preparation": "Blend 10 cloves garlic + 10 hot chilis + 1L water, strain",
                    "application": "Dilute 1:5, spray as preventive",
                    "frequency": "Weekly",
                    "cost": "~100 KES per treatment"
                }
            ],
            "commercial_options": [
                {
                    "product": "Ridomil Gold MZ (Mancozeb + Metalaxyl)",
                    "dosage": "50g per 20L water",
                    "cost": "~600 KES per 1kg pack",
                    "application": "Spray every 10-14 days, start BEFORE symptoms",
                    "notes": "PREVENTIVE application critical"
                },
                {
                    "product": "Acrobat MZ",
                    "dosage": "50g per 20L water",
                    "cost": "~550 KES per 500g",
                    "application": "Alternate with Ridomil for resistance management",
                    "notes": "Effective curative and preventive"
                }
            ],
            "prevention": [
                "Use certified disease-free seed potatoes",
                "Plant resistant varieties (e.g., Asante, Sherekea)",
                "Avoid planting in very wet/humid conditions",
                "Space plants properly for airflow",
                "Apply preventive fungicide BEFORE disease appears"
            ]
        },
        "Maize Streak Virus": {
            "immediate_actions": [
                "🦗 Control leafhopper vectors immediately",
                "🌾 Remove and destroy severely infected plants",
                "📍 Monitor entire field for spread"
            ],
            "local_remedies": [
                {
                    "method": "Neem Oil Spray (for vector control)",
                    "preparation": "100ml neem oil + 20L water + few drops soap (emulsifier)",
                    "application": "Spray to repel leafhoppers",
                    "frequency": "Every 5 days",
                    "cost": "~400 KES per 250ml neem oil"
                }
            ],
            "commercial_options": [
                {
                    "product": "Confidor 200 SL (Imidacloprid)",
                    "dosage": "30ml per 20L water",
                    "cost": "~350 KES per 100ml",
                    "application": "Spray to control leafhopper vectors",
                    "notes": "Targets the insect vector, not the virus"
                }
            ],
            "prevention": [
                "Plant resistant varieties (e.g., DH04, Duma 43)",
                "Plant early to avoid peak vector populations",
                "Remove volunteer maize plants (virus reservoir)",
                "Use seed treatment with insecticide",
                "NOTE: No cure for virus once infected - focus on prevention!"
            ]
        },
        "Bean Fly": {
            "immediate_actions": [
                "👀 Inspect leaves for mining trails",
                "✂️ Remove and destroy heavily infested leaves",
                "🌱 Monitor for adult flies (yellow with black spots)"
            ],
            "local_remedies": [
                {
                    "method": "Wood Ash Dusting",
                    "preparation": "Use fine wood ash from cooking fire",
                    "application": "Dust plants early morning when dew is present",
                    "frequency": "Every 3-4 days",
                    "cost": "Free"
                },
                {
                    "method": "Neem + Soap Spray",
                    "preparation": "50ml neem oil + bar soap (grated) in 20L water",
                    "application": "Spray both sides of leaves",
                    "frequency": "Weekly",
                    "cost": "~200 KES per treatment"
                }
            ],
            "commercial_options": [
                {
                    "product": "Dimethoate 40 EC",
                    "dosage": "30ml per 20L water",
                    "cost": "~250 KES per 100ml",
                    "application": "Spray at first sign of mining",
                    "notes": "Systemic action"
                }
            ],
            "prevention": [
                "Treat seeds with insecticide before planting",
                "Plant early in season",
                "Use trap crops (plant early beans to attract flies)",
                "Practice crop rotation"
            ]
        },
        "Angular Leaf Spot": {
            "immediate_actions": [
                "🍂 Remove infected leaves immediately",
                "💧 Avoid overhead watering",
                "🌿 Increase plant spacing if possible"
            ],
            "local_remedies": [
                {
                    "method": "Baking Soda Spray",
                    "preparation": "1 tablespoon baking soda + 1 tablespoon vegetable oil + few drops soap in 5L water",
                    "application": "Spray thoroughly on all foliage",
                    "frequency": "Every 7 days",
                    "cost": "~50 KES per treatment"
                }
            ],
            "commercial_options": [
                {
                    "product": "Mancozeb 80 WP",
                    "dosage": "50g per 20L water",
                    "cost": "~200 KES per 1kg",
                    "application": "Spray every 10-14 days",
                    "notes": "Start at flowering stage"
                }
            ],
            "prevention": [
                "Use disease-free certified seed",
                "Practice 2-3 year crop rotation",
                "Bury or burn crop residues",
                "Plant resistant varieties"
            ]
        }
    }
    
    return remedy_library.get(issue_name, {
        "immediate_actions": ["Consult agricultural extension officer"],
        "local_remedies": [],
        "commercial_options": [],
        "prevention": ["Practice good field hygiene", "Monitor regularly"]
    })


def send_community_alert(
    report_id: str,
    radius_km: float = 5.0
) -> Dict:
    """
    Send alert to all farmers within radius of pest/disease outbreak
    
    Args:
        report_id: ID of the confirmed pest/disease report
        radius_km: Alert radius in kilometers (default 5km)
    
    Returns:
        Alert details with recipients list
    """
    # Find the report
    pest_reports = load_pest_reports()
    disease_reports = load_disease_reports()
    
    report = None
    report_type = None
    
    # Search in pest reports
    for field_id, reports in pest_reports.items():
        for r in reports:
            if r["report_id"] == report_id:
                report = r
                report_type = "pest"
                break
        if report:
            break
    
    # Search in disease reports if not found
    if not report:
        for field_id, reports in disease_reports.items():
            for r in reports:
                if r["report_id"] == report_id:
                    report = r
                    report_type = "disease"
                    break
            if report:
                break
    
    if not report:
        raise ValueError(f"Report {report_id} not found")
    
    # Only send alert for confirmed high-confidence diagnoses
    if report["diagnosis"]["confidence"] < 0.7:
        return {
            "alert_sent": False,
            "reason": "Confidence too low - needs verification first"
        }
    
    # Get field location
    from .farm_registration import get_farm_by_field_id, get_nearby_farms
    
    farm = get_farm_by_field_id(report["field_id"])
    if not farm:
        raise ValueError(f"Farm not found for field {report['field_id']}")
    
    # Get nearby farms
    nearby_farms = get_nearby_farms(farm["location"], radius_km)
    
    # Prepare alert message
    issue_name = report["diagnosis"]["identified_issue"]
    crop = report["crop"]
    
    alert_message = f"""
🐛 **PEST ALERT** - {issue_name}

📍 Location: Confirmed in your area ({nearby_farms[0]['distance_km']:.1f}km away)
🌾 Crop Affected: {crop.title()}
⚠️ Action: Check your crop immediately and apply recommended practices.

Tap to view treatment options.
    """.strip()
    
    # Get farmer phone numbers (from farms or farmer records)
    # In production, this would integrate with SMS/notification system
    recipients = []
    for nearby_farm in nearby_farms:
        if nearby_farm["field_id"] != report["field_id"]:  # Don't alert the reporter
            recipients.append({
                "farmer_id": nearby_farm["farmer_id"],
                "field_id": nearby_farm["field_id"],
                "distance_km": nearby_farm["distance_km"],
                "message": alert_message
            })
    
    # Mark alert as sent
    if report_type == "pest":
        for field_id, reports in pest_reports.items():
            for r in reports:
                if r["report_id"] == report_id:
                    r["community_alert_sent"] = True
                    r["alert_sent_at"] = datetime.utcnow().isoformat()
                    r["alert_recipients"] = len(recipients)
        save_pest_reports(pest_reports)
    else:
        for field_id, reports in disease_reports.items():
            for r in reports:
                if r["report_id"] == report_id:
                    r["community_alert_sent"] = True
                    r["alert_sent_at"] = datetime.utcnow().isoformat()
                    r["alert_recipients"] = len(recipients)
        save_disease_reports(disease_reports)
    
    # In production, send SMS/push notifications here
    # For now, return recipients list for app to handle
    
    return {
        "alert_sent": True,
        "issue_name": issue_name,
        "radius_km": radius_km,
        "total_recipients": len(recipients),
        "recipients": recipients,
        "message": alert_message
    }


def get_pest_disease_history(
    field_id: Optional[str] = None,
    crop: Optional[str] = None,
    days: int = 30
) -> Dict:
    """Get pest/disease history for field or crop"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    pest_reports = load_pest_reports()
    disease_reports = load_disease_reports()
    
    filtered_pests = []
    filtered_diseases = []
    
    # Filter pest reports
    for fid, reports in pest_reports.items():
        if field_id and fid != field_id:
            continue
        for report in reports:
            if crop and report["crop"] != crop:
                continue
            report_date = datetime.fromisoformat(report["scan_timestamp"].replace('Z', ''))
            if report_date >= cutoff_date:
                filtered_pests.append(report)
    
    # Filter disease reports
    for fid, reports in disease_reports.items():
        if field_id and fid != field_id:
            continue
        for report in reports:
            if crop and report["crop"] != crop:
                continue
            report_date = datetime.fromisoformat(report["scan_timestamp"].replace('Z', ''))
            if report_date >= cutoff_date:
                filtered_diseases.append(report)
    
    return {
        "period_days": days,
        "field_id": field_id,
        "crop": crop,
        "total_pest_reports": len(filtered_pests),
        "total_disease_reports": len(filtered_diseases),
        "pest_reports": sorted(filtered_pests, key=lambda x: x["scan_timestamp"], reverse=True),
        "disease_reports": sorted(filtered_diseases, key=lambda x: x["scan_timestamp"], reverse=True)
    }


def get_active_outbreaks(radius_km: float, center_location: Dict[str, float]) -> List[Dict]:
    """
    Get all active pest/disease outbreaks within radius
    Used for community awareness
    """
    from .farm_registration import calculate_field_distance, load_farms
    
    pest_reports = load_pest_reports()
    disease_reports = load_disease_reports()
    farms = load_farms()
    
    # Consider reports from last 14 days as "active"
    cutoff_date = datetime.utcnow() - timedelta(days=14)
    
    outbreaks = []
    
    # Check pest reports
    for field_id, reports in pest_reports.items():
        for report in reports:
            if not report["community_alert_sent"]:
                continue
            report_date = datetime.fromisoformat(report["scan_timestamp"].replace('Z', ''))
            if report_date < cutoff_date:
                continue
            
            # Get farm location
            from .farm_registration import get_farm_by_field_id
            farm = get_farm_by_field_id(field_id)
            if not farm:
                continue
            
            distance = calculate_field_distance(center_location, farm["location"])
            if distance <= radius_km:
                outbreaks.append({
                    "type": "pest",
                    "issue": report["diagnosis"]["identified_issue"],
                    "crop": report["crop"],
                    "distance_km": round(distance, 2),
                    "reported_date": report["scan_timestamp"],
                    "severity": report["diagnosis"]["severity"]
                })
    
    # Check disease reports
    for field_id, reports in disease_reports.items():
        for report in reports:
            if not report["community_alert_sent"]:
                continue
            report_date = datetime.fromisoformat(report["scan_timestamp"].replace('Z', ''))
            if report_date < cutoff_date:
                continue
            
            from .farm_registration import get_farm_by_field_id
            farm = get_farm_by_field_id(field_id)
            if not farm:
                continue
            
            distance = calculate_field_distance(center_location, farm["location"])
            if distance <= radius_km:
                outbreaks.append({
                    "type": "disease",
                    "issue": report["diagnosis"]["identified_issue"],
                    "crop": report["crop"],
                    "distance_km": round(distance, 2),
                    "reported_date": report["scan_timestamp"],
                    "severity": report["diagnosis"]["severity"]
                })
    
    return sorted(outbreaks, key=lambda x: x["distance_km"])


def generate_preventative_weather_alert(
    field_id: str,
    crop: str,
    location: Dict[str, float]
) -> Optional[Dict]:
    """
    Generate preventative pest/disease alerts based on weather conditions
    
    Uses LCRS engine to predict conditions favorable for diseases BEFORE symptoms appear
    
    Args:
        field_id: Field identifier
        crop: Crop type
        location: GPS coordinates
    
    Returns:
        Preventative alert if conditions are risky, None otherwise
    """
    from .lcrs_engine import estimate_weather_forecast_risk
    from .climate_persistence import calculate_soil_moisture_index, get_latest_soil_report
    
    # Get weather forecast
    current_month = datetime.utcnow().month
    weather_risk = estimate_weather_forecast_risk(
        location["latitude"],
        location["longitude"],
        current_month
    )
    
    # Get soil moisture if available
    soil_report = get_latest_soil_report(field_id)
    smi = 50  # Default
    if soil_report:
        smi = calculate_soil_moisture_index(soil_report["moisture_level"])
    
    alerts = []
    
    # LATE BLIGHT RISK (Potatoes, Tomatoes)
    if crop.lower() in ["potatoes", "tomato", "tomatoes"]:
        if weather_risk["precipitation_risk"] == "high" and weather_risk["temperature_pattern"] == "cool":
            alerts.append({
                "disease": "Late Blight",
                "risk_level": "HIGH",
                "conditions": "High humidity + cool temperatures = PERFECT for fungal growth",
                "forecast": "Heavy rain and cool nights expected for 48 hours",
                "preventative_actions": [
                    "🚨 URGENT: Apply organic Bordeaux mixture (copper sulfate + lime) TODAY",
                    "💧 Stop all overhead watering immediately",
                    "🌿 Increase plant spacing if possible for air circulation",
                    "🔍 Scout field daily for first symptoms (brown lesions on leaves)",
                    "🗑️ Remove any plants with early symptoms and BURN them"
                ],
                "organic_preventative": {
                    "method": "Bordeaux Mixture (Copper-based fungicide)",
                    "preparation": "1 tbsp copper sulfate + 2 tbsp lime in 10L water",
                    "application": "Spray all plants thoroughly (both leaf sides)",
                    "timing": "Apply NOW, before rain starts",
                    "cost": "~300 KES for season supply",
                    "effectiveness": "70-80% prevention if applied early"
                },
                "commercial_preventative": {
                    "product": "Ridomil Gold MZ",
                    "dosage": "50g per 20L water",
                    "timing": "Apply NOW as preventive",
                    "cost": "~600 KES",
                    "note": "Much more expensive but 90%+ effective"
                }
            })
    
    # FUNGAL DISEASE RISK (All crops)
    if weather_risk["precipitation_risk"] == "high" and smi > 70:
        alerts.append({
            "disease": "Fungal Diseases (General)",
            "risk_level": "MODERATE",
            "conditions": "Wet soil + rain forecast = fungal disease risk",
            "preventative_actions": [
                "🌬️ Improve drainage in field (dig trenches if waterlogged)",
                "🍃 Remove lower leaves touching wet soil",
                "🚫 Avoid working in field when plants are wet (spreads spores)",
                "📏 Ensure proper plant spacing for airflow"
                ],
            "organic_preventative": {
                "method": "Baking Soda Spray (Preventive)",
                "preparation": "1 tbsp baking soda + 1 tbsp vegetable oil + drops soap in 5L water",
                "application": "Spray as preventive every 7 days",
                "cost": "~50 KES",
                "effectiveness": "60-70% prevention"
            }
        })
    
    # APHID/SUCKING PEST RISK (Hot, dry conditions)
    if weather_risk["precipitation_risk"] == "low" and weather_risk["temperature_pattern"] == "hot":
        alerts.append({
            "pest": "Aphids & Sucking Pests",
            "risk_level": "MODERATE",
            "conditions": "Hot, dry weather favors aphid population explosion",
            "preventative_actions": [
                "🐞 Conserve beneficial insects (ladybugs eat aphids!)",
                "💧 Light irrigation can disrupt aphids",
                "🌿 Monitor new growth (aphids attack young shoots)",
                "🚿 Spray with plain water to knock off aphids (FREE!)"
            ],
            "organic_preventative": {
                "method": "Neem Oil + Soap Spray",
                "preparation": "50ml neem oil + bar soap in 10L water",
                "application": "Spray as preventive",
                "timing": "Early morning or evening",
                "cost": "~200 KES",
                "effectiveness": "Repels aphids before infestation"
            }
        })
    
    if not alerts:
        return None
    
    # Save alert
    alerts_history = load_preventative_alerts()
    if field_id not in alerts_history:
        alerts_history[field_id] = []
    
    alert_record = {
        "alert_id": f"{field_id}_prev_{datetime.utcnow().strftime('%Y%m%d_%H%M')}",
        "field_id": field_id,
        "crop": crop,
        "generated_at": datetime.utcnow().isoformat(),
        "weather_conditions": weather_risk,
        "soil_moisture_index": smi,
        "alerts": alerts,
        "action_taken": None,  # Farmer reports back
        "was_effective": None  # Feedback loop
    }
    
    alerts_history[field_id].append(alert_record)
    save_preventative_alerts(alerts_history)
    
    return alert_record


def record_treatment_feedback(
    report_id: str,
    treatment_applied: str,
    was_effective: bool,
    days_to_improvement: Optional[int] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Record farmer feedback on treatment effectiveness
    
    This feedback loop allows continuous improvement of recommendations
    
    Args:
        report_id: Original scan report ID
        treatment_applied: Which treatment the farmer used
        was_effective: True if problem was solved, False if not
        days_to_improvement: How many days until improvement seen
        notes: Optional farmer notes
    
    Returns:
        Feedback record
    """
    feedback_db = load_treatment_feedback()
    
    feedback = {
        "feedback_id": f"FB_{report_id}",
        "report_id": report_id,
        "treatment_applied": treatment_applied,
        "was_effective": was_effective,
        "days_to_improvement": days_to_improvement,
        "notes": notes,
        "recorded_at": datetime.utcnow().isoformat()
    }
    
    if report_id not in feedback_db:
        feedback_db[report_id] = []
    feedback_db[report_id].append(feedback)
    save_treatment_feedback(feedback_db)
    
    # Update original report with feedback
    _update_report_with_feedback(report_id, feedback)
    
    return feedback


def _update_report_with_feedback(report_id: str, feedback: Dict):
    """Update original pest/disease report with efficacy feedback"""
    pest_reports = load_pest_reports()
    disease_reports = load_disease_reports()
    
    updated = False
    
    # Check pest reports
    for field_id, reports in pest_reports.items():
        for report in reports:
            if report["report_id"] == report_id:
                report["efficacy_feedback"] = feedback
                updated = True
                break
        if updated:
            save_pest_reports(pest_reports)
            return
    
    # Check disease reports
    for field_id, reports in disease_reports.items():
        for report in reports:
            if report["report_id"] == report_id:
                report["efficacy_feedback"] = feedback
                updated = True
                break
        if updated:
            save_disease_reports(disease_reports)
            return


def get_expert_triage_queue(assigned_to: Optional[str] = None, status: str = "pending") -> List[Dict]:
    """
    Get expert triage queue
    
    Args:
        assigned_to: Filter by assigned expert ID
        status: Filter by status (pending, assigned, resolved)
    
    Returns:
        List of triage tickets
    """
    queue = load_expert_triage_queue()
    
    filtered = []
    for ticket in queue:
        if ticket["status"] != status:
            continue
        if assigned_to and ticket["assigned_expert"] != assigned_to:
            continue
        filtered.append(ticket)
    
    return sorted(filtered, key=lambda x: (x["priority"], x["queued_at"]), reverse=True)


def assign_expert_to_ticket(ticket_id: str, expert_id: str, expert_name: str) -> Dict:
    """Assign extension officer to triage ticket"""
    queue = load_expert_triage_queue()
    
    for ticket in queue:
        if ticket["ticket_id"] == ticket_id:
            ticket["assigned_expert"] = {
                "expert_id": expert_id,
                "expert_name": expert_name,
                "assigned_at": datetime.utcnow().isoformat()
            }
            ticket["status"] = "assigned"
            save_expert_triage_queue(queue)
            return ticket
    
    raise ValueError(f"Ticket {ticket_id} not found")


def submit_expert_response(
    ticket_id: str,
    expert_id: str,
    diagnosis: str,
    recommended_treatment: str,
    confidence: str,  # "high", "medium", "low"
    notes: Optional[str] = None
) -> Dict:
    """
    Extension officer submits expert diagnosis
    
    Args:
        ticket_id: Triage ticket ID
        expert_id: Extension officer ID
        diagnosis: Expert's diagnosis
        recommended_treatment: Treatment recommendation
        confidence: Expert's confidence level
        notes: Additional notes
    
    Returns:
        Updated ticket with expert response
    """
    queue = load_expert_triage_queue()
    
    for ticket in queue:
        if ticket["ticket_id"] == ticket_id:
            ticket["expert_response"] = {
                "expert_id": expert_id,
                "diagnosis": diagnosis,
                "recommended_treatment": recommended_treatment,
                "confidence": confidence,
                "notes": notes,
                "responded_at": datetime.utcnow().isoformat()
            }
            ticket["status"] = "resolved"
            save_expert_triage_queue(queue)
            
            # TODO: Send notification to farmer with expert advice
            # _notify_farmer_expert_response(ticket)
            
            return ticket
    
    raise ValueError(f"Ticket {ticket_id} not found")


def get_treatment_effectiveness_report(crop: Optional[str] = None, days: int = 90) -> Dict:
    """
    Generate report on treatment effectiveness based on farmer feedback
    
    Used to continuously improve recommendations
    
    Args:
        crop: Filter by crop (optional)
        days: Look back period (default 90 days)
    
    Returns:
        Effectiveness statistics by treatment method
    """
    feedback_db = load_treatment_feedback()
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Aggregate feedback by treatment
    treatment_stats = {}
    
    for report_id, feedbacks in feedback_db.items():
        for feedback in feedbacks:
            feedback_date = datetime.fromisoformat(feedback["recorded_at"].replace('Z', ''))
            if feedback_date < cutoff_date:
                continue
            
            treatment = feedback["treatment_applied"]
            if treatment not in treatment_stats:
                treatment_stats[treatment] = {
                    "total_uses": 0,
                    "effective_count": 0,
                    "ineffective_count": 0,
                    "avg_days_to_improvement": []
                }
            
            treatment_stats[treatment]["total_uses"] += 1
            
            if feedback["was_effective"]:
                treatment_stats[treatment]["effective_count"] += 1
                if feedback["days_to_improvement"]:
                    treatment_stats[treatment]["avg_days_to_improvement"].append(
                        feedback["days_to_improvement"]
                    )
            else:
                treatment_stats[treatment]["ineffective_count"] += 1
    
    # Calculate success rates
    for treatment, stats in treatment_stats.items():
        if stats["total_uses"] > 0:
            stats["success_rate"] = round(
                (stats["effective_count"] / stats["total_uses"]) * 100, 1
            )
        if stats["avg_days_to_improvement"]:
            stats["avg_days_to_improvement"] = round(
                sum(stats["avg_days_to_improvement"]) / len(stats["avg_days_to_improvement"]), 1
            )
        else:
            stats["avg_days_to_improvement"] = None
    
    return {
        "period_days": days,
        "crop_filter": crop,
        "treatment_statistics": treatment_stats,
        "most_effective": max(treatment_stats.items(), key=lambda x: x[1]["success_rate"])[0] if treatment_stats else None
    }
