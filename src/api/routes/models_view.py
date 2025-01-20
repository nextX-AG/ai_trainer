from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/models", include_in_schema=False)
async def models_list(request: Request):
    return templates.TemplateResponse("models/index.html", {"request": request})

@router.get("/models/new", include_in_schema=False)
async def new_model(request: Request):
    return templates.TemplateResponse("models/new.html", {"request": request}) 