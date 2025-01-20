from abc import ABC, abstractmethod
from typing import List, Any
from pathlib import Path

class BaseModule(ABC):
    """Basis-Interface für alle Cursor AI Module"""
    
    @abstractmethod
    def initialize(self):
        """Initialisiert das Modul"""
        pass
        
    @abstractmethod
    def validate(self):
        """Validiert die Konfiguration"""
        pass
        
    @abstractmethod
    def execute(self, input_data: List[Any]) -> List[Any]:
        """Führt die Hauptfunktion des Moduls aus"""
        pass
        
    @abstractmethod
    def cleanup(self):
        """Räumt Ressourcen auf"""
        pass 