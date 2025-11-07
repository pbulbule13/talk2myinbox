"""
Reminder System with Background Scheduling.
Handles scheduled reminders, notifications, and recurring tasks.
"""

from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path
import uuid
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Reminder(BaseModel):
    """Reminder data model."""
    reminder_id: str = Field(default_factory=lambda: f"rem_{uuid.uuid4().hex[:8]}")
    recipient: str = "self"
    message: str
    reminder_time: datetime
    status: str = "pending"  # pending, sent, cancelled
    created_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    notification_method: str = "log"  # log, email, browser
    recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReminderSystem:
    """
    Background reminder system using APScheduler.
    Supports one-time and recurring reminders with multiple notification methods.
    """

    def __init__(self, storage_file: Optional[str] = None):
        """
        Initialize the reminder system.

        Args:
            storage_file: Path to JSON file for persisting reminders
        """
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # Storage
        self.storage_file = storage_file or os.path.join(
            os.getenv("STORAGE_DIR", "./data"),
            "reminders.json"
        )
        Path(self.storage_file).parent.mkdir(parents=True, exist_ok=True)

        # Load existing reminders
        self.reminders: Dict[str, Reminder] = {}
        self._load_reminders()

        # Notification handlers
        self.notification_handlers = {
            "log": self._notify_log,
            "email": self._notify_email,
            "browser": self._notify_browser
        }

        logger.info("Reminder system initialized")

    def add_reminder(
        self,
        message: str,
        reminder_time: datetime,
        recipient: str = "self",
        notification_method: str = "log",
        recurring: bool = False,
        recurrence_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Reminder:
        """
        Add a new reminder.

        Args:
            message: Reminder message
            reminder_time: When to send the reminder
            recipient: Who to remind
            notification_method: How to send (log, email, browser)
            recurring: Whether this is a recurring reminder
            recurrence_pattern: Recurrence pattern if recurring
            metadata: Additional metadata

        Returns:
            Created Reminder object
        """
        # Create reminder
        reminder = Reminder(
            recipient=recipient,
            message=message,
            reminder_time=reminder_time,
            notification_method=notification_method,
            recurring=recurring,
            recurrence_pattern=recurrence_pattern,
            metadata=metadata or {}
        )

        # Schedule the reminder
        self._schedule_reminder(reminder)

        # Store reminder
        self.reminders[reminder.reminder_id] = reminder
        self._save_reminders()

        logger.info(f"Reminder scheduled: {reminder.reminder_id} for {reminder_time}")
        return reminder

    def _schedule_reminder(self, reminder: Reminder):
        """Schedule a reminder with APScheduler."""
        try:
            if reminder.recurring and reminder.recurrence_pattern:
                # Recurring reminder
                if reminder.recurrence_pattern == "daily":
                    trigger = CronTrigger(
                        hour=reminder.reminder_time.hour,
                        minute=reminder.reminder_time.minute
                    )
                elif reminder.recurrence_pattern == "weekly":
                    trigger = CronTrigger(
                        day_of_week=reminder.reminder_time.weekday(),
                        hour=reminder.reminder_time.hour,
                        minute=reminder.reminder_time.minute
                    )
                elif reminder.recurrence_pattern == "monthly":
                    trigger = CronTrigger(
                        day=reminder.reminder_time.day,
                        hour=reminder.reminder_time.hour,
                        minute=reminder.reminder_time.minute
                    )
                else:
                    logger.error(f"Unknown recurrence pattern: {reminder.recurrence_pattern}")
                    trigger = DateTrigger(run_date=reminder.reminder_time)
            else:
                # One-time reminder
                trigger = DateTrigger(run_date=reminder.reminder_time)

            # Add job to scheduler
            self.scheduler.add_job(
                func=self._send_reminder,
                trigger=trigger,
                args=[reminder.reminder_id],
                id=reminder.reminder_id,
                replace_existing=True,
                misfire_grace_time=300  # 5 minutes grace period
            )

        except Exception as e:
            logger.error(f"Failed to schedule reminder {reminder.reminder_id}: {e}")

    def _send_reminder(self, reminder_id: str):
        """Send a reminder notification."""
        try:
            reminder = self.reminders.get(reminder_id)
            if not reminder:
                logger.error(f"Reminder not found: {reminder_id}")
                return

            # Send notification
            handler = self.notification_handlers.get(
                reminder.notification_method,
                self._notify_log
            )
            success = handler(reminder)

            if success:
                # Update reminder status
                reminder.status = "sent"
                reminder.sent_at = datetime.now()

                # If not recurring, remove from scheduler
                if not reminder.recurring:
                    try:
                        self.scheduler.remove_job(reminder_id)
                    except:
                        pass

                self._save_reminders()
                logger.info(f"Reminder sent: {reminder_id}")

        except Exception as e:
            logger.error(f"Failed to send reminder {reminder_id}: {e}")

    def _notify_log(self, reminder: Reminder) -> bool:
        """Send reminder to log (console)."""
        print("\n" + "="*60)
        print(f"🔔 REMINDER: {reminder.message}")
        print(f"   For: {reminder.recipient}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        return True

    def _notify_email(self, reminder: Reminder) -> bool:
        """Send reminder via email."""
        try:
            # Import email functionality
            from tools.external_tools import SendEmailTool

            # Get email configuration
            smtp_username = os.getenv("SMTP_USERNAME")
            if not smtp_username:
                logger.error("Email notification requires SMTP configuration")
                return False

            # Determine recipient email
            if reminder.recipient == "self":
                recipient_email = smtp_username
            else:
                # Try to extract email from metadata
                recipient_email = reminder.metadata.get("email", smtp_username)

            # Send email
            email_tool = SendEmailTool()
            result = email_tool._run(
                recipient_email=recipient_email,
                subject=f"Reminder: {reminder.message[:50]}",
                body=f"""
Hi,

This is your reminder:

{reminder.message}

Scheduled for: {reminder.reminder_time.strftime('%Y-%m-%d %H:%M')}
Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Cognitive Journal Agent
"""
            )

            return "successfully" in result.lower()

        except Exception as e:
            logger.error(f"Failed to send email reminder: {e}")
            return False

    def _notify_browser(self, reminder: Reminder) -> bool:
        """
        Send browser notification (placeholder for web integration).
        In a real implementation, this would use WebSockets or Server-Sent Events.
        """
        # Store notification in a file that the frontend can poll
        notification_file = os.path.join(
            os.path.dirname(self.storage_file),
            "browser_notifications.json"
        )

        try:
            # Load existing notifications
            if os.path.exists(notification_file):
                with open(notification_file, 'r') as f:
                    notifications = json.load(f)
            else:
                notifications = []

            # Add new notification
            notifications.append({
                "id": reminder.reminder_id,
                "message": reminder.message,
                "time": datetime.now().isoformat(),
                "recipient": reminder.recipient,
                "read": False
            })

            # Save
            with open(notification_file, 'w') as f:
                json.dump(notifications, f, indent=2)

            logger.info(f"Browser notification queued: {reminder.reminder_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create browser notification: {e}")
            return False

    def get_reminders(
        self,
        status: Optional[str] = None,
        recipient: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Reminder]:
        """
        Get reminders with optional filters.

        Args:
            status: Filter by status (pending, sent, cancelled)
            recipient: Filter by recipient
            start_date: Filter by reminder time >= start_date
            end_date: Filter by reminder time <= end_date

        Returns:
            List of matching reminders
        """
        results = list(self.reminders.values())

        if status:
            results = [r for r in results if r.status == status]

        if recipient:
            results = [r for r in results if r.recipient == recipient]

        if start_date:
            results = [r for r in results if r.reminder_time >= start_date]

        if end_date:
            results = [r for r in results if r.reminder_time <= end_date]

        return sorted(results, key=lambda r: r.reminder_time)

    def cancel_reminder(self, reminder_id: str) -> bool:
        """
        Cancel a pending reminder.

        Args:
            reminder_id: ID of the reminder to cancel

        Returns:
            True if cancelled successfully
        """
        try:
            reminder = self.reminders.get(reminder_id)
            if not reminder:
                return False

            # Remove from scheduler
            try:
                self.scheduler.remove_job(reminder_id)
            except:
                pass

            # Update status
            reminder.status = "cancelled"
            self._save_reminders()

            logger.info(f"Reminder cancelled: {reminder_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel reminder {reminder_id}: {e}")
            return False

    def _load_reminders(self):
        """Load reminders from storage."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)

                for reminder_data in data:
                    reminder = Reminder(**reminder_data)
                    self.reminders[reminder.reminder_id] = reminder

                    # Re-schedule pending reminders
                    if reminder.status == "pending" and reminder.reminder_time > datetime.now():
                        self._schedule_reminder(reminder)

                logger.info(f"Loaded {len(self.reminders)} reminders from storage")

        except Exception as e:
            logger.error(f"Failed to load reminders: {e}")

    def _save_reminders(self):
        """Save reminders to storage."""
        try:
            data = [reminder.dict() for reminder in self.reminders.values()]

            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save reminders: {e}")

    def shutdown(self):
        """Shutdown the scheduler gracefully."""
        self.scheduler.shutdown()
        logger.info("Reminder system shut down")


# Global reminder system instance
_reminder_system: Optional[ReminderSystem] = None


def get_reminder_system() -> ReminderSystem:
    """Get or create the global reminder system instance."""
    global _reminder_system
    if _reminder_system is None:
        _reminder_system = ReminderSystem()
    return _reminder_system
