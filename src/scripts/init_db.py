import logging
from src.database import engine, Base
from src.models.database import Project, Scene, Download

logger = logging.getLogger(__name__)

def init_database():
    """Initialisiert die Datenbankstruktur"""
    try:
        logger.info("Erstelle Datenbanktabellen...")
        Base.metadata.create_all(bind=engine)
        logger.info("Datenbanktabellen erfolgreich erstellt")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Datenbanktabellen: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database() 