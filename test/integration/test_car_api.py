import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_car(async_client: AsyncClient):
    create_payload = {
        "model": "Mazda CX-5",
        "year": 2023,
        "status": "AVAILABLE"
    }

    response = await async_client.post("/api/v1/cars", json=create_payload)
    assert response.status_code == 201
    car_data = response.json()
    assert car_data["id"] is not None
    assert car_data["model"] == "Mazda CX-5"
    assert car_data["year"] == 2023
    assert car_data["status"] == "AVAILABLE"

    # Get by ID
    get_response = await async_client.get(f"/api/v1/cars/{car_data['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["model"] == "Mazda CX-5"


@pytest.mark.asyncio
async def test_create_car_validation_error(async_client: AsyncClient):
    invalid_payload = {
        "model": "Future Car",
        "year": 1800,  # Below ge=1900
        "status": "AVAILABLE"
    }
    response = await async_client.post("/api/v1/cars", json=invalid_payload)
    assert response.status_code == 422
    assert "ValidationError" in response.json()["error"]


@pytest.mark.asyncio
async def test_list_cars_with_filter(async_client: AsyncClient):
    await async_client.post("/api/v1/cars", json={"model": "Car A", "year": 2020, "status": "AVAILABLE"})
    await async_client.post("/api/v1/cars", json={"model": "Car B", "year": 2021, "status": "UNDER_MAINTENANCE"})

    # Filter AVAILABLE
    response = await async_client.get("/api/v1/cars?status=AVAILABLE")
    assert response.status_code == 200
    cars = response.json()
    assert len(cars) >= 1
    assert all(c["status"] == "AVAILABLE" for c in cars)


@pytest.mark.asyncio
async def test_update_car_status(async_client: AsyncClient):
    create_res = await async_client.post(
        "/api/v1/cars",
        json={"model": "BMW 3 Series", "year": 2022, "status": "AVAILABLE"}
    )
    car_id = create_res.json()["id"]

    patch_res = await async_client.patch(
        f"/api/v1/cars/{car_id}/status",
        json={"status": "UNDER_MAINTENANCE"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "UNDER_MAINTENANCE"


@pytest.mark.asyncio
async def test_update_car_put(async_client: AsyncClient):
    create_res = await async_client.post(
        "/api/v1/cars",
        json={"model": "Old Model", "year": 2020, "status": "AVAILABLE"}
    )
    car_id = create_res.json()["id"]

    put_res = await async_client.put(
        f"/api/v1/cars/{car_id}",
        json={"model": "New Model", "year": 2025}
    )
    assert put_res.status_code == 200
    assert put_res.json()["model"] == "New Model"
    assert put_res.json()["year"] == 2025


@pytest.mark.asyncio
async def test_delete_car_success(async_client: AsyncClient):
    create_res = await async_client.post(
        "/api/v1/cars",
        json={"model": "Audi A3", "year": 2021, "status": "AVAILABLE"}
    )
    car_id = create_res.json()["id"]

    del_res = await async_client.delete(f"/api/v1/cars/{car_id}")
    assert del_res.status_code == 204

    # Verify not found
    get_res = await async_client.get(f"/api/v1/cars/{car_id}")
    assert get_res.status_code == 404
