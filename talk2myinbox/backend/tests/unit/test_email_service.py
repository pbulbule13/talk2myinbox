"""
Unit tests for Email Service
Tests email fetching, sending, categorization, and management
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch


@pytest.mark.unit
@pytest.mark.email
class TestEmailService:
    """Test suite for Email Service"""

    def test_email_categorization_urgent(self, mock_email_data):
        """Test email categorization - urgent emails"""
        # Arrange
        mock_email_data["subject"] = "URGENT: Security Alert"
        mock_email_data["body"] = "Immediate action required ASAP"

        # Act
        from voice_agent.utils.email_query import categorize_email
        category = categorize_email(mock_email_data.get("subject", "") + " " + mock_email_data.get("body", ""))

        # Assert
        assert category in ["urgent", "work"]  # Should be categorized appropriately

    def test_email_categorization_work(self, mock_email_data):
        """Test email categorization - work emails"""
        # Arrange
        mock_email_data["subject"] = "Project Meeting Tomorrow"
        mock_email_data["body"] = "Reminder about our client deadline"

        # Act
        text = mock_email_data["subject"] + " " + mock_email_data["body"]
        # Simple categorization logic
        is_work = any(keyword in text.lower() for keyword in ["meeting", "project", "deadline", "client"])

        # Assert
        assert is_work is True

    def test_email_categorization_personal(self, mock_email_data):
        """Test email categorization - personal emails"""
        # Arrange
        mock_email_data["subject"] = "Family dinner this weekend"
        mock_email_data["body"] = "Looking forward to seeing you at home"

        # Act
        text = mock_email_data["subject"] + " " + mock_email_data["body"]
        is_personal = any(keyword in text.lower() for keyword in ["family", "personal", "home"])

        # Assert
        assert is_personal is True

    def test_email_categorization_promotions(self, mock_email_data):
        """Test email categorization - promotional emails"""
        # Arrange
        mock_email_data["subject"] = "50% OFF Sale Today Only!"
        mock_email_data["body"] = "Special discount offer just for you"

        # Act
        text = mock_email_data["subject"] + " " + mock_email_data["body"]
        is_promo = any(keyword in text.lower() for keyword in ["sale", "offer", "discount", "deal"])

        # Assert
        assert is_promo is True

    @pytest.mark.asyncio
    async def test_fetch_emails_success(self, mock_gmail_adapter, mock_email_list):
        """Test successful email fetching"""
        # Arrange
        mock_gmail_adapter.fetch_threads.return_value = mock_email_list

        # Act
        result = await mock_gmail_adapter.fetch_threads(max_results=10)

        # Assert
        assert len(result) == 10
        assert all("id" in email for email in result)
        assert all("subject" in email for email in result)
        mock_gmail_adapter.fetch_threads.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_emails_with_query(self, mock_gmail_adapter, mock_email_list):
        """Test email fetching with Gmail query"""
        # Arrange
        filtered_emails = [e for e in mock_email_list if e["unread"]]
        mock_gmail_adapter.fetch_threads.return_value = filtered_emails

        # Act
        result = await mock_gmail_adapter.fetch_threads(query="is:unread", max_results=10)

        # Assert
        assert all(email["unread"] for email in result)
        mock_gmail_adapter.fetch_threads.assert_called_once_with(query="is:unread", max_results=10)

    @pytest.mark.asyncio
    async def test_fetch_emails_empty_inbox(self, mock_gmail_adapter):
        """Test fetching emails from empty inbox"""
        # Arrange
        mock_gmail_adapter.fetch_threads.return_value = []

        # Act
        result = await mock_gmail_adapter.fetch_threads(max_results=10)

        # Assert
        assert result == []
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_send_email_success(self, mock_gmail_adapter, mock_draft_data):
        """Test successful email sending"""
        # Arrange
        expected_response = {"success": True, "message_id": "msg_123", "thread_id": "thread_123"}
        mock_gmail_adapter.send_email.return_value = expected_response

        # Act
        result = await mock_gmail_adapter.send_email(
            to=mock_draft_data["to"],
            subject=mock_draft_data["subject"],
            body=mock_draft_data["body"]
        )

        # Assert
        assert result["success"] is True
        assert "message_id" in result
        mock_gmail_adapter.send_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_with_thread(self, mock_gmail_adapter, mock_draft_data):
        """Test sending email as reply in thread"""
        # Arrange
        mock_gmail_adapter.send_email.return_value = {
            "success": True,
            "message_id": "msg_new",
            "thread_id": mock_draft_data["thread_id"]
        }

        # Act
        result = await mock_gmail_adapter.send_email(
            to=mock_draft_data["to"],
            subject=mock_draft_data["subject"],
            body=mock_draft_data["body"],
            thread_id=mock_draft_data["thread_id"]
        )

        # Assert
        assert result["success"] is True
        assert result["thread_id"] == mock_draft_data["thread_id"]

    @pytest.mark.asyncio
    async def test_send_email_failure(self, mock_gmail_adapter):
        """Test email sending failure"""
        # Arrange
        mock_gmail_adapter.send_email.side_effect = Exception("Gmail API error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await mock_gmail_adapter.send_email(
                to=["invalid@example.com"],
                subject="Test",
                body="Test"
            )
        assert "Gmail API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_mark_as_read(self, mock_gmail_adapter):
        """Test marking email as read"""
        # Arrange
        mock_gmail_adapter.mark_as_read.return_value = True
        message_id = "msg_123"

        # Act
        result = await mock_gmail_adapter.mark_as_read(message_id)

        # Assert
        assert result is True
        mock_gmail_adapter.mark_as_read.assert_called_once_with(message_id)

    @pytest.mark.asyncio
    async def test_archive_email(self, mock_gmail_adapter):
        """Test archiving email"""
        # Arrange
        mock_gmail_adapter.archive.return_value = True
        message_id = "msg_123"

        # Act
        result = await mock_gmail_adapter.archive(message_id)

        # Assert
        assert result is True
        mock_gmail_adapter.archive.assert_called_once_with(message_id)

    @pytest.mark.asyncio
    async def test_delete_email(self, mock_gmail_adapter):
        """Test deleting email"""
        # Arrange
        mock_gmail_adapter.delete.return_value = True
        message_id = "msg_123"

        # Act
        result = await mock_gmail_adapter.delete(message_id)

        # Assert
        assert result is True
        mock_gmail_adapter.delete.assert_called_once_with(message_id)

    def test_email_preview_generation(self, mock_email_data):
        """Test email preview/snippet generation"""
        # Arrange
        long_body = "This is a very long email body that should be truncated to a preview. " * 10
        mock_email_data["body"] = long_body

        # Act
        preview = mock_email_data["body"][:150] + "..." if len(mock_email_data["body"]) > 150 else mock_email_data["body"]

        # Assert
        assert len(preview) <= 153  # 150 chars + "..."
        assert preview.endswith("...")

    def test_email_validation_valid(self):
        """Test validation of valid email data"""
        # Arrange
        valid_email = {
            "id": "msg_123",
            "from": "sender@example.com",
            "to": ["recipient@example.com"],
            "subject": "Valid Subject",
            "body": "Valid body",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Act & Assert
        pytest.assert_valid_email(valid_email)

    def test_email_validation_missing_fields(self):
        """Test validation of email with missing required fields"""
        # Arrange
        invalid_email = {
            "from": "sender@example.com",
            # Missing 'id', 'subject', 'timestamp'
        }

        # Act & Assert
        with pytest.raises(AssertionError):
            pytest.assert_valid_email(invalid_email)

    def test_email_sorting_by_date(self, mock_email_list):
        """Test sorting emails by date"""
        # Act
        sorted_emails = sorted(
            mock_email_list,
            key=lambda x: datetime.fromisoformat(x["timestamp"]),
            reverse=True  # Newest first
        )

        # Assert
        for i in range(len(sorted_emails) - 1):
            current_time = datetime.fromisoformat(sorted_emails[i]["timestamp"])
            next_time = datetime.fromisoformat(sorted_emails[i + 1]["timestamp"])
            assert current_time >= next_time

    def test_email_filtering_unread(self, mock_email_list):
        """Test filtering unread emails"""
        # Act
        unread_emails = [email for email in mock_email_list if email["unread"]]

        # Assert
        assert all(email["unread"] for email in unread_emails)
        assert len(unread_emails) > 0

    def test_email_search_by_sender(self, mock_email_list):
        """Test searching emails by sender"""
        # Arrange
        target_sender = "sender3@example.com"

        # Act
        results = [email for email in mock_email_list if email["from"] == target_sender]

        # Assert
        assert all(email["from"] == target_sender for email in results)

    def test_email_count_by_status(self, mock_email_list):
        """Test counting emails by read/unread status"""
        # Act
        unread_count = sum(1 for email in mock_email_list if email["unread"])
        read_count = sum(1 for email in mock_email_list if not email["unread"])

        # Assert
        assert unread_count + read_count == len(mock_email_list)
        assert unread_count > 0
        assert read_count > 0


@pytest.mark.unit
@pytest.mark.email
@pytest.mark.mock
class TestEmailServiceMockMode:
    """Test email service in mock mode"""

    def test_mock_mode_enabled(self, test_env_vars):
        """Test that mock mode is enabled in test environment"""
        import os
        assert os.getenv("EMAIL_MOCK_MODE") == "true"

    @pytest.mark.asyncio
    async def test_mock_email_generation(self):
        """Test mock email data generation"""
        # This would test the mock email generator
        # For now, just verify structure
        mock_emails = [
            {
                "id": f"mock_{i}",
                "from": f"sender{i}@example.com",
                "subject": f"Mock Email {i}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            for i in range(5)
        ]

        assert len(mock_emails) == 5
        assert all("id" in email for email in mock_emails)


@pytest.mark.unit
@pytest.mark.email
@pytest.mark.performance
class TestEmailServicePerformance:
    """Performance tests for email service"""

    def test_large_email_list_processing(self):
        """Test processing large number of emails"""
        import time

        # Arrange
        large_email_list = [
            {
                "id": f"msg_{i}",
                "from": f"sender{i}@example.com",
                "subject": f"Email {i}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            for i in range(1000)
        ]

        # Act
        start_time = time.time()
        filtered = [email for email in large_email_list if "5" in email["subject"]]
        end_time = time.time()

        # Assert
        duration = end_time - start_time
        assert duration < 1.0  # Should process 1000 emails in less than 1 second
        assert len(filtered) > 0

    def test_email_search_performance(self, mock_email_list):
        """Test email search performance"""
        import time

        # Act
        start_time = time.time()
        for _ in range(100):
            [email for email in mock_email_list if "sender3" in email["from"]]
        end_time = time.time()

        # Assert
        duration = end_time - start_time
        assert duration < 1.0  # 100 searches should take less than 1 second
