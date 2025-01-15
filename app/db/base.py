from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
import uuid

# Create declarative base model
Base = declarative_base()

class BaseModel(Base):
    """Base model class that includes common fields and methods."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    @classmethod
    def get_by_id(cls, db_session, id):
        """Get a record by its ID."""
        return db_session.query(cls).filter(cls.id == id).first()
        
    @classmethod
    def get_all(cls, db_session, skip=0, limit=100):
        """Get all records with pagination."""
        return db_session.query(cls).offset(skip).limit(limit).all()
        
    @classmethod
    def create(cls, db_session, **kwargs):
        """Create a new record."""
        obj = cls(**kwargs)
        db_session.add(obj)
        db_session.commit()
        db_session.refresh(obj)
        return obj
        
    def update(self, db_session, **kwargs):
        """Update an existing record."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        db_session.commit()
        db_session.refresh(self)
        return self
        
    def delete(self, db_session):
        """Delete a record."""
        db_session.delete(self)
        db_session.commit()
        return True 