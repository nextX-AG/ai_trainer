from typing import Optional, List, Dict
from datetime import datetime
from src.database.database import get_db

class DatasetService:
    def __init__(self):
        self.db = get_db()

    def create_dataset(self, name: str, project_id: str, description: Optional[str] = None) -> Dict:
        """Erstellt ein neues Dataset"""
        return self.db.table('datasets').insert({
            'name': name,
            'project_id': project_id,
            'description': description,
            'image_count': 0,
            'processed_count': 0,
            'dataset_metadata': {},
            'created_at': datetime.utcnow().isoformat()
        }).execute()

    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Holt ein Dataset anhand seiner ID"""
        result = self.db.table('datasets').select('*').eq('id', dataset_id).execute()
        return result.data[0] if result.data else None

    def list_datasets(self, project_id: Optional[str] = None) -> List[Dict]:
        """Listet alle Datasets auf"""
        query = self.db.table('datasets').select('*')
        if project_id:
            query = query.eq('project_id', project_id)
        result = query.execute()
        return result.data

    def update_dataset(self, dataset_id: str, data: Dict) -> Dict:
        """Aktualisiert ein Dataset"""
        return self.db.table('datasets').update(data).eq('id', dataset_id).execute()

    def delete_dataset(self, dataset_id: str) -> Dict:
        """Löscht ein Dataset"""
        return self.db.table('datasets').delete().eq('id', dataset_id).execute()

    def add_images(self, dataset_id: str, image_count: int) -> Dict:
        """Erhöht den Image Counter eines Datasets"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError("Dataset nicht gefunden")
        
        new_count = dataset['image_count'] + image_count
        return self.update_dataset(dataset_id, {'image_count': new_count})

    def update_processing_status(self, dataset_id: str, processed_count: int) -> Dict:
        """Aktualisiert den Processing Status eines Datasets"""
        return self.update_dataset(dataset_id, {'processed_count': processed_count}) 