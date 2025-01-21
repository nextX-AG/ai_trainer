import pytest
import os
from pathlib import Path
from dotenv import load_dotenv
from src.services.scraping_service import ScrapingService
from src.scripts.download_models import download_shape_predictor

# Lade .env.development vor allen Tests
load_dotenv('.env.development')

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Stellt sicher, dass die Umgebungsvariablen geladen sind"""
    assert os.getenv('SUPABASE_URL') is not None, "SUPABASE_URL nicht gefunden"
    assert os.getenv('SUPABASE_KEY') is not None, "SUPABASE_KEY nicht gefunden"

@pytest.fixture(scope="session", autouse=True)
def setup_models():
    """Lädt das benötigte Modell vor den Tests"""
    download_shape_predictor()

@pytest.fixture
def scraping_service():
    """Erstellt eine Instanz des ScrapingService"""
    return ScrapingService()

@pytest.fixture
def test_config():
    """Test-Konfiguration für das Scraping"""
    return {
        "sources": {
            "porndb": True,
            "instagram": False,
            "pinterest": False,
            "google": False
        },
        "porndb": {
            "searchType": "performers",
            "search": "test",
            "sort": "name",
            "page": 1,
            "take": 1,
            "gender": "f",
            "status": "active"
        },
        "limits": {
            "min": 1,
            "max": 2
        },
        "filters": {
            "faceOnly": True,
            "minResolution": True,
            "adultContent": True
        }
    }

async def test_create_scraping_job(scraping_service, test_config):
    """Testet die Erstellung eines Scraping-Jobs"""
    job = await scraping_service.create_job(test_config)
    assert job.id is not None
    assert job.status == "pending"
    assert job.config == test_config

async def test_start_scraping(scraping_service, test_config):
    """Testet den Start eines Scraping-Jobs"""
    result = await scraping_service.start_scraping(test_config)
    assert result["status"] == "started"
    assert "job_id" in result

async def test_job_status(scraping_service, test_config):
    """Testet die Status-Abfrage eines Jobs"""
    # Starte einen Job
    result = await scraping_service.start_scraping(test_config)
    job_id = result["job_id"]
    
    # Prüfe den Status
    status = await scraping_service.get_job_status(job_id)
    assert status is not None
    assert status["id"] == job_id
    assert status["status"] in ["pending", "running", "completed", "failed"] 