#!/bin/bash

# 프로젝트 이름 설정
PROJECT_NAME="ecommerce"

# 디렉토리 생성
mkdir -p $PROJECT_NAME/app/{api/v1/endpoints,core,models,db,services,tests,utils}
mkdir -p $PROJECT_NAME/alembic/versions
mkdir -p $PROJECT_NAME/scripts

# 파일 생성 및 내용 추가

# main.py
cat <<EOL > $PROJECT_NAME/app/main.py
from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import engine

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

@app.on_event("startup")
def on_startup():
    init_db(engine)

app.include_router(api_router, prefix=settings.API_V1_STR)
EOL

# config.py
cat <<EOL > $PROJECT_NAME/app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-commerce API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
EOL

# security.py
cat <<EOL > $PROJECT_NAME/app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
EOL

# logging_config.py
cat <<EOL > $PROJECT_NAME/app/core/logging_config.py
import logging
from logging.config import dictConfig

logging_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

dictConfig(logging_config)
EOL

# api.py
cat <<EOL > $PROJECT_NAME/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import users, items, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
EOL

# users.py
cat <<EOL > $PROJECT_NAME/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.db.session import get_db
from app.services.user_service import create_user, get_user

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_new_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = create_user(db=db, user_in=user_in)
    return user

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
EOL

# items.py
cat <<EOL > $PROJECT_NAME/app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.db.session import get_db
from app.services.item_service import create_item, get_items

router = APIRouter()

@router.post("/", response_model=schemas.Item)
def create_new_item(item_in: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = create_item(db=db, item_in=item_in)
    return item

@router.get("/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = get_items(db=db, skip=skip, limit=limit)
    return items
EOL

# auth.py
cat <<EOL > $PROJECT_NAME/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.core.security import create_access_token, verify_password
from app.db.session import get_db

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
EOL

# schemas.py
cat <<EOL > $PROJECT_NAME/app/api/v1/schemas.py
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: str
    password: str
EOL

# user.py
cat <<EOL > $PROJECT_NAME/app/models/user.py
from sqlalchemy import Boolean, Column, Integer, String
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
EOL

# item.py
cat <<EOL > $PROJECT_NAME/app/models/item.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Item(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))

    owner = relationship("User", back_populates="items")
EOL

# base.py
cat <<EOL > $PROJECT_NAME/app/db/base.py
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
EOL

# session.py
cat <<EOL > $PROJECT_NAME/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOL

# init_db.py
cat <<EOL > $PROJECT_NAME/app/db/init_db.py
from app.db.session import SessionLocal
from app.db.base import Base
from app.models import user, item

def init_db(engine):
    Base.metadata.create_all(bind=engine)
EOL

# user_service.py
cat <<EOL > $PROJECT_NAME/app/services/user_service.py
from sqlalchemy.orm import Session
from app import models, schemas
from app.core.security import get_password_hash

def create_user(db: Session, user_in: schemas.UserCreate):
    hashed_password = get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
EOL

# item_service.py
cat <<EOL > $PROJECT_NAME/app/services/item_service.py
from sqlalchemy.orm import Session
from app import models, schemas

def create_item(db: Session, item_in: schemas.ItemCreate, user_id: int):
    item = models.Item(**item_in.dict(), owner_id=user_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Item).offset(skip).limit(limit).all()
EOL

# test_users.py
cat <<EOL > $PROJECT_NAME/app/tests/test_users.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={"email": "user@example.com", "password": "secret"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
EOL

# test_items.py
cat <<EOL > $PROJECT_NAME/app/tests/test_items.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post("/api/v1/items/", json={"title": "Item 1", "description": "This is an item"})
    assert response.status_code == 200
    assert response.json()["title"] == "Item 1"
EOL

# email.py
cat <<EOL > $PROJECT_NAME/app/utils/email.py
def send_email(email_to: str, subject: str = "", body: str = ""):
    print(f"Sending email to {email_to}: {subject}\n{body}")
EOL

# hashing.py
cat <<EOL > $PROJECT_NAME/app/utils/hashing.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
EOL

# env.py
cat <<EOL > $PROJECT_NAME/alembic/env.py
from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from app.db.base import Base

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOL

# Dockerfile
cat <<EOL > $PROJECT_NAME/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOL

# docker-compose.yml
cat <<EOL > $PROJECT_NAME/docker-compose.yml
version: "3.9"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./ecommerce.db
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: example
      POSTGRES_DB: ecommerce
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOL

# .env
cat <<EOL > $PROJECT_NAME/.env
DATABASE_URL=sqlite:///./ecommerce.db
SECRET_KEY=super-secret-key
EOL

# pyproject.toml
cat <<EOL > $PROJECT_NAME/pyproject.toml
[tool.poetry]
name = "ecommerce"
version = "0.1.0"
description = "An e-commerce backend using FastAPI"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.68.0"
uvicorn = "^0.15.0"
sqlalchemy = "^1.4.22"
pydantic = "^1.8.2"
alembic = "^1.6.5"
python-jose = "^3.2.0"
passlib = "^1.7.4"
pytest = "^6.2.4"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOL

# README.md
cat <<EOL > $PROJECT_NAME/README.md
# E-commerce API

This project is an example of an e-commerce backend built using FastAPI.

## Features

- User registration and authentication
- Product management
- Order processing
- JWT-based authentication

## Requirements

- Python 3.9+
- Docker (for containerization)

## Installation

1. Clone the repository:

   \`\`\`bash
   git clone https://github.com/yourusername/ecommerce-api.git
   cd ecommerce-api
   \`\`\`

2. Install dependencies:

   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Run the server:

   \`\`\`bash
   uvicorn app.main:app --reload
   \`\`\`

## Running with Docker

1. Build the Docker image:

   \`\`\`bash
   docker-compose build
   \`\`\`

2. Start the services:

   \`\`\`bash
   docker-compose up
   \`\`\`

## Running Tests

To run tests, simply use:

\`\`\`bash
pytest
\`\`\`

## License

This project is licensed under the MIT License.
EOL

echo "Project structure created successfully!"

