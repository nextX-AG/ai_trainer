from src.base.module import BaseModule
from src.config import ProcessingConfig
import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
from PIL import Image
from mtcnn import MTCNN

class ProcessingModule(BaseModule):
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.face_detector = None
        
    def initialize(self):
        self.logger.info("Initialisiere Processing Modul")
        # Face Detection Model laden
        if self.config.face_detection_model == "mtcnn":
            self.face_detector = MTCNN()
        else:
            self.face_detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        
    def validate(self):
        self.config.validate()
        
    def execute(self, input_data: List[Path]) -> List[np.ndarray]:
        """
        Verarbeitet die eingegebenen Bilder
        
        Args:
            input_data: Liste von Pfaden zu Eingabebildern
            
        Returns:
            List[np.ndarray]: Verarbeitete Bilder
        """
        processed_images = []
        
        for image_path in input_data:
            try:
                # Bild laden und verarbeiten
                image = self._load_and_preprocess(image_path)
                
                # Gesichtserkennung durchführen
                faces = self._detect_faces(image)
                
                # Augmentation wenn aktiviert
                if self.config.augmentation_enabled:
                    faces = self._apply_augmentation(faces)
                    
                processed_images.extend(faces)
                
            except Exception as e:
                self.logger.error(f"Fehler bei der Verarbeitung von {image_path}: {str(e)}")
                continue
                
        return processed_images
        
    def cleanup(self):
        self.logger.info("Räume Processing Modul auf")
        # Ressourcen freigeben
        self.face_detector = None
        
    def _load_and_preprocess(self, image_path: Path) -> np.ndarray:
        """Lädt und preprocessed ein einzelnes Bild"""
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Konnte Bild nicht laden: {image_path}")
        return cv2.resize(img, self.config.input_size)

    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Verbesserte Bildvorverarbeitung"""
        # Größenanpassung für bessere Erkennung
        max_dimension = 1200
        height, width = image.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            image = cv2.resize(image, None, fx=scale, fy=scale)
        
        # Farbraumkonvertierung und Kontrastverbesserung
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # CLAHE auf L-Kanal
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Schärfen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        cl = cv2.filter2D(cl, -1, kernel)
        
        # Zusammenführen und zurück zu BGR
        enhanced_lab = cv2.merge((cl,a,b))
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Rauschreduzierung
        denoised = cv2.fastNlMeansDenoisingColored(enhanced_bgr)
        
        return denoised
        
    def _detect_faces(self, image: np.ndarray) -> List[np.ndarray]:
        """Erkennt Gesichter im Bild"""
        if self.config.face_detection_model == "mtcnn":
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            detections = self.face_detector.detect_faces(rgb_image)
            faces = []
            for detection in detections:
                if detection['confidence'] >= self.config.min_confidence:
                    x, y, w, h = detection['box']
                    faces.append(image[y:y+h, x:x+w])
            return faces
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.1, 4)
            return [image[y:y+h, x:x+w] for (x, y, w, h) in faces]
        
    def _apply_augmentation(self, images: List[np.ndarray]) -> List[np.ndarray]:
        """Wendet Datenaugmentation auf die Bilder an"""
        augmented = []
        # Basis-Augmentationen wie Rotation, Spiegelung etc.
        return augmented 

    def _remove_duplicates(self, faces: List[np.ndarray], overlap_threshold: float = 0.5) -> List[np.ndarray]:
        """Entfernt überlappende Gesichter"""
        if len(faces) <= 1:
            return faces
        
        kept_faces = []
        faces_sorted = sorted(faces, key=lambda x: x.shape[0] * x.shape[1], reverse=True)
        
        for face in faces_sorted:
            if not kept_faces:
                kept_faces.append(face)
                continue
            
            # Prüfe Überlappung mit bereits behaltenen Gesichtern
            is_duplicate = False
            for kept_face in kept_faces:
                if self._calculate_similarity(face, kept_face) > overlap_threshold:
                    is_duplicate = True
                    break
                
            if not is_duplicate:
                kept_faces.append(face)
            
        return kept_faces

    def _calculate_similarity(self, face1: np.ndarray, face2: np.ndarray) -> float:
        """Berechnet die Ähnlichkeit zwischen zwei Gesichtern basierend auf Größe und Inhalt"""
        # Resize auf gleiche Größe für Vergleich
        size = (64, 64)
        face1_resized = cv2.resize(face1, size)
        face2_resized = cv2.resize(face2, size)
        
        # Berechne Ähnlichkeit
        diff = cv2.absdiff(face1_resized, face2_resized)
        similarity = 1 - (np.sum(diff) / (size[0] * size[1] * 255 * 3))
        
        return similarity 

    def _load_image(self, image_path: Path) -> np.ndarray:
        """Lädt ein Bild in beliebigem Format"""
        # Versuche zuerst mit OpenCV zu laden
        image = cv2.imread(str(image_path))
        
        if image is None:
            try:
                # Wenn OpenCV fehlschlägt, versuche es mit Pillow
                pil_image = Image.open(image_path)
                # Konvertiere zu RGB falls nötig
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                # Konvertiere zu numpy array
                image = np.array(pil_image)
                # Konvertiere von RGB zu BGR für OpenCV
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            except Exception as e:
                raise ValueError(f"Konnte Bild nicht laden: {image_path} - {str(e)}")
        
        if image is None:
            raise ValueError(f"Konnte Bild nicht laden: {image_path}")
        
        return image 

    def _is_valid_face(self, face_img: np.ndarray) -> bool:
        """Prüft ob ein erkanntes Gesicht valide ist"""
        if face_img.shape[0] < 20 or face_img.shape[1] < 20:
            return False
        
        # Weniger restriktives Seitenverhältnis für verschiedene Posen
        aspect_ratio = face_img.shape[0] / face_img.shape[1]
        if not (0.4 <= aspect_ratio <= 2.5):  # Erlaubt mehr Variation
            return False
        
        # Prüfe Bildkontrast
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        contrast = gray.std()
        if contrast < 15:  # Niedrigerer Schwellwert
            return False
        
        return True 