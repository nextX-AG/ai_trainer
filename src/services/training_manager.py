from typing import Dict, Optional
import json
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TrainingManager:
    def __init__(self):
        self.active_trainings: Dict[str, Dict] = {}
        self.status_dir = Path("data/training_status")
        self.status_dir.mkdir(parents=True, exist_ok=True)
        
    def start_training(self, project_id: str, config: dict) -> dict:
        """Startet ein neues Training"""
        status = {
            "project_id": project_id,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "current_epoch": 0,
            "total_epochs": config.get("epochs", 100),
            "current_loss": None,
            "best_loss": float("inf"),
            "last_update": datetime.now().isoformat()
        }
        
        self.active_trainings[project_id] = status
        self._save_status(project_id, status)
        return status
        
    def update_progress(self, project_id: str, epoch: int, loss: float):
        """Aktualisiert den Trainingsfortschritt"""
        if project_id not in self.active_trainings:
            return
            
        status = self.active_trainings[project_id]
        status["current_epoch"] = epoch
        status["current_loss"] = loss
        status["last_update"] = datetime.now().isoformat()
        
        if loss < status["best_loss"]:
            status["best_loss"] = loss
            
        self._save_status(project_id, status)
        
    def get_status(self, project_id: str) -> Optional[dict]:
        """Gibt den aktuellen Trainingsstatus zurück"""
        return self.active_trainings.get(project_id)
        
    def _save_status(self, project_id: str, status: dict):
        """Speichert den Status in einer Datei"""
        status_file = self.status_dir / f"{project_id}_status.json"
        with status_file.open("w") as f:
            json.dump(status, f, indent=2) 