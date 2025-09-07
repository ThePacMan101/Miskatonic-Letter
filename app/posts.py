from fastapi import APIRouter,Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from db import Posts, Users, Badges, Tags, PostsTags
from db import get_db,serialize_post_face,serialize_post_content
from sqlalchemy.orm import Session
from sqlalchemy import or_

import json

router = APIRouter(tags=['Posts'])
templates = Jinja2Templates(directory="templates")

@router.get("/Posts", response_class=HTMLResponse)
async def get_posts(request: Request, page: int = 1,q:str = "",db:Session = Depends(get_db),sort:str = "Newest"):
    POSTS_PER_PAGE = 5
    posts = db.query(Posts)
    if q:
        posts = posts.join(Users     , Posts.author_id   ==  Users.user_id     )\
                     .join(PostsTags , Posts.post_id     ==  PostsTags.post_id )\
                     .join(Tags      , PostsTags.tag_id  ==  Tags.tag_id       )\

        q_lower = f"%{q.lower()}%"
        posts = posts.filter(
            or_(
                Posts.post_title.ilike(q_lower),
                Posts.post_title.ilike(q_lower),
                Posts.post_content.ilike(q_lower),
                Users.user_name.ilike(q_lower),
                Tags.tag_lable.ilike(q_lower)
            )
        ).distinct()
    total_posts = posts.count()
    total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    page_posts  = posts.offset((page-1)*POSTS_PER_PAGE).limit(POSTS_PER_PAGE).all()
    serialized_posts = [serialize_post_face(post,db) for post in page_posts]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": serialized_posts,
            "page": page,
            "total_pages": total_pages,
            "q":q
        }
    )

@router.get("/Posts/{id}", response_class=HTMLResponse)
async def get_post(request: Request, id: str,db:Session = Depends(get_db)):
    post = db.query(Posts).filter(Posts.post_id==id).first()
    serialized_post = serialize_post_content(post,db)
    return templates.TemplateResponse(
        "post.html", 
        {
            "request": request, 
            "post": serialized_post, 
        }
    )

