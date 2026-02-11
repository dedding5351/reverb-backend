from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import List, Optional

class PostSchema(BaseModel):
    id: Optional[str] = None
    title: str
    url: HttpUrl
    description: Optional[str] = None
    authors: Optional[List[str]] = Field(default_factory=list)
    published_date: Optional[datetime] = None
    site_name: Optional[str] = None
    source_id: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    content: Optional[str] = None
    embedding: Optional[List[float]] = None
    read_time_minutes: Optional[int] = None
    created_at: Optional[datetime] = None
    is_liked: bool = False
    is_bookmarked: bool = False

    class Config:
        from_attributes = True
