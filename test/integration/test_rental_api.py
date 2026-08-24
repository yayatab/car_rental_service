import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_rental_lifecycle_api(async_client: AsyncClient):
    # 1. Add car
    car_res = await async_client.post(
        "/api/v1/cars",
        json={"model": "Kia EV6", "year": 2024, "status": "AVAILABLE"}
    )
    assert car_res.status_code == 201
    car_id = car_res.json()["id"]

    # 2. Start rental
    rental_res = await async_client.post(
        "/api/v1/rentals",
        json={"car_id": car_id, "customer_name": "Daniel Craig"}
    )
    assert rental_res.status_code == 201
    rental_data = rental_res.json()
    rental_id = rental_data["id"]
    assert rental_data["car_id"] == car_id
    assert rental_data["customer_name"] == "Daniel Craig"
    assert rental_data["end_date"] is None

    # 3. Verify car status is IN_USE
    car_check = await async_client.get(f"/api/v1/cars/{car_id}")
    assert car_check.json()["status"] == "IN_USE"

    # 4. Attempting to rent again should fail with 409 Conflict
    conflict_res = await async_client.post(
        "/api/v1/rentals",
        json={"car_id": car_id, "customer_name": "Second Customer"}
    )
    assert conflict_res.status_code == 409

    # 5. End rental
    end_res = await async_client.post(f"/api/v1/rentals/{rental_id}/end")
    assert end_res.status_code == 200
    assert end_res.json()["rental"]["end_date"] is not None

    # 6. Verify car status reverted to AVAILABLE
    car_check_after = await async_client.get(f"/api/v1/cars/{car_id}")
    assert car_check_after.json()["status"] == "AVAILABLE"


@pytest.mark.asyncio
async def test_list_rentals_filters(async_client: AsyncClient):
    # Add two cars
    c1 = (await async_client.post("/api/v1/cars", json={"model": "Car X", "year": 2022, "status": "AVAILABLE"})).json()[
        "id"]
    c2 = (await async_client.post("/api/v1/cars", json={"model": "Car Y", "year": 2023, "status": "AVAILABLE"})).json()[
        "id"]

    # Start rental for c1
    r1 = (await async_client.post("/api/v1/rentals", json={"car_id": c1, "customer_name": "User 1"})).json()["id"]
    # Start and end rental for c2
    r2 = (await async_client.post("/api/v1/rentals", json={"car_id": c2, "customer_name": "User 2"})).json()["id"]
    await async_client.post(f"/api/v1/rentals/{r2}/end")

    # Filter active only
    active_list = (await async_client.get("/api/v1/rentals?active_only=true")).json()
    assert any(r["id"] == r1 for r in active_list)
    assert not any(r["id"] == r2 for r in active_list)

    # Filter by car_id
    c1_list = (await async_client.get(f"/api/v1/rentals?car_id={c1}")).json()
    assert all(r["car_id"] == c1 for r in c1_list)

    # Get single rental by ID
    single_res = await async_client.get(f"/api/v1/rentals/{r1}")
    assert single_res.status_code == 200
    assert single_res.json()["id"] == r1


@pytest.mark.asyncio
async def test_rent_nonexistent_car_returns_404(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/rentals",
        json={"car_id": 9999, "customer_name": "Ghost"}
    )
    assert response.status_code == 404
    assert "Vehicle with ID 9999 was not found" in response.json()["message"]


@pytest.mark.asyncio
async def test_end_nonexistent_rental_returns_404(async_client: AsyncClient):
    response = await async_client.post("/api/v1/rentals/9999/end")
    assert response.status_code == 404
