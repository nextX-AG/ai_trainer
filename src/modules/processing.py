from src.base.module import BaseModule
from src.config import ProcessingConfig
import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
from PIL import Image

class ProcessingModule(BaseModule):
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.face_detector = None
        
    def initialize(self):
        self.logger.info("Initialisiere Processing Modul")
        # Face Detection Model laden
        self._initialize_face_detector()
        
    def validate(self):
        if not isinstance(self.config.input_size, tuple) or len(self.config.input_size) != 2:
            raise ValueError("input_size muss ein Tuple mit (height, width) sein")
        
        if not hasattr(self, 'face_detector'):
            raise RuntimeError("Face detector wurde nicht initialisiert")
            
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
        
    def _initialize_face_detector(self):
        """Initialisiert das Gesichtserkennungsmodell"""
        if self.config.face_detection_model == "mtcnn":
            from mtcnn import MTCNN
            self.face_detector = MTCNN()  # Verwende Standardparameter
        elif self.config.face_detection_model == "opencv":
            # Erweiterte Cascades für verschiedene Gesichtspositionen
            cascade_files = [
                'haarcascade_frontalface_default.xml',
                'haarcascade_frontalface_alt.xml',
                'haarcascade_frontalface_alt2.xml',
                'haarcascade_frontalface_alt_tree.xml',  # Für komplexere Gesichtsstrukturen
                'haarcascade_profileface.xml',  # Für Seitenansichten
            ]
            
            self.face_detectors = []
            for cascade_file in cascade_files:
                cascade_path = cv2.data.haarcascades + cascade_file
                detector = cv2.CascadeClassifier(cascade_path)
                if not detector.empty():
                    self.face_detectors.append(detector)
            
            if not self.face_detectors:
                raise RuntimeError("Konnte keine Haar Cascades laden")
        elif self.config.face_detection_model == "dlib":
            # Dlib Face Detector initialisieren
            try:
                import dlib
                self.face_detector = dlib.get_frontal_face_detector()
            except ImportError:
                raise RuntimeError("Dlib ist nicht installiert")
        else:
            raise ValueError(f"Unbekanntes Face Detection Model: {self.config.face_detection_model}")
            
    def _load_and_preprocess(self, image_path: Path) -> np.ndarray:
        """Lädt und preprocessed ein einzelnes Bild"""
        # Lade das Bild
        image = self._load_image(image_path)
        
        # Bildverbesserung
        image = self._enhance_image(image)
        
        # Auf einheitliche Größe bringen
        image = cv2.resize(image, self.config.input_size)
        return image

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
            # MTCNN erwartet RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Erkenne Gesichter
            detections = self.face_detector.detect_faces(rgb_image)
            
            faces = []
            for detection in detections:
                confidence = detection['confidence']
                if confidence >= self.config.min_confidence:
                    x, y, w, h = detection['box']
                    
                    # Füge Padding hinzu
                    padding_h = int(h * 0.3)
                    padding_w = int(w * 0.3)
                    
                    x1 = max(0, x - padding_w)
                    y1 = max(0, y - padding_h)
                    x2 = min(image.shape[1], x + w + padding_w)
                    y2 = min(image.shape[0], y + h + padding_h)
                    
                    face_img = image[y1:y2, x1:x2]
                    
                    # Speichere zusätzliche Informationen
                    face_info = {
                        'image': face_img,
                        'confidence': confidence,
                        'keypoints': detection['keypoints']
                    }
                    faces.append(face_info)
            
            # Sortiere nach Konfidenz
            faces.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Gib nur die Bilder zurück
            return [face['image'] for face in faces]
        
        elif self.config.face_detection_model == "opencv":
            # Verbessere Bildqualität
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            # Erweiterte Parameter für schwierige Fälle
            scale_factors = [1.05, 1.08, 1.1, 1.15]  # Feinere Abstufung
            min_neighbors_values = [2, 3, 4]  # Weniger restriktiv
            min_sizes = [(20, 20), (30, 30), (50, 50)]
            
            all_faces = []
            
            # Versuche verschiedene Bildrotationen
            angles = [0, -15, 15]  # Probiere verschiedene Winkel
            
            for angle in angles:
                if angle != 0:
                    # Rotiere das Bild
                    height, width = gray.shape[:2]
                    center = (width/2, height/2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated_gray = cv2.warpAffine(gray, rotation_matrix, (width, height))
                    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
                else:
                    rotated_gray = gray
                    rotated_image = image
                
                # Verwende alle verfügbaren Detektoren
                for detector in self.face_detectors:
                    for scale_factor in scale_factors:
                        for min_neighbors in min_neighbors_values:
                            for min_size in min_sizes:
                                faces = detector.detectMultiScale(
                                    rotated_gray,
                                    scaleFactor=scale_factor,
                                    minNeighbors=min_neighbors,
                                    minSize=min_size,
                                    maxSize=(int(image.shape[0]*0.95), int(image.shape[1]*0.95))
                                )
                                
                                if len(faces) > 0:
                                    for (x, y, w, h) in faces:
                                        # Größerer Bereich für bessere Erfassung
                                        padding_h = int(h * 0.4)  # 40% vertikales Padding
                                        padding_w = int(w * 0.3)  # 30% horizontales Padding
                                        
                                        x1 = max(0, x - padding_w)
                                        y1 = max(0, y - padding_h)
                                        x2 = min(rotated_image.shape[1], x + w + padding_w)
                                        y2 = min(rotated_image.shape[0], y + h + padding_h)
                                        
                                        face_img = rotated_image[y1:y2, x1:x2]
                                        
                                        if self._is_valid_face(face_img):
                                            all_faces.append(face_img)
            
            # Entferne Duplikate mit angepasstem Schwellwert
            if all_faces:
                filtered_faces = self._remove_duplicates(all_faces, overlap_threshold=0.3)
                return filtered_faces
            
            return all_faces
        
        elif self.config.face_detection_model == "dlib":
            # Konvertiere zu RGB für dlib
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Erkenne Gesichter
            face_locations = self.face_detector(rgb_image)
            
            faces = []
            for face in face_locations:
                x = face.left()
                y = face.top()
                w = face.right() - x
                h = face.bottom() - y
                faces.append(image[y:y+h, x:x+w])
            
            return faces
        
        return []
        
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