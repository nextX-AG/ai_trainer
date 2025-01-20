import uvicorn
import logging
from pathlib import Path
from src.config import ProjectConfig, ProcessingConfig
from src.project import Project

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_test_config():
    return ProjectConfig(
        project_info={
            "id": "test-project",
            "name": "Test Project",
            "description": "Development Test Project",
            "owner": "dev"
        },
        processing=ProcessingConfig(
            input_size=(224, 224),
            augmentation_enabled=True,
            face_detection_model="mtcnn",
            min_confidence=0.9,
            batch_size=32
        )
    )

def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Initialize project
    config = create_test_config()
    project = Project(config)
    
    try:
        project.initialize()
        project.validate()
        
        # Start API server
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except Exception as e:
        logger.error(f"Fehler beim Starten: {str(e)}")
    finally:
        project.cleanup()

if __name__ == "__main__":
    main() 