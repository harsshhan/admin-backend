from db.database import Base, engine
from models import user, file, folder, share

def init_db():
    Base.metadata.create_all(bind=engine)