from pathlib import Path
import subprocess
import os
import logging
from typing import Dict, Any
from dataclasses import dataclass
from src.config import FaceSwapConfig

@dataclass
class DFLPaths:
    workspace: Path
    source: Path
    target: Path
    aligned: Path
    models: Path
    merged: Path

class DeepFaceLabIntegration:
    def __init__(self, project_id: str, config: FaceSwapConfig):
        self.project_id = project_id
        self.config = config
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
        """Bereitet den Arbeitsbereich vor"""
        try:
            # Erstelle Verzeichnisse
            for path in self.paths.__dict__.values():
                path.mkdir(parents=True, exist_ok=True)
                
            # Initialisiere DFL-Umgebung
            self._run_dfl_command("init")
            
            return {"status": "success", "message": "Workspace erfolgreich erstellt"}
        except Exception as e:
            self.logger.error(f"Fehler bei Workspace-Erstellung: {str(e)}")
            raise
            
    async def extract_faces(self, video_path: Path):
        """Extrahiert Gesichter aus dem Video"""
        try:
            # Kopiere Video in source/target Verzeichnis
            # Extrahiere Frames und Gesichter
            self._run_dfl_command("extract", {
                "input-dir": video_path,
                "output-dir": self.paths.source,
                "detector": "s3fd",
                "face-type": "whole_face",
                "max-faces-from-image": 1
            })
            
            return {"status": "success", "message": "Gesichter erfolgreich extrahiert"}
        except Exception as e:
            self.logger.error(f"Fehler bei Gesichtsextraktion: {str(e)}")
            raise
            
    async def train_model(self):
        """Startet das Training des Models"""
        try:
            # Konfiguriere und starte Training
            training_args = {
                "model-dir": self.paths.models,
                "model-name": "SAEHD",
                "batch-size": self.config.batch_size,
                "resolution": self.config.resolution,
                "iterations": self.config.iterations
            }
            
            # Starte Training-Prozess
            process = self._run_dfl_command("train", training_args, async_mode=True)
            
            return {
                "status": "training_started",
                "process_id": process.pid,
                "model_path": str(self.paths.models)
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Training: {str(e)}")
            raise
            
    async def convert_video(self, input_path: Path, output_path: Path, options: Dict[str, Any]):
        """Konvertiert ein Video mit dem trainierten Model"""
        try:
            conversion_args = {
                "input-dir": input_path,
                "output-dir": output_path,
                "model-dir": self.paths.models,
                "denoise-power": options.get("denoise_power", 0.4),
                "color-correction": options.get("color_correction", True),
                "face-alignment": options.get("face_alignment", True)
            }
            
            self._run_dfl_command("convert", conversion_args)
            
            return {
                "status": "success",
                "output_path": str(output_path)
            }
        except Exception as e:
            self.logger.error(f"Fehler bei Konvertierung: {str(e)}")
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