from fastapi import FastAPI , routing
from routes import base_router , data_router
from helpers import get_settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


app = FastAPI()

@app.on_event("startup")
async def startup():
    settings = get_settings()
    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(app.db_engine, class_=AsyncSession, expire_on_commit=False)

@app.on_event("shutdown")
async def shutdown():
    app.db_engine.dispose()


app.include_router(base_router)
app.include_router(data_router)