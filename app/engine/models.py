from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import List, Optional

class PostMetadata(BaseModel):
    title: str
    url: HttpUrl
    description: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    published_date: Optional[datetime] = None
    site_name: Optional[str] = None
    image_url: Optional[HttpUrl] = None
