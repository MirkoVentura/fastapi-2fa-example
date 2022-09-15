from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    fullname = Column(String)
    email = Column(String)
    need_otp = Column(Boolean)
    otp_secret = Column(String)
