from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(256), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)
    profile_picture = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    create_date = Column(DateTime, default=datetime.now())

    # Relations: a user can have many posts and comments
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    image = Column(String(256), nullable=True)
    create_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relations: a post belongs to one user and can have many comments
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, nullable=False)
    create_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    # Relations: a comment belongs to a user and a post
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='uix_user_post'),)

    # Relations: A post can have many likes
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
