from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session

router = APIRouter(tags=["health"])
depends_session = Depends(get_session)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Liveness",
    description="Проверка, что сервис запущен.",
)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/check-db",
    status_code=status.HTTP_200_OK,
    summary="Readiness",
    description="Проверка доступности базы данных. При недоступности базы данных — 503.",
)
async def ready(session: AsyncSession = depends_session) -> dict[str, str]:
    await session.scalars(text("SELECT 1"))
    return {"status": "ready"}
