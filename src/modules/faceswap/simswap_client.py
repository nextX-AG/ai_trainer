import torch
from pathlib import Path
from typing import Optional, Dict
import cv2
import numpy as np
from simswap.models.model import SimSwap
from simswap.utils.inference import process_video
import aiohttp
import uuid

class SimSwapClient:
    def __init__(self, config: Optional[Dict] = None, base_url: str = "http://simswap:8000"):
        self.config = config or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.initialized = False
        self.base_url = base_url
        
    async def initialize(self):
        """Lädt das SimSwap Modell"""
        if not self.initialized:
            self.model = SimSwap()
            self.model.to(self.device)
            self.model.eval()
            self.initialized = True
            
    async def process_video(self, 
                          source_path: Path,
                          target_path: Path,
                          output_path: Path):
        """Verarbeitet ein Video mit SimSwap"""
        if not self.initialized:
            await self.initialize()
            
        try:
            # Gesicht aus Quellbild extrahieren
            source_img = cv2.imread(str(source_path))
            
            # Video verarbeiten
            process_video(
                self.model,
                str(target_path),
                str(output_path),
                source_img,
                crop_size=224,
                no_smooth=False
            )
            
            return {
                "status": "success",
                "output_path": str(output_path)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def extract_faces(self, video_path: Path, output_dir: Path):
        """Extrahiert Gesichter aus einem Video"""
        try:
            # Video öffnen
            cap = cv2.VideoCapture(str(video_path))
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Alle 30 Frames ein Gesicht extrahieren
                if frame_count % 30 == 0:
                    # Gesichtserkennung
                    faces = self.model.face_detector(frame)
                    
                    for i, face in enumerate(faces):
                        face_img = frame[face[1]:face[3], face[0]:face[2]]
                        output_path = output_dir / f"face_{frame_count}_{i}.jpg"
                        cv2.imwrite(str(output_path), face_img)
                        
                frame_count += 1
                
            cap.release()
            
            return {
                "status": "success",
                "faces_extracted": frame_count,
                "output_dir": str(output_dir)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def swap_faces(self, source_path: Path, target_path: Path) -> dict:
        """Sendet Anfrage an SimSwap Service"""
        job_id = str(uuid.uuid4())
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('source',
                          open(source_path, 'rb'),
                          filename=source_path.name)
            data.add_field('target',
                          open(target_path, 'rb'),
                          filename=target_path.name)
            data.add_field('job_id', job_id)
            
            async with session.post(f"{self.base_url}/swap", data=data) as response:
                return await response.json()
                
    async def check_health(self) -> dict:
        """Überprüft den Service-Status"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                return await response.json() 