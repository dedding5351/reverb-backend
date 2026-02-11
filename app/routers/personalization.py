from typing import List
from fastapi import APIRouter, Depends
from app.schemas.post import PostSchema
from app.services.personalization_service import PersonalizationService, get_personalization_service
from app.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(
    prefix="/personalization",
    tags=["personalization"]
)

class LikeRequest(BaseModel):
    post_id: str

@router.post("/likes")
def like_post(
    body: LikeRequest, 
    user: User = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    service.like_post(user.id, body.post_id)
    return {"status": "success", "message": "Post liked"}

@router.delete("/likes/{post_id}")
def unlike_post(
    post_id: str, 
    user: User = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    service.unlike_post(user.id, post_id)
    return {"status": "success", "message": "Post unliked"}

@router.get("/likes", response_model=List[PostSchema])
def get_liked_posts(
    user: User = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    return service.get_liked_posts(user.id)

# Bookmarks

class BookmarkRequest(BaseModel):
    post_id: str

@router.post("/bookmarks")
def bookmark_post(
    body: BookmarkRequest, 
    user: User = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    service.bookmark_post(user.id, body.post_id)
    return {"status": "success", "message": "Post bookmarked"}

@router.delete("/bookmarks/{post_id}")
def unbookmark_post(
    post_id: str, 
    user: User = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    service.unbookmark_post(user.id, post_id)
    return {"status": "success", "message": "Post unbookmarked"}

@router.get("/bookmarks", response_model=List[PostSchema])
def get_bookmarked_posts(
    user: User = Depends(get_current_user),
    service: PersonalizationService = Depends(get_personalization_service)
):
    return service.get_bookmarked_posts(user.id)
