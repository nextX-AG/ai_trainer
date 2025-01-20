from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import (
    projects, views, 
    projects_view, training_view, 
    datasets_view, models_view
)

app = FastAPI(title="AI Trainer API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion anpassen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routen
app.include_router(projects.router, prefix="/api", tags=["api"])

# Frontend Routen
app.include_router(views.router, tags=["views"])
app.include_router(projects_view.router, tags=["views"])
app.include_router(training_view.router, tags=["views"])
app.include_router(datasets_view.router, tags=["views"])
app.include_router(models_view.router, tags=["views"])

# Statische Dateien
app.mount("/static", StaticFiles(directory="src/api/static"), name="static") 