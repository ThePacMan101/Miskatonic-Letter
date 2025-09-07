from fastapi import APIRouter,Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from db import get_db,serialize_post_face,Posts, Users, Badges, Tags, PostsTags
from sqlalchemy.orm import Session
from sqlalchemy import or_

import json

router = APIRouter(tags=['Posts'])
templates = Jinja2Templates(directory="templates")

@router.get("/Posts", response_class=HTMLResponse)
async def get_posts(request: Request, page: int = 1,q:str = "",db:Session = Depends(get_db)):
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
        )
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
async def get_post(request: Request, id: str):
    with open("data/posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)
    post = next((p for p in posts if p.get("id") == id), None)
    page = request.query_params.get("page", 1)
    q = request.query_params.get("q", "")
    return templates.TemplateResponse("post.html", {"request": request, "post": post, "page": page, "q": q})



# @router.get("/Posts", response_class=HTMLResponse)
# async def get_posts(request: Request, page: int = 1,q:str = ""):
#     POSTS_PER_PAGE = 4
#     with open("data/posts.json", "r", encoding="utf-8") as f:
#         posts = json.load(f)
#     if q:
#         q_lower = q.lower()
#         def matches(post):
#             title = post.get("title","").lower()
#             author = post.get("author",{}).get("name","").lower()
#             content = " ".join(post.get("content",[])).lower()
#             tags = [tag.lower() for tag in post.get("tags",[])]
#             return (
#                 q_lower in title 
#                 or q_lower in author 
#                 or q_lower in content 
#                 or any(q_lower in tag for tag in tags)
#             )
#         posts = [p for p in posts if matches(p)]
#     total_pages = (len(posts) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
#     start = (page - 1) * POSTS_PER_PAGE
#     end = start + POSTS_PER_PAGE
#     page_posts = posts[start:end]
#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "posts": page_posts,
#             "page": page,
#             "total_pages": total_pages,
#             "q":q
#         }
#     )

# @router.get("/Posts/{id}", response_class=HTMLResponse)
# async def get_post(request: Request, id: str):
#     with open("data/posts.json", "r", encoding="utf-8") as f:
#         posts = json.load(f)
#     post = next((p for p in posts if p.get("id") == id), None)
#     page = request.query_params.get("page", 1)
#     q = request.query_params.get("q", "")
#     return templates.TemplateResponse("post.html", {"request": request, "post": post, "page": page, "q": q})

