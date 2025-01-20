import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import os
from src.api.routes import projects, inference, models
from src.api.views.projects_view import router as projects_view_router
from src.api.views.training_view import router as training_view_router
from src.api.views.datasets_view import router as datasets_view_router
from src.api.views.models_view import router as models_view_router
from src.api.views.settings_view import router as settings_view_router, Settings

# Verzeichnisse erstellen
Path("temp").mkdir(exist_ok=True)
Path("data/models").mkdir(parents=True, exist_ok=True)
Path("src/api/static/js").mkdir(parents=True, exist_ok=True)

# Lade Umgebungsvariablen
load_dotenv('.env.development')

# Überprüfe, ob die notwendigen Variablen gesetzt sind
if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
    raise Exception("SUPABASE_URL und SUPABASE_KEY müssen in .env.development gesetzt sein")

app = FastAPI(title="AI Trainer API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion anpassen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routen (mit /api prefix)
app.include_router(projects.router, prefix="/api", tags=["api"])
app.include_router(inference.router, prefix="/api", tags=["api"])
app.include_router(models.router, prefix="/api", tags=["api"])

# Frontend Routen (ohne prefix)
app.include_router(projects_view_router)
app.include_router(training_view_router)
app.include_router(datasets_view_router)
app.include_router(models_view_router)
app.include_router(settings_view_router)

# Statische Dateien
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

# Settings laden
settings = Settings.load()

# Logging konfigurieren
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if settings.debug_mode:
    logger.info("=== Debug Mode aktiviert ===")

@app.get("/debug-routes")
async def debug_routes():
    """Zeigt alle registrierten Routen"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": route.methods if hasattr(route, "methods") else None
        })
    return {"routes": routes}

@app.get("/test-logging")
async def test_logging():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    return {"message": "Check the logs"} 