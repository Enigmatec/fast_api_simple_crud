from fastapi import FastAPI, Depends, HTTPException
from database import create_db_and_tables, get_session
from contextlib import asynccontextmanager
from models import User, Post
from sqlmodel import Session, select

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/users", response_model=list[User], tags=['users'])
async def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.post("/users", response_model=User, tags=['users'])
async def create_user(user: User, session: Session = Depends(get_session)):
    user = User(name=user.name, email=user.email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User is not found")
    return user

@app.put("/users/{user_id}", response_model=User, tags=["users"])
async def update_user(user_id: int, user: User, session: Session = Depends(get_session)):
    get_user = session.get(User, user_id)
    if not get_user:
        raise HTTPException(status_code=404, detail="User is not found")
    
    get_user.name = user.name
    get_user.email = user.email
    session.add(get_user)
    session.commit()
    session.refresh(get_user) 
    return user

@app.delete("/users/{user_id}", status_code=204, tags=["users"])
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"detail" : "User is deleted"}

#POST

@app.get("/posts", response_model=list[Post], tags=["posts"])
async def list_posts(session: Session = Depends(get_session)):
    posts = session.exec(select(Post)).all()
    return posts

@app.get("/posts/{post_id}", response_model=Post, tags=["posts"])
async def get_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post: 
        raise HTTPException(status_code=404, detail="Post not found")
    return post



#User Posts
@app.get("/users/{user_id}/posts", response_model=list[Post], tags=["user posts"])
async def list_user_posts(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.posts

@app.post("/users/{user_id}/posts", response_model=Post, tags=["user posts"])
async def create_user_post(user_id: int, post: Post, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post = Post(title = post.title, content=post.content)
    user.posts.append(post)
    session.add(user)
    session.commit()
    session.refresh(post)
    return post