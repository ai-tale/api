from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.story import Story
from app.models.page import Page
from app.schemas.page import Page as PageSchema, PageUpdate, PageCreate, ImageGenerationRequest
from app.services import image_generator

router = APIRouter()

@router.get("/story/{story_id}", response_model=List[PageSchema])
async def read_story_pages(
    story_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pages for a specific story."""
    # Verify story exists and user has access
    story = db.query(Story).filter(Story.id == story_id).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story {story_id} not found"
        )
    
    # Verify ownership
    if story.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this story"
        )
    
    # Get pages
    pages = db.query(Page).filter(Page.story_id == story_id)\
        .order_by(Page.number).all()
    
    return pages

@router.get("/{page_id}", response_model=PageSchema)
async def read_page(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific page by ID."""
    # Get page
    page = db.query(Page).filter(Page.id == page_id).first()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page_id} not found"
        )
    
    # Verify user has access to the associated story
    story = db.query(Story).filter(Story.id == page.story_id).first()
    
    if story.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this page"
        )
    
    return page

@router.put("/{page_id}", response_model=PageSchema)
async def update_page(
    page_id: int,
    page_update: PageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a page."""
    # Get page
    page = db.query(Page).filter(Page.id == page_id).first()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page_id} not found"
        )
    
    # Verify user has access to the associated story
    story = db.query(Story).filter(Story.id == page.story_id).first()
    
    if story.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this page"
        )
    
    # Update page fields
    update_data = page_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(page, key, value)
    
    db.add(page)
    db.commit()
    db.refresh(page)
    
    return page

@router.post("", response_model=PageSchema)
async def create_page(
    page_data: PageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new page."""
    # Verify story exists and user has access
    story = db.query(Story).filter(Story.id == page_data.story_id).first()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story {page_data.story_id} not found"
        )
    
    # Verify ownership
    if story.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add pages to this story"
        )
    
    # Create page
    new_page = Page(
        number=page_data.number,
        content=page_data.content,
        image_prompt=page_data.image_prompt,
        story_id=page_data.story_id
    )
    
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    
    return new_page

@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a page."""
    # Get page
    page = db.query(Page).filter(Page.id == page_id).first()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page_id} not found"
        )
    
    # Verify user has access to the associated story
    story = db.query(Story).filter(Story.id == page.story_id).first()
    
    if story.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this page"
        )
    
    db.delete(page)
    db.commit()
    
    return None

async def _generate_image_task(
    page_id: int,
    prompt: str,
    style: str,
    db: Session
):
    """Background task for image generation."""
    try:
        # Get the page
        page = db.query(Page).filter(Page.id == page_id).first()
        if not page:
            return
        
        # Generate the image
        result = await image_generator.generate_image(prompt, style)
        
        # Update the page with image URL
        page.image_url = result["s3_url"] if result["s3_url"] else result["url"]
        db.add(page)
        db.commit()
        
    except Exception as e:
        # Log the error but don't update anything
        pass

@router.post("/{page_id}/generate-image", response_model=PageSchema)
async def generate_image(
    page_id: int,
    image_request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an image for a page."""
    # Get page
    page = db.query(Page).filter(Page.id == page_id).first()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page_id} not found"
        )
    
    # Verify user has access to the associated story
    story = db.query(Story).filter(Story.id == page.story_id).first()
    
    if story.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to generate images for this page"
        )
    
    # Update image prompt if provided
    if image_request.prompt:
        page.image_prompt = image_request.prompt
        db.add(page)
        db.commit()
        db.refresh(page)
    
    # Start background task for image generation
    background_tasks.add_task(
        _generate_image_task,
        page_id=page.id,
        prompt=page.image_prompt,
        style=image_request.style,
        db=db
    )
    
    return page 