from fastapi import APIRouter

base_router = APIRouter()


@base_router.get("/")
async def get_home():
    """Currently inactive"""
    return {"message": "Starlink API. See /docs"}