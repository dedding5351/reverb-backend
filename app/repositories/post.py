from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.post import Post

class PostRepository:
    def __init__(self, db: Session = None):
        from app.database import SessionLocal
        self.db = db or SessionLocal()

    def create_or_update(self, post: Post) -> Post:
        # Check if exists (Business Logic / Upsert)
        existing = self.db.query(Post).filter(Post.url == str(post.url)).first()
        
        if existing:
            # Update existing fields
            existing.title = post.title
            existing.description = post.description
            existing.authors = post.authors
            existing.published_date = post.published_date
            existing.site_name = post.site_name
            existing.source_id = post.source_id
            existing.image_url = str(post.image_url) if post.image_url else None
            existing.content = post.content
            
            # Persist update
            return existing.save(self.db)
        else:
            # Persist new
            return post.save(self.db)

    def get_by_url(self, url: str) -> Optional[Post]:
        return self.db.query(Post).filter(Post.url == url).first()

    def get_by_id(self, post_id: str) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def list(self, limit: int = 20, offset: int = 0, source_id: Optional[str] = None, sort_by: str = "published_date", sort_order: str = "desc", ids: Optional[List[str]] = None) -> List[Post]:
        query = self.db.query(Post)
        
        if ids is not None:
             query = query.filter(Post.id.in_(ids))

        if source_id:
            query = query.filter(Post.source_id == source_id)
            
        # Sorting
        if hasattr(Post, sort_by):
            field = getattr(Post, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(field.desc())
            else:
                query = query.order_by(field.asc())
        else:
            # Fallback default
            query = query.order_by(Post.published_date.desc())
            
        return query.offset(offset).limit(limit).all()
