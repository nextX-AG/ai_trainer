from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from src.database.database import get_db
from pydantic import BaseModel
from enum import Enum
from src.services.project_service import ProjectService

router = APIRouter()
supabase = get_db()
project_service = ProjectService()

class SourceType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"

class DataSource(str, Enum):
    URL = "url"           # Direkte URLs
    PORNDB = "porndb"     # PornDB API
    SEARCH = "search"     # Suchfunktion

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner: str
    source_type: SourceType
    data_source: DataSource
    search_query: Optional[str] = None  # Für Suche
    source_urls: Optional[List[str]] = None  # Für direkte URLs
    porndb_config: Optional[Dict] = None  # Für PornDB-spezifische Einstellungen
    scraping_config: Optional[Dict] = {
        "min_duration": 10,
        "max_duration": 300,
        "quality": "720p",
        "categories": [],
        "limit": 100  # Maximale Anzahl zu scrapender Items
    }

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class SceneCreate(BaseModel):
    name: str
    description: str
    keywords: List[str]
    target_attributes: Dict

@router.post("/projects/")
async def create_project(project: ProjectCreate):
    return project_service.create_project(project.name, project.description)

@router.get("/projects/")
async def list_projects(status: Optional[str] = None):
    return project_service.list_projects(status)

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}")
async def update_project(project_id: str, project: ProjectUpdate):
    return project_service.update_project(project_id, project.dict(exclude_unset=True))

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    return project_service.delete_project(project_id)

@router.post("/projects/{project_id}/scenes")
async def create_scene(project_id: str, scene: SceneCreate):
    try:
        data = {
            "project_id": project_id,
            "name": scene.name,
            "description": scene.description,
            "keywords": scene.keywords,
            "target_attributes": scene.target_attributes
        }
        response = supabase.table('scenes').insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 