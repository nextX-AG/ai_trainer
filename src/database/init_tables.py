from src.database.database import get_db
import os

def init_tables():
    db = get_db()
    
    # Models Tabelle erstellen
    db.rpc(
        'exec_sql',
        {
            'query': """
                CREATE TABLE IF NOT EXISTS models (
                    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
                    name text NOT NULL,
                    project_id uuid REFERENCES projects(id),
                    type text NOT NULL,
                    version text DEFAULT '1.0',
                    metrics jsonb DEFAULT '{}',
                    parameters jsonb DEFAULT '{}',
                    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
    ).execute()
    
    # Datasets Tabelle erstellen
    db.rpc(
        'exec_sql',
        {
            'query': """
                CREATE TABLE IF NOT EXISTS datasets (
                    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
                    name text NOT NULL,
                    project_id uuid REFERENCES projects(id),
                    description text,
                    image_count integer DEFAULT 0,
                    processed_count integer DEFAULT 0,
                    dataset_metadata jsonb DEFAULT '{}',
                    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
                );
            """
        }
    ).execute()

if __name__ == "__main__":
    init_tables() 