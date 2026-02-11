from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.bookmark import Bookmark
from app.models.post import Post

class BookmarkRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_bookmark(self, user_id: str, post_id: str) -> Bookmark:
        bookmark = Bookmark(user_id=user_id, post_id=post_id)
        self.db.add(bookmark)
        self.db.commit()
        return bookmark

    def remove_bookmark(self, user_id: str, post_id: str):
        bookmark = self.db.query(Bookmark).filter(
            Bookmark.user_id == user_id, 
            Bookmark.post_id == post_id
        ).first()
        if bookmark:
            self.db.delete(bookmark)
            self.db.commit()

    def has_bookmarked(self, user_id: str, post_id: str) -> bool:
        return self.db.query(Bookmark).filter(
            Bookmark.user_id == user_id, 
            Bookmark.post_id == post_id
        ).first() is not None

    def get_user_bookmarks(self, user_id: str) -> List[Post]:
        # Returns the actual Post objects bookmarked by the user
        return self.db.query(Post).join(Bookmark).filter(Bookmark.user_id == user_id).all()
