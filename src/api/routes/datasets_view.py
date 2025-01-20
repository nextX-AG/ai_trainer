from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/datasets", include_in_schema=False)
async def datasets_list(request: Request):
    return templates.TemplateResponse("datasets/index.html", {"request": request})

@router.get("/datasets/new", include_in_schema=False)
async def new_dataset(request: Request):
    return templates.TemplateResponse("datasets/new.html", {"request": request}) 