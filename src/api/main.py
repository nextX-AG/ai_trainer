from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path
from sqlalchemy.orm import Session
from src.utils.db import get_db
from supabase import Client
from src.database import get_db as supabase_get_db

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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