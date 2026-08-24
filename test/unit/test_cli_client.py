import httpx
import pytest

from src.cli.client import RentalApiClient


def test_client_list_cars(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(200, json=[{"id": 1, "model": "Car 1", "year": 2022, "status": "AVAILABLE"}],
                              request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    cars = client.list_cars(status="AVAILABLE")
    assert len(cars) == 1
    assert cars[0]["model"] == "Car 1"


def test_client_get_car(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(200, json={"id": 1, "model": "Car 1", "year": 2022, "status": "AVAILABLE"},
                              request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    car = client.get_car(1)
    assert car["id"] == 1


def test_client_add_car(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(201, json={"id": 2, "model": "Tesla", "year": 2024, "status": "AVAILABLE"},
                              request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    car = client.add_car("Tesla", 2024)
    assert car["id"] == 2


def test_client_update_car_status(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(200, json={"id": 1, "model": "Car 1", "year": 2022, "status": "IN_USE"}, request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    car = client.update_car_status(1, "IN_USE")
    assert car["status"] == "IN_USE"


def test_client_delete_car(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(204, request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    # Should not raise exception
    client.delete_car(1)


def test_client_start_rental(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(201, json={"id": 1, "car_id": 1, "customer_name": "Alice",
                                         "start_date": "2026-08-24T12:00:00Z", "end_date": None}, request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    rental = client.start_rental(1, "Alice")
    assert rental["id"] == 1


def test_client_end_rental(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(200,
                              json={"rental": {"id": 1, "end_date": "2026-08-24T14:00:00Z"}, "message": "Rental ended"},
                              request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    res = client.end_rental(1)
    assert res["message"] == "Rental ended"


def test_client_list_rentals(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(200, json=[{"id": 1, "customer_name": "Alice"}], request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    rentals = client.list_rentals(active_only=True, car_id=1)
    assert len(rentals) == 1


def test_client_get_rental(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(200, json={"id": 1, "customer_name": "Alice"}, request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    rental = client.get_rental(1)
    assert rental["id"] == 1


def test_client_health_check(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(200, json={"status": "healthy", "version": "0.1.0", "database": "connected"},
                              request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    health = client.health_check()
    assert health["status"] == "healthy"


def test_client_error_handling(monkeypatch):
    client = RentalApiClient()

    def mock_send(self, request, **kwargs):
        return httpx.Response(404, json={"error": "CarNotFoundError", "message": "Car 99 not found"}, request=request)

    monkeypatch.setattr(httpx.Client, "send", mock_send)
    with pytest.raises(RuntimeError) as exc_info:
        client.get_car(99)
    assert "CarNotFoundError" in str(exc_info.value)
    assert "HTTP 404" in str(exc_info.value)
