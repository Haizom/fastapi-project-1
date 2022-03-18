from fastapi import Depends, FastAPI, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, hashing, authentication
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# get all blogs
@app.get("/blog", tags=['blogs'], response_model=List[schemas.ShowBlog])
async def get_all_blogs(db: Session = Depends(get_db), 
                        current_user: schemas.User = Depends(authentication.get_current_user)):
    all_blogs = db.query(models.Blog).all()
    return all_blogs

# get a blog by id
@app.get("/blog/{id}", tags=['blogs'], response_model=schemas.ShowBlog)
async def get_one_blog(id, response: Response, db: Session = Depends(get_db),
                        current_user: schemas.User = Depends(authentication.get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"the blog with the {id} id is not found")
    return blog

# post (add) a blog
@app.post("/blog/", response_model=schemas.Blog, status_code=status.HTTP_201_CREATED, tags=['blogs'])
async def post_blog(request : schemas.Blog, db: Session = Depends(get_db),
                    current_user: schemas.User = Depends(authentication.get_current_user)):
    new_blog = models.Blog( title = request.title, body = request.body, user_id = 1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

# delete a blog by id
@app.delete("/blog/{id}", tags=['blogs'])
async def delete_blog(id, response: Response, db: Session = Depends(get_db),
                        current_user: schemas.User = Depends(authentication.get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"the blog with the {id} id is not found")
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)
    db.commit()
    return {"delete details": "blog deleted successfully"}

# update a blog by id and 
@app.put("/blog/{id}", status_code = status.HTTP_202_ACCEPTED, tags=['blogs'])
async def update_blog(id, request: schemas.Blog, db: Session= Depends(get_db),
                        current_user: schemas.User = Depends(authentication.get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail= f"the blog with the {id} id is not found")
    db.query(models.Blog).filter(models.Blog.id == id).update({models.Blog.title: request.title, models.Blog.body: request.body}, synchronize_session='evaluate', update_args=None)
    db.commit()
    return {"update details": "blog updated successfully"}

# post (add) a user
@app.post("/user/", status_code=status.HTTP_201_CREATED,tags=['users'])
async def post_user(request : schemas.User, db: Session = Depends(get_db)):
    new_user = models.User(name = request.name, password = hashing.Hash.hash(request.password), email = request.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# get all users
@app.get("/user", response_model=List[schemas.ShowUser],tags=['users'])
async def get_all_users(db: Session = Depends(get_db)):
    all_users = db.query(models.User).all()
    return all_users

# get a user by id
@app.get("/user/{id}", response_model=schemas.ShowUser,tags=['users'])
async def get_one_user(id, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"the user with the {id} id is not found")
    return user

# login
@app.post("/login", status_code=status.HTTP_201_CREATED,tags=['login'])
async def login(request : OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="incorrect username")
    if not hashing.Hash.verifyPass(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="incorrect password") 
    
    access_token = authentication.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

