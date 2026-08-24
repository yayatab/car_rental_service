from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RentalCreate(BaseModel):
    car_id: int = Field(
        ...,
        gt=0,
        description="ID of the vehicle to rent"
    )
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Customer's full name"
    )


class RentalResponse(BaseModel):
    id: int = Field(..., description="Unique rental record identifier")
    car_id: int = Field(..., description="Rented vehicle ID")
    customer_name: str = Field(..., description="Customer full name")
    start_date: datetime = Field(..., description="Rental start timestamp")
    end_date: datetime | None = Field(None, description="Rental end timestamp (null if active)")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class RentalEndResponse(BaseModel):
    rental: RentalResponse = Field(..., description="Completed rental record")
    message: str = Field(..., description="Status summary message")
