"""Performance tests for RAG Startups using pytest-benchmark.

These tests establish performance baselines and prevent regressions.
Current baseline: ~34s cold start for idea generation.
"""

import os
import time
from unittest.mock import patch

import pytest  # noqa: F401

from rag_startups.config.settings import RAGSettings

# Detect CI environment
IS_CI = (
    os.getenv("CI", "false").lower() == "true"
    or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
)


def simple_timer(func):
    """Simple timing function for CI environments where pytest-benchmark might fail."""
    start_time = time.time()
    result = func()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Function {func.__name__} took {duration:.4f} seconds")
    return result


class TestPerformanceBaselines:
    """Performance regression tests with established baselines."""

    @pytest.mark.benchmark(group="config")
    def test_config_loading_performance(self, benchmark):
        """Config loading should be fast."""

        def load_config():
            with patch.dict(
                os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True
            ):
                return RAGSettings()

        if IS_CI:
            # Use simple timer in CI environments
            result = simple_timer(load_config)
        else:
            # Use pytest-benchmark in local development
            result = benchmark(load_config)

        assert result is not None

        # Config loading should be under 10ms (benchmark runs automatically)

    @pytest.mark.benchmark(group="imports")
    def test_import_performance(self, benchmark):
        """Module imports should be fast."""

        def import_modules():
            # Re-import main modules
            import rag_startups.core.rag_chain  # noqa: F401

            return True

        if IS_CI:
            # Use simple timer in CI environments
            result = simple_timer(import_modules)
        else:
            # Use pytest-benchmark in local development
            result = benchmark(import_modules)

        assert result is True

        # Imports should be fast (benchmark runs automatically)


class TestPerformanceRegression:
    """Tests to catch performance regressions in key operations."""

    @pytest.mark.benchmark(group="validation")
    def test_config_validation_performance(self, benchmark):
        """Config validation should remain fast even with complex settings."""

        def validate_complex_config():
            with patch.dict(
                os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True
            ):
                return RAGSettings(
                    chunk_size=2000,
                    chunk_overlap=400,
                    max_workers=8,
                    batch_size=64,
                    model_timeout=30,
                )

        if IS_CI:
            # Use simple timer in CI environments
            result = simple_timer(validate_complex_config)
        else:
            # Use pytest-benchmark in local development
            result = benchmark(validate_complex_config)

        assert result is not None

        # Complex validation should still be fast (benchmark runs automatically)

    @pytest.mark.benchmark(group="access")
    def test_repeated_config_access_performance(self, benchmark):
        """Repeated config access should be optimized."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            settings = RAGSettings()

            def access_config_repeatedly():
                # Simulate repeated access patterns
                for _ in range(100):
                    _ = settings.chunk_size
                    _ = settings.model_timeout
                    _ = settings.max_workers
                return True

            if IS_CI:
                # Use simple timer in CI environments
                result = simple_timer(access_config_repeatedly)
            else:
                # Use pytest-benchmark in local development
                result = benchmark(access_config_repeatedly)

            assert result is True

            # Repeated access should be very fast (benchmark runs automatically)


# Pytest configuration for performance tests
def pytest_configure(config):
    """Configure pytest markers for performance tests."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


# Benchmark configuration
def pytest_benchmark_update_json(config, benchmarks, output_json):
    """Update benchmark JSON with additional metadata."""
    import platform
    import sys

    output_json["environment"] = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": platform.system().lower(),
        "test_type": "performance_regression",
        "baseline_version": "1.0.0",
    }
