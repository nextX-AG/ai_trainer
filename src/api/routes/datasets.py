from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.services.dataset_service import DatasetService

router = APIRouter()
dataset_service = DatasetService()

class DatasetCreate(BaseModel):
    name: str
    project_id: str
    description: Optional[str] = None

@router.get("/datasets/")
async def list_datasets(project_id: Optional[str] = None):
    """Listet alle Datasets auf"""
    result = dataset_service.list_datasets(project_id)
    return result.data if hasattr(result, 'data') else result

@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Holt ein spezifisches Dataset"""
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset nicht gefunden")
    return dataset

@router.post("/datasets/")
async def create_dataset(dataset: DatasetCreate):
    """Erstellt ein neues Dataset"""
    return dataset_service.create_dataset(
        name=dataset.name,
        project_id=dataset.project_id,
        description=dataset.description
    )

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Löscht ein Dataset"""
    return dataset_service.delete_dataset(dataset_id) 