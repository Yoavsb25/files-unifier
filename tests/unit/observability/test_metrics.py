"""
Unit tests for metrics module.
"""

import pytest
import time
from pdf_merger.observability.metrics import (
    MetricsCollector,
    Metric,
    get_metrics_collector
)


class TestMetric:
    """Test cases for Metric dataclass."""
    
    def test_metric_creation(self):
        """Test creating a Metric."""
        metric = Metric(
            name="test_metric",
            value=42.5,
            timestamp=1234567890.0,
            tags={"tag1": "value1"}
        )
        
        assert metric.name == "test_metric"
        assert metric.value == 42.5
        assert metric.timestamp == 1234567890.0
        assert metric.tags == {"tag1": "value1"}
    
    def test_metric_default_tags(self):
        """Test Metric with default tags."""
        metric = Metric(
            name="test_metric",
            value=10.0,
            timestamp=1234567890.0
        )
        
        assert metric.tags == {}


class TestMetricsCollector:
    """Test cases for MetricsCollector class."""
    
    def test_metrics_collector_init_enabled(self):
        """Test initializing MetricsCollector with enabled state."""
        collector = MetricsCollector(enabled=True)
        
        assert collector.enabled is True
        assert len(collector.metrics) == 0
        assert len(collector.counters) == 0
        assert len(collector.timers) == 0
    
    def test_metrics_collector_init_disabled(self):
        """Test initializing MetricsCollector with disabled state."""
        collector = MetricsCollector(enabled=False)
        
        assert collector.enabled is False
    
    def test_record_counter_enabled(self):
        """Test recording counter when enabled."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_counter("test_counter", value=5)
        
        assert collector.get_counter("test_counter") == 5
        assert len(collector.metrics) == 1
        assert collector.metrics[0].name == "test_counter"
        assert collector.metrics[0].value == 5.0
    
    def test_record_counter_disabled(self):
        """Test recording counter when disabled."""
        collector = MetricsCollector(enabled=False)
        
        collector.record_counter("test_counter", value=5)
        
        assert collector.get_counter("test_counter") == 0
        assert len(collector.metrics) == 0
    
    def test_record_counter_default_value(self):
        """Test recording counter with default value."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_counter("test_counter")
        
        assert collector.get_counter("test_counter") == 1
    
    def test_record_counter_with_tags(self):
        """Test recording counter with tags."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_counter("test_counter", value=3, tags={"type": "merge"})
        
        assert collector.get_counter("test_counter") == 3
        assert collector.metrics[0].tags == {"type": "merge"}
    
    def test_record_counter_multiple(self):
        """Test recording counter multiple times."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_counter("test_counter", value=2)
        collector.record_counter("test_counter", value=3)
        collector.record_counter("test_counter", value=1)
        
        assert collector.get_counter("test_counter") == 6
        assert len(collector.metrics) == 3
    
    def test_record_timer_enabled(self):
        """Test recording timer when enabled."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_timer("test_timer", duration=1.5)
        
        assert len(collector.timers["test_timer"]) == 1
        assert collector.timers["test_timer"][0] == 1.5
        assert len(collector.metrics) == 1
        assert collector.metrics[0].name == "test_timer"
        assert collector.metrics[0].value == 1.5
    
    def test_record_timer_disabled(self):
        """Test recording timer when disabled."""
        collector = MetricsCollector(enabled=False)
        
        collector.record_timer("test_timer", duration=1.5)
        
        assert len(collector.timers["test_timer"]) == 0
        assert len(collector.metrics) == 0
    
    def test_record_timer_with_tags(self):
        """Test recording timer with tags."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_timer("test_timer", duration=2.0, tags={"operation": "merge"})
        
        assert collector.metrics[0].tags == {"operation": "merge"}
    
    def test_record_timer_multiple(self):
        """Test recording timer multiple times."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_timer("test_timer", duration=1.0)
        collector.record_timer("test_timer", duration=2.0)
        collector.record_timer("test_timer", duration=1.5)
        
        assert len(collector.timers["test_timer"]) == 3
        assert collector.timers["test_timer"] == [1.0, 2.0, 1.5]
    
    def test_record_gauge_enabled(self):
        """Test recording gauge when enabled."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_gauge("test_gauge", value=42.5)
        
        assert len(collector.metrics) == 1
        assert collector.metrics[0].name == "test_gauge"
        assert collector.metrics[0].value == 42.5
    
    def test_record_gauge_disabled(self):
        """Test recording gauge when disabled."""
        collector = MetricsCollector(enabled=False)
        
        collector.record_gauge("test_gauge", value=42.5)
        
        assert len(collector.metrics) == 0
    
    def test_record_gauge_with_tags(self):
        """Test recording gauge with tags."""
        collector = MetricsCollector(enabled=True)
        
        collector.record_gauge("test_gauge", value=10.0, tags={"unit": "mb"})
        
        assert collector.metrics[0].tags == {"unit": "mb"}
    
    def test_get_counter_existing(self):
        """Test getting existing counter."""
        collector = MetricsCollector(enabled=True)
        collector.record_counter("test_counter", value=5)
        
        assert collector.get_counter("test_counter") == 5
    
    def test_get_counter_nonexistent(self):
        """Test getting non-existent counter."""
        collector = MetricsCollector(enabled=True)
        
        assert collector.get_counter("nonexistent") == 0
    
    def test_get_timer_stats_existing(self):
        """Test getting timer stats for existing timer."""
        collector = MetricsCollector(enabled=True)
        collector.record_timer("test_timer", duration=1.0)
        collector.record_timer("test_timer", duration=2.0)
        collector.record_timer("test_timer", duration=3.0)
        
        stats = collector.get_timer_stats("test_timer")
        
        assert stats['min'] == 1.0
        assert stats['max'] == 3.0
        assert stats['avg'] == 2.0
        assert stats['count'] == 3
    
    def test_get_timer_stats_nonexistent(self):
        """Test getting timer stats for non-existent timer."""
        collector = MetricsCollector(enabled=True)
        
        stats = collector.get_timer_stats("nonexistent")
        
        assert stats['min'] == 0
        assert stats['max'] == 0
        assert stats['avg'] == 0
        assert stats['count'] == 0
    
    def test_get_timer_stats_single_value(self):
        """Test getting timer stats with single value."""
        collector = MetricsCollector(enabled=True)
        collector.record_timer("test_timer", duration=5.0)
        
        stats = collector.get_timer_stats("test_timer")
        
        assert stats['min'] == 5.0
        assert stats['max'] == 5.0
        assert stats['avg'] == 5.0
        assert stats['count'] == 1
    
    def test_get_summary(self):
        """Test getting metrics summary."""
        collector = MetricsCollector(enabled=True)
        collector.record_counter("counter1", value=5)
        collector.record_counter("counter2", value=3)
        collector.record_timer("timer1", duration=1.0)
        collector.record_timer("timer1", duration=2.0)
        collector.record_gauge("gauge1", value=10.0)
        
        summary = collector.get_summary()
        
        assert 'counters' in summary
        assert 'timers' in summary
        assert 'total_metrics' in summary
        assert summary['counters']['counter1'] == 5
        assert summary['counters']['counter2'] == 3
        assert 'timer1' in summary['timers']
        assert summary['total_metrics'] == 5

    def test_export_json(self):
        """Test exporting metrics as JSON string for debugging or persistence."""
        import json
        collector = MetricsCollector(enabled=True)
        collector.record_counter("test_counter", value=2)
        collector.record_timer("test_timer", duration=1.5)
        out = collector.export_json()
        assert isinstance(out, str)
        parsed = json.loads(out)
        assert parsed["counters"]["test_counter"] == 2
        assert "test_timer" in parsed["timers"]
        assert parsed["total_metrics"] == 2
    
    def test_clear(self):
        """Test clearing all metrics."""
        collector = MetricsCollector(enabled=True)
        collector.record_counter("counter1", value=5)
        collector.record_timer("timer1", duration=1.0)
        collector.record_gauge("gauge1", value=10.0)
        
        collector.clear()
        
        assert len(collector.metrics) == 0
        assert len(collector.counters) == 0
        assert len(collector.timers) == 0


class TestGetMetricsCollector:
    """Test cases for get_metrics_collector function."""
    
    def test_get_metrics_collector_creates_instance(self):
        """Test getting metrics collector creates new instance."""
        # Reset global state
        import pdf_merger.observability.metrics as metrics_module
        metrics_module._metrics_collector = None
        
        collector1 = get_metrics_collector(enabled=True)
        
        assert collector1 is not None
        assert isinstance(collector1, MetricsCollector)
    
    def test_get_metrics_collector_returns_same_instance(self):
        """Test getting metrics collector returns same instance."""
        # Reset global state
        import pdf_merger.observability.metrics as metrics_module
        metrics_module._metrics_collector = None
        
        collector1 = get_metrics_collector(enabled=True)
        collector2 = get_metrics_collector(enabled=False)
        
        # Should return same instance (singleton)
        assert collector1 is collector2
    
    def test_get_metrics_collector_enabled(self):
        """Test getting metrics collector with enabled flag."""
        # Reset global state
        import pdf_merger.observability.metrics as metrics_module
        metrics_module._metrics_collector = None
        
        collector = get_metrics_collector(enabled=True)
        
        assert collector.enabled is True
