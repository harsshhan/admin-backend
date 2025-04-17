import os
import hashlib
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.folder import Folder
from models.file import File
from models.share import Share
from typing import List
from dotenv import load_dotenv
import mimetypes

load_dotenv()
STORAGE_PATH = os.getenv("STORAGE_PATH")

def get_folder_full_path(db: Session, folder_id: int) -> str:
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        return None
    
    path_parts = [folder.name]
    current = folder
    
    while current.parent_folder_id:
        parent = db.query(Folder).filter(Folder.id == current.parent_folder_id).first()
        if not parent:
            break
        path_parts.insert(0, parent.name)
        current = parent
    
    path_parts.insert(0, current.owner_email)
    return os.path.join(STORAGE_PATH, *path_parts)

def get_unique_filename(folder_path: str, original_filename: str) -> str:
    name, ext = os.path.splitext(original_filename)
    counter = 0
    new_filename = original_filename
    
    while os.path.exists(os.path.join(folder_path, new_filename)):
        counter += 1
        new_filename = f"{name} ({counter}){ext}"
    return new_filename

def upload_file_service(file: UploadFile, folder_id: int, user_email: str, db: Session):    
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            raise Exception("Folder not found")
        if folder.owner_email != user_email:
            share = db.query(Share).filter(
                Share.file_or_folder_id == folder_id,
                Share.shared_with_email == user_email,
                Share.is_folder == True,
                Share.permission == "edit"
            ).first()
            
            if not share:
                raise Exception("No write permission for this folder")

        folder_path = get_folder_full_path(db, folder_id)
        if not folder_path:
            raise Exception("Invalid folder path")
        
        unique_filename = get_unique_filename(folder_path, file.filename)
        file_path = os.path.join(folder_path, unique_filename)
        file_content = file.file.read()
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        db_file = File(
            name=unique_filename, 
            path=file_path,
            owner_email=user_email,
            size=len(file_content),
            mime_type=mimetypes.guess_type(file.filename)[0],
            folder_id=folder_id
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return {
            "id": db_file.id,
            "name": db_file.name,
            "size": db_file.size,
            "mime_type": db_file.mime_type
        }
        
    except Exception as e:
        if 'db_file' in locals():
            db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise Exception(f"Upload failed: {str(e)}")

def download_file_service(file_id: int, user_email: str, db: Session):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise Exception("File not found")
    
    if file.owner_email != user_email:
        share = db.query(Share).filter(
            Share.file_or_folder_id == file.folder_id,
            Share.shared_with_email == user_email,
            Share.is_folder == False
        ).first()
        
        if not share:
            raise Exception("No access to this file")
    
    if not os.path.exists(file.path):
        raise Exception("File not found in storage")
    
    try:
        with open(file.path, "rb") as f:
            file_content = f.read()
            
        return {
            "content": file_content,
            "filename": file.name,
            "mime_type": file.mime_type,
            "size": file.size
        }
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

def list_files_service(folder_id: int, user_email: str, db: Session):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise Exception("Folder not found")

    if folder.owner_email != user_email:
        share = db.query(Share).filter(
            Share.file_or_folder_id == folder_id,
            Share.shared_with_email == user_email,
            Share.is_folder == True
        ).first()
        
        if not share:
            raise Exception("No access to this folder")

    files = db.query(File).filter(File.folder_id == folder_id).all()
    return [
        {
            "id": file.id,
            "name": file.name,
            "size": file.size,
            "mime_type": file.mime_type,
            "created_at": file.created_at.isoformat()
        }
        for file in files
    ]

def delete_file_service(file_id: int, user_email: str, db: Session):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise Exception("File not found")
    
    if file.owner_email != user_email:
        raise Exception("No permission to delete this file")
    
    try:
        if os.path.exists(file.path):
            os.remove(file.path)
        
        db.delete(file)
        db.commit()
        return {"message": "File deleted successfully"}
    except Exception as e:
        db.rollback()
        raise Exception(f"Delete failed: {str(e)}")