from fastapi import FastAPI 
from routers.auth import auth_router
from routers.folder import folder_router
from routers.file import file_router

app = FastAPI()


app.include_router(prefix='/auth', tags=['Auth'], router=auth_router)
app.include_router(prefix='/folder', tags=['Folder'], router=folder_router)
app.include_router(prefix='/file', tags=['File'], router=file_router)
