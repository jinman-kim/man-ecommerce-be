from db.session import SessionLocal
from db.base import Base
from models import user, item

def init_db(engine):
    Base.metadata.create_all(bind=engine)
