from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = Column(String, nullable=False)
    status = Column(String, default="active")
    
    # Beziehungen
    scenes = relationship("Scene", back_populates="project")
    downloads = relationship("Download", back_populates="project")

class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    keywords = Column(JSON)  # Liste von Keywords
    target_attributes = Column(JSON)  # Dictionary von Attributen
    
    # Beziehungen
    project = relationship("Project", back_populates="scenes")
    images = relationship("Image", back_populates="scene")

class Download(Base):
    __tablename__ = "downloads"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    url = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, downloading, completed, error
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)  # Zusätzliche Metadaten
    
    # Beziehungen
    project = relationship("Project", back_populates="downloads") 