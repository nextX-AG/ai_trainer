from pathlib import Path
import json
import shutil
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ModelRegistry:
    def __init__(self):
        self.models_dir = Path("data/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def save_model(self, project_id: str, model_path: Path, metadata: dict) -> dict:
        """Speichert ein trainiertes Modell"""
        model_id = f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        target_dir = self.models_dir / model_id
        target_dir.mkdir(parents=True)
        
        # Modell kopieren
        target_path = target_dir / "model.pth"
        shutil.copy(model_path, target_path)
        
        # Metadata speichern
        metadata.update({
            "model_id": model_id,
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "model_path": str(target_path)
        })
        
        with (target_dir / "metadata.json").open("w") as f:
            json.dump(metadata, f, indent=2)
            
        return metadata
        
    def get_model(self, model_id: str) -> Optional[Dict]:
        """Lädt ein Modell und seine Metadata"""
        model_dir = self.models_dir / model_id
        if not model_dir.exists():
            return None
            
        with (model_dir / "metadata.json").open() as f:
            metadata = json.load(f)
            
        return metadata
        
    def list_models(self, project_id: Optional[str] = None) -> List[Dict]:
        """Listet alle verfügbaren Modelle"""
        models = []
        for model_dir in self.models_dir.iterdir():
            if not model_dir.is_dir():
                continue
                
            try:
                with (model_dir / "metadata.json").open() as f:
                    metadata = json.load(f)
                    
                if project_id and metadata["project_id"] != project_id:
                    continue
                    
                models.append(metadata)
            except Exception as e:
                logger.error(f"Fehler beim Laden von Modell {model_dir}: {e}")
                
        return sorted(models, key=lambda x: x["created_at"], reverse=True) 