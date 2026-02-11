from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.repositories.like import LikeRepository
from app.repositories.bookmark import BookmarkRepository
from app.models.post import Post

class PersonalizationService:
    def __init__(self, db: Session):
        self.repo = LikeRepository(db)
        self.bookmark_repo = BookmarkRepository(db)

    def like_post(self, user_id: str, post_id: str):
        if not self.repo.has_liked(user_id, post_id):
            self.repo.add_like(user_id, post_id)

    def unlike_post(self, user_id: str, post_id: str):
        self.repo.remove_like(user_id, post_id)

    def get_liked_posts(self, user_id: str) -> List[Post]:
        return self.repo.get_user_likes(user_id)

    # Bookmarks
    def bookmark_post(self, user_id: str, post_id: str):
        if not self.bookmark_repo.has_bookmarked(user_id, post_id):
            self.bookmark_repo.add_bookmark(user_id, post_id)

    def unbookmark_post(self, user_id: str, post_id: str):
        self.bookmark_repo.remove_bookmark(user_id, post_id)

    def get_bookmarked_posts(self, user_id: str) -> List[Post]:
        return self.bookmark_repo.get_user_bookmarks(user_id)

def get_personalization_service(db: Session = Depends(get_db)) -> PersonalizationService:
    return PersonalizationService(db)
