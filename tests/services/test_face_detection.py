import cv2
import numpy as np
import pytest
from pathlib import Path
from src.services.face_detection_service import FaceDetectionService
from src.scripts.download_models import download_shape_predictor

@pytest.fixture(scope="session", autouse=True)
def setup_models():
    """Lädt das benötigte Modell vor den Tests"""
    download_shape_predictor()

@pytest.fixture
def face_detector():
    """Erstellt eine Instanz des FaceDetectionService"""
    return FaceDetectionService()

@pytest.fixture
def test_image():
    """Lädt ein Testbild"""
    test_image_path = Path("tests/test_data/test_face.jpg")
    if not test_image_path.exists():
        raise FileNotFoundError(f"Testbild nicht gefunden: {test_image_path}")
    return cv2.imread(str(test_image_path))

def test_face_detection(face_detector, test_image):
    """Testet die Gesichtserkennung"""
    faces = face_detector.detect_faces(test_image)
    
    # Prüfe ob mindestens ein Gesicht erkannt wurde
    assert len(faces) > 0
    
    # Prüfe die erste Erkennung
    face = faces[0]
    assert face.confidence > 0.5
    assert len(face.keypoints) == 68  # dlib liefert 68 Landmarks
    assert all(isinstance(x, int) for x in face.box)
    assert all(isinstance(x, int) for x in face.size)
    assert all(isinstance(x, int) for x in face.position)

def test_face_extraction(face_detector, test_image):
    """Testet die Gesichtsextraktion"""
    faces = face_detector.detect_faces(test_image)
    assert len(faces) > 0
    
    # Extrahiere das erste Gesicht
    face_image = face_detector.extract_face(test_image, faces[0])
    
    # Prüfe die Ausgabe
    assert face_image is not None
    assert isinstance(face_image, np.ndarray)
    assert face_image.shape[:2] == (224, 224)  # Standard Größe

def test_visualization(face_detector, test_image):
    """Testet die Visualisierung der Erkennung"""
    faces = face_detector.detect_faces(test_image)
    assert len(faces) > 0
    
    # Zeichne Erkennungen
    img_with_faces = test_image.copy()
    for face in faces:
        x, y, w, h = face.box
        # Zeichne Box
        cv2.rectangle(img_with_faces, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Zeichne Keypoints
        for point in face.keypoints.values():
            cv2.circle(img_with_faces, point, 2, (0, 0, 255), -1)
    
    # Speichere Visualisierung
    output_dir = Path("tests/output")
    output_dir.mkdir(exist_ok=True)
    cv2.imwrite(str(output_dir / "face_detection_result.jpg"), img_with_faces) 