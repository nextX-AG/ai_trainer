import torch
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict
import logging
from src.models.simswap import SimSwap
from src.services.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

class InferenceService:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.model_id = None
        self.registry = ModelRegistry()
        
    async def load_model(self, model_id: str):
        """Lädt ein Modell aus der Registry"""
        if self.model_id == model_id:
            return
            
        metadata = self.registry.get_model(model_id)
        if not metadata:
            raise ValueError(f"Modell {model_id} nicht gefunden")
            
        self.model = SimSwap()
        state_dict = torch.load(metadata['model_path'], map_location=self.device)
        self.model.load_state_dict(state_dict['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        self.model_id = model_id
        
        logger.info(f"Modell {model_id} geladen")
        
    async def process_video(self, 
                          source_path: Path,
                          target_path: Path,
                          output_path: Path,
                          model_id: str) -> Dict:
        """Verarbeitet ein Video mit Face-Swapping"""
        try:
            # Modell laden
            await self.load_model(model_id)
            
            # Video öffnen
            cap = cv2.VideoCapture(str(target_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Output Video Writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Quellbild laden
            source_img = cv2.imread(str(source_path))
            source_img = cv2.cvtColor(source_img, cv2.COLOR_BGR2RGB)
            source_tensor = self.preprocess_image(source_img)
            
            frame_count = 0
            with torch.no_grad():
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    # Frame verarbeiten
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_tensor = self.preprocess_image(frame_rgb)
                    
                    # Face-Swap durchführen
                    output = self.model(source_tensor, frame_tensor)
                    output_frame = self.postprocess_image(output)
                    
                    # Frame speichern
                    out.write(cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR))
                    frame_count += 1
                    
                    if frame_count % 10 == 0:
                        logger.info(f"Verarbeitet: {frame_count}/{total_frames} Frames")
                    
            cap.release()
            out.release()
            
            return {
                "status": "success",
                "frames_processed": frame_count,
                "output_path": str(output_path)
            }
            
        except Exception as e:
            logger.error(f"Fehler bei der Videoverarbeitung: {str(e)}")
            raise
            
    def preprocess_image(self, img: np.ndarray) -> torch.Tensor:
        """Bereitet ein Bild für das Modell vor"""
        img = cv2.resize(img, (256, 256))
        img = img.astype(np.float32) / 127.5 - 1.0
        img = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
        return img.to(self.device)
        
    def postprocess_image(self, tensor: torch.Tensor) -> np.ndarray:
        """Konvertiert den Modell-Output zurück in ein Bild"""
        img = tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        img = ((img + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
        return img 