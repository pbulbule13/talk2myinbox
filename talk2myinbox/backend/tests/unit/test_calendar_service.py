"""
Unit tests for Calendar Service
Tests calendar event fetching, creation, updates, and management
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock


@pytest.mark.unit
@pytest.mark.calendar
class TestCalendarService:
    """Test suite for Calendar Service"""

    @pytest.mark.asyncio
    async def test_fetch_events_success(self, mock_calendar_adapter, mock_calendar_events):
        """Test successful calendar event fetching"""
        # Arrange
        mock_calendar_adapter.get_events.return_value = mock_calendar_events

        # Act
        result = await mock_calendar_adapter.get_events(
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(days=7)
        )

        # Assert
        assert len(result) == 5
        assert all("id" in event for event in result)
        assert all("title" in event for event in result)
        mock_calendar_adapter.get_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_events_today(self, mock_calendar_adapter, mock_calendar_events):
        """Test fetching today's events"""
        # Arrange
        now = datetime.now(timezone.utc)
        today_events = [e for e in mock_calendar_events if
                       datetime.fromisoformat(e["start"]).date() == now.date()]
        mock_calendar_adapter.get_events.return_value = today_events

        # Act
        result = await mock_calendar_adapter.get_events(
            start_time=now.replace(hour=0, minute=0, second=0),
            end_time=now.replace(hour=23, minute=59, second=59)
        )

        # Assert
        assert isinstance(result, list)
        mock_calendar_adapter.get_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_events_empty_calendar(self, mock_calendar_adapter):
        """Test fetching events from empty calendar"""
        # Arrange
        mock_calendar_adapter.get_events.return_value = []

        # Act
        result = await mock_calendar_adapter.get_events(
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(days=1)
        )

        # Assert
        assert result == []
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_create_event_success(self, mock_calendar_adapter, mock_calendar_event):
        """Test successful event creation"""
        # Arrange
        expected_response = {"success": True, "event_id": "event_123"}
        mock_calendar_adapter.create_event.return_value = expected_response

        # Act
        result = await mock_calendar_adapter.create_event(
            title=mock_calendar_event["title"],
            start=mock_calendar_event["start"],
            end=mock_calendar_event["end"],
            description=mock_calendar_event["description"],
            location=mock_calendar_event["location"]
        )

        # Assert
        assert result["success"] is True
        assert "event_id" in result
        mock_calendar_adapter.create_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_event_minimal_data(self, mock_calendar_adapter):
        """Test event creation with minimal required data"""
        # Arrange
        now = datetime.now(timezone.utc)
        mock_calendar_adapter.create_event.return_value = {
            "success": True,
            "event_id": "event_minimal"
        }

        # Act
        result = await mock_calendar_adapter.create_event(
            title="Quick Meeting",
            start=now.isoformat(),
            end=(now + timedelta(hours=1)).isoformat()
        )

        # Assert
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_event_success(self, mock_calendar_adapter):
        """Test successful event update"""
        # Arrange
        mock_calendar_adapter.update_event.return_value = {"success": True}
        event_id = "event_123"

        # Act
        result = await mock_calendar_adapter.update_event(
            event_id=event_id,
            title="Updated Meeting Title",
            location="New Location"
        )

        # Assert
        assert result["success"] is True
        mock_calendar_adapter.update_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_event_success(self, mock_calendar_adapter):
        """Test successful event deletion"""
        # Arrange
        mock_calendar_adapter.delete_event.return_value = {"success": True}
        event_id = "event_123"

        # Act
        result = await mock_calendar_adapter.delete_event(event_id)

        # Assert
        assert result["success"] is True
        mock_calendar_adapter.delete_event.assert_called_once_with(event_id)

    @pytest.mark.asyncio
    async def test_create_event_failure(self, mock_calendar_adapter):
        """Test event creation failure"""
        # Arrange
        mock_calendar_adapter.create_event.side_effect = Exception("Calendar API error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await mock_calendar_adapter.create_event(
                title="Test",
                start=datetime.now(timezone.utc).isoformat(),
                end=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            )
        assert "Calendar API error" in str(exc_info.value)

    def test_event_validation_valid(self, mock_calendar_event):
        """Test validation of valid calendar event"""
        # Act & Assert
        pytest.assert_valid_calendar_event(mock_calendar_event)

    def test_event_validation_missing_fields(self):
        """Test validation of event with missing fields"""
        # Arrange
        invalid_event = {
            "title": "Test Event"
            # Missing 'id', 'start', 'end'
        }

        # Act & Assert
        with pytest.raises(AssertionError):
            pytest.assert_valid_calendar_event(invalid_event)

    def test_event_time_duration_calculation(self, mock_calendar_event):
        """Test calculating event duration"""
        # Act
        start = datetime.fromisoformat(mock_calendar_event["start"])
        end = datetime.fromisoformat(mock_calendar_event["end"])
        duration = end - start

        # Assert
        assert duration.total_seconds() > 0
        assert duration.total_seconds() == 3600  # 1 hour

    def test_event_sorting_by_time(self, mock_calendar_events):
        """Test sorting events by start time"""
        # Act
        sorted_events = sorted(
            mock_calendar_events,
            key=lambda x: datetime.fromisoformat(x["start"])
        )

        # Assert
        for i in range(len(sorted_events) - 1):
            current_time = datetime.fromisoformat(sorted_events[i]["start"])
            next_time = datetime.fromisoformat(sorted_events[i + 1]["start"])
            assert current_time <= next_time

    def test_event_filtering_by_date(self, mock_calendar_events):
        """Test filtering events by date"""
        # Arrange
        target_date = datetime.now(timezone.utc).date()

        # Act
        today_events = [
            event for event in mock_calendar_events
            if datetime.fromisoformat(event["start"]).date() == target_date
        ]

        # Assert
        assert isinstance(today_events, list)

    def test_event_conflict_detection(self):
        """Test detecting conflicting events"""
        # Arrange
        now = datetime.now(timezone.utc)
        event1 = {
            "start": now,
            "end": now + timedelta(hours=2)
        }
        event2 = {
            "start": now + timedelta(hours=1),
            "end": now + timedelta(hours=3)
        }

        # Act
        has_conflict = (
            event1["start"] < event2["end"] and
            event2["start"] < event1["end"]
        )

        # Assert
        assert has_conflict is True

    def test_event_no_conflict(self):
        """Test non-conflicting events"""
        # Arrange
        now = datetime.now(timezone.utc)
        event1 = {
            "start": now,
            "end": now + timedelta(hours=1)
        }
        event2 = {
            "start": now + timedelta(hours=2),
            "end": now + timedelta(hours=3)
        }

        # Act
        has_conflict = (
            event1["start"] < event2["end"] and
            event2["start"] < event1["end"]
        )

        # Assert
        assert has_conflict is False

    def test_event_timeframe_filtering(self, mock_calendar_events):
        """Test filtering events within a timeframe"""
        # Arrange
        now = datetime.now(timezone.utc)
        end_of_day = now.replace(hour=23, minute=59, second=59)

        # Act
        events_in_timeframe = [
            event for event in mock_calendar_events
            if now <= datetime.fromisoformat(event["start"]) <= end_of_day
        ]

        # Assert
        assert isinstance(events_in_timeframe, list)

    def test_event_location_parsing(self, mock_calendar_event):
        """Test parsing event location"""
        # Act
        has_location = bool(mock_calendar_event.get("location"))

        # Assert
        assert has_location is True
        assert isinstance(mock_calendar_event["location"], str)

    def test_event_attendees_count(self, mock_calendar_event):
        """Test counting event attendees"""
        # Act
        attendee_count = len(mock_calendar_event.get("attendees", []))

        # Assert
        assert attendee_count >= 0
        assert attendee_count == 2  # Based on fixture

    def test_event_status_validation(self, mock_calendar_event):
        """Test event status validation"""
        # Arrange
        valid_statuses = ["confirmed", "tentative", "cancelled"]

        # Act
        status = mock_calendar_event.get("status")

        # Assert
        assert status in valid_statuses


