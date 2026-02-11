from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.models.post import Post
from app.schemas.post import PostSchema
from app.services.post_service import PostService, get_post_service

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

from app.dependencies import get_current_user_optional
from app.models.user import User

@router.get("/", response_model=List[PostSchema])
def get_posts(
    limit: int = 20, 
    offset: int = 0, 
    source_id: Optional[str] = None,
    sort_by: str = "published_date",
    sort_order: str = "desc",
    liked_only: bool = False,
    bookmarked_only: bool = False,
    user: Optional[User] = Depends(get_current_user_optional),
    service: PostService = Depends(get_post_service)
):
    user_id = user.id if user else None
    
    if (liked_only or bookmarked_only) and not user_id:
         raise HTTPException(status_code=401, detail="Authentication required for filtering by likes/bookmarks")

    return service.get_posts(
        limit=limit, 
        offset=offset, 
        source_id=source_id, 
        sort_by=sort_by, 
        sort_order=sort_order,
        user_id=user_id,
        liked_only=liked_only,
        bookmarked_only=bookmarked_only
    )

@router.get("/{post_id}", response_model=PostSchema)
def get_post(post_id: str, service: PostService = Depends(get_post_service)):
    post = service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
