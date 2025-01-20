from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

@dataclass
class ProjectConfig:
    id: str  # Eindeutige Projekt-ID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    owner: str  # User-ID oder Name
    status: str  # "active", "training", "completed", etc.

@dataclass
class ScrapingConfig:
    keywords: List[str]
    sources: List[str]  # z.B. ["instagram", "pinterest", "google"]
    min_images: int
    max_images: int
    filters: List[str]  # z.B. ["face_only", "min_resolution_1080p"]
    proxy_settings: Optional[Dict[str, str]] = None

@dataclass
class SceneConfig:
    name: str
    description: str
    keywords: List[str]  # Spezifische Keywords für diese Szene
    target_attributes: Dict[str, float]  # z.B. {"brightness": 0.7, "contrast": 0.8}
    reference_images: List[str] = None  # Pfade zu Referenzbildern

@dataclass
class DataStructureConfig:
    project_root: Path
    raw_data: Path
    processed_data: Path
    training_data: Path
    models: Path
    logs: Path
    exports: Path

@dataclass
class ProcessingConfig:
    input_size: tuple
    face_detection_model: str
    min_confidence: float = 0.9
    batch_size: int = 32
    
@dataclass
class AugmentationConfig:
    enabled: bool = True
    rotation_range: tuple = (-20, 20)
    brightness_range: tuple = (0.8, 1.2)
    contrast_range: tuple = (0.8, 1.2)
    noise_probability: float = 0.2
    blur_probability: float = 0.2

@dataclass
class FaceSwapConfig:
    framework: str = "deepfacelab"  # oder "simswap"
    model_type: str = "SAEHD"  # DeepFaceLab-spezifisch
    resolution: int = 224
    batch_size: int = 8
    iterations: int = 500000
    target_features: List[str] = field(default_factory=lambda: [
        "face_position",
        "expression",
        "lighting",
        "age",
        "gender"
    ])

@dataclass
class TrainingConfig:
    # Erweiterte Parameter für Faceswap-Training
    model_type: str
    epochs: int
    learning_rate: float
    batch_size: int
    validation_split: float = 0.2
    early_stopping_patience: int = 5
    checkpoint_frequency: int = 10
    face_swap_config: FaceSwapConfig = None
    
    # Spezifische Parameter für Video-Training
    temporal_coherence: bool = True  # Für flüssigere Übergänge
    frame_sequence_length: int = 16  # Anzahl der Frames pro Sequenz
    motion_consistency: bool = True  # Für bessere Bewegungsübergänge

@dataclass
class ProjectStructure:
    """Standardisierte Projektstruktur"""
    def __init__(self, project_root: Path):
        self.root = project_root
        self.structure = {
            "raw": {
                "scraped": project_root / "data" / "raw" / "scraped",
                "uploaded": project_root / "data" / "raw" / "uploaded",
                "reference": project_root / "data" / "raw" / "reference"
            },
            "processed": {
                "faces": project_root / "data" / "processed" / "faces",
                "scenes": project_root / "data" / "processed" / "scenes"
            },
            "training": {
                "positive": project_root / "data" / "training" / "positive",
                "negative": project_root / "data" / "training" / "negative",
                "validation": project_root / "data" / "training" / "validation"
            },
            "models": {
                "checkpoints": project_root / "models" / "checkpoints",
                "exported": project_root / "models" / "exported"
            },
            "logs": project_root / "logs",
            "exports": project_root / "exports"
        }
    
    def create_structure(self):
        """Erstellt die komplette Verzeichnisstruktur"""
        for category in self.structure.values():
            if isinstance(category, dict):
                for path in category.values():
                    path.mkdir(parents=True, exist_ok=True)
            else:
                category.mkdir(parents=True, exist_ok=True)

@dataclass
class ProjectConfig:
    """Hauptkonfiguration für ein Projekt"""
    project_info: ProjectConfig
    scraping: ScrapingConfig
    scenes: List[SceneConfig]
    data_structure: DataStructureConfig
    processing: ProcessingConfig
    augmentation: AugmentationConfig
    training: TrainingConfig
    
    def initialize_project(self):
        """Initialisiert die Projektstruktur"""
        structure = ProjectStructure(self.data_structure.project_root)
        structure.create_structure() 