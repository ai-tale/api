from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import json
from typing import List, Optional

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.story import Story, StoryStatus
from app.schemas.story import Story as StorySchema, StoryCreate, StoryUpdate, StoryGenerationRequest
from app.services import story_generator

router = APIRouter()

@router.post("", response_model=StorySchema)
async def create_story(
    story_data: StoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new story."""
    # Create story in database
    generation_params = None
    if story_data.generation_parameters:
        generation_params = json.dumps(story_data.generation_parameters)
        
    new_story = Story(
        title=story_data.title,
        description=story_data.description,
        language=story_data.language,
        theme=story_data.theme,
        age_group=story_data.age_group,
        status=StoryStatus.DRAFT,
        generation_parameters=generation_params,
        user_id=current_user.id
    )
    
    db.add(new_story)
    db.commit()
    db.refresh(new_story)
    
    return new_story

@router.get("", response_model=List[StorySchema])
async def read_stories(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all stories for the current user."""
    stories = db.query(Story).filter(Story.user_id == current_user.id)\
        .offset(skip).limit(limit).all()
    
    return stories

@router.get("/{story_id}", response_model=StorySchema)
async def read_story(
    story_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific story by ID."""
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
    
    return story

@router.put("/{story_id}", response_model=StorySchema)
async def update_story(
    story_id: int,
    story_update: StoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a story."""
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
            detail="Not authorized to modify this story"
        )
    
    # Update story fields
    update_data = story_update.dict(exclude_unset=True)
    
    # Handle generation parameters separately
    if "generation_parameters" in update_data and update_data["generation_parameters"] is not None:
        update_data["generation_parameters"] = json.dumps(update_data["generation_parameters"])
    
    for key, value in update_data.items():
        setattr(story, key, value)
    
    db.add(story)
    db.commit()
    db.refresh(story)
    
    return story

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a story."""
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
            detail="Not authorized to delete this story"
        )
    
    db.delete(story)
    db.commit()
    
    return None

async def _generate_story_task(
    story_id: int,
    parameters: dict,
    db: Session
):
    """Background task for story generation."""
    try:
        # Get the story
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            return
        
        # Update status to generating
        story.status = StoryStatus.GENERATING
        db.add(story)
        db.commit()
        
        # Generate the story
        result = await story_generator.generate_story(parameters)
        
        # Update the story with generated content
        story.content = result["full_text"]
        story.status = StoryStatus.COMPLETED
        db.add(story)
        db.commit()
        
        # Create pages for the story
        from app.models.page import Page
        
        for page_data in result["pages"]:
            page = Page(
                number=page_data["number"],
                content=page_data["content"],
                image_prompt=page_data["image_prompt"],
                story_id=story_id
            )
            db.add(page)
        
        db.commit()
        
    except Exception as e:
        # Update status to failed
        story = db.query(Story).filter(Story.id == story_id).first()
        if story:
            story.status = StoryStatus.FAILED
            db.add(story)
            db.commit()

@router.post("/{story_id}/generate", response_model=StorySchema)
async def generate_story(
    story_id: int,
    generation_params: StoryGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate content for a story."""
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
            detail="Not authorized to generate content for this story"
        )
    
    # Check if story is already generating
    if story.status == StoryStatus.GENERATING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story is already being generated"
        )
    
    # Update story parameters
    parameters = generation_params.dict()
    story.generation_parameters = json.dumps(parameters)
    
    # If title is provided in parameters but not in story, use it
    if not story.title and parameters.get("title"):
        story.title = parameters["title"]
    
    if parameters.get("title") is None:
        parameters["title"] = story.title
    
    # Update theme and age group if provided
    if parameters.get("theme") and not story.theme:
        story.theme = parameters["theme"]
    
    if parameters.get("age_group") and not story.age_group:
        story.age_group = parameters["age_group"]
    
    # Set status to generating
    story.status = StoryStatus.GENERATING
    db.add(story)
    db.commit()
    db.refresh(story)
    
    # Start background task for generation
    background_tasks.add_task(
        _generate_story_task,
        story_id=story.id,
        parameters=parameters,
        db=db
    )
    
    return story 