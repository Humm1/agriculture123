"""
Enhanced Model Training API Routes
Supports all 7 AI model types with dataset generation and training
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import subprocess
import sys
from pathlib import Path

from app.services.enhanced_model_training import EnhancedModelTrainingService

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

# Initialize service
ml_service = EnhancedModelTrainingService()

# ===================================
# REQUEST/RESPONSE MODELS
# ===================================

class TrainingRequest(BaseModel):
    model_type: str  # 'pest_detection', 'disease_detection', 'soil_diagnostics', 'yield_prediction', 'climate_prediction'
    epochs: Optional[int] = 10
    generate_datasets: Optional[bool] = False  # Whether to generate datasets first


class DatasetGenerationRequest(BaseModel):
    force_regenerate: Optional[bool] = False


# ===================================
# DATASET GENERATION ENDPOINTS
# ===================================

@router.post("/datasets/generate")
async def generate_datasets(request: DatasetGenerationRequest, background_tasks: BackgroundTasks):
    """Generate training datasets"""
    
    def run_generation():
        """Background task to generate datasets"""
        try:
            script_path = Path(__file__).parent.parent.parent / "generate_training_datasets.py"
            if not script_path.exists():
                raise FileNotFoundError(f"Dataset generation script not found: {script_path}")
            
            # Run dataset generation script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Dataset generation failed: {result.stderr}")
            
            print("✅ Dataset generation completed!")
            print(result.stdout)
            
        except Exception as e:
            print(f"❌ Dataset generation error: {str(e)}")
    
    # Check if datasets already exist
    training_data_dir = Path(__file__).parent.parent.parent / "training_data"
    
    if training_data_dir.exists() and not request.force_regenerate:
        return {
            "success": False,
            "message": "Datasets already exist. Set force_regenerate=true to regenerate.",
            "data_dir": str(training_data_dir)
        }
    
    # Start generation in background
    background_tasks.add_task(run_generation)
    
    return {
        "success": True,
        "message": "Dataset generation started in background",
        "estimated_time": "5-10 minutes",
        "output_dir": str(training_data_dir)
    }


@router.get("/datasets/status")
async def get_dataset_status():
    """Check if training datasets are available"""
    training_data_dir = Path(__file__).parent.parent.parent / "training_data"
    
    datasets = {
        "pest_detection": training_data_dir / "pest_detection",
        "disease_detection": training_data_dir / "disease_detection",
        "storage_assessment": training_data_dir / "storage_assessment",
        "soil_diagnostics": training_data_dir / "soil_diagnostics",
        "plant_health": training_data_dir / "plant_health",
        "climate_prediction": training_data_dir / "climate_prediction" / "climate_timeseries.csv",
        "yield_prediction": training_data_dir / "yield_prediction" / "yield_prediction.csv"
    }
    
    status = {}
    for name, path in datasets.items():
        if path.exists():
            if path.is_dir():
                # Count images
                num_images = sum(1 for _ in path.rglob("*.png"))
                status[name] = {
                    "available": True,
                    "type": "image_dataset",
                    "num_images": num_images,
                    "path": str(path)
                }
            else:
                # CSV file
                status[name] = {
                    "available": True,
                    "type": "csv_dataset",
                    "size_mb": path.stat().st_size / (1024 * 1024),
                    "path": str(path)
                }
        else:
            status[name] = {
                "available": False,
                "type": "unknown",
                "message": "Dataset not generated yet"
            }
    
    all_available = all(s["available"] for s in status.values())
    
    return {
        "success": True,
        "all_datasets_ready": all_available,
        "datasets": status,
        "checked_at": datetime.now().isoformat()
    }


# ===================================
# MODEL TRAINING ENDPOINTS
# ===================================

def train_model_background(model_type: str, epochs: int):
    """Background task for model training"""
    try:
        ml_service.train_model(model_type, epochs=epochs)
    except Exception as e:
        print(f"❌ Training error: {str(e)}")


@router.post("/train")
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Start model training"""
    
    # Check if already training
    status = ml_service.get_status()
    if status["is_training"]:
        return {
            "success": False,
            "message": "Training already in progress",
            "current_model": status["current_model"],
            "progress": status["progress"]
        }
    
    # Validate model type
    valid_types = ["pest_detection", "disease_detection", "soil_diagnostics", 
                   "yield_prediction", "climate_prediction"]
    if request.model_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_type. Must be one of: {valid_types}"
        )
    
    # Check if datasets exist
    training_data_dir = Path(__file__).parent.parent.parent / "training_data"
    if not training_data_dir.exists():
        return {
            "success": False,
            "message": "Training datasets not found. Generate datasets first using /api/ml/datasets/generate",
            "action_required": "generate_datasets"
        }
    
    # Start training in background
    background_tasks.add_task(train_model_background, request.model_type, request.epochs)
    
    return {
        "success": True,
        "message": f"Training started for {request.model_type}",
        "model_type": request.model_type,
        "epochs": request.epochs,
        "started_at": datetime.now().isoformat()
    }


