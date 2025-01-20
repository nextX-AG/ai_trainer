from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.model_service import ModelService
from src.services.project_service import ProjectService
import logging

logger = logging.getLogger(__name__)

# Router mit explizitem Prefix
router = APIRouter(prefix="")  # Stellt sicher, dass die Route unter /models erreichbar ist
templates = Jinja2Templates(directory="src/api/templates")

model_service = ModelService()
project_service = ProjectService()

@router.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """Rendert die Models-Übersichtsseite"""
    logger.info("=== DEBUG: Models View Start ===")
    try:
        # Models abrufen
        logger.info("1. Calling model_service.list_models()")
        models = model_service.list_models()
        logger.info(f"2. Got models response: {models}")
        
        # Hier ist der wichtige Teil - wir müssen sicherstellen, dass wir die Daten korrekt extrahieren
        if isinstance(models, list):
            models_data = models
        else:
            models_data = models.data if hasattr(models, 'data') else models
        logger.info(f"3. Final models_data for template: {models_data}")
        
        # Projects abrufen
        logger.info("4. Calling project_service.list_projects()")
        projects = project_service.list_projects()
        projects_data = projects.data if hasattr(projects, 'data') else projects
        
        # Debug-Ausgabe im Template aktivieren
        return templates.TemplateResponse(
            "models.html",
            {
                "request": request,
                "models": models_data,
                "projects": projects_data,
                "debug": True  # Aktiviert Debug-Ausgabe im Template
            }
        )
    except Exception as e:
        logger.error(f"ERROR in models_page: {str(e)}")
        raise 

@router.get("/models-test")
async def models_test():
    logger.info("Models test route called")
    return {"message": "Models view is working"} 