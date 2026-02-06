from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.post import Post
from app.repositories.post import PostRepository
from app.database import get_db

class PostService:
    def __init__(self, db: Session):
        self.repo = PostRepository(db)

    def get_posts(self, limit: int = 20, offset: int = 0, source_id: Optional[str] = None) -> List[Post]:
        return self.repo.list(limit=limit, offset=offset, source_id=source_id)

    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        # Repo doesn't have get_by_id yet, only get_by_url. 
        # We need to add get_by_id to repo or find it in list.
        # Let's add get_by_id to repo in next step or use filter here (inefficient)
        # For now, assuming we will add it to repo.
        return self.repo.get_by_id(post_id)

def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)
