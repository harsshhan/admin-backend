from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session
from db.crud import get_db
from models.folder import NewFolder, ShareFolderFile
from auth.dependency import get_current_user
from models.user import User
from services.folder_service import create_folder_service, list_folder_service, share_folder_service, list_shared_files_service

folder_router = APIRouter()

@folder_router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_folder(folder: NewFolder, current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        print(current_user)
        result = create_folder_service(folder,owner_email=current_user['email'],db=db)
        return {
            "message": "Folder created successfully",
            "folder": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@folder_router.post("/share", status_code=status.HTTP_200_OK)
async def share_folder(share_data: ShareFolderFile, current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        result = share_folder_service(share_data,current_user['email'], db=db)
        return {
            "message": "Folder shared successfully",
            "shared_with": result["shared_with"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@folder_router.get("/list")
async def list_folders(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    try:
        
        folders = list_folder_service( current_user['email'],db)
        return {"folders": folders}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@folder_router.get("/shared")
async def get_shared_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(current_user['email'])
    files = list_shared_files_service(current_user['email'], db)
    return {"shared_files": files}