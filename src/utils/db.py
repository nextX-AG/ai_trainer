from contextlib import contextmanager
from typing import Generator
from src.database import SessionLocal

@contextmanager
def get_db() -> Generator:
    """Provides a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close() 