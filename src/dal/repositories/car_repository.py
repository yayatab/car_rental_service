from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dal.models.car import Car, CarStatus
from src.dal.repositories.base import BaseAsyncRepository


class CarRepository(BaseAsyncRepository[Car]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Car, session)

    async def get_by_id_for_update(self, car_id: int) -> Car | None:
        result = await self.session.execute(
            select(Car).where(Car.id == car_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def list_cars(
            self,
            status: CarStatus | None = None,
            offset: int = 0,
            limit: int = 100
    ) -> Sequence[Car]:
        query = select(Car)
        if status is not None:
            query = query.where(Car.status == status)

        query = query.order_by(Car.id.asc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_by_status(self) -> dict[CarStatus, int]:
        query = select(Car.status, func.count(Car.id)).group_by(Car.status)
        result = await self.session.execute(query)
        counts = {status: 0 for status in CarStatus}
        for status_val, count_val in result.all():
            counts[status_val] = count_val
        return counts
