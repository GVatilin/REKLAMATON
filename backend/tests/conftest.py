# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from os import environ
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.main import getApp
from app.config import get_settings
from app.database.connection import refresh_engine
from tests.utils import make_alembic_config


@pytest_asyncio.fixture(scope="function")
async def postgres() -> str:
    """
    Создает временную БД для запуска теста.
    """
    settings = get_settings()

    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name
    settings.POSTGRES_HOST = 'localhost'
    environ["POSTGRES_HOST"] = 'localhost'

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)
    try:
        yield settings.database_uri
    finally:
        drop_database(tmp_url)


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri: str):
    async_engine = create_async_engine(database_uri, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture
def alembic_config(postgres) -> Config:
    """
    Создает файл конфигурации для alembic.
    """
    cmd_options = SimpleNamespace(config="app/database/", name="alembic", pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
def alembic_engine():
    """
    Override this fixture to provide pytest-alembic powered tests with a database handle.
    """
    settings = get_settings()
    return create_async_engine(settings.databaseUri, echo=True)


@pytest_asyncio.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    """
    Проводит миграции.
    """
    await run_async_upgrade(alembic_config, postgres)


@pytest_asyncio.fixture
async def client(migrated_postgres) -> AsyncClient:
    """
    Returns a client that can be used to interact with the application.
    """
    app = getApp()
    refresh_engine()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test/api/v1") as client:
        yield client


@pytest_asyncio.fixture
async def engine_async(postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> sessionmaker:
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session


@pytest_asyncio.fixture
async def active_user_token(client: AsyncClient):
    data = {
        "username": "activeuser",
        "password": "activeuser",
    }
    await client.post(url="/user/register", json=data)
    response = await client.post(url="/user/token", data=data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
