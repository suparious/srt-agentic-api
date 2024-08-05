"""
This module serves as the main entry point for memory-related endpoints.
It imports and re-exports the router from the memory package, which contains
all the memory operations split into separate files for better organization.
"""

from app.api.endpoints.memory import router

# Re-export the router
__all__ = ["router"]
