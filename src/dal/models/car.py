from __future__ import annotations

import enum

from sqlalchemy import Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.dal.models.base import Base, TimestampMixin
from src.dal.models.rental import Rental


class CarStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"


class Car(Base, TimestampMixin):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[CarStatus] = mapped_column(
        SQLEnum(CarStatus, native_enum=False, length=50),
        nullable=False,
        default=CarStatus.AVAILABLE,
        index=True
    )

    rentals: Mapped[list[Rental]] = relationship(
        "Rental",
        back_populates="car",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Car(id={self.id}, model='{self.model}', year={self.year}, status='{self.status}')>"
