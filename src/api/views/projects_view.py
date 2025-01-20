from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.project_service import ProjectService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")
project_service = ProjectService()

@router.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """Rendert die Projekte-Übersichtsseite"""
    logger.info("=== DEBUG: Projects View Start ===")
    try:
        # Projekte abrufen
        logger.info("1. Calling project_service.list_projects()")
        projects = project_service.list_projects()
        logger.info(f"2. Got projects response: {projects}")
        
        # Daten extrahieren
        projects_data = projects.data if hasattr(projects, 'data') else projects
        logger.info(f"3. Final projects_data for template: {projects_data}")
        
        # Template rendern
        return templates.TemplateResponse(
            "projects.html",
            {
                "request": request,
                "projects": projects_data,
                "debug": True  # Aktiviert Debug-Ausgabe im Template
            }
        )
    except Exception as e:
        logger.error(f"ERROR in projects_page: {str(e)}")
        raise 