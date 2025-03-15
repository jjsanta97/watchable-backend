import os
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session, joinedload
from starlette import status
from models import models
from schemas.post_schemas import PostCreate
from core.dependencies import get_db
from routes.auth import get_current_user
from typing import Annotated

router = APIRouter(prefix="/posts", tags=["posts"])

UPLOAD_DIR = "uploads/post_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create_post", status_code=status.HTTP_201_CREATED)
async def create_post(title: str = Form(...), body: str = Form(...), image: UploadFile = File(None),
                      current_user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    image_path = None
    if image:
        image_name = f"user_{current_user.id}_{image.filename}"
        image_path = os.path.join(UPLOAD_DIR, image_name)

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

        image_path = image_path.replace("\\", "/")

    new_post = models.Post(title=title, body=body, image=image_path, user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"message": "Post created successfully", "post": new_post}


@router.put("/{post_id}", status_code=status.HTTP_201_CREATED)
async def update_post(post_id: int, post_data: PostCreate, current_user: Annotated[dict, Depends(get_current_user)],
                      db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post.body = post_data.body
    db.commit()
    db.refresh(post)

    return post


@router.delete("/{post_id}")
async def delete_post(post_id: int, current_user: Annotated[dict, Depends(get_current_user)],
                      db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()

    return {"message": "Post eliminated successfully"}


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_posts(current_user: Annotated[dict, Depends(get_current_user)], db: Session = Depends(get_db)):
    posts = db.query(models.Post).options(joinedload(models.Post.author)).filter(
        models.Post.user_id != current_user.id).order_by(models.Post.create_date.desc()).all()

    for post in posts:
        post.likesCount = db.query(models.Like).filter(models.Like.post_id == post.id).count()
        post.userLike = db.query(models.Like).filter(models.Like.post_id == post.id,
                                                     models.Like.user_id == current_user.id).first()
        post.commentsCount = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()

    return {"posts": posts}


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_posts(current_user: Annotated[dict, Depends(get_current_user)], user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # posts = db.query(models.Post).filter(models.Post.author == user_id).order_by(models.Post.create_date.desc()).all()
    posts = db.query(models.Post).options(joinedload(models.Post.author)).filter(
        models.Post.user_id == user.id).order_by(models.Post.create_date.desc()).all()

    for post in posts:
        post.likesCount = db.query(models.Like).filter(models.Like.post_id == post.id).count()
        post.userLike = db.query(models.Like).filter(models.Like.post_id == post.id,
                                                     models.Like.user_id == current_user.id).first()
        post.commentsCount = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()

    return {"posts": posts}
