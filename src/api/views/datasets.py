from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.dataset_service import DatasetService
from src.services.project_service import ProjectService

router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")

dataset_service = DatasetService()
project_service = ProjectService()

@router.get("/datasets", response_class=HTMLResponse)
async def datasets_page(request: Request):
    """Rendert die Datasets-Übersichtsseite"""
    # Debug-Ausgabe hinzufügen
    datasets = dataset_service.list_datasets()
    print("Gefundene Datasets:", datasets)  # Debug-Print
    
    return templates.TemplateResponse(
        "datasets.html",
        {
            "request": request,
            "datasets": datasets.data if hasattr(datasets, 'data') else datasets,  # Supabase Response handling
            "projects": project_service.list_projects().data
        }
    ) 