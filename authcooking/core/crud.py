from sqlalchemy.orm import Session
from . import models, schemas
from .security import pwd_context
import pyotp

def get_user_by_username(db: Session, username: str):
    return db.query(models.UserInfo).filter(models.UserInfo.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.UserInfo(
        username=user.username,
        password=hashed_password,
        fullname=user.fullname,
        email = user.email,
        need_otp = user.need_otp,
        otp_secret = get_seed())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_seed():
    return pyotp.random_base32()
