import aiohttp
import asyncio
from pathlib import Path

class DFLClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        
    async def upload_video(self, video_path: Path):
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('video',
                          open(video_path, 'rb'),
                          filename=video_path.name)
            
            async with session.post(f"{self.server_url}/process", data=data) as response:
                return await response.json()
                
    async def get_status(self, job_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.server_url}/status/{job_id}") as response:
                return await response.json() 