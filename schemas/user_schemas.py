from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime


# Schema to create new user
class UserCreate(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: constr(min_length=10)

    class Config:
        str_min_length = 1

# Schema to update user
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None

# Schema to update user password
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


# class User(BaseModel):
#     id: int
#     username: str
#     email: EmailStr
#     date_created: datetime
#
#     # This class allows to covert data from SQLachemy to Pydantic
#     class Config:
#         from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
