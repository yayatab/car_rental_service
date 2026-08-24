# DriveNow – Vehicle Management & Rental System

[![Tests](https://img.shields.io/badge/Tests-45%20Passed%20(92%25%20Coverage)-brightgreen.svg)]()

DriveNow is an enterprise-grade vehicle fleet and rental transaction management service. Designed with **Layered Clean
Architecture**, SOLID principles, fully asynchronous database I/O, Pydantic V2 data validation, Prometheus metrics,
structured dual-target logging, and an interactive CLI client.

For detailed architecture rationale and database selection analysis, see [reasoning.md](reasoning.md).

---

## Key Features

- **Fleet Management**: Add, update, delete, and list vehicles with status filtering (`AVAILABLE`, `IN_USE`,
  `UNDER_MAINTENANCE`).
- **Rental Transactions**: Start new rentals with concurrency safety and conclude rentals with automatic vehicle status
  transitions.
- **Asynchronous Architecture**: End-to-end async operations using FastAPI, SQLAlchemy 2.0 Async, and `aiomysql`.
- **Interactive CLI Client**: Powered by `typer` + `rich` for formatted tables and intuitive commands.
- **Dual Observability**:
  - **Logging**: Standard Python `logging` writing simultaneously to console and rotating files (`logs/app.log`).
  - **Metrics**: Real-time Prometheus metrics (`/metrics`) tracking active vehicles, ongoing rentals, and request
    latency.
- **Pluggable Event System**: Abstract domain event publisher for decoupled workflows (in-memory + message queue ready).

---

## System Architecture

```
CarRental/
├── src/
│   ├── dal/              # Data Access Layer
│   |   ├── models/       # ORM Layer: SQLAlchemy declarative models (Car, Rental)
│   |   └──repositories/  # Data Access Layer: SQLAlchemy async CRUD repositories
│   ├── api/              # Presentation Layer: FastAPI routers, dependencies, and middleware
│   ├── cli/              # Presentation Layer: Typer CLI and HTTP client
│   ├── services/         # Business Logic Layer: Fleet & Rental domain services
│   ├── schemas/          # Validation Layer: Pydantic V2 request & response DTOs
│   ├── core/             # Infrastructure: Config, Async DB Engine, Logging, Metrics
│   └── events/           # Event Layer: Domain events & publisher interface
├── test/                 # Test Suite: Unit & Integration tests (47 tests, 92% coverage)
├── resources/sql/        # Database DDL initialization script (init.sql)
├── docker-compose.yaml   # Container orchestration for MySQL and API
├── Dockerfile            # Production container build
└── main.py               # Unified entrypoint (Server and CLI)
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) or standard `pip`
- Docker & Docker Compose (for containerized setup)

### 2. Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd CarRental

# Sync and install dependencies with uv
uv sync --all-extras

# Or install editable with uv pip
uv pip install -e ".[dev]"
```

### 3. Run Locally with uv

```bash
# Start the FastAPI REST server
uv run python main.py server --host 0.0.0.0 --port 8000

# In another terminal, run CLI commands with uv
uv run python main.py cli cars list
```

### 4. Run with Docker Compose

Start both the MySQL 8.0 database (pre-seeded via `init.sql`) and the FastAPI backend:

```bash
docker-compose up -d --build
```

- **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## CLI Client Usage

The CLI client communicates with the REST API using Rich formatting:

### Fleet Commands (`cars`)

```bash
# List all cars
uv run python main.py cli cars list

# Filter cars by status (AVAILABLE, IN_USE, UNDER_MAINTENANCE)
uv run python main.py cli cars list --status AVAILABLE

# Register a new car
uv run python main.py cli cars add --model "Tesla Model Y" --year 2024 --status AVAILABLE

# Get car details
uv run python main.py cli cars get 1

# Update car status
uv run python main.py cli cars update-status 1 --status UNDER_MAINTENANCE

# Delete a car (only permitted if not rented)
uv run python main.py cli cars delete 4
```

### Rental Commands (`rentals`)

```bash
# Start a new rental
uv run python main.py cli rentals start --car-id 1 --customer "Alice Johnson"

# List ongoing active rentals
uv run python main.py cli rentals list --active

# Conclude/end an active rental
uv run python main.py cli rentals end 1
```

### Health Command

```bash
uv run python main.py cli health
```

---

## REST API Reference

| Method   | Endpoint                   | Description                                  |
|----------|----------------------------|----------------------------------------------|
| `POST`   | `/api/v1/cars`             | Register a new vehicle                       |
| `GET`    | `/api/v1/cars`             | List vehicles (optional `?status=AVAILABLE`) |
| `GET`    | `/api/v1/cars/{id}`        | Get vehicle details                          |
| `PATCH`  | `/api/v1/cars/{id}/status` | Update vehicle status                        |
| `PUT`    | `/api/v1/cars/{id}`        | Update vehicle details                       |
| `DELETE` | `/api/v1/cars/{id}`        | Delete vehicle                               |
| `POST`   | `/api/v1/rentals`          | Register/start a rental                      |
| `POST`   | `/api/v1/rentals/{id}/end` | Conclude an active rental                    |
| `GET`    | `/api/v1/rentals`          | List rentals (optional `?active_only=true`)  |
| `GET`    | `/api/v1/rentals/{id}`     | Get rental details                           |
| `GET`    | `/health`                  | Health check & DB status                     |
| `GET`    | `/metrics`                 | Prometheus metrics scrape                    |

---

## Testing & Code Coverage

The project includes unit tests, integration tests, and CLI tests using `pytest` and `aiosqlite` in-memory test
databases:

```bash
# Run test suite with coverage report using uv
uv run pytest -v --cov=src test/
```

Test results: **45 passed, 92% coverage**.
