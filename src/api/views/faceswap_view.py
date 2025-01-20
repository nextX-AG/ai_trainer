from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.model_service import ModelService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")
model_service = ModelService()

@router.get("/faceswap", response_class=HTMLResponse)
async def faceswap_page(request: Request):
    """Rendert die Face Swap Studio Seite"""
    try:
        # Alle Models laden und nach Typ filtern
        models = model_service.list_models()
        models_data = models.data if hasattr(models, 'data') else models
        
        # Nur SimSwap Models filtern
        simswap_models = [
            model for model in models_data 
            if model.get('type', '').lower() == 'simswap'
        ]
        
        return templates.TemplateResponse(
            "faceswap.html",
            {
                "request": request,
                "models": simswap_models,
                "debug": True,
                "show_debug_info": False
            }
        )
    except Exception as e:
        logger.error(f"ERROR in faceswap_page: {str(e)}")
        raise 