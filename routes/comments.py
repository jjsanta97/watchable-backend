from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from models import models
from schemas.comment_schemas import CommentCreate, Comment
from core.dependencies import get_db
from routes.auth import get_current_user
from typing import Annotated, List

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/create_comment", status_code=status.HTTP_201_CREATED)
def create_comment(comment_data: CommentCreate, current_user: Annotated[dict, Depends(get_current_user)],
                   db: Session = Depends(get_db)):
    new_comment = models.Comment(body=comment_data.body, user_id=current_user.id, post_id=comment_data.post_id)

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment, ["author"])

    return {"message": "Comment created successfully", "comment": new_comment}


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, current_user: Annotated[dict, Depends(get_current_user)],
                   db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id,
                                              models.Comment.user_id == current_user.id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    db.delete(comment)
    db.commit()

    return {"message": "Comment eliminated successfully"}


@router.get("/{post_id}", response_model=List[Comment])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    #comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(
    #    models.Comment.id.desc()).all()
    comments = db.query(models.Comment).options(joinedload(models.Comment.author)).filter(
        models.Comment.post_id == post_id).order_by(models.Comment.create_date.desc()).all()
    return comments
