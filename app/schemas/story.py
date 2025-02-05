from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from enum import Enum

from app.models.story import StoryStatus

# Story schema
class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None
    language: Optional[str] = "en"
    theme: Optional[str] = None
    age_group: Optional[str] = None

# Schema for creating a new story
class StoryCreate(StoryBase):
    generation_parameters: Optional[Dict[str, Any]] = None

# Schema for updating story
class StoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    age_group: Optional[str] = None
    status: Optional[StoryStatus] = None
    generation_parameters: Optional[Dict[str, Any]] = None

# Schema for story output
class Story(StoryBase):
    id: int
    content: Optional[str] = None
    status: StoryStatus
    user_id: int
    generation_parameters: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
        
# Schema for story generation request
class StoryGenerationRequest(BaseModel):
    title: Optional[str] = None
    theme: Optional[str] = None
    age_group: Optional[str] = "children"
    language: Optional[str] = "en"
    characters: Optional[List[str]] = None
    setting: Optional[str] = None
    mood: Optional[str] = "happy"
    length: Optional[str] = "medium"  # short, medium, long
    style: Optional[str] = "fairy tale"
    custom_prompt: Optional[str] = None
    
    @validator('language')
    def language_must_be_supported(cls, v):
        supported_languages = ["en", "es", "fr", "de", "zh", "ja"]
        if v not in supported_languages:
            raise ValueError(f"Language '{v}' not supported. Choose from: {', '.join(supported_languages)}")
        return v 