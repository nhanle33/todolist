from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import TagCreate, TagUpdate, TagResponse
from app.services.tag import TagService, PaginatedTagResponse
from app.db import get_db, User
from app.routers.todo import get_current_user

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=TagResponse, status_code=201)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tag"""
    service = TagService(db)
    return service.create_tag(tag)


@router.get("", response_model=PaginatedTagResponse)
def list_tags(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tags"""
    service = TagService(db)
    return service.list_tags(limit, offset)


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a tag by id"""
    service = TagService(db)
    tag = service.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a tag"""
    service = TagService(db)
    tag = service.update_tag(tag_id, tag_update)
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a tag"""
    service = TagService(db)
    success = service.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")
    return None
