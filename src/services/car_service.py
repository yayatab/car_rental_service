from __future__ import annotations

import time
from typing import Sequence

from src.core.exceptions import (
    CarHasActiveRentalsError,
    CarNotFoundError,
    InvalidOperationError,
)
from src.core.logging import logger
from src.core.metrics import (
    CAR_OPERATIONS_TOTAL,
    OPERATION_DURATION_SECONDS,
    update_fleet_metrics,
)
from src.dal.models import Car, CarStatus
from src.dal.repositories.car_repository import CarRepository
from src.dal.repositories.rental_repository import RentalRepository
from src.schemas.car import CarCreate, CarUpdate


class CarService:

    def __init__(self, car_repo: CarRepository, rental_repo: RentalRepository) -> None:
        self.car_repo = car_repo
        self.rental_repo = rental_repo

    async def add_car(self, payload: CarCreate) -> Car:
        start_time = time.perf_counter()
        try:
            car = Car(
                model=payload.model.strip(),
                year=payload.year,
                status=payload.status
            )
            created_car = await self.car_repo.add(car)
            logger.info(
                f"[CAR_ADDED] ID={created_car.id} | Model='{created_car.model}' | "
                f"Year={created_car.year} | Status={created_car.status.value}"
            )
            CAR_OPERATIONS_TOTAL.labels(operation="add", status="success").inc()
            await self.refresh_metrics()
            return created_car
        except Exception:
            CAR_OPERATIONS_TOTAL.labels(operation="add", status="error").inc()
            raise
        finally:
            OPERATION_DURATION_SECONDS.labels(operation="car_add").observe(
                time.perf_counter() - start_time
            )

    async def get_car_by_id(self, car_id: int) -> Car:
        car = await self.car_repo.get_by_id(car_id)
        if not car:
            raise CarNotFoundError(f"Vehicle with ID {car_id} was not found.")
        return car

    async def list_cars(
            self,
            status: CarStatus | None = None,
            offset: int = 0,
            limit: int = 100
    ) -> Sequence[Car]:
        cars = await self.car_repo.list_cars(status=status, offset=offset, limit=limit)
        await self.refresh_metrics()
        return cars

    async def update_car(self, car_id: int, payload: CarUpdate) -> Car:
        start_time = time.perf_counter()
        try:
            car = await self.get_car_by_id(car_id)

            if payload.status is not None and payload.status != car.status:
                await self._validate_status_transition(car, payload.status)
                car.status = payload.status

            if payload.model is not None:
                car.model = payload.model.strip()
            if payload.year is not None:
                car.year = payload.year

            updated_car = await self.car_repo.update(car)
            logger.info(f"[CAR_UPDATED] ID={car_id} | Status={updated_car.status.value}")
            CAR_OPERATIONS_TOTAL.labels(operation="update", status="success").inc()
            await self.refresh_metrics()
            return updated_car
        except Exception:
            CAR_OPERATIONS_TOTAL.labels(operation="update", status="error").inc()
            raise
        finally:
            OPERATION_DURATION_SECONDS.labels(operation="car_update").observe(
                time.perf_counter() - start_time
            )

    async def update_car_status(self, car_id: int, new_status: CarStatus) -> Car:
        return await self.update_car(car_id, CarUpdate(status=new_status))

    async def delete_car(self, car_id: int) -> None:
        start_time = time.perf_counter()
        try:
            car = await self.get_car_by_id(car_id)
            active_rental = await self.rental_repo.get_active_rental_for_car(car_id)
            if active_rental:
                raise CarHasActiveRentalsError(
                    f"Cannot delete vehicle #{car_id} because it currently has an active rental (#{active_rental.id})."
                )

            await self.car_repo.delete(car)
            logger.info(f"[CAR_DELETED] ID={car_id} | Model='{car.model}'")
            CAR_OPERATIONS_TOTAL.labels(operation="delete", status="success").inc()
            await self.refresh_metrics()
        except Exception:
            CAR_OPERATIONS_TOTAL.labels(operation="delete", status="error").inc()
            raise
        finally:
            OPERATION_DURATION_SECONDS.labels(operation="car_delete").observe(
                time.perf_counter() - start_time
            )

    async def _validate_status_transition(self, car: Car, target_status: CarStatus) -> None:
        if car.status == CarStatus.IN_USE and target_status != CarStatus.IN_USE:
            active_rental = await self.rental_repo.get_active_rental_for_car(car.id)
            if active_rental:
                raise InvalidOperationError(
                    f"Vehicle #{car.id} cannot transition to {target_status.value} while rented in active rental #{active_rental.id}."
                )

    async def refresh_metrics(self) -> None:
        counts = await self.car_repo.count_by_status()
        active_rentals = await self.rental_repo.count_active()
        update_fleet_metrics(
            available_count=counts.get(CarStatus.AVAILABLE, 0),
            in_use_count=counts.get(CarStatus.IN_USE, 0),
            maintenance_count=counts.get(CarStatus.UNDER_MAINTENANCE, 0),
            ongoing_rentals=active_rentals
        )
