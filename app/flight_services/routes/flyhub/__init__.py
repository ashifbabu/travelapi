from fastapi import APIRouter
from .auth import router as auth_router
from .search import router as search_router

router = APIRouter()
router.include_router(auth_router, prefix="/flyhub", tags=["FlyHub Authentication"])
router.include_router(search_router, prefix="/flyhub", tags=["FlyHub Flight Search"])
