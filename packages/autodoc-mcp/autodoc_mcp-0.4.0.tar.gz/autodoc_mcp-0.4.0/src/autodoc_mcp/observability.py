"""Observability and metrics collection for AutoDocs MCP Server."""

import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RequestMetrics:
    """Track request performance metrics."""

    request_id: str
    operation: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    success: bool = False
    error_type: str | None = None
    cache_hit: bool = False
    package_name: str | None = None
    dependency_count: int = 0

    @property
    def duration_ms(self) -> float:
        """Calculate request duration in milliseconds."""
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for logging."""
        return {
            "request_id": self.request_id,
            "operation": self.operation,
            "duration_ms": round(self.duration_ms, 2),
            "success": self.success,
            "error_type": self.error_type,
            "cache_hit": self.cache_hit,
            "package_name": self.package_name,
            "dependency_count": self.dependency_count,
            "timestamp": self.start_time,
        }


class MetricsCollector:
    """Collect and aggregate performance metrics."""

    def __init__(self) -> None:
        self.active_requests: dict[str, RequestMetrics] = {}
        self.completed_requests: list[RequestMetrics] = []
        self.max_completed = 1000  # Keep last 1000 requests

    def start_request(self, request_id: str, operation: str) -> RequestMetrics:
        """Start tracking a request."""
        metrics = RequestMetrics(request_id=request_id, operation=operation)
        self.active_requests[request_id] = metrics
        return metrics

    def finish_request(
        self,
        request_id: str,
        success: bool = True,
        error_type: str | None = None,
        cache_hit: bool = False,
        package_name: str | None = None,
        dependency_count: int = 0,
    ) -> None:
        """Finish tracking a request."""
        if request_id in self.active_requests:
            metrics = self.active_requests.pop(request_id)
            metrics.end_time = time.time()
            metrics.success = success
            metrics.error_type = error_type
            metrics.cache_hit = cache_hit
            metrics.package_name = package_name
            metrics.dependency_count = dependency_count

            # Log the completed request
            logger.info("Request completed", **metrics.to_dict())

            # Store for aggregation (ring buffer)
            self.completed_requests.append(metrics)
            if len(self.completed_requests) > self.max_completed:
                self.completed_requests.pop(0)

    def get_stats(self) -> dict[str, Any]:
        """Get aggregated performance statistics."""
        if not self.completed_requests:
            return {
                "total_requests": 0,
                "active_requests": len(self.active_requests),
                "cache_hit_rate": 0.0,
                "success_rate": 0.0,
                "operations": {},
                "response_times": {"avg_ms": 0.0},
            }

        total = len(self.completed_requests)
        successful = sum(1 for r in self.completed_requests if r.success)
        cache_hits = sum(1 for r in self.completed_requests if r.cache_hit)

        durations = [r.duration_ms for r in self.completed_requests]

        # Calculate percentiles
        sorted_durations = sorted(durations)
        p50_idx = max(0, int(0.5 * len(sorted_durations)) - 1)
        p95_idx = max(0, int(0.95 * len(sorted_durations)) - 1)
        p99_idx = max(0, int(0.99 * len(sorted_durations)) - 1)

        # Operation breakdown
        operations = {}
        for r in self.completed_requests:
            op = r.operation
            if op not in operations:
                operations[op] = {
                    "count": 0,
                    "success_count": 0,
                    "avg_duration_ms": 0.0,
                    "cache_hits": 0,
                }
            operations[op]["count"] += 1
            if r.success:
                operations[op]["success_count"] += 1
            if r.cache_hit:
                operations[op]["cache_hits"] += 1

        # Calculate averages for operations
        for op_name, op_stats in operations.items():
            op_requests = [r for r in self.completed_requests if r.operation == op_name]
            if op_requests:
                op_durations = [r.duration_ms for r in op_requests]
                op_stats["avg_duration_ms"] = round(
                    sum(op_durations) / len(op_durations), 2
                )

        return {
            "total_requests": total,
            "success_rate": round(successful / total * 100, 2),
            "cache_hit_rate": round(cache_hits / total * 100, 2),
            "active_requests": len(self.active_requests),
            "operations": operations,
            "response_times": {
                "avg_ms": round(sum(durations) / len(durations), 2),
                "p50_ms": round(sorted_durations[p50_idx], 2),
                "p95_ms": round(sorted_durations[p95_idx], 2),
                "p99_ms": round(sorted_durations[p99_idx], 2),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
            },
            "timestamp": time.time(),
        }

    def get_health_metrics(self) -> dict[str, Any]:
        """Get metrics relevant for health checks."""
        if not self.completed_requests:
            return {
                "active_requests": len(self.active_requests),
                "total_completed": 0,
                "recent_errors": 0,
            }

        # Look at last 100 requests for health indicators
        recent_requests = self.completed_requests[-100:]
        recent_errors = sum(1 for r in recent_requests if not r.success)

        return {
            "active_requests": len(self.active_requests),
            "total_completed": len(self.completed_requests),
            "recent_errors": recent_errors,
            "recent_requests": len(recent_requests),
            "error_rate_recent": round(recent_errors / len(recent_requests) * 100, 2)
            if recent_requests
            else 0.0,
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()


@asynccontextmanager
async def track_request(
    operation: str, request_id: str | None = None
) -> AsyncGenerator[RequestMetrics, None]:
    """Context manager to track request metrics."""
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]

    metrics = metrics_collector.start_request(request_id, operation)

    try:
        yield metrics
        # Don't automatically finish here - let the caller set specific details
    except Exception as e:
        metrics_collector.finish_request(
            request_id, success=False, error_type=type(e).__name__
        )
        raise


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector


def setup_production_logging() -> None:
    """Configure structured logging for production."""
    import logging
    import sys

    processors: list[Any] = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.JSONRenderer(),  # JSON for production
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def setup_development_logging() -> None:
    """Configure structured logging for development."""
    import logging
    import sys

    processors: list[Any] = [
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),  # Pretty console output for dev
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )
