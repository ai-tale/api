from fastapi import APIRouter

from app.api.endpoints import auth, users, stories, pages

# Create API router
api_router = APIRouter()

# Include various endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(stories.router, prefix="/stories", tags=["Stories"])
api_router.include_router(pages.router, prefix="/pages", tags=["Pages"]) 