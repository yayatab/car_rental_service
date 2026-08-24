from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from src.api.dependencies import get_rental_service
from src.schemas.rental import RentalCreate, RentalEndResponse, RentalResponse
from src.services.rental_service import RentalService

router = APIRouter(prefix="/rentals", tags=["Rentals"])


@router.post(
    "",
    response_model=RentalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new rental",
    description="Starts a new rental transaction for an available vehicle and sets car status to IN_USE."
)
async def start_rental(
        payload: RentalCreate,
        service: RentalService = Depends(get_rental_service)
) -> RentalResponse:
    rental = await service.start_rental(payload)
    return RentalResponse.model_validate(rental)


@router.post(
    "/{rental_id}/end",
    response_model=RentalEndResponse,
    summary="End an active rental",
    description="Completes an active rental transaction and reverts the vehicle status to AVAILABLE."
)
async def end_rental(
        rental_id: int = Path(..., gt=0, description="Rental ID"),
        service: RentalService = Depends(get_rental_service)
) -> RentalEndResponse:
    rental = await service.end_rental(rental_id)
    return RentalEndResponse(
        rental=RentalResponse.model_validate(rental),
        message=f"Rental #{rental_id} successfully ended. Vehicle is now AVAILABLE."
    )


@router.get(
    "/{rental_id}",
    response_model=RentalResponse,
    summary="Get rental by ID",
    description="Retrieves details for a specific rental transaction."
)
async def get_rental(
        rental_id: int = Path(..., gt=0, description="Rental ID"),
        service: RentalService = Depends(get_rental_service)
) -> RentalResponse:
    rental = await service.get_rental_by_id(rental_id)
    return RentalResponse.model_validate(rental)


@router.get(
    "",
    response_model=List[RentalResponse],
    summary="List rentals",
    description="Retrieves a list of rentals with optional filters for active status and vehicle ID."
)
async def list_rentals(
        active_only: bool = Query(False, description="Filter for active ongoing rentals only"),
        car_id: Optional[int] = Query(None, description="Filter rentals for a specific car ID"),
        offset: int = Query(0, ge=0, description="Pagination offset"),
        limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
        service: RentalService = Depends(get_rental_service)
) -> List[RentalResponse]:
    rentals = await service.list_rentals(
        active_only=active_only,
        car_id=car_id,
        offset=offset,
        limit=limit
    )
    return [RentalResponse.model_validate(r) for r in rentals]
