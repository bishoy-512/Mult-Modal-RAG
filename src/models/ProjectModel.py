from .BaseModel import BaseModel
from .db_schemes import Project
from sqlalchemy.future import select

class ProjectModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)

    async def create_new_project(self , project_id : str):
        project = Project(project_id = project_id)
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        return project
    
    async def get_exist_project(self, project_id : str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if project:
                    return project
                else:
                    return None