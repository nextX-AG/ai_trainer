import aiohttp
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio
import json

@dataclass
class PornDBConfig:
    api_key: str
    base_url: str = "https://api.porndb.me/api"
    max_retries: int = 3
    timeout: int = 30

@dataclass
class VideoFilter:
    min_duration: Optional[int] = None  # Mindestlänge in Sekunden
    max_duration: Optional[int] = None  # Maximallänge in Sekunden
    min_quality: Optional[str] = None   # z.B. "720p", "1080p"
    categories: List[str] = None        # Liste von Kategorien
    exclude_categories: List[str] = None # Auszuschließende Kategorien
    min_rating: Optional[float] = None  # Minimale Bewertung (0-5)
    date_after: Optional[str] = None    # Datum (YYYY-MM-DD)
    date_before: Optional[str] = None   # Datum (YYYY-MM-DD)

class PornDBScraper:
    def __init__(self, config: PornDBConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Content-Type": "application/json",
            "X-PORNDB-APIKEY": config.api_key
        }
        
    async def search_videos(self, 
                          searchword: str, 
                          page: int = 1, 
                          take: int = 50) -> Dict:
        """Sucht Videos in der PornDB"""
        payload = {
            "Searchword": searchword,
            "Take": take,
            "Page": page
        }
        
        return await self._make_request("video/search", payload)
        
    async def get_video_details(self, video_id: str) -> Dict:
        """Holt detaillierte Informationen zu einem Video"""
        payload = {
            "Id": video_id
        }
        
        return await self._make_request("video/getbyid", payload)
        
    async def get_pornsites(self, 
                           page: int = 1, 
                           take: int = 50) -> Dict:
        """Holt Liste der verfügbaren Pornoseiten"""
        payload = {
            "Take": take,
            "Page": page
        }
        
        return await self._make_request("pornsite/getbyfilter", payload)
        
    async def search_videos_filtered(self, 
                                   searchword: str,
                                   filters: VideoFilter,
                                   page: int = 1,
                                   take: int = 50) -> Dict:
        """Erweiterte Videosuche mit Filtern"""
        payload = {
            "Searchword": searchword,
            "Take": take,
            "Page": page,
            "Filters": {
                "MinDuration": filters.min_duration,
                "MaxDuration": filters.max_duration,
                "MinQuality": filters.min_quality,
                "Categories": filters.categories,
                "ExcludeCategories": filters.exclude_categories,
                "MinRating": filters.min_rating,
                "DateAfter": filters.date_after,
                "DateBefore": filters.date_before
            }
        }
        
        # Entferne None-Werte aus dem Payload
        payload["Filters"] = {k: v for k, v in payload["Filters"].items() if v is not None}
        
        return await self._make_request("video/search", payload)
        
    async def _make_request(self, 
                          endpoint: str, 
                          payload: Dict,
                          retry_count: int = 0) -> Dict:
        """Führt einen API-Request durch"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}/{endpoint}",
                    headers=self.headers,
                    json=payload,
                    timeout=self.config.timeout
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limit
                        if retry_count < self.config.max_retries:
                            wait_time = int(response.headers.get('Retry-After', 60))
                            self.logger.warning(f"Rate limit erreicht. Warte {wait_time} Sekunden...")
                            await asyncio.sleep(wait_time)
                            return await self._make_request(endpoint, payload, retry_count + 1)
                        else:
                            raise Exception("Maximale Anzahl an Retry-Versuchen erreicht")
                    else:
                        raise Exception(f"API-Fehler: {response.status} - {await response.text()}")
                        
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout bei Request zu {endpoint}")
            if retry_count < self.config.max_retries:
                return await self._make_request(endpoint, payload, retry_count + 1)
            raise
            
        except Exception as e:
            self.logger.error(f"Fehler bei API-Request: {str(e)}")
            raise

    async def download_video(self, video_url: str, save_path: str) -> bool:
        """Lädt ein Video herunter"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, headers=self.headers) as response:
                    if response.status == 200:
                        with open(save_path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        return True
                    else:
                        self.logger.error(f"Fehler beim Download: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Download-Fehler: {str(e)}")
            return False 