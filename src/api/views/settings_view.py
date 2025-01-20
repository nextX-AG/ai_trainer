from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")

CONFIG_FILE = Path("config/settings.json")
CONFIG_FILE.parent.mkdir(exist_ok=True)

class Settings(BaseModel):
    debug_mode: bool = False
    log_level: str = "INFO"
    supabase_url: str = ""
    supabase_key: str = ""
    
    @classmethod
    def load(cls):
        if CONFIG_FILE.exists():
            return cls.parse_file(CONFIG_FILE)
        return cls()
    
    def save(self):
        CONFIG_FILE.write_text(self.json(indent=2))

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    settings = Settings.load()
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": settings,
            "log_levels": ["DEBUG", "INFO", "WARNING", "ERROR"]
        }
    )

@router.post("/settings")
async def update_settings(settings: Settings):
    settings.save()
    # Logging neu konfigurieren
    logging.getLogger().setLevel(settings.log_level)
    return {"status": "success"} 