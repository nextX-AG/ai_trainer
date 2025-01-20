from fastapi import APIRouter, UploadFile, File, HTTPException
from src.modules.faceswap.deepfacelab import DeepFaceLabIntegration
from pathlib import Path
import shutil
import asyncio
from src.modules.faceswap.dfl_client import DFLClient
from src.config import get_settings
from src.modules.faceswap.simswap_client import SimSwapClient

router = APIRouter()

settings = get_settings()
dfl_client = DFLClient(settings.DFL_SERVER_URL)
simswap = SimSwapClient()

@router.post("/projects/{project_id}/faceswap/prepare")
async def prepare_faceswap(project_id: str):
    """Bereitet die Faceswap-Umgebung vor"""
    try:
        dfl = DeepFaceLabIntegration(project_id)
        result = await dfl.prepare_workspace()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/faceswap/extract")
async def extract_faces(project_id: str, video: UploadFile = File(...)):
    """Extrahiert Gesichter aus dem Video"""
    try:
        # Video temporär speichern
        temp_path = Path(f"temp/{video.filename}")
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        dfl = DeepFaceLabIntegration(project_id)
        result = await dfl.extract_faces(temp_path)

        # Temporäre Datei löschen
        temp_path.unlink()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/faceswap/process")
async def process_video(
    project_id: str,
    source: UploadFile = File(...),
    target: UploadFile = File(...)
):
    """Verarbeitet ein Video mit SimSwap"""
    try:
        # Temporäre Pfade
        source_path = Path(f"temp/{source.filename}")
        target_path = Path(f"temp/{target.filename}")
        output_path = Path(f"data/projects/{project_id}/output_{target.filename}")
        
        # Dateien speichern
        with source_path.open("wb") as buffer:
            shutil.copyfileobj(source.file, buffer)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(target.file, buffer)
            
        # Video verarbeiten
        result = await simswap.process_video(
            source_path=source_path,
            target_path=target_path,
            output_path=output_path
        )
        
        # Cleanup
        source_path.unlink()
        target_path.unlink()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 