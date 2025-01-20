from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def index():
    """Leitet von der Root-URL zu /projects weiter"""
    logger.debug("Redirecting from / to /projects")
    # Nur status_code=302 für temporäre Weiterleitung
    return RedirectResponse(url="/projects", status_code=302) 