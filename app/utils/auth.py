from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from app.config import settings
import logging

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
logger = logging.getLogger(__name__)

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    logger.debug(f"Received API key: {api_key_header}")
    logger.debug(f"Expected API key: {settings.API_KEY}")
    logger.debug(f"Full settings object: {settings}")
    if api_key_header == settings.API_KEY:
        return api_key_header
    else:
        logger.warning("API key validation failed")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )

def validate_api_key(api_key: str) -> bool:
    return api_key == settings.API_KEY