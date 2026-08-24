import pytest

from src.core.exceptions import (
    CarNotFoundError,
    CarUnavailableError,
    RentalAlreadyEndedError,
    RentalNotFoundError,
)
from src.dal.models import CarStatus
from src.schemas.car import CarCreate
from src.schemas.rental import RentalCreate
from src.services.car_service import CarService
from src.services.rental_service import RentalService


@pytest.mark.asyncio
async def test_start_rental_success_updates_car_status(
        car_service: CarService,
        rental_service: RentalService
):
    car = await car_service.add_car(CarCreate(model="Toyota Yaris", year=2022, status=CarStatus.AVAILABLE))
    rental = await rental_service.start_rental(RentalCreate(car_id=car.id, customer_name="Alice Smith"))

    assert rental.id is not None
    assert rental.car_id == car.id
    assert rental.customer_name == "Alice Smith"
    assert rental.start_date is not None
    assert rental.end_date is None

    # Check vehicle status changed to IN_USE
    updated_car = await car_service.get_car_by_id(car.id)
    assert updated_car.status == CarStatus.IN_USE


@pytest.mark.asyncio
async def test_start_rental_unavailable_car_fails(
        car_service: CarService,
        rental_service: RentalService
):
    car = await car_service.add_car(CarCreate(model="Honda Civic", year=2021, status=CarStatus.UNDER_MAINTENANCE))

    with pytest.raises(CarUnavailableError):
        await rental_service.start_rental(RentalCreate(car_id=car.id, customer_name="Bob"))


@pytest.mark.asyncio
async def test_start_rental_nonexistent_car_fails(rental_service: RentalService):
    with pytest.raises(CarNotFoundError):
        await rental_service.start_rental(RentalCreate(car_id=9999, customer_name="Charlie"))


@pytest.mark.asyncio
async def test_end_rental_success_reverts_car_status(
        car_service: CarService,
        rental_service: RentalService
):
    car = await car_service.add_car(CarCreate(model="Ford Focus", year=2023, status=CarStatus.AVAILABLE))
    rental = await rental_service.start_rental(RentalCreate(car_id=car.id, customer_name="David"))

    ended_rental = await rental_service.end_rental(rental.id)
    assert ended_rental.end_date is not None

    # Verify vehicle status is AVAILABLE again
    updated_car = await car_service.get_car_by_id(car.id)
    assert updated_car.status == CarStatus.AVAILABLE


@pytest.mark.asyncio
async def test_end_rental_already_ended_fails(
        car_service: CarService,
        rental_service: RentalService
):
    car = await car_service.add_car(CarCreate(model="Kia Rio", year=2020, status=CarStatus.AVAILABLE))
    rental = await rental_service.start_rental(RentalCreate(car_id=car.id, customer_name="Eve"))

    await rental_service.end_rental(rental.id)

    with pytest.raises(RentalAlreadyEndedError):
        await rental_service.end_rental(rental.id)


@pytest.mark.asyncio
async def test_end_nonexistent_rental_fails(rental_service: RentalService):
    with pytest.raises(RentalNotFoundError):
        await rental_service.end_rental(9999)
