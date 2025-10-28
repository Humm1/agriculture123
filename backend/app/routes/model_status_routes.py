"""
ML Models Status API Routes
Provides information about available AI models and training data
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime

from app.services.model_manager import get_model_manager, get_system_status

router = APIRouter(prefix="/api/models", tags=["ML Models"])


@router.get("/status")
async def get_models_status():
    """
    Get status of all AI models
    
    Returns information about:
    - Available trained models
    - Loaded models
    - Training datasets
    - System configuration
    """
    try:
        status = get_system_status()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "models": status["models"],
            "training_data": status["training_data"],
            "paths": status["paths"],
            "summary": status["summary"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving model status: {str(e)}"
        )


@router.get("/list")
async def list_available_models():
    """List all available AI models with their details"""
    try:
        model_manager = get_model_manager()
        models = model_manager.list_available_models()
        
        return {
            "success": True,
            "total_models": len(models),
            "models": models
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing models: {str(e)}"
        )


@router.get("/{model_name}/info")
async def get_model_info(model_name: str):
    """Get detailed information about a specific model"""
    try:
        model_manager = get_model_manager()
        
        config = model_manager.get_model_config(model_name)
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Model not found: {model_name}"
            )
        
        # Check if model is available
        is_available = config["path"].exists()
        is_loaded = model_name in model_manager.models
        
        # Get class mapping if available
        classes = model_manager.get_class_mapping(model_name)
        
        return {
            "success": True,
            "model_name": model_name,
            "available": is_available,
            "loaded": is_loaded,
            "type": config["type"],
            "description": config["description"],
            "input_shape": config.get("input_shape"),
            "classes": classes if classes else None,
            "num_classes": len(classes) if classes else None,
            "path": str(config["path"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving model info: {str(e)}"
        )


@router.post("/{model_name}/load")
async def load_model(model_name: str):
    """Manually load a specific model into memory"""
    try:
        model_manager = get_model_manager()
        
        model = model_manager.get_model(model_name)
        
        if model is None:
            raise HTTPException(
                status_code=404,
                detail=f"Model not found or failed to load: {model_name}"
            )
        
        return {
            "success": True,
            "message": f"Model {model_name} loaded successfully",
            "model_name": model_name,
            "type": model_manager.get_model_config(model_name)["type"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading model: {str(e)}"
        )


@router.post("/{model_name}/unload")
async def unload_model(model_name: str):
    """Unload a model from memory"""
    try:
        model_manager = get_model_manager()
        model_manager.unload_model(model_name)
        
        return {
            "success": True,
            "message": f"Model {model_name} unloaded successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error unloading model: {str(e)}"
        )


@router.get("/training-data/status")
async def get_training_data_status():
    """Get information about available training datasets"""
    try:
        model_manager = get_model_manager()
        data_info = model_manager.get_training_data_info()
        
        return {
            "success": True,
            "synthetic_data": data_info["synthetic_data"],
            "public_data": data_info["public_data"],
            "total_datasets": data_info["total_datasets"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving training data status: {str(e)}"
        )


@router.get("/health")
async def models_health_check():
    """Health check for ML models system"""
    try:
        model_manager = get_model_manager()
        status = model_manager.get_system_status()
        
        total_configured = status["summary"]["total_models_configured"]
        total_available = status["summary"]["total_models_available"]
        
        health_status = "healthy" if total_available >= total_configured * 0.5 else "degraded"
        
        return {
            "success": True,
            "status": health_status,
            "models_available": f"{total_available}/{total_configured}",
            "system_ready": total_available > 0,
            "message": "ML models system operational" if total_available > 0 else "No models available - run training"
        }
    
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": str(e)
        }
