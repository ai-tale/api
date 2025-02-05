from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

class User(BaseModel):
    """User model for the application."""
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    stories = relationship("Story", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>" 