from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from app.config import settings
from app.utils.logging import setup_logger

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
auth_logger = setup_logger("auth", settings.LOG_DIR + "/auth.log")


async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    auth_logger.debug(f"Received API key: {api_key_header}")
    auth_logger.debug(f"Expected API key: {settings.API_KEY}")
    auth_logger.debug(f"API keys match: {api_key_header == settings.API_KEY}")

    if not api_key_header:
        auth_logger.warning("No API key provided")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="No API key provided"
        )

    if api_key_header == settings.API_KEY:
        auth_logger.info("API key validation successful")
        return api_key_header
    else:
        auth_logger.warning(
            f"API key validation failed. Received: {api_key_header}, Expected: {settings.API_KEY}"
        )
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )


def validate_api_key(api_key: str) -> bool:
    is_valid = api_key == settings.API_KEY
    auth_logger.debug(f"Validating API key: {api_key}")
    auth_logger.debug(f"Expected API key: {settings.API_KEY}")
    auth_logger.debug(f"API keys match: {is_valid}")
    if is_valid:
        auth_logger.info("API key validation successful")
    else:
        auth_logger.warning("API key validation failed")
    return is_valid
