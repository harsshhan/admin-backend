from sqlalchemy.orm import Session
from models.user import User
from db.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_user(db: Session, email: str):
    db_user = User(email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  
    return db_user


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user: 
        return user.dict
    else:
        return None