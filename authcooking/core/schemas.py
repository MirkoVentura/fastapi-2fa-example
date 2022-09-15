from typing import List
from pydantic import BaseModel


class UserInfoBase(BaseModel):
    username: str
    fullname: str
    email: str


class UserCreate(UserInfoBase):
    password: str
    need_otp: bool


class UserInfo(UserInfoBase):
    id: int

    class Config:
        orm_mode = True


class UserAuthenticate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    message: str