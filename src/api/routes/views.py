from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from src.database.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
supabase = get_db()

@router.get("/", include_in_schema=False)
async def overview(request: Request):
    # Hole Statistiken aus der Datenbank
    try:
        projects = supabase.table('projects').select("*").execute()
        scenes = supabase.table('scenes').select("*").execute()
        downloads = supabase.table('downloads').select("*").execute()
        
        stats = {
            "total_projects": len(projects.data),
            "total_scenes": len(scenes.data),
            "total_downloads": len(downloads.data),
            "recent_projects": projects.data[:5] if projects.data else []
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")  # Für Debugging
        stats = {
            "total_projects": 0,
            "total_scenes": 0,
            "total_downloads": 0,
            "recent_projects": []
        }
        
    return templates.TemplateResponse("overview.html", {
        "request": request,
        "stats": stats
    }) 