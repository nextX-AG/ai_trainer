from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import asyncio
import json

app = FastAPI()

class DFLServer:
    def __init__(self):
        self.dfl_path = Path("/root/DeepFaceLab")
        self.workspace_root = Path("/data/workspaces")
        
    async def process_video(self, video_path: Path, workspace_id: str):
        workspace = self.workspace_root / workspace_id
        workspace.mkdir(parents=True, exist_ok=True)
        
        # DFL Kommandos ausführen
        cmd = [
            "python", 
            str(self.dfl_path / "main.py"),
            "extract",
            "--input-dir", str(video_path.parent),
            "--output-dir", str(workspace / "aligned")
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        return {"status": "processing", "workspace_id": workspace_id}

@app.post("/process")
async def process_video(video: UploadFile = File(...)):
    server = DFLServer()
    # Video verarbeiten und Status zurückgeben
    return await server.process_video(video) 