from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import Session
from app.database import Base
from datetime import datetime
import uuid

# SQLAlchemy Model (Active Record)
class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    url = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    authors = Column(JSON, default=list)  # Storing list of strings as JSON
    published_date = Column(DateTime, nullable=True)
    site_name = Column(String, nullable=True)
    source_id = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def save(self, db: Session):
        # Simple DB Write (Active Record)
        db.add(self)
        db.commit()
        db.refresh(self)
        return self


