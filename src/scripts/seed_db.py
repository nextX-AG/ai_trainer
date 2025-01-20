import logging
from datetime import datetime
from src.utils.db import get_db
from src.models.database import Project, Scene, Download

logger = logging.getLogger(__name__)

def seed_database():
    """Fügt Test-Daten in die Datenbank ein"""
    with get_db() as db:
        # Test-Projekt erstellen
        project = Project(
            id="test-project-1",
            name="Test Projekt",
            description="Ein Testprojekt für die Entwicklung",
            owner="dev",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status="active"
        )
        db.add(project)
        
        # Test-Szene erstellen
        scene = Scene(
            project_id=project.id,
            name="Test Szene",
            description="Eine Testszene",
            keywords=["test", "entwicklung"],
            target_attributes={"brightness": 0.7, "contrast": 0.8}
        )
        db.add(scene)
        
        # Test-Download erstellen
        download = Download(
            id="test-download-1",
            project_id=project.id,
            url="https://example.com/test.mp4",
            status="pending",
            progress=0.0,
            metadata={"size": "1GB", "format": "mp4"}
        )
        db.add(download)
        
        logger.info("Test-Daten erfolgreich eingefügt")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database() 