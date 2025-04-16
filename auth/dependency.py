from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .jwt_handler import decode_access_token
from db.crud import get_db, Session
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        email = decode_access_token(token)
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"email": user.email,"id":user.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )