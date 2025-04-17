from sqlalchemy.orm import Session
from models.user import User
from models.folder import Folder, ShareFolderFile

from models.share import Share
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

def get_folder_info(db: Session, folder_id: int, owner_email: str):
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.owner_email == owner_email
    ).first()

    if not folder:
        return None
    
    return folder

def add_share_email(db: Session, data: ShareFolderFile, shared_by: str, shared_with: str):
    db_share = Share(
        file_or_folder_id=data.folder_file_id,
        is_folder=data.is_folder,
        shared_by_email=shared_by,
        shared_with_email=shared_with,
        permission=data.permission
    )    
    db.add(db_share)
    db.commit()
    db.refresh(db_share)

    return db_share


def get_all_child_folders(db: Session, folder_id: int):
    folders = [folder_id]
    child_folders = db.query(Folder).filter(Folder.parent_folder_id == folder_id).all()
    
    for child in child_folders:
        folders.extend(get_all_child_folders(db, child.id))
    
    return folders