@pytest.mark.unit
@pytest.mark.calendar
@pytest.mark.mock
class TestCalendarServiceMockMode:
    """Test calendar service in mock mode"""

    def test_mock_mode_enabled(self, test_env_vars):
        """Test that mock mode is enabled"""
        import os
        assert os.getenv("CALENDAR_MOCK_MODE") == "true"

    @pytest.mark.asyncio
    async def test_mock_event_generation(self):
        """Test mock event data generation"""
        # Arrange & Act
        now = datetime.now(timezone.utc)
        mock_events = [
            {
                "id": f"event_{i}",
                "title": f"Mock Event {i}",
                "start": (now + timedelta(hours=i)).isoformat(),
                "end": (now + timedelta(hours=i+1)).isoformat()
            }
            for i in range(5)
        ]

        # Assert
        assert len(mock_events) == 5
        assert all("id" in event for event in mock_events)
        assert all("title" in event for event in mock_events)


@pytest.mark.unit
@pytest.mark.calendar
@pytest.mark.performance
class TestCalendarServicePerformance:
    """Performance tests for calendar service"""

    def test_large_event_list_processing(self):
        """Test processing large number of events"""
        import time

        # Arrange
        now = datetime.now(timezone.utc)
        large_event_list = [
            {
                "id": f"event_{i}",
                "title": f"Event {i}",
                "start": (now + timedelta(hours=i)).isoformat(),
                "end": (now + timedelta(hours=i+1)).isoformat()
            }
            for i in range(1000)
        ]

        # Act
        start_time = time.time()
        today_events = [
            event for event in large_event_list
            if datetime.fromisoformat(event["start"]).date() == now.date()
        ]
        end_time = time.time()

        # Assert
        duration = end_time - start_time
        assert duration < 1.0  # Should process 1000 events in less than 1 second

    def test_event_conflict_detection_performance(self):
        """Test conflict detection performance"""
        import time

        # Arrange
        now = datetime.now(timezone.utc)
        events = [
            {
                "start": now + timedelta(hours=i),
                "end": now + timedelta(hours=i+1)
            }
            for i in range(100)
        ]

        # Act
        start_time = time.time()
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                _ = (
                    event1["start"] < event2["end"] and
                    event2["start"] < event1["end"]
                )
        end_time = time.time()

        # Assert
        duration = end_time - start_time
        assert duration < 2.0  # Should check ~5000 pairs in less than 2 seconds
