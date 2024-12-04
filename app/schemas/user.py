from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserDelete(BaseModel):
    username: str
    password: str
    double_check_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
