from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/training", include_in_schema=False)
async def training_dashboard(request: Request):
    return templates.TemplateResponse("training/index.html", {"request": request})

@router.get("/training/new", include_in_schema=False)
async def new_training(request: Request):
    return templates.TemplateResponse("training/new.html", {"request": request}) 