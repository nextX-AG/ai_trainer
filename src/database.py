from supabase import create_client, Client
from src.config import get_settings

settings = get_settings()

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)

def get_db() -> Client:
    return supabase 