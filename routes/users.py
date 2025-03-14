import os
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status, Query
from sqlalchemy.orm import Session
from models import models
from passlib.context import CryptContext
from schemas.user_schemas import UserCreate, UserUpdate, PasswordUpdate
from core.dependencies import get_db
from routes.auth import get_current_user
from typing import Annotated

router = APIRouter(prefix="/users", tags=["users"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIR = "uploads/profile_pictures"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = models.User(
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        password=bcrypt_context.hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user": new_user}


@router.get("/me", status_code=status.HTTP_200_OK)
async def root(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user


@router.put("/me", status_code=status.HTTP_200_OK)
async def update_profile(updated_data: UserUpdate, current_user: Annotated[dict, Depends(get_current_user)],
                         db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if updated_data.email and updated_data.email != user.email:
        existing_email = db.query(models.User).filter(models.User.email == updated_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already in use")

    if updated_data.username and updated_data.username != user.username:
        existing_username = db.query(models.User).filter(models.User.username == updated_data.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")

    user.full_name = updated_data.full_name or user.full_name
    user.username = updated_data.username or user.username
    user.email = updated_data.email or user.email
    user.description = updated_data.description or user.description

    db.commit()
    db.refresh(user)

    return {"message": "Profile updated successfully", "user": user}


@router.put("/me/change-password", status_code=status.HTTP_200_OK)
async def update_password(password_data: PasswordUpdate, current_user: Annotated[dict, Depends(get_current_user)],
                          db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(password_data.current_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    hashed_password = bcrypt_context.hash(password_data.new_password)
    user.password = hashed_password

    db.commit()

    return {"message": "Password updated successfully"}


@router.post("/upload-profile-picture", status_code=status.HTTP_200_OK)
async def upload_profile_picture(file: UploadFile = File(...), current_user: dict = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    user_id = current_user.id
    filename = f"user_{user_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.profile_picture = file_path.replace("\\", "/")
    db.commit()
    db.refresh(user)

    return {"message": "Profile picture updated successfully", "profile_picture": file_path}


@router.get("/search")
async def search_users(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.username.ilike(f"%{query}%")).all()

    return {"users": users}
