from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base
from pydantic import BaseModel
from typing import List, Literal, Optional

class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_email = Column(String, index=True)
    parent_folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship("Folder")


class NewFolder(BaseModel):
    name: str
    parent_folder_id: Optional[int] = None

class ShareFolderFile(BaseModel):
    folder_file_id: int
    is_folder: bool 
    permission: Literal['view','edit']
    user_emails: List[str]