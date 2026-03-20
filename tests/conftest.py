import asyncio
import os
from importlib import import_module

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine


def _db_url(*, database: str) -> str:
    user = os.environ.get("POSTGRES__USER", "postgres")
    password = os.environ.get("POSTGRES__PASSWORD", "postgres")
    host = os.environ.get("POSTGRES__HOST", "db")
    port = int(os.environ.get("POSTGRES__PORT", "5432"))
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


@pytest.fixture(scope="session")
def api_key() -> str:
    return os.environ.get("API_KEY", "test-api-key")


@pytest.fixture(scope="session")
def test_db_name() -> str:
    return os.environ.get("TEST_POSTGRES_DB", "test_db")


@pytest.fixture(scope="session", autouse=True)
def _set_env_for_tests(test_db_name: str, api_key: str) -> None:
    os.environ.setdefault("POSTGRES__USER", "postgres")
    os.environ.setdefault("POSTGRES__PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES__HOST", "db")
    os.environ.setdefault("POSTGRES__PORT", "5432")
    os.environ["POSTGRES__DB"] = test_db_name
    os.environ["API_KEY"] = api_key


@pytest.fixture(scope="session")
def seeded_db(test_db_name: str) -> None:
    if os.environ.get("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("Integration tests are disabled (set RUN_INTEGRATION_TESTS=1)")

    async def _drop_create() -> None:
        engine = create_async_engine(_db_url(database="postgres"))
        async with engine.connect() as conn:
            conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.exec_driver_sql(f'DROP DATABASE IF EXISTS "{test_db_name}"')
            await conn.exec_driver_sql(f'CREATE DATABASE "{test_db_name}"')
        await engine.dispose()

    asyncio.run(_drop_create())

    project_root = os.path.dirname(os.path.dirname(__file__))
    alembic_cfg = Config(os.path.join(project_root, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(project_root, "alembic"))
    command.upgrade(alembic_cfg, "head")

    import scripts.seed_db as seed_mod

    asyncio.run(seed_mod.seed())


@pytest.fixture(scope="session")
def integration_app(seeded_db):
    return import_module("main").app
