from fastapi import APIRouter, HTTPException
from typing import List, Dict
from src.database.database import get_db
from pydantic import BaseModel

router = APIRouter()
supabase = get_db()

class ProjectCreate(BaseModel):
    name: str
    description: str
    owner: str

class SceneCreate(BaseModel):
    name: str
    description: str
    keywords: List[str]
    target_attributes: Dict

@router.post("/projects/")
async def create_project(project: ProjectCreate):
    try:
        data = {
            "name": project.name,
            "description": project.description,
            "owner": project.owner,
            "status": "active"
        }
        response = supabase.table('projects').insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    response = supabase.table('projects').select("*").eq('id', project_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Project not found")
    return response.data[0]

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

@router.get("/projects/")
async def list_projects():
    try:
        response = supabase.table('projects').select("*").order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 