from typing import Any, Dict, List, Optional

import httpx


class RentalApiClient:

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_v1 = f"{self.base_url}/api/v1"
        self.timeout = timeout

    # ---------------- Car Operations ---------------- #

    def list_cars(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if status:
            params["status"] = status
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.get("/cars", params=params)
            self._handle_error(response)
            return response.json()

    def get_car(self, car_id: int) -> Dict[str, Any]:
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.get(f"/cars/{car_id}")
            self._handle_error(response)
            return response.json()

    def add_car(self, model: str, year: int, status: str = "AVAILABLE") -> Dict[str, Any]:
        payload = {"model": model, "year": year, "status": status}
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.post("/cars", json=payload)
            self._handle_error(response)
            return response.json()

    def update_car_status(self, car_id: int, status: str) -> Dict[str, Any]:
        payload = {"status": status}
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.patch(f"/cars/{car_id}/status", json=payload)
            self._handle_error(response)
            return response.json()

    def delete_car(self, car_id: int) -> None:
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.delete(f"/cars/{car_id}")
            self._handle_error(response)

    # ---------------- Rental Operations ---------------- #

    def start_rental(self, car_id: int, customer_name: str) -> Dict[str, Any]:
        payload = {"car_id": car_id, "customer_name": customer_name}
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.post("/rentals", json=payload)
            self._handle_error(response)
            return response.json()

    def end_rental(self, rental_id: int) -> Dict[str, Any]:
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.post(f"/rentals/{rental_id}/end")
            self._handle_error(response)
            return response.json()

    def list_rentals(self, active_only: bool = False, car_id: Optional[int] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"active_only": active_only}
        if car_id is not None:
            params["car_id"] = car_id
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.get("/rentals", params=params)
            self._handle_error(response)
            return response.json()

    def get_rental(self, rental_id: int) -> Dict[str, Any]:
        with httpx.Client(base_url=self.api_v1, timeout=self.timeout) as client:
            response = client.get(f"/rentals/{rental_id}")
            self._handle_error(response)
            return response.json()

    # ---------------- System Operations ---------------- #

    def health_check(self) -> Dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.get("/health")
            self._handle_error(response)
            return response.json()

    # ---------------- Error Helper ---------------- #

    @staticmethod
    def _handle_error(response: httpx.Response) -> None:
        if response.is_success:
            return

        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
            error_type = error_data.get("error", "Error")
            raise RuntimeError(f"[{error_type}] {message} (HTTP {response.status_code})")
        except (ValueError, KeyError):
            raise RuntimeError(f"API Error {response.status_code}: {response.text}")
