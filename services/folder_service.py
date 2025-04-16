import os
from models import user
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv
from db.crud import get_folder_info, add_share_email, get_all_child_folders
from models.share import Share
from models.folder import NewFolder, ShareFolderFile, Folder 
from sqlalchemy.exc import SQLAlchemyError
load_dotenv()

STORAGE_PATH = os.getenv("STORAGE_PATH")


def get_folder_path(db: Session, folder_id: int, owner_email: str):
    folder = get_folder_info(db, folder_id, owner_email)
    
    if not folder:
        return None
    
    path = [folder.name]
    current_folder = folder
    
    while current_folder.parent_folder_id:
        parent = get_folder_info(db, folder_id, owner_email)
        if not parent:
            break
        path.insert(0, parent.name)
        current_folder = parent
    
    return path

def create_folder_service(folder: NewFolder, owner_email: str, db: Session):
    try:
    
        if folder.parent_folder_id:
            folder_hierarchy = get_folder_path(db, folder.parent_folder_id, owner_email)
            if not folder_hierarchy:
                raise Exception("Parent folder not found")
            base_path = os.path.join(STORAGE_PATH, owner_email, *folder_hierarchy)
        else:
            base_path = os.path.join(STORAGE_PATH, owner_email)

        folder_path = os.path.join(base_path, folder.name)

        existing_folder = db.query(Folder).filter(
            Folder.name == folder.name,
            Folder.owner_email == owner_email,
            Folder.parent_folder_id == folder.parent_folder_id
        ).first()
        
        if existing_folder:
            raise Exception("Folder with this name already exists in this location")

        if os.path.exists(folder_path):
            raise Exception("Folder already exists in filesystem")

        os.makedirs(folder_path, exist_ok=False)

        db_folder = Folder(
            name=folder.name,
            owner_email=owner_email,
            parent_folder_id=folder.parent_folder_id
        )

        db.add(db_folder)
        db.commit()
        db.refresh(db_folder)

        return {
            "id": db_folder.id,
            "name": db_folder.name,
            "parent_folder_id": db_folder.parent_folder_id,
            "created_at": db_folder.created_at.isoformat()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Database error: " + str(e))
    except OSError as e:
        raise Exception("Filesystem error: " + str(e))

def list_folder_service(owner_email: str, db: Session):
    folders = db.query(Folder).filter(Folder.owner_email == owner_email).all()
    return [
        {
            "id": folder.id,
            "name": folder.name,
            "owner_email": folder.owner_email,
            "parent_folder_id": folder.parent_folder_id
        }
        for folder in folders
    ]

def list_shared_files_service(user_email: str, db: Session):
    shared = db.query(Folder, Share).join(Share, Share.file_or_folder_id == Folder.id)\
        .filter(
            Share.shared_with_email == user_email,
            Share.is_folder == True
        ).all()
    
    return [
        {
            "id": folder.id,
            "name": folder.name,
            "owner_email": folder.owner_email,
            "parent_folder_id": folder.parent_folder_id,
            "shared_by": share.shared_by_email,
            "permission": share.permission,
            "created_at": folder.created_at.isoformat()
        }
        for folder, share in shared
    ]

def share_folder_service(share_data: ShareFolderFile, user_email: str, db: Session):
    shared = []
    
    folder = db.query(Folder).filter(
        Folder.id == share_data.folder_file_id
    ).first()
    
    if not folder or folder.parent_folder_id is not None:
        raise Exception("Only root folders can be shared")

    folders_to_share = get_all_child_folders(db, share_data.folder_file_id)
    
    for email in share_data.user_emails:
        existing_share = db.query(Share).filter(
            Share.file_or_folder_id.in_(folders_to_share),
            Share.shared_with_email == email
        ).first()
        
        if existing_share:
            raise Exception(f"User {email} already has access to this folder or its children")
        
        for folder_id in folders_to_share:
            share_data_copy = ShareFolderFile(
                folder_file_id=folder_id,
                is_folder=True, 
                user_emails=[email],
                permission=share_data.permission
            )
            
            share = add_share_email(
                db=db,
                data=share_data_copy,
                shared_by=user_email,
                shared_with=email
            )
            
            if folder_id == share_data.folder_file_id: 
                shared.append(share.shared_with_email)

    return {"shared_with": shared}

