from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from core.config import settings


def verify_api_key(
    x_api_key: str = Security(APIKeyHeader(name="X-API-Key", auto_error=False)),
) -> None:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
