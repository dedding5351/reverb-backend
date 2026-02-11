from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.like import Like
from app.models.post import Post

class LikeRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_like(self, user_id: str, post_id: str) -> Like:
        like = Like(user_id=user_id, post_id=post_id)
        self.db.add(like)
        self.db.commit()
        return like

    def remove_like(self, user_id: str, post_id: str):
        like = self.db.query(Like).filter(
            Like.user_id == user_id, 
            Like.post_id == post_id
        ).first()
        if like:
            self.db.delete(like)
            self.db.commit()

    def has_liked(self, user_id: str, post_id: str) -> bool:
        return self.db.query(Like).filter(
            Like.user_id == user_id, 
            Like.post_id == post_id
        ).first() is not None

    def get_user_likes(self, user_id: str) -> List[Post]:
        # Returns the actual Post objects liked by the user
        return self.db.query(Post).join(Like).filter(Like.user_id == user_id).all()
