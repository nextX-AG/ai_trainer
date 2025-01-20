from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.services.model_service import ModelService
from src.services.dataset_service import DatasetService
from src.services.training_service import TrainingService

router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")

model_service = ModelService()
dataset_service = DatasetService()
training_service = TrainingService()

@router.get("/training", response_class=HTMLResponse)
async def training_overview(request: Request):
    """Zeigt die Training-Übersichtsseite"""
    models = model_service.list_models()
    return templates.TemplateResponse(
        "training_overview.html",
        {
            "request": request,
            "models": models
        }
    )

@router.get("/training/{model_id}", response_class=HTMLResponse)
async def training_detail(request: Request, model_id: str):
    """Zeigt die Detail-Trainingsseite für ein Model"""
    model = model_service.get_model(model_id)
    if not model:
        return RedirectResponse(url="/training")
    
    # Hole alle Datasets für das Projekt
    datasets = dataset_service.list_datasets(project_id=model.get('project_id'))
    
    # Hole den aktuellen/letzten Training Job
    training_jobs = training_service.list_training_jobs(model_id=model_id)
    current_job = training_jobs[0] if training_jobs else None
    
    return templates.TemplateResponse(
        "training.html",
        {
            "request": request,
            "model": model,
            "datasets": datasets,
            "training_job": current_job
        }
    ) 