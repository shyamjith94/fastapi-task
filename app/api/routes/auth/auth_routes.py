from typing import Dict, List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.api.depends import Database
from app.api.models import User
from app.api.schema import UserCreate, UserRead,LoginRead
from app.api.utils.auth import get_current_user, get_password_hash,verify_password, create_access_token
from app.logs import logger

auth_router = APIRouter(prefix="/auth")
db_class = Database()



@auth_router.post("/signup", response_model=UserRead)
def register(*, user_in: UserCreate, db: Session = Depends(db_class.get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exist")

    hashed_password = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/login", response_model=LoginRead)
def login(*, user_in: UserCreate, db: Session = Depends(db_class.get_db)):
    user = db.query(User).filter(User.username==user_in.username).first()
    password_verified = verify_password(user_in.password, user.password)
    if not user or not password_verified:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    data = {"access_token":access_token, "token_type":"bearer"}
    return data


@auth_router.get("/me", response_model=UserRead)
def read_users_me(current_user:User = Depends(get_current_user)):
    return current_user