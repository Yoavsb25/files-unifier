"""
Unit tests for telemetry module.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from pdf_merger.observability.telemetry import (
    TelemetryService,
    TelemetryEvent,
    get_telemetry_service
)


class TestTelemetryEvent:
    """Test cases for TelemetryEvent dataclass."""
    
    def test_telemetry_event_creation(self):
        """Test creating a TelemetryEvent."""
        event = TelemetryEvent(
            event_type="test_event",
            timestamp=1234567890.0,
            data={"key": "value"}
        )
        
        assert event.event_type == "test_event"
        assert event.timestamp == 1234567890.0
        assert event.data == {"key": "value"}
        assert event.session_id is None
    
    def test_telemetry_event_with_session_id(self):
        """Test creating TelemetryEvent with session_id."""
        event = TelemetryEvent(
            event_type="test_event",
            timestamp=1234567890.0,
            data={},
            session_id="session-123"
        )
        
        assert event.session_id == "session-123"


class TestTelemetryService:
    """Test cases for TelemetryService class."""
    
    def test_telemetry_service_init_disabled(self):
        """Test initializing TelemetryService with disabled state."""
        service = TelemetryService(enabled=False)
        
        assert service.enabled is False
        assert service.endpoint is None
        assert len(service.events) == 0
        assert service.session_id is None
    
    def test_telemetry_service_init_enabled(self):
        """Test initializing TelemetryService with enabled state."""
        service = TelemetryService(enabled=True, endpoint="https://example.com/telemetry")
        
        assert service.enabled is True
        assert service.endpoint == "https://example.com/telemetry"
        assert len(service.events) == 0
    
    def test_record_event_disabled(self):
        """Test recording event when disabled."""
        service = TelemetryService(enabled=False)
        
        service.record_event("test_event", {"key": "value"})
        
        assert len(service.events) == 0
    
    def test_record_event_enabled(self):
        """Test recording event when enabled."""
        service = TelemetryService(enabled=True)
        
        service.record_event("test_event", {"key": "value"})
        
        assert len(service.events) == 1
        event = service.events[0]
        assert event.event_type == "test_event"
        assert event.data == {"key": "value"}
        assert event.session_id is None
        assert isinstance(event.timestamp, float)
    
    def test_record_event_with_session_id(self):
        """Test recording event with session_id."""
        service = TelemetryService(enabled=True)
        service.session_id = "session-123"
        
        service.record_event("test_event")
        
        assert len(service.events) == 1
        assert service.events[0].session_id == "session-123"
    
    def test_record_event_no_data(self):
        """Test recording event without data."""
        service = TelemetryService(enabled=True)
        
        service.record_event("test_event")
        
        assert len(service.events) == 1
        assert service.events[0].data == {}
    
    def test_record_event_multiple(self):
        """Test recording multiple events."""
        service = TelemetryService(enabled=True)
        
        service.record_event("event1", {"data1": "value1"})
        service.record_event("event2", {"data2": "value2"})
        service.record_event("event3")
        
        assert len(service.events) == 3
        assert service.events[0].event_type == "event1"
        assert service.events[1].event_type == "event2"
        assert service.events[2].event_type == "event3"
    
    def test_get_system_info(self):
        """Test getting system information."""
        service = TelemetryService()
        
        info = service.get_system_info()
        
        assert 'platform' in info
        assert 'platform_version' in info
        assert 'python_version' in info
        assert 'app_version' in info
        # Should not contain personal data
        assert 'username' not in info
        assert 'machine' not in info
    
    def test_flush_disabled(self):
        """Test flushing when disabled."""
        service = TelemetryService(enabled=False)
        service.events.append(TelemetryEvent("test", time.time(), {}))
        
        service.flush()
        
        # Events should remain (not flushed when disabled)
        assert len(service.events) == 1
    
    def test_flush_no_events(self):
        """Test flushing when no events."""
        service = TelemetryService(enabled=True)
        
        service.flush()
        
        # Should not raise error
        assert len(service.events) == 0
    
    def test_flush_with_endpoint(self):
        """Test flushing with endpoint configured."""
        service = TelemetryService(enabled=True, endpoint="https://example.com/telemetry")
        service.events.append(TelemetryEvent("test", time.time(), {}))
        
        with patch('pdf_merger.observability.telemetry.logger') as mock_logger:
            service.flush()
            
            # Should log that it would send events
            mock_logger.debug.assert_called()
            assert len(service.events) == 0  # Events should be cleared
    
    def test_flush_without_endpoint(self):
        """Test flushing without endpoint configured."""
        service = TelemetryService(enabled=True, endpoint=None)
        service.events.append(TelemetryEvent("test", time.time(), {}))
        
        with patch('pdf_merger.observability.telemetry.logger') as mock_logger:
            service.flush()
            
            # Should log that telemetry was collected but not sent
            mock_logger.debug.assert_called()
            assert len(service.events) == 0  # Events should be cleared
    
    def test_flush_clears_events(self):
        """Test that flush clears events."""
        service = TelemetryService(enabled=True)
        service.events.append(TelemetryEvent("event1", time.time(), {}))
        service.events.append(TelemetryEvent("event2", time.time(), {}))
        
        service.flush()
        
        assert len(service.events) == 0


class TestGetTelemetryService:
    """Test cases for get_telemetry_service function."""
    
    def test_get_telemetry_service_creates_instance(self):
        """Test getting telemetry service creates new instance."""
        # Reset global state
        import pdf_merger.observability.telemetry as tel_module
        tel_module._telemetry_service = None
        
        service1 = get_telemetry_service(enabled=False)
        
        assert service1 is not None
        assert isinstance(service1, TelemetryService)
    
    def test_get_telemetry_service_returns_same_instance(self):
        """Test getting telemetry service returns same instance."""
        # Reset global state
        import pdf_merger.observability.telemetry as tel_module
        tel_module._telemetry_service = None
        
        service1 = get_telemetry_service(enabled=False)
        service2 = get_telemetry_service(enabled=True)
        
        # Should return same instance (singleton)
        assert service1 is service2
    
    def test_get_telemetry_service_enabled(self):
        """Test getting telemetry service with enabled flag."""
        # Reset global state
        import pdf_merger.observability.telemetry as tel_module
        tel_module._telemetry_service = None
        
        service = get_telemetry_service(enabled=True)
        
        assert service.enabled is True
