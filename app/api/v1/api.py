from fastapi import APIRouter
from api.v1.endpoints import users, items, auth, test, index

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(test.router, prefix="/test", tags=["test data"])
api_router.include_router(index.router, prefix="/index", tags=["index single item"])
