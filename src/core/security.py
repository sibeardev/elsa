from fastapi import Header, HTTPException, status

from core.config import settings


def api_key_guard(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
