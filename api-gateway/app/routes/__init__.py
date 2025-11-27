from fastapi import APIRouter

from .health import router as health_router
from .bitnet import router as bitnet_router
from .yolo import router as yolo_router
from .database import router as database_router

router = APIRouter()

router.include_router(health_router)
router.include_router(bitnet_router, prefix="/bitnet", tags=["BitNet"])
router.include_router(yolo_router, prefix="/yolo", tags=["YOLO"])
router.include_router(database_router, prefix="/requests", tags=["Database"])

__all__ = ["router"]

