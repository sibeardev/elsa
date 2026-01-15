import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config import settings
from src.models import Base

config = context.config
fileConfig(config.config_file_name)
connectable = create_async_engine(settings.POSTGRES.URL, poolclass=pool.NullPool)


async def run_migrations_online():
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Offline mode not supported with async engine")
else:
    asyncio.run(run_migrations_online())
