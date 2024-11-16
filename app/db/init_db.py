from app.db.session import SessionLocal
from app.db.base import Base
from app.models import user, item

def init_db(engine):
    Base.metadata.create_all(bind=engine)
