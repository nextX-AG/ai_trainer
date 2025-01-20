from abc import ABC, abstractmethod

class BaseModule(ABC):
    """Basis-Interface für alle Cursor AI Module"""
    
    @abstractmethod
    def initialize(self):
        """Modul initialisieren"""
        pass
        
    @abstractmethod
    def validate(self):
        """Eingabedaten und Konfiguration validieren"""
        pass
        
    @abstractmethod
    def execute(self):
        """Hauptlogik des Moduls ausführen"""
        pass
        
    @abstractmethod
    def cleanup(self):
        """Aufräumen nach der Ausführung"""
        pass 