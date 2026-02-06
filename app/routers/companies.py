from fastapi import APIRouter, Depends
from typing import List
from app.schemas.source import SourceSchema
from app.services.source_service import SourceService, get_source_service

router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)

@router.get("/", response_model=List[SourceSchema])
def get_companies(service: SourceService = Depends(get_source_service)):
    return service.get_sources()
