from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

class Page(BaseModel):
    """Page model for story pages."""
    __tablename__ = "pages"
    
    number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    image_prompt = Column(Text, nullable=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    
    # Relationships
    story = relationship("Story", back_populates="pages")
    
    def __repr__(self):
        return f"<Page {self.number} of Story {self.story_id}>"
    
    class Config:
        orm_mode = True 