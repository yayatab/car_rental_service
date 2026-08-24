from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Sequence

from src.core.exceptions import (
    CarNotFoundError,
    CarUnavailableError,
    RentalAlreadyEndedError,
    RentalNotFoundError,
)
from src.core.logging import logger
from src.core.metrics import (
    OPERATION_DURATION_SECONDS,
    RENTAL_OPERATIONS_TOTAL,
    update_fleet_metrics,
)
from src.dal.models import CarStatus
from src.dal.models import Rental
from src.dal.repositories.car_repository import CarRepository
from src.dal.repositories.rental_repository import RentalRepository
from src.schemas.rental import RentalCreate


class RentalService:

    def __init__(self, car_repo: CarRepository, rental_repo: RentalRepository) -> None:
        self.car_repo = car_repo
        self.rental_repo = rental_repo

    async def start_rental(self, payload: RentalCreate) -> Rental:
        start_time = time.perf_counter()
        try:
            # 1. Fetch car with row lock to prevent race conditions
            car = await self.car_repo.get_by_id_for_update(payload.car_id)
            if not car:
                raise CarNotFoundError(f"Vehicle with ID {payload.car_id} was not found.")

            # 2. Invariant check: car must be AVAILABLE
            if car.status != CarStatus.AVAILABLE:
                raise CarUnavailableError(
                    f"Vehicle '{car.model}' (ID {car.id}) is currently {car.status.value} and cannot be rented."
                )

            # 3. Transition car status to IN_USE
            car.status = CarStatus.IN_USE
            await self.car_repo.update(car)

            # 4. Create rental transaction record
            rental = Rental(
                car_id=payload.car_id,
                customer_name=payload.customer_name.strip(),
                start_date=datetime.now(timezone.utc),
                end_date=None
            )
            created_rental = await self.rental_repo.add(rental)

            logger.info(
                f"[RENTAL_STARTED] RentalID={created_rental.id} | "
                f"CarID={payload.car_id} | Customer='{payload.customer_name}'"
            )
            RENTAL_OPERATIONS_TOTAL.labels(operation="start", status="success").inc()
            await self._refresh_metrics()
            return created_rental
        except Exception:
            RENTAL_OPERATIONS_TOTAL.labels(operation="start", status="error").inc()
            raise
        finally:
            OPERATION_DURATION_SECONDS.labels(operation="rental_start").observe(
                time.perf_counter() - start_time
            )

    async def end_rental(self, rental_id: int) -> Rental:
        start_time = time.perf_counter()
        try:
            # 1. Fetch rental with row lock
            rental = await self.rental_repo.get_by_id_for_update(rental_id)
            if not rental:
                raise RentalNotFoundError(f"Rental transaction #{rental_id} was not found.")

            # 2. Invariant check: rental must be active
            if rental.end_date is not None:
                raise RentalAlreadyEndedError(
                    f"Rental #{rental_id} was already completed on {rental.end_date}."
                )

            # 3. Mark rental as completed
            rental.end_date = datetime.now(timezone.utc)
            updated_rental = await self.rental_repo.update(rental)

            # 4. Revert car status to AVAILABLE
            car = await self.car_repo.get_by_id_for_update(rental.car_id)
            if car:
                car.status = CarStatus.AVAILABLE
                await self.car_repo.update(car)

            logger.info(
                f"[RENTAL_ENDED] RentalID={rental_id} | CarID={rental.car_id} | "
                f"Customer='{rental.customer_name}' | EndDate={rental.end_date or 'none'}"
            )
            RENTAL_OPERATIONS_TOTAL.labels(operation="end", status="success").inc()
            await self._refresh_metrics()
            return updated_rental
        except Exception:
            RENTAL_OPERATIONS_TOTAL.labels(operation="end", status="error").inc()
            raise
        finally:
            OPERATION_DURATION_SECONDS.labels(operation="rental_end").observe(
                time.perf_counter() - start_time
            )

    async def get_rental_by_id(self, rental_id: int) -> Rental:
        rental = await self.rental_repo.get_by_id(rental_id)
        if not rental:
            raise RentalNotFoundError(f"Rental record #{rental_id} was not found.")
        return rental

    async def list_rentals(
            self,
            active_only: bool = False,
            car_id: int | None = None,
            offset: int = 0,
            limit: int = 100
    ) -> Sequence[Rental]:
        rentals = await self.rental_repo.list_rentals(
            active_only=active_only,
            car_id=car_id,
            offset=offset,
            limit=limit
        )
        await self._refresh_metrics()
        return rentals

    async def _refresh_metrics(self) -> None:
        counts = await self.car_repo.count_by_status()
        active_rentals = await self.rental_repo.count_active()
        update_fleet_metrics(
            available_count=counts.get(CarStatus.AVAILABLE, 0),
            in_use_count=counts.get(CarStatus.IN_USE, 0),
            maintenance_count=counts.get(CarStatus.UNDER_MAINTENANCE, 0),
            ongoing_rentals=active_rentals
        )
