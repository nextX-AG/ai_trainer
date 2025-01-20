import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class EnhancementConfig:
    denoise_strength: float = 10.0
    sharpen_strength: float = 0.5
    brightness_correction: bool = True
    contrast_correction: bool = True
    color_correction: bool = True
    stabilization: bool = True
    frame_interpolation: bool = True

class VideoEnhancer:
    def __init__(self, project_id: str, config: EnhancementConfig):
        self.project_id = project_id
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def enhance_video(self, input_path: Path, output_path: Path, problem_frames: List[int]) -> Dict:
        """Verbessert die Videoqualität"""
        try:
            cap = cv2.VideoCapture(str(input_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Initialisiere VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Stabilisierung vorbereiten
            if self.config.stabilization:
                stabilizer = cv2.VideoStabilizer_create()
            
            frame_buffer = []
            enhanced_count = 0
            
            with ThreadPoolExecutor() as executor:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    # Verarbeite Frame in separatem Thread
                    future = executor.submit(
                        self._enhance_frame, 
                        frame, 
                        frame_buffer if self.config.stabilization else None
                    )
                    enhanced_frame = future.result()
                    
                    if self.config.stabilization:
                        frame_buffer.append(enhanced_frame)
                        if len(frame_buffer) > 30:  # Puffergröße begrenzen
                            frame_buffer.pop(0)
                    
                    out.write(enhanced_frame)
                    enhanced_count += 1
                    
            cap.release()
            out.release()
            
            return {
                "status": "success",
                "frames_enhanced": enhanced_count,
                "output_path": str(output_path)
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Videoverbesserung: {str(e)}")
            raise

    def _enhance_frame(self, frame: np.ndarray, frame_buffer: Optional[List[np.ndarray]] = None) -> np.ndarray:
        """Verbessert ein einzelnes Frame"""
        enhanced = frame.copy()
        
        # Rauschunterdrückung
        if self.config.denoise_strength > 0:
            enhanced = cv2.fastNlMeansDenoisingColored(
                enhanced,
                None,
                self.config.denoise_strength,
                self.config.denoise_strength,
                7,
                21
            )
        
        # Schärfung
        if self.config.sharpen_strength > 0:
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]]) * self.config.sharpen_strength
            enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        # Helligkeits- und Kontrastkorrektur
        if self.config.brightness_correction or self.config.contrast_correction:
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            if self.config.brightness_correction:
                # CLAHE auf L-Kanal
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                l = clahe.apply(l)
            
            if self.config.contrast_correction:
                # Kontraststeigerung
                l = cv2.normalize(l, None, 0, 255, cv2.NORM_MINMAX)
            
            enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        
        # Farbkorrektur
        if self.config.color_correction:
            enhanced = self._correct_colors(enhanced)
        
        # Stabilisierung
        if self.config.stabilization and frame_buffer:
            enhanced = self._stabilize_frame(enhanced, frame_buffer)
        
        return enhanced

    def _correct_colors(self, frame: np.ndarray) -> np.ndarray:
        """Korrigiert Farben im Frame"""
        # Automatische Weißbalance
        result = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
        return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

    def _stabilize_frame(self, frame: np.ndarray, frame_buffer: List[np.ndarray]) -> np.ndarray:
        """Stabilisiert ein Frame basierend auf vorherigen Frames"""
        if len(frame_buffer) < 2:
            return frame
            
        # Berechne Bewegung zwischen Frames
        prev_frame = frame_buffer[-1]
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, 
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Bewegungskompensation
        h, w = frame.shape[:2]
        map_x = np.float32(np.meshgrid(np.arange(w), np.arange(h))[0])
        map_y = np.float32(np.meshgrid(np.arange(w), np.arange(h))[1])
        map_x += flow[:,:,0]
        map_y += flow[:,:,1]
        
        return cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR) 