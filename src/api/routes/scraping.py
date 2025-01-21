from fastapi import APIRouter, HTTPException
from typing import Dict
from src.services.scraping_service import ScrapingService

router = APIRouter()
scraping_service = ScrapingService()

@router.post("/scraping/start")
async def start_scraping(config: Dict):
    """Startet einen Scraping-Job"""
    try:
        return await scraping_service.start_scraping(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scraping/status/{job_id}")
async def get_job_status(job_id: str):
    """Gibt den Status eines Jobs zurück"""
    status = await scraping_service.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status 