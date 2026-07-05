import time
from typing import Any

from prometheus_client import Counter as PromCounter, Gauge, Histogram, generate_latest

BOOKINGS_CREATED = PromCounter("app_bookings_created_total", "Appointments booked", ["source_channel"])
BOOKING_FAILURES = PromCounter("app_booking_failures_total", "Booking failures", ["error_type"])
AI_TOOL_LATENCY = Histogram("app_ai_tool_latency_seconds", "AI tool call latency", ["tool_name"])
WEBHOOK_FAILURES = PromCounter("app_webhook_failures_total", "Webhook processing failures", ["provider"])
ACTIVE_CONNECTIONS = Gauge("app_active_connections", "Active WebSocket connections")


def record_booking(source_channel: str) -> None:
    BOOKINGS_CREATED.labels(source_channel=source_channel).inc()


def record_booking_failure(error_type: str) -> None:
    BOOKING_FAILURES.labels(error_type=error_type).inc()


def record_ai_tool_latency(tool_name: str, duration: float) -> None:
    AI_TOOL_LATENCY.labels(tool_name=tool_name).observe(duration)


def record_webhook_failure(provider: str) -> None:
    WEBHOOK_FAILURES.labels(provider=provider).inc()


class Timer:
    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        self.start: float | None = None

    def __enter__(self) -> "Timer":
        self.start = time.monotonic()
        return self

    def __exit__(self, *args: Any) -> None:
        if self.start is not None:
            record_ai_tool_latency(self.tool_name, time.monotonic() - self.start)


def metrics_output() -> bytes:
    return generate_latest()


__all__ = [
    "BOOKINGS_CREATED",
    "BOOKING_FAILURES",
    "AI_TOOL_LATENCY",
    "WEBHOOK_FAILURES",
    "ACTIVE_CONNECTIONS",
    "record_booking",
    "record_booking_failure",
    "record_ai_tool_latency",
    "record_webhook_failure",
    "Timer",
    "metrics_output",
]
