from supabase import create_client
import os
from typing import Optional
from functools import lru_cache
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv('.env.development')

def get_db():
    print("\n=== DEBUG: Database Connection ===")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')[:20]}...")  # Nur Anfang der URL für Sicherheit
    print(f"SUPABASE_KEY exists: {bool(os.getenv('SUPABASE_KEY'))}")
    
    if not hasattr(get_db, "instance"):
        get_db.instance = create_client(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        )
        print("Created new DB instance")
    else:
        print("Using existing DB instance")
    
    return get_db.instance

def create_tables():
    """Erstellt die Tabellen über die Supabase REST API"""
    db = get_db()
    
    # SQL für die Tabellenerstellung
    sql = """
    -- Projects Tabelle
    CREATE TABLE IF NOT EXISTS projects (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Datasets Tabelle
    CREATE TABLE IF NOT EXISTS datasets (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT NOT NULL,
        description TEXT,
        project_id UUID REFERENCES projects(id),
        image_count INTEGER DEFAULT 0,
        processed_count INTEGER DEFAULT 0,
        dataset_metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Models Tabelle
    CREATE TABLE IF NOT EXISTS models (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT NOT NULL,
        type TEXT,
        project_id UUID REFERENCES projects(id),
        version TEXT,
        metrics JSONB,
        parameters JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Training Jobs Tabelle
    CREATE TABLE IF NOT EXISTS training_jobs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        model_id UUID REFERENCES models(id),
        dataset_id UUID REFERENCES datasets(id),
        status TEXT,
        progress FLOAT DEFAULT 0.0,
        metrics JSONB,
        parameters JSONB,
        started_at TIMESTAMPTZ DEFAULT NOW(),
        completed_at TIMESTAMPTZ
    );

    -- Face Swaps Tabelle
    CREATE TABLE IF NOT EXISTS face_swaps (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        project_id UUID REFERENCES projects(id),
        model_id UUID REFERENCES models(id),
        source_path TEXT,
        target_path TEXT,
        result_path TEXT,
        parameters JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # SQL über RPC ausführen
    db.rpc('exec_sql', {'query': sql}).execute()
    print("Tabellen wurden erfolgreich erstellt!") 