import pytest

from src.core.exceptions import (
    CarHasActiveRentalsError,
    CarNotFoundError,
    InvalidOperationError,
)
from src.dal.models import CarStatus
from src.schemas.car import CarCreate, CarUpdate
from src.schemas.rental import RentalCreate
from src.services.car_service import CarService
from src.services.rental_service import RentalService


@pytest.mark.asyncio
async def test_add_car_success(car_service: CarService):
    payload = CarCreate(model="Toyota Corolla", year=2022, status=CarStatus.AVAILABLE)
    car = await car_service.add_car(payload)

    assert car.id is not None
    assert car.model == "Toyota Corolla"
    assert car.year == 2022
    assert car.status == CarStatus.AVAILABLE


@pytest.mark.asyncio
async def test_get_car_not_found(car_service: CarService):
    with pytest.raises(CarNotFoundError):
        await car_service.get_car_by_id(9999)


@pytest.mark.asyncio
async def test_list_cars_with_status_filter(car_service: CarService):
    await car_service.add_car(CarCreate(model="Car 1", year=2021, status=CarStatus.AVAILABLE))
    await car_service.add_car(CarCreate(model="Car 2", year=2022, status=CarStatus.IN_USE))
    await car_service.add_car(CarCreate(model="Car 3", year=2023, status=CarStatus.UNDER_MAINTENANCE))

    available = await car_service.list_cars(status=CarStatus.AVAILABLE)
    assert len(available) == 1
    assert available[0].model == "Car 1"

    maintenance = await car_service.list_cars(status=CarStatus.UNDER_MAINTENANCE)
    assert len(maintenance) == 1
    assert maintenance[0].model == "Car 3"


@pytest.mark.asyncio
async def test_update_car_status(car_service: CarService):
    car = await car_service.add_car(CarCreate(model="Hyundai Ioniq", year=2023, status=CarStatus.AVAILABLE))
    updated = await car_service.update_car_status(car.id, CarStatus.UNDER_MAINTENANCE)

    assert updated.status == CarStatus.UNDER_MAINTENANCE


@pytest.mark.asyncio
async def test_delete_car_with_active_rental_fails(
        car_service: CarService,
        rental_service: RentalService
):
    car = await car_service.add_car(CarCreate(model="Tesla Model 3", year=2024, status=CarStatus.AVAILABLE))
    await rental_service.start_rental(RentalCreate(car_id=car.id, customer_name="Alice"))

    with pytest.raises(CarHasActiveRentalsError):
        await car_service.delete_car(car.id)


@pytest.mark.asyncio
async def test_invalid_status_transition_while_rented_fails(
        car_service: CarService,
        rental_service: RentalService
):
    car = await car_service.add_car(CarCreate(model="Mazda 3", year=2021, status=CarStatus.AVAILABLE))
    await rental_service.start_rental(RentalCreate(car_id=car.id, customer_name="Bob"))

    with pytest.raises(InvalidOperationError):
        await car_service.update_car(car.id, CarUpdate(status=CarStatus.UNDER_MAINTENANCE))
