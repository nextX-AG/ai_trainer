from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.model_service import ModelService
from src.services.dataset_service import DatasetService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")

model_service = ModelService()
dataset_service = DatasetService()

@router.get("/training", response_class=HTMLResponse)
async def training_page(request: Request):
    """Rendert die Training-Übersichtsseite"""
    logger.info("=== DEBUG: Training View Start ===")
    try:
        # Models und Datasets abrufen
        models = model_service.list_models()
        models_data = models.data if hasattr(models, 'data') else models
        
        datasets = dataset_service.list_datasets()
        datasets_data = datasets.data if hasattr(datasets, 'data') else datasets
        
        # Standardmäßig das erste Model auswählen, falls vorhanden
        selected_model = models_data[0] if models_data else {
            "id": None,
            "name": "Kein Model verfügbar",
            "version": "0.0"
        }
        
        return templates.TemplateResponse(
            "training.html",
            {
                "request": request,
                "models": models_data,
                "datasets": datasets_data,
                "model": selected_model,  # Das ausgewählte Model für die Anzeige
                "training_job": None,  # Hier später das aktuelle Training einfügen
                "debug": True
            }
        )
    except Exception as e:
        logger.error(f"ERROR in training_page: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 