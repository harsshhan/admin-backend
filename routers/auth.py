from fastapi import APIRouter, Depends, HTTPException, status
from models.user import UserLogin, CreateUser
from db.crud import get_user_by_email, create_user, get_db
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from auth.jwt_handler import create_access_token
from auth.dependency import get_current_user

auth_router = APIRouter()



# def create_access_token(data: dict):
#     to_encode = data.copy()
#     print(to_encode)
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@auth_router.post("/signup")
def signup(data: CreateUser, db: Session = Depends(get_db)):
    if not data.email.endswith("@srmist.edu.in"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SRM Institute email addresses are allowed"
        )
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if data.email == 'harsh@srmist.edu.in' and data.password == 'harshan':
        create_user(db, data.email)
        access_token = create_access_token(data.email)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    
    # Generate token
    

@auth_router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    if not data.email.endswith("@srmist.edu.in"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SRM Institute email addresses are allowed"
        )
    user = get_user_by_email(db, data.email)
    print(user)
    if not user :  # In production, use proper password hashing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data.email)
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me")
def read_user(current_user: str = Depends(get_current_user)):
    return {"email": current_user}