import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path
from sqlalchemy.orm import Session
from src.utils.db import get_db
from supabase import Client
from src.database import get_db as supabase_get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routes import projects, scenes, training
from .routes import datasets, models
from .views import projects as project_views, training as training_views
from .views import datasets as dataset_views
from .views import models as model_views

# Logging Konfiguration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statische Dateien und Templates einbinden
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")
templates = Jinja2Templates(directory="src/api/templates")

# API Routen
app.include_router(projects.router, prefix="/api", tags=["api"])
app.include_router(scenes.router, prefix="/api", tags=["api"])
app.include_router(training.router, prefix="/api", tags=["api"])
app.include_router(datasets.router, prefix="/api", tags=["api"])
app.include_router(models.router, prefix="/api", tags=["api"])

# View Routen
app.include_router(project_views.router, tags=["views"])
app.include_router(training_views.router, tags=["views"])
app.include_router(dataset_views.router, tags=["views"])
app.include_router(model_views.router, tags=["views"])

class SearchRequest(BaseModel):
    keyword: str

class DownloadRequest(BaseModel):
    videoId: str

@app.post("/api/projects/{project_id}/search")
async def search_videos(project_id: str, request: SearchRequest):
    try:
        # TODO: Implementiere Videosuche
        return {"results": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects/{project_id}/download")
async def download_video(
    project_id: str, 
    request: DownloadRequest,
    db: Client = Depends(supabase_get_db)
):
    try:
        # Erstelle neuen Download-Eintrag in Supabase
        data = {
            "id": generate_download_id(),
            "project_id": project_id,
            "url": request.videoId,
            "status": "pending",
            "progress": 0.0,
            "metadata": {}
        }
        
        result = db.table("downloads").insert(data).execute()
        
        return {"downloadId": data["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/download/{download_id}/progress")
async def get_download_progress(project_id: str, download_id: str):
    try:
        # TODO: Implementiere Download-Progress
        return {"progress": 0, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-logging")
async def test_logging():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    return {"message": "Check the logs"} 