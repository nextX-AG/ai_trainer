from typing import Optional, List, Dict
from datetime import datetime
from src.database.database import get_db

class ModelService:
    def __init__(self):
        self.db = get_db()

    def create_model(self, name: str, project_id: str, model_type: str, version: str = "1.0") -> Dict:
        """Erstellt ein neues Model"""
        return self.db.table('models').insert({
            'name': name,
            'project_id': project_id,
            'type': model_type,
            'version': version,
            'metrics': {},
            'parameters': {},
            'created_at': datetime.utcnow().isoformat()
        }).execute()

    def get_model(self, model_id: str) -> Optional[Dict]:
        """Holt ein Model anhand seiner ID"""
        result = self.db.table('models').select('*').eq('id', model_id).execute()
        return result.data[0] if result.data else None

    def list_models(self, project_id: Optional[str] = None) -> List[Dict]:
        """Listet alle Models auf"""
        print("\n=== DEBUG: ModelService.list_models Start ===")
        try:
            print("1. Building query")
            query = self.db.table('models').select('*')
            if project_id:
                query = query.eq('project_id', project_id)
            
            print("2. Executing query")
            result = query.execute()
            print(f"3. Raw result type: {type(result)}")
            print(f"4. Raw result: {result}")
            
            if hasattr(result, 'data'):
                print(f"5a. Has data attribute: {result.data}")
                return result.data
            
            print("5b. No data attribute, returning raw result")
            return result
        except Exception as e:
            print(f"ERROR in list_models: {str(e)}")
            raise

    def update_model(self, model_id: str, data: Dict) -> Dict:
        """Aktualisiert ein Model"""
        return self.db.table('models').update(data).eq('id', model_id).execute()

    def delete_model(self, model_id: str) -> Dict:
        """Löscht ein Model"""
        return self.db.table('models').delete().eq('id', model_id).execute()

    def update_metrics(self, model_id: str, metrics: Dict) -> Dict:
        """Aktualisiert die Metriken eines Models"""
        model = self.get_model(model_id)
        if not model:
            raise ValueError("Model nicht gefunden")
        
        current_metrics = model.get('metrics', {})
        current_metrics.update(metrics)
        return self.update_model(model_id, {'metrics': current_metrics})

    def update_parameters(self, model_id: str, parameters: Dict) -> Dict:
        """Aktualisiert die Parameter eines Models"""
        model = self.get_model(model_id)
        if not model:
            raise ValueError("Model nicht gefunden")
        
        current_params = model.get('parameters', {})
        current_params.update(parameters)
        return self.update_model(model_id, {'parameters': current_params}) 