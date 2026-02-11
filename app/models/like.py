from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from app.database import Base
from datetime import datetime

class Like(Base):
    __tablename__ = "likes"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # basic save helper if needed, but repo will likely handle add/delete
