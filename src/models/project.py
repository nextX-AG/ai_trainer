from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: str
    owner: str
    scene_type: str

class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]

class ProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    message: Optional[str]

class ScrapingStatus(BaseModel):
    project_id: str
    total_images: int
    downloaded_images: int
    failed_downloads: int
    status: str  # "running", "completed", "failed"
    progress: float
    error_message: Optional[str]

class TrainingStatus(BaseModel):
    project_id: str
    epoch: int
    total_epochs: int
    loss: float
    accuracy: float
    status: str  # "preparing", "training", "completed", "failed"
    progress: float
    error_message: Optional[str] 