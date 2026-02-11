from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
import jwt
from datetime import datetime, timedelta
from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def login_or_signup(self, phone_number: str) -> User:
        user = self.repo.get_by_phone(phone_number)
        if user:
            return user
        new_user = User(phone_number=phone_number)
        return self.repo.create_or_update(new_user)
    
    def create_access_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": user_id, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user_id
        except jwt.PyJWTError:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)
