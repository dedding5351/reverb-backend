from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session = None):
        from app.database import SessionLocal
        self.db = db or SessionLocal()

    def get_by_phone(self, phone_number: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone_number == phone_number).first()

    def create_or_update(self, user: User) -> User:
        # Check if exists
        existing = self.get_by_phone(str(user.phone_number))
        
        if existing:
            # Update fields if we had any other fields. 
            # For now just return existing or update timestamp?
            # Let's just return existing for login flow
            return existing
        else:
            # Persist new
            return user.save(self.db)
