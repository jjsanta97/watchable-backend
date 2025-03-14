from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.database import engine
from models import models
from routes import auth, users, posts, comments, likes
from starlette import status
from fastapi.middleware.cors import CORSMiddleware

import logging

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

app = FastAPI(title="Watchable")

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite Angular en desarrollo
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Permite todos los headers
)

# Servir archivos estáticos desde la carpeta "uploads"
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Welcome to Watchable API!"}
