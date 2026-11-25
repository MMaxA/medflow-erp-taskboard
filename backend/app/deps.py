from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import decode_token
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    payload=decode_token(token)
    if not payload or not payload.get("sub"): raise HTTPException(status_code=401,detail="Invalid or expired token",headers={"WWW-Authenticate":"Bearer"})
    user=db.query(User).filter(User.email==payload["sub"]).first()
    if not user or not user.is_active: raise HTTPException(status_code=401,detail="Inactive user")
    return user
def require_roles(*roles):
    def checker(user:User=Depends(current_user)):
        if user.role not in roles: raise HTTPException(status_code=403,detail="Insufficient permissions")
        return user
    return checker
