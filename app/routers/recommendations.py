from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.post import PostSchema
from app.services.search_service import get_search_service

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

@router.get("/similar/{post_id}", response_model=List[PostSchema])
async def get_similar_posts(post_id: str, limit: int = 3):
    """
    Get a list of posts similar to the provided post ID.
    Default limit is 3.
    """
    search_service = get_search_service()
    
    similar_posts_with_distance = await search_service.get_similar_posts(post_id, limit=limit)
    
    # Unpack tuples (Post, distance) -> [Post]
    posts = [post for post, distance in similar_posts_with_distance]
    
    return posts
