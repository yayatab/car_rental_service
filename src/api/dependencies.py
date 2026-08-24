from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.dal.repositories.car_repository import CarRepository
from src.dal.repositories.rental_repository import RentalRepository
from src.services.car_service import CarService
from src.services.rental_service import RentalService


def get_car_repository(session: AsyncSession = Depends(get_db_session)) -> CarRepository:
    return CarRepository(session=session)


def get_rental_repository(session: AsyncSession = Depends(get_db_session)) -> RentalRepository:
    return RentalRepository(session=session)


def get_car_service(car_repo: CarRepository = Depends(get_car_repository),
                    rental_repo: RentalRepository = Depends(get_rental_repository)
                    ) -> CarService:
    return CarService(car_repo=car_repo, rental_repo=rental_repo)


def get_rental_service(car_repo: CarRepository = Depends(get_car_repository),
                       rental_repo: RentalRepository = Depends(get_rental_repository)) -> RentalService:
    return RentalService(car_repo=car_repo, rental_repo=rental_repo)
