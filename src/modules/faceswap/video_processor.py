import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class VideoMetadata:
    fps: float
    total_frames: int
    width: int
    height: int
    duration: float
    codec: str

@dataclass
class ProcessingStats:
    frames_processed: int
    faces_detected: int
    avg_face_size: Tuple[int, int]
    quality_score: float
    problem_frames: List[int]

class VideoProcessor:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
        
    async def analyze_video(self, video_path: Path) -> Dict:
        """Analysiert ein Video für die Verarbeitung"""
        try:
            metadata = self._get_video_metadata(video_path)
            stats = await self._analyze_frames(video_path, metadata)
            
            recommendations = self._generate_recommendations(metadata, stats)
            
            return {
                "metadata": metadata,
                "stats": stats,
                "recommendations": recommendations,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Fehler bei Videoanalyse: {str(e)}")
            raise

    def _get_video_metadata(self, video_path: Path) -> VideoMetadata:
        """Extrahiert Metadaten aus dem Video"""
        cap = cv2.VideoCapture(str(video_path))
        
        return VideoMetadata(
            fps=cap.get(cv2.CAP_PROP_FPS),
            total_frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            duration=cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            codec=self._get_codec_info(cap)
        )

    async def _analyze_frames(self, video_path: Path, metadata: VideoMetadata) -> ProcessingStats:
        """Analysiert die Einzelbilder des Videos"""
        cap = cv2.VideoCapture(str(video_path))
        face_sizes = []
        problem_frames = []
        faces_detected = 0
        
        with ThreadPoolExecutor() as executor:
            frame_number = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Analysiere Frame in separatem Thread
                future = executor.submit(self._process_frame, frame, frame_number)
                result = future.result()
                
                if result["faces"]:
                    faces_detected += len(result["faces"])
                    face_sizes.extend([face.shape[:2] for face in result["faces"]])
                
                if result["problems"]:
                    problem_frames.append(frame_number)
                    
                frame_number += 1
                
        avg_face_size = tuple(np.mean(face_sizes, axis=0).astype(int)) if face_sizes else (0, 0)
        
        return ProcessingStats(
            frames_processed=frame_number,
            faces_detected=faces_detected,
            avg_face_size=avg_face_size,
            quality_score=self._calculate_quality_score(metadata, faces_detected, problem_frames),
            problem_frames=problem_frames
        )

    def _process_frame(self, frame: np.ndarray, frame_number: int) -> Dict:
        """Verarbeitet ein einzelnes Frame"""
        problems = []
        faces = []
        
        # Prüfe Bildqualität
        blur_score = cv2.Laplacian(frame, cv2.CV_64F).var()
        if blur_score < 100:
            problems.append(f"Frame {frame_number}: Unscharf (Score: {blur_score:.2f})")
            
        # Prüfe Belichtung
        brightness = np.mean(frame)
        if brightness < 40 or brightness > 215:
            problems.append(f"Frame {frame_number}: Schlechte Belichtung ({brightness:.2f})")
            
        # Gesichtserkennung
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        detected_faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in detected_faces:
            face_img = frame[y:y+h, x:x+w]
            faces.append(face_img)
            
        return {
            "faces": faces,
            "problems": problems
        }

    def _calculate_quality_score(self, metadata: VideoMetadata, faces_detected: int, problem_frames: List[int]) -> float:
        """Berechnet einen Qualitätsscore für das Video"""
        expected_faces = metadata.total_frames  # Erwarten ein Gesicht pro Frame
        face_detection_rate = faces_detected / expected_faces
        problem_rate = len(problem_frames) / metadata.total_frames
        
        # Gewichtete Berechnung
        score = (
            0.5 * face_detection_rate +  # 50% Gesichtserkennung
            0.3 * (1 - problem_rate) +   # 30% Problemfreie Frames
            0.2 * (metadata.fps / 30)     # 20% FPS-Qualität
        )
        
        return min(max(score, 0.0), 1.0)  # Normalisiere auf 0-1

    def _generate_recommendations(self, metadata: VideoMetadata, stats: ProcessingStats) -> List[str]:
        """Generiert Empfehlungen basierend auf der Analyse"""
        recommendations = []
        
        if stats.quality_score < 0.6:
            recommendations.append("Video-Qualität könnte problematisch sein für gute Ergebnisse")
            
        if metadata.fps < 24:
            recommendations.append("Niedrige FPS könnten zu ruckligen Ergebnissen führen")
            
        if stats.avg_face_size[0] < 128 or stats.avg_face_size[1] < 128:
            recommendations.append("Gesichter sind relativ klein - höhere Auflösung empfohlen")
            
        if len(stats.problem_frames) > metadata.total_frames * 0.1:
            recommendations.append("Viele problematische Frames - Vorverarbeitung empfohlen")
            
        return recommendations

    def _get_codec_info(self, cap: cv2.VideoCapture) -> str:
        """Ermittelt den verwendeten Codec"""
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        return "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)]) 