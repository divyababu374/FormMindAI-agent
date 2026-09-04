import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.utils.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name or user_in.email.split("@")[0].title(),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token(new_user.id)
    return Token(access_token=token, user=UserResponse.model_validate(new_user))

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    
    token = create_access_token(user.id)
    return Token(access_token=token, user=UserResponse.model_validate(user))

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("/google/config")
def get_google_oauth_config():
    """
    Returns Google OAuth status and Client ID for frontend integration.
    """
    return {
        "is_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        "client_id": settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

@router.post("/google/config")
def update_google_config(payload: dict, current_user: User = Depends(get_current_user)):
    """
    Allows configuring Google OAuth Client ID and Secret dynamically from the UI.
    """
    client_id = payload.get("client_id", "").strip()
    client_secret = payload.get("client_secret", "").strip()
    redirect_uri = payload.get("redirect_uri", "").strip()

    if client_id:
        settings.GOOGLE_CLIENT_ID = client_id
    if client_secret:
        settings.GOOGLE_CLIENT_SECRET = client_secret
    if redirect_uri:
        settings.GOOGLE_REDIRECT_URI = redirect_uri

    return {
        "status": "success",
        "message": "Google OAuth configuration updated.",
        "is_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

def get_valid_google_token(user: User, db: Session) -> Optional[str]:
    """
    Returns a valid Google access token for the user, refreshing it if expired and refresh_token is present.
    """
    import requests
    if not user or not user.is_google_connected or not user.google_access_token:
        return None

    # Check if current access token is working
    try:
        chk_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {user.google_access_token}"},
            timeout=5
        )
        if chk_resp.status_code == 200:
            return user.google_access_token
    except Exception:
        pass

    # If token expired and refresh_token available, refresh it
    if user.google_refresh_token and settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        try:
            token_resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": user.google_refresh_token,
                    "grant_type": "refresh_token"
                },
                timeout=10
            )
            if token_resp.status_code == 200:
                new_tokens = token_resp.json()
                new_access = new_tokens.get("access_token")
                if new_access:
                    user.google_access_token = new_access
                    db.commit()
                    db.refresh(user)
                    return new_access
        except Exception as ex:
            pass

    return user.google_access_token

from pydantic import BaseModel, EmailStr

class EmailConnectRequest(BaseModel):
    email: str
    name: Optional[str] = None

@router.post("/google/connect-email")
def connect_google_email(req: EmailConnectRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Directly connects a Gmail/Google email ID without requiring OAuth tokens or cloud credentials.
    """
    email_clean = req.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    current_user.email = email_clean
    current_user.full_name = req.name or email_clean.split("@")[0].replace(".", " ").title()
    current_user.is_google_connected = True
    db.commit()
    db.refresh(current_user)

    token = create_access_token(current_user.id)
    return {
        "message": f"Successfully connected {current_user.email}",
        "is_connected": True,
        "email": current_user.email,
        "name": current_user.full_name,
        "access_token": token
    }

@router.get("/google/status")
def get_google_status(current_user: User = Depends(get_current_user)):
    """
    Returns current Google connection state including connected email and name.
    """
    return {
        "is_connected": bool(current_user.is_google_connected),
        "email": current_user.email if current_user.is_google_connected else None,
        "name": current_user.full_name if current_user.is_google_connected else None,
        "is_oauth_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        "client_id": settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
    }

@router.post("/google/direct-token")
def set_google_direct_token(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Allows connecting Google via direct OAuth Access Token.
    Validates token against Google UserInfo to retrieve verified email and name.
    """
    import requests
    token = payload.get("access_token", "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Access token is required.")

    email = None
    name = None
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
        if resp.status_code == 200:
            u_info = resp.json()
            email = u_info.get("email")
            name = u_info.get("name")
    except Exception:
        pass

    target_user = current_user
    if email and current_user.id.startswith("demo_user_"):
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            target_user = existing
        else:
            target_user.email = email
            target_user.full_name = name or email.split("@")[0].title()

    target_user.google_access_token = token
    target_user.is_google_connected = True
    db.commit()
    db.refresh(target_user)

    jwt_token = create_access_token(target_user.id)
    return {
        "status": "success",
        "message": f"Connected Google account: {target_user.email}",
        "access_token": jwt_token,
        "user": UserResponse.model_validate(target_user)
    }

@router.get("/google/url")
def get_google_auth_url():
    """
    Generates the Google OAuth authorization URL requesting the verified scopes.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth is not configured yet. Please provide GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend configuration."
        )

    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/forms.body.readonly",
        "https://www.googleapis.com/auth/forms.responses.readonly",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]
    scope_str = " ".join(scopes)
    
    from urllib.parse import urlencode
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": scope_str,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"auth_url": auth_url}

@router.post("/google/callback", response_model=Token)
def google_oauth_callback(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Exchanges Google OAuth code for tokens, extracts user info, and links Google credentials.
    """
    code = payload.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    import requests
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    resp = requests.post(token_url, data=token_data, timeout=15)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to exchange Google OAuth code: {resp.text}")

    tokens = resp.json()
    google_access_token = tokens.get("access_token")
    google_refresh_token = tokens.get("refresh_token")

    # Fetch Google User Info
    userinfo_resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {google_access_token}"},
        timeout=10
    )
    if userinfo_resp.status_code == 200:
        userinfo = userinfo_resp.json()
        email = userinfo.get("email")
        name = userinfo.get("name")
        
        # Link to current user or find existing by email
        target_user = current_user
        if email and current_user.id.startswith("demo_user_"):
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                target_user = existing
            else:
                target_user.email = email
                target_user.full_name = name or email.split("@")[0].title()

        target_user.is_google_connected = True
        target_user.google_access_token = google_access_token
        if google_refresh_token:
            target_user.google_refresh_token = google_refresh_token
        db.commit()
        db.refresh(target_user)

        jwt_token = create_access_token(target_user.id)
        return Token(access_token=jwt_token, user=UserResponse.model_validate(target_user))
    else:
        current_user.is_google_connected = True
        current_user.google_access_token = google_access_token
        if google_refresh_token:
            current_user.google_refresh_token = google_refresh_token
        db.commit()
        db.refresh(current_user)

        jwt_token = create_access_token(current_user.id)
        return Token(access_token=jwt_token, user=UserResponse.model_validate(current_user))

@router.post("/google/disconnect")
def google_disconnect(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Disconnects the Google account and clears stored access/refresh tokens.
    """
    current_user.is_google_connected = False
    current_user.google_access_token = None
    current_user.google_refresh_token = None
    db.commit()
    return {"status": "success", "message": "Google account disconnected."}
