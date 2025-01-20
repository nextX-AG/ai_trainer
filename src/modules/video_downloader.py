import aiohttp
import asyncio
import aiofiles
from pathlib import Path
from typing import Optional, Callable
import logging
from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class DownloadProgress:
    total_bytes: int
    downloaded_bytes: int
    speed: float  # Bytes pro Sekunde
    eta: float    # Geschätzte verbleibende Zeit in Sekunden

class VideoDownloader:
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
        
    async def download(self,
                      url: str,
                      save_path: Path,
                      headers: Optional[dict] = None,
                      progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> bool:
        """
        Lädt ein Video herunter mit Fortschrittsanzeige und Pause/Resume-Unterstützung
        """
        temp_path = save_path.with_suffix(save_path.suffix + '.tmp')
        
        try:
            async with aiohttp.ClientSession() as session:
                # Hole Content-Length für Fortschrittsanzeige
                async with session.head(url, headers=headers) as response:
                    total_size = int(response.headers.get('content-length', 0))
                
                # Prüfe ob teilweise heruntergeladen
                start_byte = temp_path.stat().st_size if temp_path.exists() else 0
                
                if start_byte:
                    headers = headers or {}
                    headers['Range'] = f'bytes={start_byte}-'
                
                async with session.get(url, headers=headers) as response:
                    if not response.status == 200:
                        raise Exception(f"Download fehlgeschlagen: {response.status}")
                    
                    mode = 'ab' if start_byte else 'wb'
                    async with aiofiles.open(temp_path, mode) as f:
                        downloaded = start_byte
                        start_time = asyncio.get_event_loop().time()
                        
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback:
                                elapsed = asyncio.get_event_loop().time() - start_time
                                speed = downloaded / elapsed if elapsed > 0 else 0
                                eta = (total_size - downloaded) / speed if speed > 0 else 0
                                
                                progress = DownloadProgress(
                                    total_bytes=total_size,
                                    downloaded_bytes=downloaded,
                                    speed=speed,
                                    eta=eta
                                )
                                progress_callback(progress)
                
                # Nach erfolgreichem Download umbenennen
                temp_path.rename(save_path)
                return True
                
        except Exception as e:
            self.logger.error(f"Download-Fehler: {str(e)}")
            return False 