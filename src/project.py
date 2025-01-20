from pathlib import Path
from src.config import ProjectConfig
from src.modules.processing import ProcessingModule
import logging

class Project:
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processing_module = ProcessingModule(config.processing)
        
    def initialize(self):
        """Initialisiert das Projekt"""
        self.logger.info(f"Initialisiere Projekt: {self.config.project_info.name}")
        
        # Erstelle Projektstruktur
        self.config.initialize_project()
        
        # Initialisiere Module
        self.processing_module.initialize()
        
    def validate(self):
        """Validiert die Projektkonfiguration"""
        self.processing_module.validate()
        
    def cleanup(self):
        """Räumt Projektressourcen auf"""
        self.processing_module.cleanup() 