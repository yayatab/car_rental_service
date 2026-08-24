from src.api.routes.cars import router as cars_router
from src.api.routes.rentals import router as rentals_router
from src.api.routes.system import router as system_router

__all__ = ["cars_router", "rentals_router", "system_router"]
