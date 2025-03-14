from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from models import models
from schemas.like_schema import LikeCreate
from core.dependencies import get_db
from routes.auth import get_current_user
from typing import Annotated

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/likes")
# post_id: int
def like_post(like_data: LikeCreate, current_user: Annotated[dict, Depends(get_current_user)],
              db: Session = Depends(get_db)):
    post_id = like_data.post_id
    existing_like = db.query(models.Like).filter(models.Like.user_id == current_user.id,
                                                 models.Like.post_id == post_id).first()
    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already liked this post")
    new_like = models.Like(user_id=current_user.id, post_id=post_id)

    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return {"message": "Like created successfully", "comment": new_like}


@router.delete("/{like_id}")
def unlike_post(like_id: int, current_user: Annotated[dict, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    like = db.query(models.Like).filter(models.Like.id == like_id, models.Like.user_id == current_user.id).first()

    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
    db.delete(like)
    db.commit()

    return {"message": "Like eliminated successfully"}
