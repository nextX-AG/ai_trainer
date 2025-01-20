from fastapi import APIRouter, HTTPException, WebSocket, BackgroundTasks
from src.services.training_service import TrainingService
from src.services.training_manager import TrainingManager
from src.config import TrainingConfig
from pathlib import Path
import asyncio
import logging
from pydantic import BaseModel
from typing import Dict, Optional
from src.services.model_service import ModelService
from src.services.dataset_service import DatasetService

router = APIRouter()
logger = logging.getLogger(__name__)
training_manager = TrainingManager()
training_service = TrainingService()
model_service = ModelService()
dataset_service = DatasetService()

class TrainingConfig(BaseModel):
    dataset_id: str
    batch_size: int = 32
    epochs: int = 100
    learning_rate: float = 0.001

@router.post("/projects/{project_id}/train")
async def start_training(project_id: str, background_tasks: BackgroundTasks):
    """Startet das Training für ein Projekt"""
    try:
        config = TrainingConfig()
        service = TrainingService(config)
        
        # Training vorbereiten
        dataset_path = Path(f"data/projects/{project_id}/dataset")
        service.setup(dataset_path)
        
        # Training Status initialisieren
        status = training_manager.start_training(project_id, config.__dict__)
        
        # Training im Hintergrund starten
        background_tasks.add_task(train_project, project_id, service)
        
        return status
        
    except Exception as e:
        logger.error(f"Fehler beim Trainingsstart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def train_project(project_id: str, service: TrainingService):
    """Führt das Training durch"""
    try:
        for epoch in range(service.config.epochs):
            loss = await service.train_epoch()
            training_manager.update_progress(project_id, epoch, loss)
            
    except Exception as e:
        logger.error(f"Fehler während des Trainings: {str(e)}")
        training_manager.update_progress(project_id, -1, float("inf"))

@router.websocket("/projects/{project_id}/training/ws")
async def training_status_websocket(websocket: WebSocket, project_id: str):
    """WebSocket für Live-Updates des Trainingsfortschritts"""
    await websocket.accept()
    
    try:
        while True:
            status = training_manager.get_status(project_id)
            if status:
                await websocket.send_json(status)
            await asyncio.sleep(1)  # Update-Intervall
            
    except Exception as e:
        logger.error(f"WebSocket Fehler: {str(e)}")
    finally:
        await websocket.close()

@router.get("/projects/{project_id}/training/status")
async def get_training_status(project_id: str):
    """Gibt den aktuellen Training-Status zurück"""
    status = training_manager.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail="Training nicht gefunden")
    return status

@router.post("/models/{model_id}/train")
async def start_training_model(model_id: str, config: TrainingConfig):
    """Startet das Training für ein Model"""
    model = model_service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model nicht gefunden")
    
    dataset = dataset_service.get_dataset(config.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset nicht gefunden")
    
    training_job = training_service.create_training_job(
        model_id=model_id,
        dataset_id=config.dataset_id,
        parameters={
            "batch_size": config.batch_size,
            "epochs": config.epochs,
            "learning_rate": config.learning_rate
        }
    )
    
    # Hier würden wir das Training in einem Background-Task starten
    # TODO: Implementiere Background-Task für Training
    
    return training_job

@router.post("/models/{model_id}/train/stop")
async def stop_training_model(model_id: str):
    """Stoppt das Training für ein Model"""
    # TODO: Implementiere Training-Stop
    return {"status": "stopped"}

@router.get("/models/{model_id}/train/status")
async def get_training_status_model(model_id: str):
    """Holt den aktuellen Training-Status"""
    jobs = training_service.list_training_jobs(model_id=model_id)
    if not jobs:
        raise HTTPException(status_code=404, detail="Kein Training-Job gefunden")
    
    current_job = jobs[0]  # Nehme den neuesten Job
    return current_job 