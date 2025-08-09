"""Tests for observability and metrics system."""

import time
import unittest.mock

import pytest

from autodocs_mcp.observability import (
    MetricsCollector,
    RequestMetrics,
    get_metrics_collector,
    track_request,
)


class TestRequestMetrics:
    """Test RequestMetrics functionality."""

    def test_request_metrics_creation(self):
        """Test creating request metrics."""
        metrics = RequestMetrics(
            request_id="test-123",
            operation="test_operation",
        )

        assert metrics.request_id == "test-123"
        assert metrics.operation == "test_operation"
        assert metrics.success is False
        assert metrics.error_type is None
        assert metrics.cache_hit is False
        assert metrics.package_name is None
        assert metrics.dependency_count == 0

    def test_duration_calculation(self):
        """Test duration calculation."""
        start_time = time.time()
        metrics = RequestMetrics(
            request_id="test-123",
            operation="test_operation",
            start_time=start_time,
        )

        # Should calculate duration from start_time to now
        duration = metrics.duration_ms
        assert duration > 0

        # Should use end_time if set
        end_time = start_time + 1.5  # 1.5 seconds later
        metrics.end_time = end_time
        assert metrics.duration_ms == 1500.0  # 1.5 seconds in ms

    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = RequestMetrics(
            request_id="test-123",
            operation="test_operation",
            start_time=1234567890.0,
            end_time=1234567891.5,
            success=True,
            error_type="TestError",
            cache_hit=True,
            package_name="test-package",
            dependency_count=3,
        )

        data = metrics.to_dict()

        expected_keys = {
            "request_id",
            "operation",
            "duration_ms",
            "success",
            "error_type",
            "cache_hit",
            "package_name",
            "dependency_count",
            "timestamp",
        }
        assert set(data.keys()) == expected_keys
        assert data["request_id"] == "test-123"
        assert data["operation"] == "test_operation"
        assert data["duration_ms"] == 1500.0
        assert data["success"] is True
        assert data["error_type"] == "TestError"
        assert data["cache_hit"] is True
        assert data["package_name"] == "test-package"
        assert data["dependency_count"] == 3
        assert data["timestamp"] == 1234567890.0


class TestMetricsCollector:
    """Test MetricsCollector functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.collector = MetricsCollector()

    def test_start_request(self):
        """Test starting request tracking."""
        metrics = self.collector.start_request("req-123", "test_op")

        assert metrics.request_id == "req-123"
        assert metrics.operation == "test_op"
        assert "req-123" in self.collector.active_requests
        assert self.collector.active_requests["req-123"] == metrics

    def test_finish_request_success(self):
        """Test finishing request successfully."""
        self.collector.start_request("req-123", "test_op")

        # Finish the request
        self.collector.finish_request(
            "req-123",
            success=True,
            cache_hit=True,
            package_name="test-package",
            dependency_count=2,
        )

        # Should be removed from active requests
        assert "req-123" not in self.collector.active_requests

        # Should be added to completed requests
        assert len(self.collector.completed_requests) == 1
        completed = self.collector.completed_requests[0]
        assert completed.success is True
        assert completed.cache_hit is True
        assert completed.package_name == "test-package"
        assert completed.dependency_count == 2
        assert completed.end_time is not None

    def test_finish_request_error(self):
        """Test finishing request with error."""
        self.collector.start_request("req-123", "test_op")

        # Finish the request with error
        self.collector.finish_request(
            "req-123",
            success=False,
            error_type="TestError",
            package_name="test-package",
        )

        # Should be removed from active requests
        assert "req-123" not in self.collector.active_requests

        # Should be added to completed requests
        assert len(self.collector.completed_requests) == 1
        completed = self.collector.completed_requests[0]
        assert completed.success is False
        assert completed.error_type == "TestError"
        assert completed.package_name == "test-package"

    def test_finish_nonexistent_request(self):
        """Test finishing a request that doesn't exist."""
        # Should not raise an error
        self.collector.finish_request("nonexistent", success=True)

        assert len(self.collector.completed_requests) == 0
        assert len(self.collector.active_requests) == 0

    def test_ring_buffer_behavior(self):
        """Test that completed requests form a ring buffer."""
        # Set a small max for testing
        self.collector.max_completed = 3

        # Add more requests than the max
        for i in range(5):
            self.collector.start_request(f"req-{i}", "test_op")
            self.collector.finish_request(f"req-{i}", success=True)

        # Should only keep the last 3
        assert len(self.collector.completed_requests) == 3
        request_ids = [r.request_id for r in self.collector.completed_requests]
        assert request_ids == ["req-2", "req-3", "req-4"]

    def test_get_stats_empty(self):
        """Test getting stats with no requests."""
        stats = self.collector.get_stats()

        expected_keys = {
            "total_requests",
            "active_requests",
            "cache_hit_rate",
            "success_rate",
            "operations",
            "response_times",
        }
        assert set(stats.keys()) == expected_keys
        assert stats["total_requests"] == 0
        assert stats["active_requests"] == 0
        assert stats["cache_hit_rate"] == 0.0
        assert stats["success_rate"] == 0.0
        assert stats["operations"] == {}

    @pytest.mark.skip(
        "Complex time mocking issue - percentile calculation test needs refactoring"
    )
    def test_get_stats_with_requests(self):
        """Test getting stats with completed requests."""
        # Add some test requests
        requests_data = [
            ("req-1", "scan_deps", True, True, 100.0),  # Success, cache hit
            ("req-2", "get_docs", True, False, 200.0),  # Success, no cache
            ("req-3", "scan_deps", False, False, 50.0),  # Failure
            ("req-4", "get_docs", True, True, 150.0),  # Success, cache hit
        ]

        # Mock time.time() to return predictable values
        current_time = 1000.0
        time_values = []

        for _req_id, _operation, _success, _cache_hit, duration_ms in requests_data:
            # Start time for this request
            time_values.append(current_time)
            # End time for this request
            time_values.append(current_time + (duration_ms / 1000.0))

        with unittest.mock.patch(
            "autodocs_mcp.observability.time.time", side_effect=time_values
        ):
            for req_id, operation, success, cache_hit, _duration_ms in requests_data:
                self.collector.start_request(req_id, operation)
                self.collector.finish_request(
                    req_id, success=success, cache_hit=cache_hit
                )

        stats = self.collector.get_stats()

        # Check overall stats
        assert stats["total_requests"] == 4
        assert stats["success_rate"] == 75.0  # 3/4 successful
        assert stats["cache_hit_rate"] == 50.0  # 2/4 cache hits
        assert stats["active_requests"] == 0

        # Check response times
        response_times = stats["response_times"]
        assert response_times["avg_ms"] == 125.0  # (100+200+50+150)/4
        assert response_times["min_ms"] == 50.0
        assert response_times["max_ms"] == 200.0
        assert response_times["p50_ms"] == 125.0  # median of [50, 100, 150, 200]

        # Check operations breakdown
        operations = stats["operations"]
        assert "scan_deps" in operations
        assert "get_docs" in operations
        assert operations["scan_deps"]["count"] == 2
        assert operations["get_docs"]["count"] == 2

    def test_get_health_metrics(self):
        """Test getting health-related metrics."""
        # Add some requests with errors
        for i in range(5):
            self.collector.start_request(f"req-{i}", "test_op")
            success = i < 3  # First 3 succeed, last 2 fail
            self.collector.finish_request(f"req-{i}", success=success)

        health_metrics = self.collector.get_health_metrics()

        assert health_metrics["active_requests"] == 0
        assert health_metrics["total_completed"] == 5
        assert health_metrics["recent_errors"] == 2
        assert health_metrics["recent_requests"] == 5
        assert health_metrics["error_rate_recent"] == 40.0  # 2/5 = 40%

    def test_get_health_metrics_empty(self):
        """Test getting health metrics with no requests."""
        health_metrics = self.collector.get_health_metrics()

        assert health_metrics["active_requests"] == 0
        assert health_metrics["total_completed"] == 0
        assert health_metrics["recent_errors"] == 0


