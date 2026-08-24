from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    CarHasActiveRentalsError,
    CarRentalException,
    CarUnavailableError,
    EntityNotFoundError,
    InvalidOperationError,
    RentalAlreadyEndedError,
)
from src.schemas.common import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(_: Request, exc: EntityNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details
            ).model_dump(mode="json")
        )

    @app.exception_handler(CarUnavailableError)
    async def car_unavailable_handler(_: Request, exc: CarUnavailableError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details
            ).model_dump(mode="json")
        )

    @app.exception_handler(CarHasActiveRentalsError)
    async def car_has_active_rentals_handler(_: Request, exc: CarHasActiveRentalsError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details
            ).model_dump(mode="json")
        )

    @app.exception_handler(RentalAlreadyEndedError)
    async def rental_already_ended_handler(_: Request, exc: RentalAlreadyEndedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details
            ).model_dump(mode="json")
        )

    @app.exception_handler(InvalidOperationError)
    async def invalid_operation_handler(_: Request, exc: InvalidOperationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details
            ).model_dump(mode="json")
        )

    @app.exception_handler(CarRentalException)
    async def generic_domain_handler(_: Request, exc: CarRentalException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details
            ).model_dump(mode="json")
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        error_msgs = [f"{e['loc'][-1]}: {e['msg']}" for e in errors if 'loc' in e and len(e['loc']) > 0]
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="ValidationError",
                message="Request validation failed: " + "; ".join(error_msgs),
                details=errors
            ).model_dump(mode="json")
        )
