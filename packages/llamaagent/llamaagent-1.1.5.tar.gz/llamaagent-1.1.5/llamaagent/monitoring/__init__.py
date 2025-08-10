"""Monitoring module for LlamaAgent.

Exports lightweight interfaces and wiring helpers so that optional
submodules can be imported safely by consumers like the API layer.
"""

from typing import Any

# Lightweight monitor for simple usage
class Monitor:
    """Basic monitoring."""

    def __init__(self):
        self.metrics: dict[str, Any] = {}

    def record(self, metric: str, value: Any) -> None:
        """Record a metric."""
        self.metrics[metric] = value


# Re-export health checker from concrete module for convenience
try:
    from .health import HealthChecker  # type: ignore
except Exception:  # pragma: no cover - optional at import time
    class HealthChecker:  # minimal fallback
        def register_check(self, name: str, check_func):
            return None


# Provide a simple setup hook that attaches monitoring middleware when available
def setup_monitoring(app: Any | None = None, config: dict[str, Any] | None = None) -> None:
    """Initialize monitoring systems when middleware is available."""
    try:
        from .middleware import setup_monitoring_middleware  # type: ignore

        if app is not None:
            setup_monitoring_middleware(app, config)
    except Exception:
        # Middleware not available or import error; proceed silently
        return None


__all__ = ["Monitor", "HealthChecker", "setup_monitoring"]
