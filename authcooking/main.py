from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import pyotp
from core import models, schemas, crud, auth
from core.database import DBInit
from datetime import datetime, timedelta




ACCESS_TOKEN_EXPIRE_MINUTES=15

def get_main_db():
    session = None
    try:
        session = DBInit("sqlite:///./main.db").get_session()
        session = session()
        yield session
    finally:
        session.close()

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"msg" : "pong"}

@app.post("/users/register", status_code=201, response_model=schemas.UserInfo, tags=["users"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_main_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=409, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/users/auth", response_model=schemas.Token, tags=["users"])
def authenticate_user(user: schemas.UserAuthenticate, db: Session = Depends(get_main_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user is None:
        raise HTTPException(status_code=403, detail="Username or password is incorrect")
    else:
        is_password_correct = auth.check_username_password(db, user)
        if is_password_correct is False:
            raise HTTPException(status_code=403, detail="Username or password is incorrect")
        else:
            if db_user.need_otp is False:
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = auth.encode_jwt_token(
                    data={"sub": user.username}, expires_delta=access_token_expires)
                return {"access_token": access_token, "token_type": "Bearer", "message": f'welcome {db_user.fullname}'}
            else:
                totp = pyotp.TOTP(db_user.otp_secret, interval=60)
                otp = totp.now()
                return {"access_token": f'{otp}', "token_type": "OTP_CHALLANGE", "message": "We sent an email with the otp, go check it" }

@app.post("/users/auth/verify-otp", response_model=schemas.Token, tags=["users"])
def validate_otp(user: schemas.UserAuthenticate, db: Session = Depends(get_main_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(
            status_code=403,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    totp = pyotp.TOTP(db_user.otp_secret, interval = 60)
    if totp.verify(user.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.encode_jwt_token(
                    data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "Bearer", "message": f'welcome {db_user.fullname}'}
    else :
        raise HTTPException(status_code=403, detail="Username or otp is incorrect")
