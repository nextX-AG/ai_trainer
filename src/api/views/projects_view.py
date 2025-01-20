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
async def projects_page(request: Request, show_modal: bool = False):
    """Rendert die Projekte-Übersichtsseite"""
    try:
        projects = project_service.list_projects()
        projects_data = projects.data if hasattr(projects, 'data') else projects
        
        return templates.TemplateResponse(
            "projects.html",
            {
                "request": request,
                "projects": projects_data,
                "debug": True,  # Erstmal immer True für die Entwicklung
                "show_debug_info": False,
            }
        )
    except Exception as e:
        logger.error(f"ERROR in projects_page: {str(e)}")
        raise 