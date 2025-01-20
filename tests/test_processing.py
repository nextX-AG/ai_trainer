import pytest
from pathlib import Path
import numpy as np
from src.config import ProcessingConfig
from src.modules.processing import ProcessingModule
import cv2
import os

@pytest.fixture
def basic_config():
    return ProcessingConfig(
        input_size=(224, 224),
        augmentation_enabled=False,
        face_detection_model="opencv"
    )

@pytest.fixture
def processing_module(basic_config):
    return ProcessingModule(basic_config)

@pytest.fixture
def mtcnn_config():
    return ProcessingConfig(
        input_size=(224, 224),
        augmentation_enabled=False,
        face_detection_model="mtcnn",
        min_confidence=0.9
    )

@pytest.fixture
def mtcnn_processing_module(mtcnn_config):
    return ProcessingModule(mtcnn_config)

def test_initialization(processing_module):
    """Test ob das Modul korrekt initialisiert wird"""
    processing_module.initialize()
    assert hasattr(processing_module, 'face_detector')

def test_validation_input_size():
    """Test ob die Validierung der input_size funktioniert"""
    invalid_config = ProcessingConfig(
        input_size=(224,),  # Ungültiges Tuple
        augmentation_enabled=False,
        face_detection_model="opencv"
    )
    module = ProcessingModule(invalid_config)
    
    with pytest.raises(ValueError, match="input_size muss ein Tuple mit.*"):
        module.validate()

def test_load_and_preprocess(processing_module, tmp_path):
    """Test ob Bilder korrekt geladen und vorverarbeitet werden"""
    # Erstelle ein Test-Bild
    test_image_path = tmp_path / "test_image.jpg"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(test_image_path), img)
    
    # Verarbeite das Bild
    processed = processing_module._load_and_preprocess(test_image_path)
    
    assert processed.shape[:2] == processing_module.config.input_size 

def test_face_detection(processing_module):
    """Test ob die Gesichtserkennung funktioniert"""
    # Verwende ein vordefiniertes Testbild mit einem echten Gesicht
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_image_path = os.path.join(current_dir, "test_data", "test_face.jpg")
    
    # Stelle sicher, dass das Testbild existiert
    if not os.path.exists(test_image_path):
        # Erstelle ein synthetisches Gesichtsmuster, das besser erkennbar ist
        img = np.ones((300, 300, 3), dtype=np.uint8) * 255
        
        # Zeichne ein "Gesicht" mit mehr Merkmalen
        # Kopf
        cv2.ellipse(img, (150, 150), (70, 100), 0, 0, 360, (200, 200, 200), -1)
        # Augen
        cv2.circle(img, (120, 120), 15, (0, 0, 0), -1)  # Linkes Auge
        cv2.circle(img, (180, 120), 15, (0, 0, 0), -1)  # Rechtes Auge
        # Mund
        cv2.ellipse(img, (150, 180), (30, 20), 0, 0, 180, (0, 0, 0), -1)
        
        # Speichere das Testbild
        os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
        cv2.imwrite(test_image_path, img)
    
    # Initialisiere das Modul
    processing_module.initialize()
    
    # Verarbeite das Bild
    image = processing_module._load_and_preprocess(test_image_path)
    faces = processing_module._detect_faces(image)
    
    # Es sollte mindestens ein Gesicht erkannt werden
    assert len(faces) > 0
    # Jedes erkannte Gesicht sollte ein numpy array sein
    assert all(isinstance(face, np.ndarray) for face in faces)
    # Überprüfe die Größe der erkannten Gesichter
    for face in faces:
        assert face.shape[0] > 0 and face.shape[1] > 0 

