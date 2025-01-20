from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")

@router.get("/scraping", response_class=HTMLResponse)
async def scraping_page(request: Request):
    """Rendert die Scraping-Konfigurationsseite"""
    try:
        return templates.TemplateResponse(
            "scraping.html",
            {
                "request": request,
                "debug": True,
                "show_debug_info": False
            }
        )
    except Exception as e:
        logger.error(f"ERROR in scraping_page: {str(e)}")
        raise 