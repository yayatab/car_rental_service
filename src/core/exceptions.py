from typing import Any


class CarRentalException(Exception):

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class EntityNotFoundError(CarRentalException):
    pass


class CarNotFoundError(EntityNotFoundError):
    pass


class RentalNotFoundError(EntityNotFoundError):
    pass


class CarUnavailableError(CarRentalException):
    pass


class RentalAlreadyEndedError(CarRentalException):
    pass


class CarHasActiveRentalsError(CarRentalException):
    pass


class InvalidOperationError(CarRentalException):
    pass
