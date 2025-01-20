from src.database.database import Database
from src.config import get_settings
import logging

logger = logging.getLogger(__name__)

def test_database():
    settings = get_settings()
    db = Database(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    try:
        # Erstelle ein Test-Projekt
        project = db.create_project(
            name="Test Projekt 2",
            description="Ein weiteres Test-Projekt",
            owner="dev"
        )
        logger.info(f"Projekt erstellt: {project}")
        
        # Erstelle eine Test-Scene
        scene = db.create_scene(
            project_id=project['id'],
            name="Test Scene 2",
            description="Eine weitere Test-Scene",
            keywords=["test", "demo", "v2"],
            target_attributes={"type": "validation", "difficulty": "medium"}
        )
        logger.info(f"Scene erstellt: {scene}")
        
        # Hole alle Scenes des Projekts
        scenes = db.get_project_scenes(project['id'])
        logger.info(f"Projekt Scenes: {scenes}")
        
    except Exception as e:
        logger.error(f"Fehler: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    test_database() 