from prometheus_client import Counter, Gauge, Histogram

ACTIVE_CARS_GAUGE = Gauge(
    "active_cars_total",
    "Number of cars in fleet grouped by operational status",
    ["status"]
)

ONGOING_RENTALS_GAUGE = Gauge(
    "ongoing_rentals_total",
    "Number of currently ongoing (active) rentals"
)

# used for latency
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["method", "endpoint", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
)

OPERATION_DURATION_SECONDS = Histogram(
    "business_operation_duration_seconds",
    "Duration of business operations in seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

RENTAL_OPERATIONS_TOTAL = Counter(
    "rental_operations_total",
    "Total count of rental operations",
    ["operation", "status"]
)

CAR_OPERATIONS_TOTAL = Counter(
    "car_operations_total",
    "Total count of car fleet management operations",
    ["operation", "status"]
)


def update_fleet_metrics(available_count: int, in_use_count: int, maintenance_count: int, ongoing_rentals: int) -> None:
    ACTIVE_CARS_GAUGE.labels(status="AVAILABLE").set(available_count)
    ACTIVE_CARS_GAUGE.labels(status="IN_USE").set(in_use_count)
    ACTIVE_CARS_GAUGE.labels(status="UNDER_MAINTENANCE").set(maintenance_count)
    ONGOING_RENTALS_GAUGE.set(ongoing_rentals)
