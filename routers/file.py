from unittest import result
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from db.crud import get_db, Session
from auth.dependency import get_current_user
from models.user import User
from services.file_service import list_files_service, upload_file_service


file_router = APIRouter()

@file_router.post("/upload")
def upload_file(folder_id: int = Form(...), file: UploadFile = File(...),current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        result = upload_file_service(file=file, folder_id=folder_id, user_email=current_user['email'], db=db)
        return {
            "message": "File Uploaded successfully",
            "folder": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder not found"
        )


@file_router.get("/list")
def list_files(folder_id: int = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        result  = list_files_service( folder_id=folder_id, user_email=current_user['email'], db=db)
        return {
            "message": "Files listed successfully",
            "files": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder not found"
        )
