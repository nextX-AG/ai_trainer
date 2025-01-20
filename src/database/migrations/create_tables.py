from src.database.database import get_db

def create_tables():
    db = get_db()
    
    # Models Tabelle
    db.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            project_id TEXT NOT NULL,
            type TEXT NOT NULL,
            version TEXT DEFAULT '1.0',
            metrics JSONB DEFAULT '{}',
            parameters JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Datasets Tabelle
    db.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            project_id TEXT NOT NULL,
            description TEXT,
            image_count INTEGER DEFAULT 0,
            processed_count INTEGER DEFAULT 0,
            dataset_metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

if __name__ == "__main__":
    create_tables() 