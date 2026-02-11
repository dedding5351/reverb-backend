from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=UserResponse)
def login_or_signup(
    user_data: UserCreate, 
    service: AuthService = Depends(get_auth_service)
):
    user = service.login_or_signup(user_data.phone_number)
    # Generate JWT
    access_token = service.create_access_token(user.id)
    
    return UserResponse(
        id=user.id,
        phone_number=user.phone_number,
        created_at=user.created_at,
        access_token=access_token,
        token_type="bearer"
    )
