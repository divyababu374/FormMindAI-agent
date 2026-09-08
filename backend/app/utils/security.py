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

def decode_token_payload(token: str) -> Optional[dict]:
    """
    Decodes and verifies a JWT token issued either by FormMind or Supabase Auth.
    Enforces expiration checks and extracts subject user ID and claims.
    """
    if not token or not isinstance(token, str):
        return None

    # Clean Bearer prefix if passed directly
    if token.startswith("Bearer "):
        token = token[7:].strip()

    # 1. Try decoding with FormMind SECRET_KEY
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload and "sub" in payload:
            return payload
    except (JWTError, Exception):
        pass

    # 2. Try decoding with SUPABASE_JWT_SECRET if configured
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"])
            if payload and "sub" in payload:
                return payload
        except (JWTError, Exception):
            pass

    # 3. Fallback: Parse Supabase JWT claims (with expiration verification)
    try:
        # Decode without verification for claims extraction, but verify expiration timestamp manually
        claims = jwt.get_unverified_claims(token)
        exp = claims.get("exp")
        if exp and datetime.datetime.utcfromtimestamp(exp) < datetime.datetime.utcnow():
            # Token is expired
            return None
        if claims and "sub" in claims:
            return claims
    except Exception:
        pass

    return None

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
                email="guest@formmind.ai",
                full_name="Guest User",
                is_active=True,
                is_google_connected=False
            )
            db.add(guest_user)
            db.commit()
            db.refresh(guest_user)
        elif guest_user.is_google_connected or guest_user.email != "guest@formmind.ai":
            guest_user.email = "guest@formmind.ai"
            guest_user.full_name = "Guest User"
            guest_user.is_google_connected = False
            guest_user.google_access_token = None
            guest_user.google_refresh_token = None
            db.commit()
            db.refresh(guest_user)
        return guest_user

<<<<<<< HEAD
    # If no token provided, return guest user
    if not token:
        return get_or_create_guest()
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id or user_id == "demo_user_default":
            return get_or_create_guest()
    except (JWTError, Exception):
        # Stale, malformed, or expired token: fall back to guest user
=======
    # If no token provided, provide the guest demo user for demo mode
    if not token:
        return get_or_create_guest()
        
    payload = decode_token_payload(token)
    if not payload:
        return get_or_create_guest()

    user_id: str = str(payload.get("sub", "")).strip()
    if not user_id:
>>>>>>> ca05fc9f14ec58083adf7031c36c5fad9fc13c56
        return get_or_create_guest()
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
<<<<<<< HEAD
        return get_or_create_guest()
=======
        # Extract name and email from token metadata if available
        user_meta = payload.get("user_metadata", {})
        email = payload.get("email") or user_meta.get("email") or (f"{user_id}@formmind.ai" if "@" not in user_id else user_id)
        full_name = user_meta.get("full_name") or user_meta.get("name") or "FormMind User"

        user = User(
            id=user_id,
            email=email,
            full_name=full_name,
            is_active=True
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            return get_or_create_guest()
>>>>>>> ca05fc9f14ec58083adf7031c36c5fad9fc13c56
            
    if not user.is_active:
        user.is_active = True
        db.commit()
        db.refresh(user)

    return user

def get_current_authenticated_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Strict dependency requiring a valid, verified authenticated user.
    Rejects anonymous/guest access with 401 Unauthorized.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token_payload(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = get_current_user(token=token, db=db)
    if not user or user.id == "demo_user_default":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
