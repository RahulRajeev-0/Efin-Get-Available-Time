# app/crud.py
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate


def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email, time_zone=user.time_zone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
