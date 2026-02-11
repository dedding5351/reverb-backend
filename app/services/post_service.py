from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.post import Post
from app.repositories.post import PostRepository
from app.database import get_db
from app.services.personalization_service import PersonalizationService

class PostService:
    def __init__(self, db: Session):
        self.repo = PostRepository(db)
        self.personalization_service = PersonalizationService(db)

    def get_posts(self, limit: int = 20, offset: int = 0, source_id: Optional[str] = None, sort_by: str = "published_date", sort_order: str = "desc", user_id: Optional[str] = None, liked_only: bool = False, bookmarked_only: bool = False) -> List[Post]:
        filter_ids = None

        if user_id and (liked_only or bookmarked_only):
            # Fetch relevant IDs
            target_ids = set()
            if liked_only:
                liked = self.personalization_service.get_liked_posts(user_id)
                target_ids.update(p.id for p in liked)
            
            if bookmarked_only:
                # If both are true, should it be union or intersection? 
                # Let's assume Union for "My Saved Stuff" or Intersection?
                # Usually these are separate tabs. If both, maybe Intersection?
                # Let's do Union for now if multiple, or just handle them.
                # Actually, if I say "Liked Only" AND "Bookmarked Only", I probably want posts that are BOTH.
                bookmarked = self.personalization_service.get_bookmarked_posts(user_id)
                b_ids = {p.id for p in bookmarked}
                if liked_only:
                    target_ids = target_ids.intersection(b_ids)
                else:
                    target_ids = b_ids
            
            filter_ids = list(target_ids)
            if not filter_ids:
                return [] # No posts match criteria

        posts = self.repo.list(limit=limit, offset=offset, source_id=source_id, sort_by=sort_by, sort_order=sort_order, ids=filter_ids)
        
        if user_id:
            # We need to check which of these posts are liked.
            # Efficient way: Get all liked post IDs for user, or check individually?
            # Better: Get all liked post IDs for this user
            liked_posts = self.personalization_service.get_liked_posts(user_id)
            liked_ids = {p.id for p in liked_posts}
            
            bookmarked_posts = self.personalization_service.get_bookmarked_posts(user_id)
            bookmarked_ids = {p.id for p in bookmarked_posts}
            
            for post in posts:
                # Dynamically set attribute for Pydantic (since it's not a DB column on Post)
                # We simply attach it to the object instance
                post.is_liked = post.id in liked_ids
                post.is_bookmarked = post.id in bookmarked_ids
        
        return posts

    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        # Repo doesn't have get_by_id yet, only get_by_url. 
        # We need to add get_by_id to repo or find it in list.
        # Let's add get_by_id to repo in next step or use filter here (inefficient)
        # For now, assuming we will add it to repo.
        return self.repo.get_by_id(post_id)

def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)
