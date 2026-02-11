from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.services.gemini_service import get_gemini_service, GeminiService
from app.models.post import Post
from typing import List, Tuple
import logging
from dotenv import load_dotenv
import numpy as np

load_dotenv()

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.gemini_service = get_gemini_service()

    async def search(self, query: str, limit: int = 5) -> List[Tuple[Post, float]]:
        """
        Semantic search for posts using the vector database.
        Returns a list of (Post, distance) tuples.
        """
        db: Session = SessionLocal()
        try:
            # 1. Generate embedding for query
            query_embedding = await self.gemini_service.generate_embedding(query)
            
            # Ensure list for pgvector
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # 2. Search using pgvector
            # Post.embedding.l2_distance(query_embedding)
            results = db.query(Post, Post.embedding.l2_distance(query_embedding).label("distance")) \
                .order_by(Post.embedding.l2_distance(query_embedding)) \
                .limit(limit) \
                .all()
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
        finally:
            db.close()

    async def get_similar_posts(self, post_id: str, limit: int = 5) -> List[Tuple[Post, float]]:
        """
        Finds posts similar to a given post ID.
        """
        db: Session = SessionLocal()
        try:
            # 1. Get embedding for the post
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post or post.embedding is None:
                logger.warning(f"Post {post_id} not found or has no embedding.")
                return []
            
            post_embedding = post.embedding
             # Ensure list for pgvector
            if hasattr(post_embedding, "tolist"):
                post_embedding = post_embedding.tolist()

            # 2. Search
            # Exclude self
            results = db.query(Post, Post.embedding.l2_distance(post_embedding).label("distance")) \
                .filter(Post.id != post_id) \
                .order_by(Post.embedding.l2_distance(post_embedding)) \
                .limit(limit) \
                .all()
            
            return results

        except Exception as e:
            logger.error(f"Similar posts search failed: {e}")
            return []
        finally:
            db.close()

def get_search_service() -> SearchService:
    return SearchService()
