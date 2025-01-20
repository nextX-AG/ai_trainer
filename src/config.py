from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
import logging

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
    input_size: Tuple[int, int]
    augmentation_enabled: bool
    face_detection_model: str
    min_confidence: float = 0.9
    batch_size: int = 32
    
    def validate(self):
        if not isinstance(self.input_size, tuple) or len(self.input_size) != 2:
            raise ValueError("input_size muss ein Tuple mit zwei Werten sein")
        if not isinstance(self.augmentation_enabled, bool):
            raise ValueError("augmentation_enabled muss ein Boolean sein")
        if self.face_detection_model not in ["opencv", "mtcnn"]:
            raise ValueError("Nicht unterstütztes Gesichtserkennungsmodell")

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
    batch_size: int = 4
    epochs: int = 100
    learning_rate: float = 0.0001
    num_workers: int = 4
    checkpoint_interval: int = 1000
    validation_interval: int = 100
    
    # SimSwap spezifische Parameter
    id_loss_weight: float = 10.0
    attr_loss_weight: float = 10.0
    rec_loss_weight: float = 10.0
    
    # Modell Parameter
    latent_dim: int = 512
    n_layers: int = 50
    channel_multiplier: int = 2

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

class Settings(BaseModel):
    debug_mode: bool = False
    log_level: str = "INFO"
    supabase_url: str = ""
    supabase_key: str = ""
    porndb_api_key: str = "25a7db06eb6b42f752447eef22159c82"  # Default API Key
    
    @classmethod
    def load(cls):
        if CONFIG_FILE.exists():
            return cls.parse_file(CONFIG_FILE)
        return cls()
    
    def save(self):
        CONFIG_FILE.write_text(self.json(indent=2))

# Globale Settings-Instanz
settings = Settings.load()

CONFIG_FILE = Path("config/settings.json")
CONFIG_FILE.parent.mkdir(exist_ok=True) 