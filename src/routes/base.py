from fastapi import APIRouter
from helpers import get_settings

base_router = APIRouter()

@base_router.get("/Home")
def welcome():
    settings = get_settings()
    return {
        "DEVELOPER_NAME": settings.DEVELOPER_NAME,
        "APP_NAME": settings.APP_NAME,
        "APP_VERSION": settings.APP_VERSION
    }
