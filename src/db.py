import os
from supabase import create_client, Client
from functools import lru_cache

@lru_cache()
def get_db() -> Client:
    """
    Erstellt eine gecachte Datenbankverbindung zu Supabase
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL und SUPABASE_KEY müssen in .env.development gesetzt sein")
        
    return create_client(supabase_url, supabase_key) 