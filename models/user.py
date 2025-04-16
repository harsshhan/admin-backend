from sqlalchemy import Column, Integer, String
from db.database import Base
from pydantic import BaseModel, EmailStr

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)


    @property
    def dict(self): 
        return {
            "id": self.id,
            "email": self.email
        }





class UserLogin(BaseModel):
    email: EmailStr
    password:str

class CreateUser(BaseModel):
    email: EmailStr
    password:str