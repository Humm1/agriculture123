"""
Crop Lifecycle Calendar System
Generates detailed farming calendars based on crop growth stages and lifespan
Integrates AI for intelligent scheduling and practice optimization
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

# Import AI intelligence
try:
    from .model_manager import get_model_manager
    MODEL_MANAGER_AVAILABLE = True
except ImportError:
    MODEL_MANAGER_AVAILABLE = False

try:
    from .ai_calendar_intelligence import (
        adjust_practice_date_with_weather,
        optimize_fertilizer_timing_with_leaching,
        refine_harvest_window_with_photos
    )
    AI_INTELLIGENCE_AVAILABLE = True
except ImportError:
    AI_INTELLIGENCE_AVAILABLE = False


class CropLifecycleCalendar:
    """
    Comprehensive crop lifecycle calendar generator
    
    Features:
    - Stage-specific practice recommendations
    - AI-optimized scheduling
    - Weather-adjusted timings
    - Growth monitoring integration
    - Resource planning
    """
    
    def __init__(self):
        self.model_manager = None
        if MODEL_MANAGER_AVAILABLE:
            self.model_manager = get_model_manager()
    
    def generate_lifecycle_calendar(
        self,
        crop: str,
        variety: str,
        planting_date: str,
        plot_id: str,
        location: Optional[Dict] = None,
        soil_type: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive lifecycle calendar
        
        Returns calendar with:
        - All growth stages with dates
        - Stage-specific practices
        - AI-optimized timings
        - Resource requirements
        - Risk alerts
        """
        
        # Get crop lifecycle model
        lifecycle = self._get_crop_lifecycle(crop, variety)
        
        if not lifecycle:
            return {
                "success": False,
                "error": f"No lifecycle model found for {crop} ({variety})"
            }
        
        planting = datetime.fromisoformat(planting_date.replace('Z', ''))
        
        calendar = {
            "plot_id": plot_id,
            "crop": crop,
            "variety": variety,
            "planting_date": planting_date,
            "maturity_days": lifecycle["maturity_days"],
            "expected_harvest_date": (planting + timedelta(days=lifecycle["maturity_days"])).isoformat(),
            "location": location,
            "soil_type": soil_type,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_enabled": MODEL_MANAGER_AVAILABLE and AI_INTELLIGENCE_AVAILABLE,
            "stages": [],
            "practices": [],
            "milestones": [],
            "resource_plan": {},
            "risk_calendar": []
        }
        
        # Generate stage-by-stage schedule
        for stage_key, stage_data in lifecycle["stages"].items():
            stage_start = planting + timedelta(days=stage_data["start"])
            stage_end = planting + timedelta(days=stage_data["end"])
            
            stage_info = {
                "stage": stage_key,
                "name": stage_data["name"],
                "start_date": stage_start.isoformat(),
                "end_date": stage_end.isoformat(),
                "duration_days": stage_data["end"] - stage_data["start"],
                "dap_start": stage_data["start"],
                "dap_end": stage_data["end"],
                "practices": self._get_stage_practices(crop, variety, stage_key, planting),
                "monitoring": self._get_stage_monitoring(crop, stage_key),
                "resources": self._get_stage_resources(crop, stage_key)
            }
            
            calendar["stages"].append(stage_info)
        
        # Generate critical practices timeline
        if "critical_practices" in lifecycle:
            for practice_key, dap in lifecycle["critical_practices"].items():
                practice_date = planting + timedelta(days=dap)
                
                # AI optimization if available
                if AI_INTELLIGENCE_AVAILABLE and location:
                    try:
                        adjusted_date = adjust_practice_date_with_weather(
                            practice_date.isoformat(),
                            practice_key,
                            location
                        )
                        practice_date = datetime.fromisoformat(adjusted_date)
                    except Exception as e:
                        print(f"[CALENDAR] AI adjustment failed: {e}")
                
                practice = {
                    "practice_id": f"{plot_id}_{practice_key}_{dap}",
                    "practice": practice_key,
                    "description": self._get_practice_description(practice_key, crop),
                    "scheduled_date": practice_date.isoformat(),
                    "dap": dap,
                    "priority": self._get_practice_priority(practice_key),
                    "estimated_hours": self._get_practice_duration(practice_key),
                    "estimated_cost": self._get_practice_cost(practice_key, crop),
                    "status": "pending",
                    "ai_optimized": AI_INTELLIGENCE_AVAILABLE and location is not None
                }
                
                calendar["practices"].append(practice)
        
        # Generate milestones
        calendar["milestones"] = self._generate_milestones(crop, variety, planting, lifecycle)
        
        # Generate resource plan
        calendar["resource_plan"] = self._generate_resource_plan(crop, variety, lifecycle)
        
        # Generate risk calendar
        calendar["risk_calendar"] = self._generate_risk_calendar(crop, lifecycle, planting)
        
        return {
            "success": True,
            "calendar": calendar,
            "ai_features_enabled": MODEL_MANAGER_AVAILABLE and AI_INTELLIGENCE_AVAILABLE
        }
    
    def _get_crop_lifecycle(self, crop: str, variety: str) -> Optional[Dict]:
        """Get crop lifecycle model"""
        # Import growth models
        from .growth_model import CROP_GROWTH_MODELS
        
        crop_lower = crop.lower()
        variety_lower = variety.lower()
        
        if crop_lower in CROP_GROWTH_MODELS:
            crop_model = CROP_GROWTH_MODELS[crop_lower]
            
            # Try to find specific variety
            if "varieties" in crop_model:
                if variety_lower in crop_model["varieties"]:
                    return crop_model["varieties"][variety_lower]
                
                # Use default variety
                default = crop_model.get("default_variety", "")
                if default in crop_model["varieties"]:
                    return crop_model["varieties"][default]
        
        return None
    
    def _get_stage_practices(self, crop: str, variety: str, stage: str, planting: datetime) -> List[Dict]:
        """Get recommended practices for a growth stage"""
        practices = []
        
        # Define stage-specific practices
        stage_practice_map = {
            "germination": [
                {"practice": "soil_moisture_check", "description": "Check soil moisture daily", "frequency": "daily"},
                {"practice": "bird_protection", "description": "Install bird scarers", "frequency": "once"}
            ],
            "emergence": [
                {"practice": "emergence_count", "description": "Count emerged seedlings", "frequency": "once"},
                {"practice": "gap_filling", "description": "Replant missing hills", "frequency": "as_needed"}
            ],
            "vegetative": [
                {"practice": "weeding", "description": "Remove weeds", "frequency": "2-3 times"},
                {"practice": "fertilizer_application", "description": "Apply fertilizer", "frequency": "1-2 times"},
                {"practice": "pest_scouting", "description": "Scout for pests", "frequency": "weekly"}
            ],
            "flowering": [
                {"practice": "pollination_support", "description": "Ensure good pollination", "frequency": "continuous"},
                {"practice": "water_management", "description": "Critical watering period", "frequency": "daily"},
                {"practice": "disease_monitoring", "description": "Monitor for diseases", "frequency": "twice_weekly"}
            ],
            "fruiting": [
                {"practice": "nutrient_boost", "description": "Apply fruiting fertilizer", "frequency": "once"},
                {"practice": "water_management", "description": "Maintain soil moisture", "frequency": "regular"},
                {"practice": "pest_control", "description": "Control fruit pests", "frequency": "as_needed"}
            ],
            "maturity": [
                {"practice": "harvest_timing", "description": "Monitor maturity indicators", "frequency": "daily"},
                {"practice": "harvest_preparation", "description": "Prepare storage", "frequency": "once"}
            ]
        }
        
        # Add crop-specific practices
        if crop.lower() == "maize":
            if stage == "tasseling":
                practices.append({
                    "practice": "detasseling",
                    "description": "Remove tassels for hybrid seed production (if applicable)",
                    "frequency": "once"
                })
            if stage == "grain_fill":
                practices.append({
                    "practice": "bird_scaring",
                    "description": "Protect grains from birds",
                    "frequency": "continuous"
                })
        
        elif crop.lower() == "potatoes":
            if stage == "tuber_initiation":
                practices.append({
                    "practice": "earthing_up",
                    "description": "Hill soil around plants",
                    "frequency": "twice"
                })
            if stage == "tuber_bulking":
                practices.append({
                    "practice": "blight_monitoring",
                    "description": "Monitor for late blight",
                    "frequency": "twice_weekly"
                })
        
        # Add generic stage practices
        if stage in stage_practice_map:
            practices.extend(stage_practice_map[stage])
        
        return practices
    
    def _get_stage_monitoring(self, crop: str, stage: str) -> Dict:
        """Get monitoring tasks for a stage"""
        monitoring = {
            "parameters": [],
            "frequency": "weekly",
            "ai_analysis": MODEL_MANAGER_AVAILABLE
        }
        
        # Stage-specific monitoring parameters
        stage_monitoring = {
            "germination": ["soil_temperature", "soil_moisture", "seed_emergence_rate"],
            "emergence": ["plant_count", "uniformity", "leaf_color"],
            "vegetative": ["plant_height", "leaf_count", "stem_diameter", "pest_incidence"],
            "flowering": ["flower_count", "pollination_success", "water_stress_signs"],
            "fruiting": ["fruit_set", "fruit_size", "disease_symptoms"],
            "maturity": ["grain_moisture", "color_change", "lodging"]
        }
        
        if stage in stage_monitoring:
            monitoring["parameters"] = stage_monitoring[stage]
        
        # Add AI-specific monitoring if available
        if MODEL_MANAGER_AVAILABLE:
            monitoring["ai_features"] = {
                "plant_health_scoring": True,
                "pest_detection": True,
                "disease_detection": True,
                "growth_rate_analysis": True
            }
        
        return monitoring
    
    def _get_stage_resources(self, crop: str, stage: str) -> Dict:
        """Get resource requirements for a stage"""
        resources = {
            "labor_hours": 0,
            "inputs": [],
            "equipment": []
        }
        
        # Stage-specific resources
        if stage in ["vegetative", "flowering"]:
            resources["labor_hours"] = 8
            resources["inputs"] = ["fertilizer", "pesticides"]
            resources["equipment"] = ["sprayer", "hoe"]
        
        elif stage == "maturity":
            resources["labor_hours"] = 20
            resources["inputs"] = ["storage_bags", "moisture_meter"]
            resources["equipment"] = ["harvesting_tools", "transport"]
        
        return resources
    
    def _get_practice_description(self, practice_key: str, crop: str) -> str:
        """Get detailed practice description"""
        descriptions = {
            "first_weeding": f"First weeding to control early weed competition in {crop}",
            "second_weeding": f"Second weeding during critical growth period",
            "first_top_dress": f"First nitrogen top dressing for {crop}",
            "second_top_dress": f"Second nitrogen application for grain filling",
            "pest_scouting_start": "Begin regular pest monitoring",
            "disease_monitoring_start": "Start disease surveillance",
            "fertilizer_application": f"Apply balanced fertilizer for {crop}",
            "earthing_up": "Hill soil around potato plants to prevent greening",
            "blight_monitoring_start": "Begin monitoring for potato late blight",
            "staking": "Install stakes for climbing bean varieties"
        }
        
        return descriptions.get(practice_key, f"{practice_key.replace('_', ' ').title()} for {crop}")
    
    def _get_practice_priority(self, practice_key: str) -> str:
        """Determine practice priority"""
        high_priority = ["first_weeding", "first_top_dress", "pest_scouting_start", "blight_monitoring_start"]
        medium_priority = ["second_weeding", "second_top_dress", "disease_monitoring_start"]
        
        if practice_key in high_priority:
            return "high"
        elif practice_key in medium_priority:
            return "medium"
        return "low"
    
    def _get_practice_duration(self, practice_key: str) -> float:
        """Estimate hours needed for practice"""
        duration_map = {
            "weeding": 8.0,
            "top_dress": 4.0,
            "pest_scouting": 2.0,
            "disease_monitoring": 2.0,
            "fertilizer_application": 4.0,
            "earthing_up": 6.0,
            "staking": 10.0
        }
        
        for key, hours in duration_map.items():
            if key in practice_key:
                return hours
        
        return 4.0  # Default
    
    def _get_practice_cost(self, practice_key: str, crop: str) -> float:
        """Estimate cost for practice (in USD)"""
        cost_map = {
            "weeding": 50.0,
            "top_dress": 80.0,
            "fertilizer_application": 100.0,
            "pest_scouting": 20.0,
            "earthing_up": 60.0,
            "staking": 150.0
        }
        
        for key, cost in cost_map.items():
            if key in practice_key:
                return cost
        
        return 50.0  # Default
    
    def _generate_milestones(self, crop: str, variety: str, planting: datetime, lifecycle: Dict) -> List[Dict]:
        """Generate key milestones in crop lifecycle"""
        milestones = []
        
        # Add planting milestone
        milestones.append({
            "milestone": "planting",
            "name": "Planting Complete",
            "date": planting.isoformat(),
            "dap": 0,
            "icon": "🌱"
        })
        
        # Add stage transition milestones
        milestone_stages = {
            "emergence": {"name": "First Emergence", "icon": "🌿"},
            "flowering": {"name": "First Flowering", "icon": "🌸"},
            "fruiting": {"name": "Fruit Set", "icon": "🌾"},
            "maturity": {"name": "Ready for Harvest", "icon": "✅"}
        }
        
        for stage_key, milestone_data in milestone_stages.items():
            if stage_key in lifecycle["stages"]:
                stage = lifecycle["stages"][stage_key]
                milestone_date = planting + timedelta(days=stage["start"])
                
                milestones.append({
                    "milestone": stage_key,
                    "name": milestone_data["name"],
                    "date": milestone_date.isoformat(),
                    "dap": stage["start"],
                    "icon": milestone_data["icon"]
                })
        
        return milestones
    
    def _generate_resource_plan(self, crop: str, variety: str, lifecycle: Dict) -> Dict:
        """Generate resource requirements plan"""
        plan = {
            "total_labor_hours": 0,
            "total_estimated_cost": 0,
            "inputs_needed": [],
            "equipment_needed": [],
            "breakdown_by_stage": []
        }
        
        # Calculate resources per stage
        for stage_key, stage_data in lifecycle["stages"].items():
            stage_resources = {
                "stage": stage_data["name"],
                "labor_hours": 10,  # Default
                "cost": 100.0,  # Default
                "inputs": []
            }
            
            # Adjust based on stage
            if stage_key in ["vegetative", "flowering"]:
                stage_resources["labor_hours"] = 15
                stage_resources["cost"] = 150.0
                stage_resources["inputs"] = ["fertilizer", "pesticides"]
            
            elif stage_key == "maturity":
                stage_resources["labor_hours"] = 25
                stage_resources["cost"] = 200.0
                stage_resources["inputs"] = ["storage_materials"]
            
            plan["total_labor_hours"] += stage_resources["labor_hours"]
            plan["total_estimated_cost"] += stage_resources["cost"]
            plan["breakdown_by_stage"].append(stage_resources)
        
        # Aggregate unique inputs
        all_inputs = set()
        for stage in plan["breakdown_by_stage"]:
            all_inputs.update(stage["inputs"])
        
        plan["inputs_needed"] = list(all_inputs)
        plan["equipment_needed"] = ["hoe", "sprayer", "harvesting_tools"]
        
        return plan
    
    def _generate_risk_calendar(self, crop: str, lifecycle: Dict, planting: datetime) -> List[Dict]:
        """Generate calendar of potential risks by stage"""
        risks = []
        
        # Define crop-specific risks by stage
        crop_risks = {
            "maize": {
                "germination": ["poor_emergence", "seed_rot", "bird_damage"],
                "vegetative": ["armyworm", "stalk_borer", "drought_stress"],
                "flowering": ["poor_pollination", "drought"],
                "grain_fill": ["armyworm", "storage_pests"]
            },
            "potatoes": {
                "vegetative": ["aphids", "early_blight"],
                "tuber_initiation": ["late_blight", "water_stress"],
                "tuber_bulking": ["late_blight", "tuber_moth"]
            },
            "beans": {
                "flowering": ["thrips", "poor_pollination"],
                "pod_formation": ["pod_borer", "anthracnose"]
            }
        }
        
        crop_lower = crop.lower()
        if crop_lower in crop_risks:
            for stage_key, stage_risks in crop_risks[crop_lower].items():
                if stage_key in lifecycle["stages"]:
                    stage = lifecycle["stages"][stage_key]
                    risk_start = planting + timedelta(days=stage["start"])
                    
                    risks.append({
                        "stage": stage_key,
                        "stage_name": stage["name"],
                        "risk_period_start": risk_start.isoformat(),
                        "risks": stage_risks,
                        "monitoring_frequency": "weekly",
                        "ai_detection_available": MODEL_MANAGER_AVAILABLE
                    })
        
        return risks


# Singleton instance
_lifecycle_calendar = None

def get_lifecycle_calendar() -> CropLifecycleCalendar:
    """Get singleton instance of lifecycle calendar"""
    global _lifecycle_calendar
    if _lifecycle_calendar is None:
        _lifecycle_calendar = CropLifecycleCalendar()
    return _lifecycle_calendar