class TestTrackRequestContextManager:
    """Test the track_request context manager."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset the global collector
        global_collector = get_metrics_collector()
        global_collector.active_requests.clear()
        global_collector.completed_requests.clear()

    async def test_track_request_success(self):
        """Test tracking a successful request."""
        collector = get_metrics_collector()

        async with track_request("test_operation") as metrics:
            assert metrics.operation == "test_operation"
            assert metrics.request_id is not None
            # Should be in active requests during execution
            assert metrics.request_id in collector.active_requests

            # Manually finish the request (as would be done in actual MCP tools)
            collector.finish_request(metrics.request_id, success=True)

        # After completion, should be moved to completed
        assert metrics.request_id not in collector.active_requests
        assert len(collector.completed_requests) == 1
        assert collector.completed_requests[0].success is True

    async def test_track_request_with_exception(self):
        """Test tracking a request that raises an exception."""
        with pytest.raises(ValueError):
            async with track_request("test_operation"):
                raise ValueError("Test error")

        # Should still be tracked as a failed request
        collector = get_metrics_collector()
        assert len(collector.completed_requests) == 1
        completed = collector.completed_requests[0]
        assert completed.success is False
        assert completed.error_type == "ValueError"

    async def test_track_request_custom_id(self):
        """Test tracking request with custom ID."""
        custom_id = "custom-request-123"
        collector = get_metrics_collector()

        async with track_request("test_operation", custom_id) as metrics:
            assert metrics.request_id == custom_id
            # Manually finish the request
            collector.finish_request(custom_id, success=True)

        assert len(collector.completed_requests) == 1
        assert collector.completed_requests[0].request_id == custom_id


class TestGlobalMetricsCollector:
    """Test the global metrics collector."""

    def test_get_metrics_collector_singleton(self):
        """Test that get_metrics_collector returns the same instance."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        assert collector1 is collector2
        assert isinstance(collector1, MetricsCollector)


class TestLoggingConfiguration:
    """Test logging configuration functions."""

    def test_setup_production_logging(self):
        """Test production logging setup."""
        from autodocs_mcp.observability import setup_production_logging

        # Should not raise any errors
        setup_production_logging()

    def test_setup_development_logging(self):
        """Test development logging setup."""
        from autodocs_mcp.observability import setup_development_logging

        # Should not raise any errors
        setup_development_logging()
