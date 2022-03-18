from pydantic import BaseModel
from typing import List, Optional

# user schema (post/add)
class User(BaseModel):
    name: str
    password: str
    email:str

# blog schema (post)
class Blog(BaseModel):
    title: str
    body: str
    
    class Config():
        orm_mode = True
        
# user schema (get)
class ShowUser(BaseModel):
    name: str
    email:str
    blogs: List[Blog] = []
    
    class Config():
        orm_mode = True

# blog schema (get)
class ShowBlog(BaseModel):
    title: str
    body: str
    creator: ShowUser
    
    class Config():
        orm_mode = True
        
# login schema (get)
class Login(BaseModel):
    username: str
    password: str
    
    class Config():
        orm_mode = True
        

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None