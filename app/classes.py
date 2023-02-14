# Request and Response classes

from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class PostResponse(Post):
    user_id: int
    votes: int
    user: UserResponse
    created_at: datetime

class Token(BaseModel):
    token: str
    token_type: str
    
class TokenData(BaseModel):
    id: str

class Vote(BaseModel):
    post_id: int
    dir: int