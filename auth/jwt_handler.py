from jose import jwt
from datetime import datetime, timedelta

# Secret key for encoding/decoding tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

def create_access_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise jwt.InvalidTokenError
        return email
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")