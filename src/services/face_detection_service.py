import cv2
import dlib
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

@dataclass
class FaceDetection:
    confidence: float
    box: Tuple[int, int, int, int]  # x, y, width, height
    keypoints: dict  # Gesichtsmerkmale
    size: Tuple[int, int]  # Breite, Höhe des Gesichts
    position: Tuple[int, int]  # x, y Position des Gesichts

class FaceDetectionService:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        logger.info("Face Detection Service initialized with dlib")
        
    def detect_faces(self, image: np.ndarray, min_confidence: float = 0.9) -> List[FaceDetection]:
        try:
            # Konvertiere zu Graustufen für dlib
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Gesichtserkennung
            faces = self.detector(gray)
            
            detections = []
            for face in faces:
                # Konfidenz aus dlib
                confidence = face.confidence() if hasattr(face, 'confidence') else 1.0
                
                if confidence >= min_confidence:
                    # Landmarks erkennen
                    shape = self.predictor(gray, face)
                    
                    # Box-Koordinaten
                    x = face.left()
                    y = face.top()
                    width = face.right() - face.left()
                    height = face.bottom() - face.top()
                    
                    # Keypoints extrahieren
                    keypoints = {}
                    for i in range(68):
                        point = shape.part(i)
                        keypoints[f"point_{i}"] = (point.x, point.y)
                    
                    detection = FaceDetection(
                        confidence=confidence,
                        box=(x, y, width, height),
                        keypoints=keypoints,
                        size=(width, height),
                        position=(x, y)
                    )
                    detections.append(detection)
            
            logger.info(f"Detected {len(detections)} faces")
            return detections
            
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            return []
    
    def extract_face(self, image: np.ndarray, face: FaceDetection, 
                    required_size: Tuple[int, int] = (224, 224)) -> Optional[np.ndarray]:
        """
        Extrahiert und skaliert ein erkanntes Gesicht
        
        Args:
            image: Original Bild
            face: Erkanntes Gesicht
            required_size: Gewünschte Ausgabegröße
            
        Returns:
            Skaliertes Gesichtsbild oder None bei Fehler
        """
        try:
            x, y, width, height = face.box
            
            # Füge Padding hinzu (20%)
            padding_x = int(width * 0.2)
            padding_y = int(height * 0.2)
            
            # Berechne neue Koordinaten mit Padding
            x1 = max(0, x - padding_x)
            y1 = max(0, y - padding_y)
            x2 = min(image.shape[1], x + width + padding_x)
            y2 = min(image.shape[0], y + height + padding_y)
            
            # Extrahiere Gesicht
            face_image = image[y1:y2, x1:x2]
            
            # Skaliere auf gewünschte Größe
            return cv2.resize(face_image, required_size)
            
        except Exception as e:
            logger.error(f"Error extracting face: {str(e)}")
            return None 