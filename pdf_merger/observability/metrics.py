"""
Metrics collection module.
Collects and tracks application metrics.

Export: get_summary() returns a dict snapshot; export_to_file(path) writes JSON
to disk (e.g. on shutdown). Schema: { "timestamp": "<iso>", "counters": {...},
"timers": {...}, "total_metrics": N }. Export is best-effort and never raises.
"""

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Protocol, runtime_checkable

from ..utils.logging_utils import get_logger

logger = get_logger("pdf_merger.observability.metrics")


@runtime_checkable
class MetricsRecorder(Protocol):
    """Minimal protocol for recording metrics. Use this type for dependency injection and test doubles."""

    def record_counter(
        self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None
    ) -> None: ...

    def record_timer(
        self, name: str, duration: float, tags: Optional[Dict[str, str]] = None
    ) -> None: ...

    def record_gauge(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None: ...


@dataclass
class Metric:
    """A single metric measurement."""

    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and stores application metrics.

    Metrics collected:
    - Processing time per row
    - File sizes processed
    - Memory usage (if available)
    - Success/failure rates
    - Match ambiguity counts

    Export: Use get_summary() for a dict snapshot, or export_json() for a JSON
    string (e.g. for logging or writing to a file on shutdown or on demand).
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize metrics collector.

        Args:
            enabled: Whether metrics collection is enabled
        """
        self.enabled = enabled
        self.metrics: List[Metric] = []
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)

    def record_counter(
        self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a counter metric.

        Args:
            name: Metric name
            value: Counter increment (default: 1)
            tags: Optional tags for the metric
        """
        if not self.enabled:
            return

        self.counters[name] += value
        self.metrics.append(
            Metric(name=name, value=float(value), timestamp=time.time(), tags=tags or {})
        )

    def record_timer(
        self, name: str, duration: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a timer metric.

        Args:
            name: Metric name
            duration: Duration in seconds
            tags: Optional tags for the metric
        """
        if not self.enabled:
            return

        self.timers[name].append(duration)
        self.metrics.append(
            Metric(name=name, value=duration, timestamp=time.time(), tags=tags or {})
        )

    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a gauge metric (current value at a point in time).

        Args:
            name: Metric name
            value: Gauge value
            tags: Optional tags for the metric
        """
        if not self.enabled:
            return

        self.metrics.append(Metric(name=name, value=value, timestamp=time.time(), tags=tags or {}))

    def get_counter(self, name: str) -> int:
        """Get counter value."""
        return self.counters.get(name, 0)

    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """
        Get timer statistics.

        Returns:
            Dictionary with min, max, avg, count
        """
        values = self.timers.get(name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}

        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values),
        }

    def get_summary(self) -> Dict:
        """
        Get summary of all metrics (snapshot of counters and timer stats).

        Returns:
            Dictionary with metric summaries (counters, timers, total_metrics).
        """
        return {
            "counters": dict(self.counters),
            "timers": {name: self.get_timer_stats(name) for name in self.timers},
            "total_metrics": len(self.metrics),
        }

    def export_json(self) -> str:
        """
        Export current metrics as a JSON string for debugging or persistence.

        Returns:
            JSON string with counters, timers, and total_metrics. Safe to log or
            write to a file on shutdown or on demand.
        """
        return json.dumps(self.get_summary(), indent=2)

    def export_to_file(self, path: Path) -> bool:
        """
        Write current metrics snapshot to a JSON file. Non-blocking and failure-safe:
        never raises; on any exception logs and returns False.

        Schema: { "timestamp": "<iso>", "counters": {...}, "timers": {...}, "total_metrics": N }.

        Args:
            path: File path to write (overwrites if exists).

        Returns:
            True if write succeeded, False otherwise.
        """
        try:
            data = self.get_summary()
            data["timestamp"] = datetime.now(timezone.utc).isoformat()
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error("Failed to export metrics to %s: %s", Path(path), e)
            return False

    def clear(self) -> None:
        """Clear all collected metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.timers.clear()


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(enabled: bool = True) -> MetricsCollector:
    """
    Get or create the global metrics collector.

    Args:
        enabled: Whether metrics collection is enabled

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(enabled=enabled)
    return _metrics_collector
