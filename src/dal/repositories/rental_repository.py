from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dal.models.rental import Rental
from src.dal.repositories.base import BaseAsyncRepository


class RentalRepository(BaseAsyncRepository[Rental]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Rental, session)

    async def get_by_id_for_update(self, rental_id: int) -> Rental | None:
        result = await self.session.execute(
            select(Rental).where(Rental.id == rental_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_active_rental_for_car(self, car_id: int) -> Rental | None:
        result = await self.session.execute(
            select(Rental).where(Rental.car_id == car_id, Rental.end_date.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_rentals(
            self,
            active_only: bool = False,
            car_id: int | None = None,
            offset: int = 0,
            limit: int = 100
    ) -> Sequence[Rental]:
        query = select(Rental)
        if active_only:
            query = query.where(Rental.end_date.is_(None))
        if car_id is not None:
            query = query.where(Rental.car_id == car_id)

        query = query.order_by(Rental.start_date.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_active(self) -> int:
        result = await self.session.execute(
            select(func.count(Rental.id)).where(Rental.end_date.is_(None))
        )
        return result.scalar_one() or 0
