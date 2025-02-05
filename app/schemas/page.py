from pydantic import BaseModel
from typing import Optional

# Page schema
class PageBase(BaseModel):
    number: int
    content: str
    image_prompt: Optional[str] = None

# Schema for creating a new page
class PageCreate(PageBase):
    story_id: int

# Schema for updating page
class PageUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None

# Schema for page output
class Page(PageBase):
    id: int
    story_id: int
    image_url: Optional[str] = None
    
    class Config:
        orm_mode = True

# Schema for image generation request
class ImageGenerationRequest(BaseModel):
    prompt: str
    page_id: Optional[int] = None
    style: Optional[str] = "digital art"
    size: Optional[str] = "1024x1024" 