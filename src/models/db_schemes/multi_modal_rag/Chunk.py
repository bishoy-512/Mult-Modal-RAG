from sqlalchemy import Column,Integer,String,ForeignKey,Index
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship
from .Base import Base
import uuid

class Chunk(Base):
    __tablename__ = "chunks"
    
    chunk_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chunk_uuid = Column(UUID(as_uuid = True), default=uuid.uuid4, unique=True, nullable=False)
    chunk_project_id = Column(String, ForeignKey("projects.project_id"))

    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_order = Column(Integer, nullable=False, autoincrement=True)
    
    project = relationship("Project", back_populates="chunks")

    __table_args__ = (Index("ix_chunk_project_id", chunk_project_id),)
