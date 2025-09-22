from fastapi import APIRouter,Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from db import Posts, Users, Badges, Tags, PostsTags
from db import get_db
from sqlalchemy.orm import Session


router = APIRouter(tags=['Login'])
templates = Jinja2Templates(directory="templates")

@router.get("/Login", response_class=HTMLResponse)
async def login(
    request: Request, 
    page: int = 1,
    q:str = "",
    sort:str = "newest",
    badge:str = "",
    db:Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "login.html",{"request": request}
    )
