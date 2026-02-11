from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    phone_number: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    created_at: datetime
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

    class Config:
        from_attributes = True
