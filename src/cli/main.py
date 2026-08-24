from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.cli.client import RentalApiClient

app = typer.Typer(help="DriveNow Fleet & Rental Management CLI")
cars_app = typer.Typer(help="Manage fleet vehicles (add, update, delete, list)")
rentals_app = typer.Typer(help="Manage rental transactions (start, end, list)")

app.add_typer(cars_app, name="cars")
app.add_typer(rentals_app, name="rentals")

console = Console()
client = RentalApiClient()

STATUS_COLORS = {
    "AVAILABLE": "[bold green]AVAILABLE[/bold green]",
    "IN_USE": "[bold yellow]IN_USE[/bold yellow]",
    "UNDER_MAINTENANCE": "[bold red]UNDER_MAINTENANCE[/bold red]",
}


@cars_app.command("list")
def list_cars(
        status: Optional[str] = typer.Option(
            None,
            "--status",
            "-s",
            help="Filter by status: AVAILABLE, IN_USE, UNDER_MAINTENANCE"
        )
) -> None:
    try:
        cars = client.list_cars(status=status)
        if not cars:
            console.print("[yellow]No vehicles found matching criteria.[/yellow]")
            return

        table = Table(title="DriveNow Vehicle Fleet", show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="center", style="bold")
        table.add_column("Model", style="bright_white")
        table.add_column("Year", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Created At", style="dim")

        for car in cars:
            status_str = STATUS_COLORS.get(car["status"], car["status"])
            table.add_row(
                str(car["id"]),
                car["model"],
                str(car["year"]),
                status_str,
                car["created_at"][:19].replace("T", " ")
            )

        console.print(table)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cars_app.command("add")
def add_car(
        model: str = typer.Option(..., "--model", "-m", help="Vehicle model name (e.g. 'Toyota Corolla')"),
        year: int = typer.Option(..., "--year", "-y", help="Vehicle manufacturing year (e.g. 2024)"),
        status: str = typer.Option("AVAILABLE", "--status", "-s",
                                   help="Initial status: AVAILABLE, IN_USE, UNDER_MAINTENANCE")
) -> None:
    try:
        car = client.add_car(model=model, year=year, status=status.upper())
        console.print(
            Panel(
                f"[bold green]Vehicle registered successfully![/bold green]\n\n"
                f"* ID: [bold]{car['id']}[/bold]\n"
                f"* Model: {car['model']}\n"
                f"* Year: {car['year']}\n"
                f"* Status: {STATUS_COLORS.get(car['status'], car['status'])}",
                title="New Vehicle Added",
                border_style="green"
            )
        )
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cars_app.command("get")
def get_car(car_id: int = typer.Argument(..., help="Unique ID of the vehicle")) -> None:
    try:
        car = client.get_car(car_id=car_id)
        console.print(
            Panel(
                f"* ID: [bold]{car['id']}[/bold]\n"
                f"* Model: {car['model']}\n"
                f"* Year: {car['year']}\n"
                f"* Status: {STATUS_COLORS.get(car['status'], car['status'])}\n"
                f"* Created: {car['created_at']}\n"
                f"* Updated: {car['updated_at']}",
                title=f"Vehicle #{car['id']} Details",
                border_style="cyan"
            )
        )
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cars_app.command("update-status")
def update_car_status(
        car_id: int = typer.Argument(..., help="Unique ID of the vehicle"),
        status: str = typer.Option(
            ...,
            "--status",
            "-s",
            help="New status: AVAILABLE, IN_USE, UNDER_MAINTENANCE"
        )
) -> None:
    try:
        car = client.update_car_status(car_id=car_id, status=status.upper())
        console.print(
            f"[green]✓ Vehicle #{car_id} status updated to[/green] {STATUS_COLORS.get(car['status'], car['status'])}"
        )
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cars_app.command("delete")
def delete_car(car_id: int = typer.Argument(..., help="Unique ID of the vehicle to delete")) -> None:
    try:
        client.delete_car(car_id=car_id)
        console.print(f"[green]✓ Vehicle #{car_id} was successfully removed from the fleet.[/green]")
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@rentals_app.command("start")
def start_rental(
        car_id: int = typer.Option(..., "--car-id", "-c", help="ID of the vehicle to rent"),
        customer: str = typer.Option(..., "--customer", "-n", help="Full name of customer")
) -> None:
    try:
        rental = client.start_rental(car_id=car_id, customer_name=customer)
        console.print(
            Panel(
                f"[bold green]Rental transaction started successfully![/bold green]\n\n"
                f"* Rental ID: [bold]{rental['id']}[/bold]\n"
                f"* Vehicle ID: {rental['car_id']}\n"
                f"* Customer: {rental['customer_name']}\n"
                f"* Start Date: {rental['start_date']}\n"
                f"* Vehicle Status: [bold yellow]IN_USE[/bold yellow]",
                title="New Rental Transaction",
                border_style="green"
            )
        )
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@rentals_app.command("end")
def end_rental(
        rental_id: int = typer.Argument(..., help="ID of the active rental to conclude")
) -> None:
    try:
        response = client.end_rental(rental_id=rental_id)
        rental = response.get("rental", response)
        console.print(
            Panel(
                f"[bold green]Rental transaction completed![/bold green]\n\n"
                f"* Rental ID: [bold]{rental['id']}[/bold]\n"
                f"* Vehicle ID: {rental['car_id']}\n"
                f"* Customer: {rental['customer_name']}\n"
                f"* Ended At: {rental['end_date']}\n"
                f"* Vehicle Status: [bold green]AVAILABLE[/bold green]",
                title="Rental Ended",
                border_style="blue"
            )
        )
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@rentals_app.command("list")
def list_rentals(
        active: bool = typer.Option(False, "--active", "-a", help="Show only active ongoing rentals"),
        car_id: Optional[int] = typer.Option(None, "--car-id", "-c", help="Filter rentals by car ID")
) -> None:
    try:
        rentals = client.list_rentals(active_only=active, car_id=car_id)
        if not rentals:
            console.print("[yellow]No rentals found matching criteria.[/yellow]")
            return

        table = Table(title="DriveNow Rental Transactions", show_header=True, header_style="bold magenta")
        table.add_column("Rental ID", justify="center", style="bold")
        table.add_column("Car ID", justify="center")
        table.add_column("Customer Name", style="bright_white")
        table.add_column("Start Date", justify="center")
        table.add_column("End Date", justify="center")
        table.add_column("Status", justify="center")

        for r in rentals:
            is_active = r["end_date"] is None
            status_str = "[bold yellow]ONGOING[/bold yellow]" if is_active else "[dim green]COMPLETED[/dim green]"
            end_date_str = r["end_date"][:19].replace("T", " ") if r["end_date"] else "-"
            table.add_row(
                str(r["id"]),
                str(r["car_id"]),
                r["customer_name"],
                r["start_date"][:19].replace("T", " "),
                end_date_str,
                status_str
            )

        console.print(table)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


# ==========================================
# System Commands
# ==========================================

@app.command("health")
def health() -> None:
    try:
        data = client.health_check()
        console.print(
            Panel(
                f"* Status: [bold green]{data['status']}[/bold green]\n"
                f"* Version: {data['version']}\n"
                f"* Database: {data['database']}",
                title="System Health Check",
                border_style="green"
            )
        )
    except Exception as exc:
        console.print(f"[bold red]Error connecting to API server:[/bold red] {exc}")


if __name__ == "__main__":
    app()
