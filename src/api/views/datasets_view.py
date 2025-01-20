from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.dataset_service import DatasetService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")
dataset_service = DatasetService()

@router.get("/datasets", response_class=HTMLResponse)
async def datasets_page(request: Request):
    datasets = dataset_service.list_datasets()
    datasets_data = datasets.data if hasattr(datasets, 'data') else datasets
    return templates.TemplateResponse(
        "datasets.html",
        {
            "request": request,
            "datasets": datasets_data,
            "debug": True
        }
    ) 