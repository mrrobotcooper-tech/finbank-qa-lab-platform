from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

REGISTRY = CollectorRegistry()

HTTP_REQUESTS = Counter(
    "finbank_http_requests_total",
    "HTTP requests by method, path template and status",
    ["method", "path", "status"],
    registry=REGISTRY,
)
HTTP_LATENCY = Histogram(
    "finbank_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    registry=REGISTRY,
)
DEPENDENCY_UP = Gauge(
    "finbank_dependency_up",
    "1 if dependency check succeeded, else 0",
    ["dependency"],
    registry=REGISTRY,
)


def render_metrics() -> bytes:
    return generate_latest(REGISTRY)


def set_dependency_up(name: str, is_up: bool) -> None:
    DEPENDENCY_UP.labels(dependency=name).set(1 if is_up else 0)
