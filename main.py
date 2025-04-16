from fastapi import FastAPI 
from routers.auth import auth_router
from routers.folder import folder_router


app = FastAPI()


app.include_router(prefix='/auth', tags=['auth'], router=auth_router)
app.include_router(prefix='/folder', tags=['auth'], router=folder_router)