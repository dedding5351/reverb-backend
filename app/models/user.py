from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Session
from app.database import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def save(self, db: Session):
        # Simple DB Write (Active Record)
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
