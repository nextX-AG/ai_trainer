from pathlib import Path
import subprocess
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.config import FaceSwapConfig
import json
import asyncio

@dataclass
class DFLPaths:
    workspace: Path
    source: Path
    target: Path
    aligned: Path
    models: Path
    merged: Path

class DeepFaceLabIntegration:
    def __init__(self, project_id: str, config: Optional[Dict] = None):
        self.project_id = project_id
        self.config = config or {}
        self.workspace_path = Path(f"data/projects/{project_id}/deepfacelab")
        self.dfl_path = Path("external/DeepFaceLab")
        self.logger = logging.getLogger(__name__)
        self.paths = self._initialize_paths()
        
    def _initialize_paths(self) -> DFLPaths:
        """Initialisiert die DeepFaceLab Verzeichnisstruktur"""
        base_path = Path(f"projects/{self.project_id}/deepfacelab")
        return DFLPaths(
            workspace=base_path,
            source=base_path / "workspace" / "data_src",
            target=base_path / "workspace" / "data_dst",
            aligned=base_path / "workspace" / "aligned",
            models=base_path / "workspace" / "model",
            merged=base_path / "workspace" / "merged"
        )
        
    async def prepare_workspace(self):
        """Bereitet den Workspace für ein neues Projekt vor"""
        try:
            # Verzeichnisse erstellen
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            (self.workspace_path / "aligned").mkdir(exist_ok=True)
            (self.workspace_path / "models").mkdir(exist_ok=True)

            return {"status": "success", "workspace": str(self.workspace_path)}
        except Exception as e:
            self.logger.error(f"Workspace preparation failed: {e}")
            raise
            
    async def extract_faces(self, video_path: Path):
        """Extrahiert Gesichter aus dem Video"""
        try:
            output_dir = self.workspace_path / "aligned"
            cmd = [
                "python",
                str(self.dfl_path / "main.py"),
                "extract",
                "--input-dir", str(video_path.parent),
                "--output-dir", str(output_dir),
                "--detector", "s3fd",
                "--face-type", "full_face",
                "--debug-dir", str(self.workspace_path / "debug")
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Face extraction failed: {stderr.decode()}")

            # Zähle extrahierte Gesichter
            face_count = len(list(output_dir.glob("*.jpg")))
            return {
                "status": "success",
                "faces_extracted": face_count,
                "output_dir": str(output_dir)
            }

        except Exception as e:
            self.logger.error(f"Face extraction failed: {e}")
            raise
            
    async def train_model(self, model_name: str = "SAEHD", iterations: int = 100000):
        """Startet das Training des Models"""
        try:
            model_dir = self.workspace_path / "models" / model_name
            model_dir.mkdir(exist_ok=True)

            cmd = [
                "python",
                str(self.dfl_path / "main.py"),
                "train",
                "--training-data-src-dir", str(self.workspace_path / "aligned"),
                "--training-data-dst-dir", str(self.workspace_path / "aligned"),
                "--model-dir", str(model_dir),
                "--model", model_name,
                "--iterations", str(iterations)
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Training-Status in Datei speichern
            status_file = self.workspace_path / "training_status.json"
            status = {
                "model": model_name,
                "iterations": iterations,
                "status": "running",
                "current_iteration": 0
            }
            status_file.write_text(json.dumps(status))

            return {
                "status": "training_started",
                "model": model_name,
                "workspace": str(self.workspace_path)
            }

        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
            
    async def convert_video(self, input_video: Path, output_path: Path):
        """Konvertiert ein Video mit dem trainierten Model"""
        try:
            cmd = [
                "python",
                str(self.dfl_path / "main.py"),
                "convert",
                "--input-dir", str(input_video.parent),
                "--output-dir", str(output_path.parent),
                "--model-dir", str(self.workspace_path / "models" / "SAEHD"),
                "--converter", "SAEHD"
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Video conversion failed: {stderr.decode()}")

            return {
                "status": "success",
                "output_video": str(output_path)
            }

        except Exception as e:
            self.logger.error(f"Video conversion failed: {e}")
            raise
            
    def _run_dfl_command(self, command: str, args: Dict[str, Any] = None, async_mode: bool = False):
        """Führt ein DeepFaceLab Kommando aus"""
        dfl_script = self._get_dfl_script_path(command)
        cmd = [str(dfl_script)]
        
        if args:
            for key, value in args.items():
                cmd.extend([f"--{key}", str(value)])
                
        self.logger.info(f"Führe DFL Kommando aus: {' '.join(cmd)}")
        
        if async_mode:
            return subprocess.Popen(cmd)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"DFL Kommando fehlgeschlagen: {result.stderr}")
            return result
            
    def _get_dfl_script_path(self, command: str) -> Path:
        """Gibt den Pfad zum entsprechenden DFL-Script zurück"""
        # Hier müssen wir die korrekten Pfade zu den DFL-Skripten einsetzen
        script_map = {
            "init": "main.py",
            "extract": "extract.py",
            "train": "train.py",
            "convert": "convert.py"
        }
        return Path("deepfacelab") / script_map[command] 