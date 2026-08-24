from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.dal.models import CarStatus


class CarBase(BaseModel):
    model: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Vehicle make and model, e.g. 'Toyota Corolla'"
    )
    year: int = Field(
        ...,
        ge=1900,
        le=2100,
        description="Manufacturing year between 1900 and 2100"
    )


class CarCreate(CarBase):
    status: CarStatus = Field(
        default=CarStatus.AVAILABLE,
        description="Initial operational status of the vehicle"
    )


class CarUpdate(BaseModel):
    model: str | None = Field(None, min_length=2, max_length=255, description="Updated model name")
    year: int | None = Field(None, ge=1900, le=2100, description="Updated manufacturing year")
    status: CarStatus | None = Field(None, description="Updated operational status")


class CarStatusUpdate(BaseModel):
    status: CarStatus = Field(..., description="New operational status for the vehicle")


class CarResponse(CarBase):
    id: int = Field(..., description="Unique vehicle identifier")
    status: CarStatus = Field(..., description="Current operational status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
