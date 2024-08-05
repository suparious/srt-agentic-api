from fastapi import APIRouter
from .add import router as add_router
from .retrieve import router as retrieve_router
from .search import router as search_router
from .delete import router as delete_router
from .operate import router as operate_router

router = APIRouter()

router.include_router(add_router)
router.include_router(retrieve_router)
router.include_router(search_router)
router.include_router(delete_router)
router.include_router(operate_router)
