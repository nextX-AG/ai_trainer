from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

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

class Settings(BaseSettings):
    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # PornDB API
    PORNDB_API_KEY: str

    # Scraping Settings
    MAX_CONCURRENT_DOWNLOADS: int = 5
    DOWNLOAD_TIMEOUT: int = 30
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # Storage
    STORAGE_PATH: str = "./data"
    TEMP_PATH: str = "./temp"

    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"

    # Processing
    FACE_DETECTION_MODEL: str = "mtcnn"
    MIN_CONFIDENCE: float = 0.9
    BATCH_SIZE: int = 32

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"

    # Paths
    MODELS_DIR: str = "./models"
    LOGS_DIR: str = "./logs"

    # GPU Settings
    CUDA_VISIBLE_DEVICES: Optional[str] = "0"

    # DFL Server Settings
    DFL_SERVER_URL: str = "http://your.hetzner.server:8000"
    DFL_API_KEY: str = "your_secret_key"

    class Config:
        env_file = ".env.development"
        case_sensitive = True

def get_settings():
    return Settings() 