from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.models.post import Post
from app.schemas.post import PostSchema
from app.services.post_service import PostService, get_post_service

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.get("/", response_model=List[PostSchema])
def get_posts(
    limit: int = 20, 
    offset: int = 0, 
    source_id: Optional[str] = None,
    service: PostService = Depends(get_post_service)
):
    return service.get_posts(limit=limit, offset=offset, source_id=source_id)

@router.get("/{post_id}", response_model=PostSchema)
def get_post(post_id: str, service: PostService = Depends(get_post_service)):
    post = service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
