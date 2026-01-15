from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session


engine = create_async_engine(settings.POSTGRES.URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
