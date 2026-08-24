from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from src.api.dependencies import get_car_service
from src.dal.models import CarStatus
from src.schemas.car import CarCreate, CarResponse, CarStatusUpdate, CarUpdate
from src.services.car_service import CarService

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post(
    "",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new vehicle",
    description="Registers a new vehicle in the DriveNow fleet."
)
async def add_car(payload: CarCreate, service: CarService = Depends(get_car_service)) -> CarResponse:
    car = await service.add_car(payload)
    return CarResponse.model_validate(car)


@router.get(
    "",
    response_model=List[CarResponse],
    summary="List all vehicles",
    description="Retrieves a list of fleet vehicles with optional status filtering and pagination."
)
async def list_cars(
        status_filter: Optional[CarStatus] = Query(None, alias="status", description="Filter cars by status"),
        offset: int = Query(0, ge=0, description="Pagination offset"),
        limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
        service: CarService = Depends(get_car_service)
) -> List[CarResponse]:
    cars = await service.list_cars(status=status_filter, offset=offset, limit=limit)
    return [CarResponse.model_validate(c) for c in cars]


@router.get(
    "/{car_id}",
    response_model=CarResponse,
    summary="Get vehicle by ID",
    description="Retrieves detailed information for a specific vehicle."
)
async def get_car(
        car_id: int = Path(..., gt=0, description="Vehicle ID"),
        service: CarService = Depends(get_car_service)
) -> CarResponse:
    car = await service.get_car_by_id(car_id)
    return CarResponse.model_validate(car)


@router.patch(
    "/{car_id}/status",
    response_model=CarResponse,
    summary="Update vehicle status",
    description="Updates the operational status of a vehicle (AVAILABLE, IN_USE, UNDER_MAINTENANCE)."
)
async def update_car_status(
        car_id: int = Path(..., gt=0, description="Vehicle ID"),
        payload: CarStatusUpdate = ...,
        service: CarService = Depends(get_car_service)
) -> CarResponse:
    car = await service.update_car_status(car_id, payload.status)
    return CarResponse.model_validate(car)


@router.put(
    "/{car_id}",
    response_model=CarResponse,
    summary="Update vehicle details",
    description="Updates vehicle attributes such as model, year, or status."
)
async def update_car(
        car_id: int = Path(..., gt=0, description="Vehicle ID"),
        payload: CarUpdate = ...,
        service: CarService = Depends(get_car_service)
) -> CarResponse:
    car = await service.update_car(car_id, payload)
    return CarResponse.model_validate(car)


@router.delete(
    "/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete vehicle",
    description="Removes a vehicle from the fleet if it is not currently rented."
)
async def delete_car(
        car_id: int = Path(..., gt=0, description="Vehicle ID"),
        service: CarService = Depends(get_car_service)
) -> None:
    await service.delete_car(car_id)
