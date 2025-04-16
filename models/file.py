from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from db.database import Base

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    path = Column(String)
    owner_email = Column(String, index=True)
    size = Column(Integer)
    mime_type = Column(String)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)