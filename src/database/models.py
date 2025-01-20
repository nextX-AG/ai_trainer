from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ProjectStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ModelType(enum.Enum):
    SIMSWAP = "simswap"
    FACESHIFTER = "faceshifter"
    CUSTOM = "custom"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    datasets = relationship("Dataset", back_populates="project")
    models = relationship("Model", back_populates="project")
    face_swaps = relationship("FaceSwap", back_populates="project")

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))
    image_count = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    dataset_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="datasets")
    training_jobs = relationship("TrainingJob", back_populates="dataset")

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ModelType))
    project_id = Column(Integer, ForeignKey("projects.id"))
    version = Column(String)
    metrics = Column(JSON)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="models")
    training_jobs = relationship("TrainingJob", back_populates="model")
    face_swaps = relationship("FaceSwap", back_populates="model")

class TrainingJob(Base):
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.id"))
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    status = Column(String)
    progress = Column(Float, default=0.0)
    metrics = Column(JSON)
    parameters = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    model = relationship("Model", back_populates="training_jobs")
    dataset = relationship("Dataset", back_populates="training_jobs")

class FaceSwap(Base):
    __tablename__ = "face_swaps"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    model_id = Column(Integer, ForeignKey("models.id"))
    source_path = Column(String)
    target_path = Column(String)
    result_path = Column(String)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="face_swaps")
    model = relationship("Model", back_populates="face_swaps") 