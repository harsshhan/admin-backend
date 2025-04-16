from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from db.database import Base

class Share(Base):
    __tablename__ = "shares"
    id = Column(Integer, primary_key=True, index=True)
    file_or_folder_id = Column(Integer)
    is_folder = Column(Boolean, default=False)
    shared_by_email = Column(String)
    shared_with_email = Column(String)
    permission = Column(String)  # 'view' or 'edit'