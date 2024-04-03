from fastapi import APIRouter

from demo_auth.views import router as demo_auth_router
from demo_auth.demo_jwt_auth import router as demo_jwt_auth_router

demo_auth_router.include_router(demo_jwt_auth_router)

router = APIRouter()
router.include_router(router=demo_auth_router)
