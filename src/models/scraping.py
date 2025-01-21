from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

class ScrapingJob(BaseModel):
    id: str
    status: str  # "pending", "running", "completed", "failed"
    config: Dict
    created_at: datetime
    updated_at: datetime
    results: Optional[Dict] = None
    error: Optional[str] = None
    progress: Optional[float] = None

class ScrapingResult(BaseModel):
    job_id: str
    source: str  # "porndb", "instagram", etc.
    url: str
    local_path: str
    metadata: Optional[Dict] = None
    downloaded_at: datetime 