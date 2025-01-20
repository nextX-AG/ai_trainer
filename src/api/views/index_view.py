from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.project_service import ProjectService
from src.services.model_service import ModelService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")
project_service = ProjectService()
model_service = ModelService()

@router.get("/")
async def index(request: Request):
    """Rendert die Overview/Dashboard Seite"""
    try:
        # Statistiken sammeln
        projects = project_service.list_projects()
        projects_data = projects.data if hasattr(projects, 'data') else projects
        
        models = model_service.list_models()
        models_data = models.data if hasattr(models, 'data') else models

        stats = {
            "projects_count": len(projects_data),
            "models_count": len(models_data),
            "datasets_count": 0  # TODO: Implementieren wenn Dataset-Service verfügbar
        }

        # Beispiel für Aktivitäten (später durch echte Daten ersetzen)
        activities = [
            {
                "description": "Neues Projekt erstellt: Test Projekt",
                "timestamp": "Vor 2 Stunden",
                "type": "project"
            },
            {
                "description": "Model SimSwap v1.0 hochgeladen",
                "timestamp": "Vor 3 Stunden",
                "type": "model"
            }
        ]

        return templates.TemplateResponse(
            "overview.html",
            {
                "request": request,
                "stats": stats,
                "activities": activities,
                "debug": True,
                "show_debug_info": False
            }
        )
    except Exception as e:
        logger.error(f"ERROR in index_page: {str(e)}")
        raise 