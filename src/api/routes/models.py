from fastapi import APIRouter, HTTPException, UploadFile, File
from src.services.model_registry import ModelRegistry
from pathlib import Path
import shutil
from pydantic import BaseModel
from typing import Optional
from src.services.model_service import ModelService
import logging

router = APIRouter()
model_registry = ModelRegistry()
model_service = ModelService()

logger = logging.getLogger(__name__)

class ModelCreate(BaseModel):
    name: str
    project_id: str
    type: str
    version: Optional[str] = "1.0"

@router.post("/models/")
async def create_model(model: ModelCreate):
    return model_service.create_model(
        name=model.name,
        project_id=model.project_id,
        model_type=model.type,
        version=model.version
    )

@router.get("/models/")
async def list_models(project_id: Optional[str] = None):
    logger.debug("=== DEBUG: Models API Route ===")
    try:
        result = model_service.list_models(project_id)
        logger.info(f"Models found: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in list_models: {str(e)}")
        raise

@router.get("/models/{model_id}")
async def get_model(model_id: str):
    model = model_service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model nicht gefunden")
    return model

@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    return model_service.delete_model(model_id)

@router.post("/models/import")
async def import_model(
    project_id: str,
    model_file: UploadFile = File(...),
    metadata: dict = {}
):
    """Importiert ein vortrainiertes Modell"""
    try:
        # Temporär speichern
        temp_path = Path(f"temp/{model_file.filename}")
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(model_file.file, buffer)
            
        # In Registry speichern
        metadata = model_registry.save_model(project_id, temp_path, metadata)
        
        # Cleanup
        temp_path.unlink()
        
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 