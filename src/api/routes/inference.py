from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from src.services.inference_service import InferenceService
from pathlib import Path
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()
inference_service = InferenceService()

@router.post("/projects/{project_id}/inference")
async def run_inference(
    project_id: str,
    background_tasks: BackgroundTasks,
    source: UploadFile = File(...),
    target: UploadFile = File(...),
    model_id: str = None
):
    """Führt Face-Swapping auf einem Video durch"""
    try:
        if not model_id:
            raise HTTPException(status_code=400, detail="model_id ist erforderlich")
            
        # Temporäre Pfade
        source_path = Path(f"temp/{source.filename}")
        target_path = Path(f"temp/{target.filename}")
        output_path = Path(f"data/projects/{project_id}/output/result_{target.filename}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Dateien speichern
        with source_path.open("wb") as buffer:
            shutil.copyfileobj(source.file, buffer)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(target.file, buffer)
            
        # Inferenz im Hintergrund starten
        background_tasks.add_task(
            process_video_task,
            project_id=project_id,
            model_id=model_id,
            source_path=source_path,
            target_path=target_path,
            output_path=output_path
        )
        
        return {
            "status": "processing",
            "project_id": project_id,
            "output_path": str(output_path)
        }
        
    except Exception as e:
        logger.error(f"Fehler bei der Inferenz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_task(
    project_id: str,
    model_id: str,
    source_path: Path,
    target_path: Path,
    output_path: Path
):
    """Background Task für die Videoverarbeitung"""
    try:
        result = await inference_service.process_video(
            source_path=source_path,
            target_path=target_path,
            output_path=output_path,
            model_id=model_id
        )
        
        # Cleanup
        source_path.unlink()
        target_path.unlink()
        
        logger.info(f"Videoverarbeitung abgeschlossen: {result}")
        
    except Exception as e:
        logger.error(f"Fehler bei der Videoverarbeitung: {str(e)}")
        # Hier könnte man den Fehler in einer DB oder Queue speichern

@router.get("/projects/{project_id}/inference/{job_id}/status")
async def get_inference_status(project_id: str, job_id: str):
    """Gibt den Status eines Inferenz-Jobs zurück"""
    try:
        # TODO: Status aus DB/Queue abrufen
        return {
            "status": "processing",
            "progress": 0.5,
            "frames_processed": 100
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/inference/results")
async def list_inference_results(project_id: str):
    """Listet alle Inferenz-Ergebnisse eines Projekts"""
    try:
        output_dir = Path(f"data/projects/{project_id}/output")
        if not output_dir.exists():
            return []
            
        results = []
        for video_path in output_dir.glob("*.mp4"):
            results.append({
                "filename": video_path.name,
                "path": str(video_path),
                "created_at": video_path.stat().st_mtime
            })
            
        return sorted(results, key=lambda x: x["created_at"], reverse=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-faces")
async def detect_faces(image_data: dict):
    """Erkennt Gesichter in einem Bild"""
    try:
        # Hier die Gesichtserkennung implementieren
        # Beispiel-Response:
        return {
            "bbox": {
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 200
            },
            "landmarks": [
                {"x": 150, "y": 150},
                {"x": 250, "y": 150},
                # ... weitere Landmarks
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 