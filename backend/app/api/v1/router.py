from fastapi import APIRouter

from app.api.v1.routes import applications, auth, cv, jobs, searches

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(cv.router)
api_router.include_router(searches.router)
api_router.include_router(jobs.router)
api_router.include_router(applications.router)
