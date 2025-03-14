from pydantic import BaseModel
from datetime import datetime


# Schema to create a post
class PostCreate(BaseModel):
    title: str
    body: str
