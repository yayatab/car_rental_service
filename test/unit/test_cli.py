from unittest.mock import patch

from typer.testing import CliRunner

from src.cli.main import app

runner = CliRunner()


def test_cli_cars_list_mocked():
    mock_cars = [
        {
            "id": 1,
            "model": "Toyota Corolla",
            "year": 2022,
            "status": "AVAILABLE",
            "created_at": "2026-08-24T12:00:00Z",
            "updated_at": "2026-08-24T12:00:00Z"
        }
    ]

    with patch("src.cli.main.client.list_cars", return_value=mock_cars):
        result = runner.invoke(app, ["cars", "list"])
        assert result.exit_code == 0
        assert "Toyota Corolla" in result.output
        assert "AVAILABLE" in result.output


def test_cli_cars_list_empty():
    with patch("src.cli.main.client.list_cars", return_value=[]):
        result = runner.invoke(app, ["cars", "list"])
        assert result.exit_code == 0
        assert "No vehicles found" in result.output


def test_cli_cars_add_mocked():
    mock_car = {
        "id": 2,
        "model": "Tesla Model 3",
        "year": 2024,
        "status": "AVAILABLE",
        "created_at": "2026-08-24T12:00:00Z",
        "updated_at": "2026-08-24T12:00:00Z"
    }

    with patch("src.cli.main.client.add_car", return_value=mock_car):
        result = runner.invoke(app, ["cars", "add", "--model", "Tesla Model 3", "--year", "2024"])
        assert result.exit_code == 0
        assert "Vehicle registered successfully" in result.output
        assert "Tesla Model 3" in result.output


def test_cli_cars_get_mocked():
    mock_car = {
        "id": 1,
        "model": "Toyota Corolla",
        "year": 2022,
        "status": "AVAILABLE",
        "created_at": "2026-08-24T12:00:00Z",
        "updated_at": "2026-08-24T12:00:00Z"
    }

    with patch("src.cli.main.client.get_car", return_value=mock_car):
        result = runner.invoke(app, ["cars", "get", "1"])
        assert result.exit_code == 0
        assert "Vehicle #1 Details" in result.output
        assert "Toyota Corolla" in result.output


def test_cli_cars_update_status_mocked():
    mock_car = {
        "id": 1,
        "model": "Toyota Corolla",
        "year": 2022,
        "status": "UNDER_MAINTENANCE",
        "created_at": "2026-08-24T12:00:00Z",
        "updated_at": "2026-08-24T12:00:00Z"
    }

    with patch("src.cli.main.client.update_car_status", return_value=mock_car):
        result = runner.invoke(app, ["cars", "update-status", "1", "--status", "UNDER_MAINTENANCE"])
        assert result.exit_code == 0
        assert "UNDER_MAINTENANCE" in result.output


def test_cli_cars_delete_mocked():
    with patch("src.cli.main.client.delete_car", return_value=None):
        result = runner.invoke(app, ["cars", "delete", "1"])
        assert result.exit_code == 0
        assert "Vehicle #1 was successfully removed" in result.output


def test_cli_rentals_start_mocked():
    mock_rental = {
        "id": 1,
        "car_id": 2,
        "customer_name": "Alice",
        "start_date": "2026-08-24T12:00:00Z",
        "end_date": None,
        "created_at": "2026-08-24T12:00:00Z",
        "updated_at": "2026-08-24T12:00:00Z"
    }

    with patch("src.cli.main.client.start_rental", return_value=mock_rental):
        result = runner.invoke(app, ["rentals", "start", "--car-id", "2", "--customer", "Alice"])
        assert result.exit_code == 0
        assert "Rental transaction started successfully" in result.output


def test_cli_rentals_end_mocked():
    mock_response = {
        "rental": {
            "id": 1,
            "car_id": 2,
            "customer_name": "Alice",
            "start_date": "2026-08-24T12:00:00Z",
            "end_date": "2026-08-24T14:00:00Z",
            "created_at": "2026-08-24T12:00:00Z",
            "updated_at": "2026-08-24T14:00:00Z"
        },
        "message": "Rental #1 successfully ended."
    }

    with patch("src.cli.main.client.end_rental", return_value=mock_response):
        result = runner.invoke(app, ["rentals", "end", "1"])
        assert result.exit_code == 0
        assert "Rental transaction completed" in result.output


def test_cli_rentals_list_mocked():
    mock_rentals = [
        {
            "id": 1,
            "car_id": 2,
            "customer_name": "Alice",
            "start_date": "2026-08-24T12:00:00Z",
            "end_date": None,
            "created_at": "2026-08-24T12:00:00Z",
            "updated_at": "2026-08-24T12:00:00Z"
        }
    ]

    with patch("src.cli.main.client.list_rentals", return_value=mock_rentals):
        result = runner.invoke(app, ["rentals", "list"])
        assert result.exit_code == 0
        assert "ONGOING" in result.output
        assert "Alice" in result.output


def test_cli_health_check_mocked():
    mock_health = {
        "status": "healthy",
        "version": "0.1.0",
        "database": "connected"
    }

    with patch("src.cli.main.client.health_check", return_value=mock_health):
        result = runner.invoke(app, ["health"])
        assert result.exit_code == 0
        assert "healthy" in result.output
        assert "connected" in result.output
