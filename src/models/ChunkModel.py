from .BaseModel import BaseModel
from .db_schemes import Chunk
from sqlalchemy.future import select
from sqlalchemy import delete, func

class ChunkModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
    
    async def create_chunk(self, chunk : Chunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk
    
    async def get_chunk(self, chunk_id : str):
        async with self.db_client() as session:
            result = await session.execute(select(Chunk).where(Chunk.chunk_id == chunk_id))
            chunk = result.scalar_one_or_none()
        return chunk
    
    async def delete_chunks_by_project_id(self, project_id: str):
        async with self.db_client() as session:
            stmt = delete(Chunk).where(Chunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    
    async def get_max_chunk_order(self, project_id: str) -> int:
        async with self.db_client() as session:
            async with session.begin():
                query = select(func.max(Chunk.chunk_order)).where(Chunk.chunk_project_id == project_id)
                result = await session.execute(query)
                max_order = result.scalar_one_or_none()
                return max_order or 0