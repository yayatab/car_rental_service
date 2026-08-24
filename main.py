import typer
import uvicorn

from src.cli.main import app as cli_app

app = typer.Typer(help="DriveNow Vehicle & Rental Management System")

app.add_typer(cli_app, name="cli", help="Run CLI management commands")


@app.command("server")
def run_server(
        host: str = typer.Option("0.0.0.0", "--host", "-h", help="Bind host address"),
        port: int = typer.Option(8000, "--port", "-p", help="Bind port number"),
        reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload on code change")
) -> None:
    uvicorn.run(
        "src.api.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    app()
