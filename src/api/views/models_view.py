from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.model_service import ModelService
from src.services.project_service import ProjectService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")
model_service = ModelService()
project_service = ProjectService()

@router.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """Rendert die Models-Übersichtsseite"""
    try:
        models = model_service.list_models()
        models_data = models.data if hasattr(models, 'data') else models
        
        projects = project_service.list_projects()
        projects_data = projects.data if hasattr(projects, 'data') else projects
        
        return templates.TemplateResponse(
            "models.html",
            {
                "request": request,
                "models": models_data,
                "projects": projects_data,
                "debug": True,  # Erstmal immer True für die Entwicklung
                "show_debug_info": False,  # Debug-Info standardmäßig ausgeschaltet
            }
        )
    except Exception as e:
        logger.error(f"ERROR in models_page: {str(e)}")
        raise 