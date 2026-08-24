# Architectural and Design Decisions

<a id="db_choice"></a>

## 1. Database Choice

### NoSQL vs SQL

The DriveNow car rental system requires relational integrity (e.g. foreign keys linking rentals to vehicles),
transactional consistency for state transitions (preventing double-rentals of vehicles), and structured querying (e.g.,
filtering vehicles by status). Therefore, an RDBMS is the ideal fit.

### RDBMS Selection (MySQL)

MySQL 8.0 was chosen because:

1. **Lightweight & High Performance**: Minimal setup overhead with high read/write throughput.
2. **Standard Compatibility**: Standard SQL dialect easily replaceable with PostgreSQL or Oracle if required.
3. **ORM Portability**: SQLAlchemy abstracts dialect-specific details, making database migrations effortless.
4. **Open Source & Cloud Ready**: Universal managed support on AWS RDS, GCP Cloud SQL, and Azure.

---

<a id="architecture_choice"></a>

## 2. Architecture: Layered Clean Architecture

The codebase strictly adheres to **Separation of Concerns** and **SOLID Principles**:

* **Presentation Layer (`src/api`, `src/cli`)**:
  - FastAPI routers handle HTTP serialization, query parsing, and response status codes.
  - Typer CLI with Rich formatting provides an intuitive terminal interface.
* **Business Logic Layer (`src/services`)**:
  - Encapsulates fleet validation rules, transactional state transitions (`AVAILABLE` <-> `IN_USE`), and metric updates.
  - Decoupled from transport mechanism (can be invoked by HTTP, CLI, or message queues).
* **Data Access Layer (`src/dal/repositories`)**:
  - Encapsulates SQLAlchemy ORM queries, row-level locking (`with_for_update`), and pagination.
* **Core / Infrastructure Layer (`src/core`)**:
  - Configuration via `pydantic-settings`, async database engine management, structured logging, and Prometheus metrics.

---

<a id="framework_choice"></a>

## 3. Web Framework: FastAPI & Pydantic V2

* **Asynchronous from Ground Up**: Native Python `async`/`await` support for non-blocking I/O operations.
* **Type Safety & Auto-Documentation**: Pydantic V2 schemas generate OpenAPI 3.1 specifications (`/docs`) and validate
  inputs with informative error messages.
* **Dependency Injection**: FastAPI's DI system cleanly provides database sessions and service instances per request.

---

<a id="orm_choice"></a>

## 4. ORM & Concurrency: SQLAlchemy 2.0 Async + aiomysql

* Modern SQLAlchemy 2.0 syntax with `Mapped[...]` and `mapped_column[...]`.
* Asynchronous MySQL driver (`aiomysql`) avoids blocking the event loop during database I/O.
* **Concurrency Safety**: `with_for_update()` row-level locks prevent race conditions during simultaneous rental
  requests for the same vehicle.

---

<a id="observability_choice"></a>

## 5. Observability: Prometheus Metrics & Dual-Target Logging

* **Metrics**: Real-time fleet gauges (`active_cars_total`, `ongoing_rentals_total`), HTTP request latency histograms,
  and operation counters exported via `/metrics`.
* **Logging**: Standard Python `logging` with simultaneous console output and rotating file storage (`logs/app.log`).

---

<a id="event_choice"></a>

## 6. Event System: Decoupled Domain Events

* Abstract `EventPublisher` interface allows seamless dispatching of domain events (`CarStatusChangedEvent`,
  `RentalStartedEvent`, `RentalEndedEvent`).
* In-memory implementation out of the box with ready-to-plug broker support (RabbitMQ / Redis / Kafka).

(and to be completely honest, i would have chosen java/kotlin. it's more type safe. and i'm more used to it)