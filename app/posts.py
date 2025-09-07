from fastapi import APIRouter,Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from db import Posts, Users, Badges, Tags, PostsTags
from db import get_db,serialize_post,serialize_badge
from sqlalchemy.orm import Session
from sqlalchemy import or_,func,desc

import json

router = APIRouter(tags=['Posts'])
templates = Jinja2Templates(directory="templates")

@router.get("/Posts", response_class=HTMLResponse)
async def get_posts(
    request: Request, 
    page: int = 1,
    q:str = "",
    sort:str = "newest",
    badge:str = "",
    db:Session = Depends(get_db)
):
    POSTS_PER_PAGE = 5
    POPULAR_BADGE_COUNT = 3
    posts = db.query(Posts)
    if badge:
        badge_query = db.query(Badges).filter(func.upper(Badges.badge_lable)==badge.upper()).first()
        if badge_query:
            posts = posts.filter(Posts.badge_id == badge_query.badge_id)
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
    
    if   sort == "views":
        posts = posts.order_by(Posts.post_views.desc())
    elif sort == "newest":
        posts = posts.order_by(Posts.post_date.desc())
    
    total_posts = posts.count()
    total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    page_posts  = posts.offset((page-1)*POSTS_PER_PAGE).limit(POSTS_PER_PAGE).all()
    serialized_posts = [serialize_post(post,db) for post in page_posts]
    
    popular_badges_query = db.query(Badges,func.count(Posts.post_id).label("post_count"))\
        .join(Posts,Badges.badge_id==Posts.badge_id)\
        .group_by(Badges.badge_id)\
        .order_by(desc("post_count"))\
        .limit(POPULAR_BADGE_COUNT)
        
    popular_badges = [serialize_badge(badge) for badge,_ in popular_badges_query]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": serialized_posts,
            "badge": badge,
            "sort": sort,
            "page": page,
            "popular_badges":popular_badges,
            "total_pages": total_pages,
            "q":q
        }
    )

@router.get("/Posts/{id}", response_class=HTMLResponse)
async def get_post(request: Request, id: str,db:Session = Depends(get_db)):
    post = db.query(Posts).filter(Posts.post_id==id).first()
    serialized_post = serialize_post(post,db)
    return templates.TemplateResponse(
        "post.html", 
        {
            "request": request, 
            "post": serialized_post, 
        }
    )
