import aiohttp
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from src.config import settings
from datetime import datetime
import asyncio
from pathlib import Path
from src.db import get_db
from src.models.scraping import ScrapingJob, ScrapingResult
from src.services.face_detection_service import FaceDetectionService

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self):
        self.porndb_api_key = settings.porndb_api_key
        self.base_url = "https://api.porndb.me/api/v1"
        self.db = get_db()
        self.face_detector = FaceDetectionService()
        
    async def create_job(self, config: Dict) -> ScrapingJob:
        """Erstellt einen neuen Scraping-Job"""
        job_data = {
            "status": "pending",
            "config": config,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = await self.db.table("scraping_jobs").insert(job_data).execute()
        return ScrapingJob(**result.data[0])

    async def update_job_status(self, job_id: str, status: str, progress: Optional[float] = None, error: Optional[str] = None):
        """Aktualisiert den Status eines Jobs"""
        update_data = {
            "status": status,
            "updated_at": datetime.now()
        }
        if progress is not None:
            update_data["progress"] = progress
        if error is not None:
            update_data["error"] = error
            
        await self.db.table("scraping_jobs").update(update_data).eq("id", job_id).execute()

    async def save_result(self, job_id: str, source: str, url: str, local_path: str, metadata: Optional[Dict] = None):
        """Speichert ein Scraping-Ergebnis"""
        result_data = {
            "job_id": job_id,
            "source": source,
            "url": url,
            "local_path": local_path,
            "metadata": metadata,
            "downloaded_at": datetime.now()
        }
        
        await self.db.table("scraping_results").insert(result_data).execute()

    async def search_performers(self, 
                              search: str = "", 
                              page: int = 1, 
                              take: int = 50,
                              gender: Optional[str] = None,
                              status: Optional[str] = None) -> Dict:
        """Sucht nach Performern in der PornDB"""
        endpoint = f"{self.base_url}/performers"
        
        params = {
            "q": search,
            "page": page,
            "take": take
        }
        
        if gender:
            params["gender"] = gender
        if status:
            params["status"] = status
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    params=params,
                    headers={"X-PORNDB-APIKEY": self.porndb_api_key}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched {len(data.get('data', []))} performers")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"PornDB API error: {error_text}")
                        return {"error": f"API returned status {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error in search_performers: {str(e)}")
            return {"error": str(e)}
            
    async def download_images(self, urls: List[str], save_path: str) -> List[str]:
        """Lädt Bilder von den angegebenen URLs herunter"""
        downloaded_files = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for url in urls:
                    try:
                        filename = url.split('/')[-1]
                        filepath = f"{save_path}/{filename}"
                        
                        async with session.get(url) as response:
                            if response.status == 200:
                                with open(filepath, 'wb') as f:
                                    f.write(await response.read())
                                downloaded_files.append(filepath)
                                logger.info(f"Downloaded: {filepath}")
                            else:
                                logger.warning(f"Failed to download {url}: {response.status}")
                                
                    except Exception as e:
                        logger.error(f"Error downloading {url}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in download_images: {str(e)}")
            
        return downloaded_files

    async def start_scraping(self, config: Dict) -> Dict:
        """Startet den Scraping-Prozess"""
        # Erstelle neuen Job
        job = await self.create_job(config)
        
        try:
            # Starte Scraping im Hintergrund
            asyncio.create_task(self._run_scraping(job.id, config))
            
            return {
                "status": "started",
                "job_id": job.id
            }
            
        except Exception as e:
            logger.error(f"Error starting scraping job: {str(e)}")
            await self.update_job_status(job.id, "failed", error=str(e))
            raise

    async def check_image_quality(self, image_path: str) -> Tuple[bool, Dict]:
        """Überprüft die Bildqualität und sucht nach Gesichtern"""
        try:
            # Bild laden
            img = cv2.imread(image_path)
            if img is None:
                return False, {"error": "Bild konnte nicht geladen werden"}
            
            # Bildgröße prüfen
            height, width = img.shape[:2]
            if width < 1080 or height < 1080:
                return False, {"error": "Bildauflösung zu niedrig"}
            
            # Gesichtserkennung
            faces = self.face_detector.detect_faces(img)
            if not faces:
                return False, {"error": "Keine Gesichter gefunden"}
            
            # Qualitätsmetriken
            quality_info = {
                "resolution": f"{width}x{height}",
                "face_count": len(faces),
                "face_details": [
                    {
                        "confidence": face.confidence,
                        "size": face.size,
                        "position": face.position
                    } for face in faces
                ]
            }
            
            return True, quality_info
            
        except Exception as e:
            logger.error(f"Error checking image quality: {str(e)}")
            return False, {"error": str(e)}

    async def download_single_image(self, url: str, save_path: str) -> Optional[str]:
        """Lädt ein einzelnes Bild herunter und prüft die Qualität"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Temporärer Dateiname
                        temp_filename = url.split('/')[-1]
                        temp_filepath = f"{save_path}/temp_{temp_filename}"
                        
                        # Bild speichern
                        content = await response.read()
                        with open(temp_filepath, 'wb') as f:
                            f.write(content)
                        
                        # Qualitätsprüfung
                        is_valid, quality_info = await self.check_image_quality(temp_filepath)
                        
                        if is_valid:
                            # Finaler Dateiname mit Qualitätsinfo
                            final_filename = f"{Path(temp_filepath).stem}_faces{quality_info['face_count']}.jpg"
                            final_filepath = f"{save_path}/{final_filename}"
                            
                            # Umbenennen
                            Path(temp_filepath).rename(final_filepath)
                            logger.info(f"Downloaded and validated: {final_filepath}")
                            return final_filepath
                        else:
                            # Lösche nicht valides Bild
                            Path(temp_filepath).unlink()
                            logger.warning(f"Image quality check failed: {quality_info['error']}")
                            return None
                    else:
                        logger.warning(f"Failed to download {url}: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error downloading image {url}: {str(e)}")
            return None

    async def _run_scraping(self, job_id: str, config: Dict):
        """Führt den eigentlichen Scraping-Prozess aus"""
        try:
            await self.update_job_status(job_id, "running", progress=0)
            
            total_downloaded = 0
            total_errors = 0
            quality_stats = {
                "total_processed": 0,
                "face_detected": 0,
                "low_resolution": 0,
                "download_errors": 0
            }
            
            if config["sources"]["porndb"]:
                porndb_config = config["porndb"]
                search_results = await self.search_performers(**porndb_config)
                
                if "error" not in search_results:
                    image_urls = []
                    for performer in search_results.get("data", []):
                        if performer.get("images"):
                            image_urls.extend(performer["images"])
                    
                    save_path = Path("data/raw/scraped")
                    save_path.mkdir(parents=True, exist_ok=True)
                    
                    for i, url in enumerate(image_urls[:config["limits"]["max"]]):
                        quality_stats["total_processed"] += 1
                        
                        try:
                            filepath = await self.download_single_image(url, str(save_path))
                            if filepath:
                                quality_stats["face_detected"] += 1
                                await self.save_result(
                                    job_id=job_id,
                                    source="porndb",
                                    url=url,
                                    local_path=filepath,
                                    metadata={
                                        "performer": performer,
                                        "quality_check": "passed"
                                    }
                                )
                                total_downloaded += 1
                            else:
                                quality_stats["low_resolution"] += 1
                                total_errors += 1
                        except Exception as e:
                            quality_stats["download_errors"] += 1
                            total_errors += 1
                            logger.error(f"Error downloading {url}: {str(e)}")
                        
                        progress = (i + 1) / len(image_urls) * 100
                        await self.update_job_status(job_id, "running", progress=progress)
            
            # Job abschließen mit Qualitätsstatistiken
            final_status = "completed" if total_errors == 0 else "completed_with_errors"
            await self.update_job_status(
                job_id, 
                final_status, 
                progress=100,
                error=f"Stats: {quality_stats}" if total_errors > 0 else None
            )
            
        except Exception as e:
            logger.error(f"Error in scraping job {job_id}: {str(e)}")
            await self.update_job_status(job_id, "failed", error=str(e))

    async def get_job_status(self, job_id: str) -> Dict:
        """Gibt den aktuellen Status eines Jobs zurück"""
        result = await self.db.table("scraping_jobs").select("*").eq("id", job_id).execute()
        if result.data:
            return result.data[0]
        return None 