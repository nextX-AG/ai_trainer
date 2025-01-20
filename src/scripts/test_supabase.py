import logging
from src.database import get_db
from src.config import get_settings

logger = logging.getLogger(__name__)

def test_supabase_connection():
    """Testet die Verbindung zu Supabase"""
    try:
        settings = get_settings()
        logger.info(f"Versuche Verbindung zu: {settings.SUPABASE_URL}")
        
        db = get_db()
        
        # Versuche eine einfache Abfrage
        response = db.table('projects').select("*").limit(1).execute()
        
        logger.info("Supabase Verbindung erfolgreich!")
        logger.info(f"Response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"Fehler bei der Supabase Verbindung: {str(e)}")
        logger.error(f"Bitte überprüfen Sie die Umgebungsvariablen SUPABASE_URL und SUPABASE_KEY")
        return False

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    test_supabase_connection() 