import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: int = 1,q:str = ""):
    POSTS_PER_PAGE = 4
    with open("data/posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)
    if q:
        q_lower = q.lower()
        def matches(post):
            title = post.get("title","").lower()
            author = post.get("author",{}).get("name","").lower()
            content = " ".join(post.get("content",[])).lower()
            tags = [tag.lower() for tag in post.get("tags",[])]
            return (
                q_lower in title 
                or q_lower in author 
                or q_lower in content 
                or any(q_lower in tag for tag in tags)
            )
        posts = [p for p in posts if matches(p)]
    total_pages = (len(posts) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    start = (page - 1) * POSTS_PER_PAGE
    end = start + POSTS_PER_PAGE
    page_posts = posts[start:end]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": page_posts,
            "page": page,
            "total_pages": total_pages,
            "q":q
        }
    )

@app.get("/post/{id}", response_class=HTMLResponse)
async def post_detail(request: Request, id: str):
    with open("data/posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)
    post = next((p for p in posts if p.get("id") == id), None)
    page = request.query_params.get("page", 1)
    q = request.query_params.get("q", "")
    return templates.TemplateResponse("post.html", {"request": request, "post": post, "page": page, "q": q})
