from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dal.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseAsyncRepository(Generic[ModelType]):

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: int) -> ModelType | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)  # ty: ignore
        )
        return result.scalar_one_or_none()

    async def list_all(self, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def add(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        await self.session.delete(entity)
        await self.session.commit()
