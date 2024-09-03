from fastapi import FastAPI
from api.v1.api import api_router
from core.config import settings
from db.init_db import init_db
from db.session import engine

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

@app.on_event("startup")
def on_startup():
    init_db(engine)

app.include_router(api_router, prefix=settings.API_V1_STR)
