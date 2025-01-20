from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import sys
import torch
import shutil
import asyncio
import logging

# SimSwap Pfad zum Python Path hinzufügen
sys.path.append("external/simswap")

from models.model import SimSwap
from utils.inference import process_video

app = FastAPI()
logger = logging.getLogger(__name__)

class SimSwapService:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.temp_dir = Path("/app/data/temp")
        self.output_dir = Path("/app/data/output")
        self.setup_dirs()
        
    def setup_dirs(self):
        """Erstellt benötigte Verzeichnisse"""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_model(self):
        if self.model is None:
            logger.info("Lade SimSwap Modell...")
            self.model = SimSwap()
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Modell geladen auf {self.device}")

service = SimSwapService()

@app.post("/swap")
async def swap_faces(
    source: UploadFile = File(...),
    target: UploadFile = File(...),
    job_id: str = None
):
    """Führt Face Swap durch"""
    try:
        # Modell laden falls noch nicht geschehen
        service.load_model()
        
        # Temporäre Dateien speichern
        source_path = service.temp_dir / f"source_{source.filename}"
        target_path = service.temp_dir / f"target_{target.filename}"
        output_path = service.output_dir / f"output_{job_id}_{target.filename}"
        
        with source_path.open("wb") as buffer:
            shutil.copyfileobj(source.file, buffer)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(target.file, buffer)
            
        # Face Swap durchführen
        process_video(
            service.model,
            str(target_path),
            str(output_path),
            str(source_path),
            crop_size=224,
            no_smooth=False
        )
        
        # Cleanup
        source_path.unlink()
        target_path.unlink()
        
        return {
            "status": "success",
            "job_id": job_id,
            "output_path": str(output_path)
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Face Swap: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Überprüft den Service-Status"""
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "device": str(service.device)
    } 