def test_face_detection_with_real_images(mtcnn_processing_module):
    """Test ob die Gesichtserkennung mit echten Bildern funktioniert"""
    # Verzeichnis mit den Testbildern
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_images_dir = os.path.join(current_dir, "test_data")
    output_dir = os.path.join(test_images_dir, "results")
    os.makedirs(output_dir, exist_ok=True)
    
    # Unterstützte Bildformate
    supported_formats = ('.jpg', '.jpeg', '.png', '.webp')
    
    # Sammle alle Testbilder
    test_images = [
        os.path.join(test_images_dir, f) 
        for f in os.listdir(test_images_dir) 
        if f.lower().endswith(supported_formats) and not f.startswith('result_')
    ]
    
    # Stelle sicher, dass wir Testbilder haben
    assert len(test_images) > 0, "Keine Testbilder im test_data Verzeichnis gefunden"
    print(f"\nGefundene Testbilder: {[os.path.basename(img) for img in test_images]}")
    
    # Initialisiere das Modul
    mtcnn_processing_module.initialize()
    
    # Teste jedes Bild
    results = []
    for image_path in test_images:
        try:
            # Originalbild laden
            original_image = cv2.imread(image_path)
            if original_image is None:
                raise ValueError(f"Konnte Bild nicht laden: {image_path}")
                
            # Bild für Gesichtserkennung verarbeiten
            processed_image = mtcnn_processing_module._load_and_preprocess(image_path)
            faces = mtcnn_processing_module._detect_faces(processed_image)
            
            # Ergebnisse speichern
            result = {
                'image': os.path.basename(image_path),
                'faces_found': len(faces),
                'success': len(faces) > 0,
                'image_size': original_image.shape
            }
            results.append(result)
            
            # Visualisiere die erkannten Gesichter im Originalbild
            if len(faces) > 0:
                # MTCNN erwartet RGB
                rgb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                # Erkenne Gesichter für die Visualisierung
                detections = mtcnn_processing_module.face_detector.detect_faces(rgb_image)
                
                for detection in detections:
                    if detection['confidence'] >= mtcnn_processing_module.config.min_confidence:
                        # Hole Box-Koordinaten
                        x, y, w, h = detection['box']
                        keypoints = detection['keypoints']
                        
                        # Zeichne Rechteck
                        cv2.rectangle(original_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        # Zeichne Keypoints
                        for point in keypoints.values():
                            cv2.circle(original_image, point, 2, (0, 0, 255), 2)
                        
                        # Zeige Konfidenz
                        confidence = f"{detection['confidence']:.2f}"
                        cv2.putText(original_image, f"Face: {confidence}", 
                                  (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.9, (0, 255, 0), 2)
                
                # Speichere das Ergebnisbild
                output_path = os.path.join(output_dir, f"result_{os.path.basename(image_path)}")
                cv2.imwrite(output_path, original_image)
            
        except Exception as e:
            results.append({
                'image': os.path.basename(image_path),
                'error': str(e),
                'success': False
            })
    
    # Gib die Ergebnisse aus
    print("\nGesichtserkennungs-Ergebnisse:")
    total_images = len(results)
    successful_detections = sum(1 for r in results if r.get('success', False))
    
    print(f"\nZusammenfassung:")
    print(f"Gesamt Bilder: {total_images}")
    print(f"Erfolgreiche Erkennungen: {successful_detections}")
    print(f"Erkennungsrate: {(successful_detections/total_images)*100:.1f}%")
    
    print("\nDetailierte Ergebnisse:")
    for result in results:
        if 'error' in result:
            print(f"❌ {result['image']}: Fehler - {result['error']}")
        else:
            status = "✅" if result['success'] else "❌"
            size_info = f"Bildgröße: {result.get('image_size', 'unbekannt')}"
            print(f"{status} {result['image']}: {result['faces_found']} Gesichter gefunden ({size_info})")
    
    # Gib den Pfad zu den Ergebnisbildern aus
    if os.path.exists(output_dir) and os.listdir(output_dir):
        print(f"\nErgebnisbilder wurden gespeichert in: {output_dir}")
    
    # Mindestens ein Bild sollte erfolgreich sein
    assert any(r.get('success', False) for r in results), "Keine Gesichter in den Testbildern erkannt" 