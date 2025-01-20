from typing import Optional, List, Dict
from datetime import datetime
from src.database.database import get_db

class ProjectService:
    def __init__(self):
        self.db = get_db()

    def create_project(self, name: str, description: Optional[str] = None) -> Dict:
        """Erstellt ein neues Projekt"""
        return self.db.table('projects').insert({
            'name': name,
            'description': description,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }).execute()

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Holt ein Projekt anhand seiner ID"""
        result = self.db.table('projects').select('*').eq('id', project_id).execute()
        return result.data[0] if result.data else None

    def list_projects(self, status: Optional[str] = None) -> List[Dict]:
        """Listet alle Projekte auf"""
        query = self.db.table('projects').select('*')
        if status:
            query = query.eq('status', status)
        result = query.execute()
        return result.data

    def update_project(self, project_id: str, data: Dict) -> Dict:
        """Aktualisiert ein Projekt"""
        data['updated_at'] = datetime.utcnow().isoformat()
        return self.db.table('projects').update(data).eq('id', project_id).execute()

    def delete_project(self, project_id: str) -> Dict:
        """Löscht ein Projekt (Soft Delete)"""
        return self.db.table('projects').update({
            'status': 'deleted',
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', project_id).execute() 