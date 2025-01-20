from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.services.project_service import ProjectService

router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")
project_service = ProjectService()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Hauptseite (redirected zu Projekte)"""
    return RedirectResponse(url="/projects")

@router.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    # Hole alle aktiven Projekte
    projects = project_service.list_projects(status="active")
    
    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request,
            "projects": projects
        }
    ) 