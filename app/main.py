import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("Python path:", sys.path)
print("Current working directory:", os.getcwd())

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.endpoints import agent, message, function, memory
from app.utils.auth import get_api_key
from app.utils.logging import main_logger
from app.config import settings

print(sys.path)
app = FastAPI(title="SolidRusT Agentic API")

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent.router, prefix="/agent", tags=["agent"])
app.include_router(message.router, prefix="/message", tags=["message"])
app.include_router(function.router, prefix="/function", tags=["function"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])

@app.get("/")
async def root():
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
