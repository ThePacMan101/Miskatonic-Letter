from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import posts

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(posts.router)


