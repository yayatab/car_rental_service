from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.api.app import create_app
from src.core.database import get_db_session
from src.dal.models.base import Base
from src.dal.repositories.car_repository import CarRepository
from src.dal.repositories.rental_repository import RentalRepository
from src.services.car_service import CarService
from src.services.rental_service import RentalService


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
def car_repo(db_session: AsyncSession) -> CarRepository:
    return CarRepository(session=db_session)


@pytest.fixture
def rental_repo(db_session: AsyncSession) -> RentalRepository:
    return RentalRepository(session=db_session)


@pytest.fixture
def car_service(car_repo: CarRepository, rental_repo: RentalRepository) -> CarService:
    return CarService(car_repo=car_repo, rental_repo=rental_repo)


@pytest.fixture
def rental_service(car_repo: CarRepository, rental_repo: RentalRepository) -> RentalService:
    return RentalService(car_repo=car_repo, rental_repo=rental_repo)


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
