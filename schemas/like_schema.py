from pydantic import BaseModel


# Schema to create a comment
class LikeCreate(BaseModel):
    post_id: int