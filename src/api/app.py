from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.api.api_utils import register_exception_handlers
from src.api.middleware import MetricsAndLoggingMiddleware
from src.api.routes.cars import router as cars_router
from src.api.routes.rentals import router as rentals_router
from src.api.routes.system import router as system_router
from src.core.config import get_settings
from src.core.database import AsyncSessionFactory
from src.core.logging import logger
from src.dal.repositories.car_repository import CarRepository
from src.dal.repositories.rental_repository import RentalRepository
from src.services.car_service import CarService


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Initializing DriveNow Vehicle Management System...")
    try:
        async with AsyncSessionFactory() as session:
            car_repo = CarRepository(session)
            rental_repo = RentalRepository(session)
            service = CarService(car_repo, rental_repo)
            await service.refresh_metrics()
        logger.info("Fleet metrics synchronized successfully.")
    except Exception as exc:
        logger.warning(f"Initial metrics synchronization skipped: {exc}")

    yield

    logger.info("Shutting down DriveNow Vehicle Management System...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Internal vehicle fleet and rental management system for DriveNow.\n\n"
            "Features:\n"
            "* Vehicle fleet management (add, update, delete, status tracking)\n"
            "* Rental transaction lifecycle (start, complete active rentals)\n"
            "* Full Prometheus metrics and structured dual logging"
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(MetricsAndLoggingMiddleware)

    register_exception_handlers(app)

    app.include_router(system_router)
    app.include_router(cars_router, prefix=settings.API_V1_PREFIX)
    app.include_router(rentals_router, prefix=settings.API_V1_PREFIX)

    return app
