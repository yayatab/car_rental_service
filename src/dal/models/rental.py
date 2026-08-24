from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.dal.models.base import Base, TimestampMixin
from src.dal.models.car import Car


class Rental(Base, TimestampMixin):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    car_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cars.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    start_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    car: Mapped[Car] = relationship("Car", back_populates="rentals", lazy="selectin")

    @property
    def is_active(self) -> bool:
        return self.end_date is None

    def __repr__(self) -> str:
        return f"<Rental(id={self.id}, car_id={self.car_id}, customer='{self.customer_name}', active={self.is_active})>"