@router.get("/training/status")
async def get_training_status():
    """Get current training status"""
    status = ml_service.get_status()
    return {
        "success": True,
        "status": status,
        "checked_at": datetime.now().isoformat()
    }


@router.get("/training/history")
async def get_training_history(model_type: Optional[str] = None):
    """Get training history"""
    history = ml_service.get_history(model_type)
    return {
        "success": True,
        "history": history,
        "total_runs": len(history),
        "retrieved_at": datetime.now().isoformat()
    }


# ===================================
# MODEL MANAGEMENT ENDPOINTS
# ===================================

@router.get("/models")
async def get_available_models():
    """Get list of trained models"""
    models = ml_service.get_available_models()
    
    return {
        "success": True,
        "models": models,
        "total_models": len(models),
        "retrieved_at": datetime.now().isoformat()
    }


@router.get("/models/{model_name}/info")
async def get_model_info(model_name: str):
    """Get detailed information about a specific model"""
    models = ml_service.get_available_models()
    
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
    
    # Get training history for this model
    model_type = model_name.replace("_model", "")
    history = ml_service.get_history(model_type)
    
    # Get latest training results
    latest_training = history[-1] if history else None
    
    return {
        "success": True,
        "model": models[model_name],
        "latest_training": latest_training,
        "training_runs": len(history),
        "retrieved_at": datetime.now().isoformat()
    }


@router.get("/models/summary")
async def get_models_summary():
    """Get summary of all models and their performance"""
    models = ml_service.get_available_models()
    history = ml_service.get_history()
    
    summary = {}
    for model_name in models:
        model_type = model_name.replace("_model", "")
        model_history = [h for h in history if h["model_type"] == model_type]
        
        if model_history:
            latest = model_history[-1]["results"]
            summary[model_type] = {
                "model_file": models[model_name],
                "performance": {
                    "accuracy": latest.get("final_val_accuracy") or latest.get("test_r2"),
                    "trained_at": latest.get("trained_at"),
                    "training_samples": latest.get("training_samples") or latest.get("test_samples")
                },
                "training_runs": len(model_history)
            }
    
    return {
        "success": True,
        "summary": summary,
        "total_models": len(summary),
        "retrieved_at": datetime.now().isoformat()
    }


# ===================================
# UTILITY ENDPOINTS
# ===================================

@router.get("/health")
async def health_check():
    """Check ML service health"""
    try:
        import tensorflow as tf
        has_tf = True
        tf_version = tf.__version__
    except:
        has_tf = False
        tf_version = None
    
    try:
        import sklearn
        has_sklearn = True
        sklearn_version = sklearn.__version__
    except:
        has_sklearn = False
        sklearn_version = None
    
    return {
        "success": True,
        "service": "ML Training Service",
        "dependencies": {
            "tensorflow": {
                "installed": has_tf,
                "version": tf_version
            },
            "scikit_learn": {
                "installed": has_sklearn,
                "version": sklearn_version
            }
        },
        "status": "healthy" if (has_tf and has_sklearn) else "degraded",
        "checked_at": datetime.now().isoformat()
    }


@router.get("/model-types")
async def get_model_types():
    """Get information about available model types"""
    return {
        "success": True,
        "model_types": {
            "pest_detection": {
                "description": "Identifies pest types in crop images",
                "input": "RGB image (224x224)",
                "output": "7 pest classes + healthy",
                "algorithm": "MobileNetV3 + Transfer Learning",
                "dataset_size": "1,050 images"
            },
            "disease_detection": {
                "description": "Detects plant diseases from leaf images",
                "input": "RGB image (224x224)",
                "output": "7 disease classes + healthy",
                "algorithm": "MobileNetV3 + Transfer Learning",
                "dataset_size": "1,050 images"
            },
            "soil_diagnostics": {
                "description": "Classifies soil type from images",
                "input": "RGB image (224x224)",
                "output": "6 soil types",
                "algorithm": "Custom CNN",
                "dataset_size": "720 images"
            },
            "yield_prediction": {
                "description": "Predicts crop yield based on environmental factors",
                "input": "14 features (soil, climate, practices)",
                "output": "Yield in tons/hectare",
                "algorithm": "Random Forest Regression",
                "dataset_size": "1,000 records"
            },
            "climate_prediction": {
                "description": "Forecasts temperature 7 days ahead",
                "input": "30-day historical weather data",
                "output": "7-day temperature forecast",
                "algorithm": "LSTM Neural Network",
                "dataset_size": "730 daily records"
            }
        }
    }
