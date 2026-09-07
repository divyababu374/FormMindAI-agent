import datetime
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    from app.models.user import User
    
    def get_or_create_guest():
        guest_user = db.query(User).filter(User.id == "demo_user_default").first()
        if not guest_user:
            guest_user = User(
                id="demo_user_default",
                email="demo@formmind.ai",
                full_name="FormMind Explorer",
                is_active=True
            )
            db.add(guest_user)
            db.commit()
            db.refresh(guest_user)
        return guest_user

    # If no token provided, we provide a persistent default/guest demo user
    if not token:
        return get_or_create_guest()
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            return get_or_create_guest()
    except (JWTError, Exception):
        # Stale, malformed, or expired token: fall back gracefully to guest user
        return get_or_create_guest()
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        # Auto-heal: If user record was wiped or db re-initialized, re-create user seamlessly
        user = User(
            id=user_id,
            email=f"{user_id}@formmind.ai" if "@" not in user_id else user_id,
            full_name="FormMind Explorer",
            is_active=True
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            return get_or_create_guest()
            
    if not user.is_active:
        user.is_active = True
        db.commit()
        db.refresh(user)

    return user
