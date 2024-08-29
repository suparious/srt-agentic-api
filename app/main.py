import os
import sys
import asyncio
from contextlib import asynccontextmanager

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("Python version:", sys.version)
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Contents of current directory:", os.listdir())
print("Initializing FastAPI app")

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from app.api.endpoints import agent_router, message_router, function_router, memory_router
from app.utils.auth import get_api_key
from app.utils.logging import main_logger
from app.config import settings
from app.core.memory import MemorySystem
from app.core.agent_manager import agent_manager
from app.core.function_manager import function_manager
from app.dependencies import get_agent_manager, get_function_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await MemorySystem.initialize_memory_systems()
        await agent_manager.initialize()
        await function_manager.initialize()
        main_logger.info("AgentManager and FunctionManager initialized")
        yield
    finally:
        # Shutdown
        main_logger.info("Starting application shutdown process")
        shutdown_tasks = [
            MemorySystem.close_memory_systems(),
            agent_manager.close(),
            function_manager.close()
        ]
        results = await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                main_logger.error(f"Error during shutdown: {str(result)}")

        # Cancel any remaining tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        main_logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        main_logger.info("Application shutdown complete")

app = FastAPI(
    title="SolidRusT Agentic API",
    description="A powerful and flexible API for creating, managing, and interacting with AI agents.",
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "SolidRusT Team",
        "url": "https://github.com/SolidRusT/srt-agentic-api",
        "email": "suparious@solidrust.net",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SolidRusT Agentic API",
        version="1.0.0",
        description="A powerful and flexible API for creating, managing, and interacting with AI agents.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TrustedHostMiddleware setup (conditional)
if settings.ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS
    )

# Include routers
def include_routers(app: FastAPI):
    app.include_router(
        agent_router,
        prefix="/agent",
        tags=["Agents"],
        dependencies=[Depends(get_agent_manager), Depends(get_function_manager)],
    )
    app.include_router(
        message_router,
        prefix="/message",
        tags=["Messages"],
        dependencies=[Depends(get_agent_manager)],
    )
    app.include_router(
        function_router,
        prefix="/function",
        tags=["Functions"],
        dependencies=[Depends(get_function_manager)],
    )
    app.include_router(
        memory_router,
        prefix="/memory",
        tags=["Memory"],
        dependencies=[Depends(get_agent_manager)],
    )

include_routers(app)

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that welcomes users to the SolidRusT Agentic API.
    """
    return {"message": "Welcome to SolidRusT Agentic API"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    main_logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    main_logger.info(f"Response status code: {response.status_code}")
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    main_logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    main_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


if __name__ == "__main__":
    import uvicorn

    main_logger.info("Starting SolidRusT Agentic API")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
