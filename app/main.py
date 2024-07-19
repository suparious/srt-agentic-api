from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import agent, message, function, memory
from app.utils.auth import get_api_key

app = FastAPI(title="SolidRusT Agentic API")

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(agent.router, prefix="/agent", tags=["agent"], dependencies=[Depends(get_api_key)])
app.include_router(message.router, prefix="/agent", tags=["message"], dependencies=[Depends(get_api_key)])
app.include_router(function.router, prefix="/agent", tags=["function"], dependencies=[Depends(get_api_key)])
app.include_router(memory.router, prefix="/agent", tags=["memory"], dependencies=[Depends(get_api_key)])

@app.get("/")
async def root():
    return {"message": "Welcome to SolidRusT Agentic API"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {"error": str(exc)}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
