from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Schema to create a comment
class CommentCreate(BaseModel):
    body: str
    post_id: int


class UserBase(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Comment(BaseModel):
    id: int
    body: str
    create_date: datetime
    author: Optional[UserBase]

    class Config:
        from_attributes = True
