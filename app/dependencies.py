from fastapi import Header, HTTPException, Depends, status
from typing import Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService, get_auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        user_id = auth_service.verify_token(token)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid User ID")
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    if not token:
        print("DEBUG: get_current_user_optional - No token provided")
        return None
    try:
        user_id = auth_service.verify_token(token)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"DEBUG: get_current_user_optional - User not found for ID: {user_id}")
        return user
    except Exception as e:
        print(f"DEBUG: get_current_user_optional - Exception: {e}")
        return None
