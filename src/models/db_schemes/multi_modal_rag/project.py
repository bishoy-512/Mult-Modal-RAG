from sqlalchemy import Column,Integer,String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .Base import Base
import uuid

class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(String, primary_key = True, nullable = False)
    project_uuid = Column(UUID(as_uuid = True), nullable = False, unique = True, default = uuid.uuid4)
    
    chunks = relationship("Chunk" , back_populates="project")
