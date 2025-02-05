from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel

class StoryStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class Story(BaseModel):
    """Story model for the application."""
    __tablename__ = "stories"
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    language = Column(String(10), default="en")
    theme = Column(String(100), nullable=True)
    age_group = Column(String(50), nullable=True)
    status = Column(Enum(StoryStatus), default=StoryStatus.DRAFT)
    generation_parameters = Column(Text, nullable=True)  # JSON string of parameters
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="stories")
    pages = relationship("Page", back_populates="story", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Story {self.title}>" 