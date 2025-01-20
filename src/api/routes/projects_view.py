from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from src.database.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
supabase = get_db()

@router.get("/projects", include_in_schema=False)
async def projects_list(request: Request):
    projects = supabase.table('projects').select("*").order('created_at', desc=True).execute()
    return templates.TemplateResponse("projects/index.html", {
        "request": request,
        "projects": projects.data
    })

@router.get("/projects/new", include_in_schema=False)
async def new_project(request: Request):
    return templates.TemplateResponse("projects/new.html", {"request": request})

@router.get("/projects/{project_id}", include_in_schema=False)
async def project_detail(request: Request, project_id: str):
    project = supabase.table('projects').select("*").eq('id', project_id).single().execute()
    scenes = supabase.table('scenes').select("*").eq('project_id', project_id).execute()
    return templates.TemplateResponse("projects/detail.html", {
        "request": request,
        "project": project.data,
        "scenes": scenes.data
    }) 