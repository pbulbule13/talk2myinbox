"""
LangChain Tool Definitions for Cognitive Journal Agent.
These tools enable agentic execution of external actions.
All tools are configurable and extensible.
"""

from langchain.tools import BaseTool
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel, Field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import os


# ===========================
# Email Tool
# ===========================

class SendEmailInput(BaseModel):
    """Input schema for SendEmailTool."""
    recipient_email: str = Field(description="Email address of the recipient")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    cc: Optional[str] = Field(default=None, description="CC recipients (comma-separated)")
    bcc: Optional[str] = Field(default=None, description="BCC recipients (comma-separated)")


class SendEmailTool(BaseTool):
    """
    Tool to draft and send emails.
    Configurable via environment variables:
    - SMTP_HOST: SMTP server hostname
    - SMTP_PORT: SMTP server port
    - SMTP_USERNAME: Email account username
    - SMTP_PASSWORD: Email account password
    """
    name: str = "send_email"
    description: str = """
    Use this tool to send emails.
    Input should include recipient_email, subject, and body.
    Optionally include cc and bcc for additional recipients.
    Example: "Send an email to john@example.com about project updates"
    """
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> str:
        """Execute the email sending."""
        try:
            # Get SMTP configuration from environment
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")

            if not smtp_username or not smtp_password:
                return "Error: Email credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD."

            # Create message
            msg = MIMEMultipart()
            msg["From"] = smtp_username
            msg["To"] = recipient_email
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = cc
            if bcc:
                msg["Bcc"] = bcc

            msg.attach(MIMEText(body, "plain"))

            # Send email
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)

            recipients = [recipient_email]
            if cc:
                recipients.extend([email.strip() for email in cc.split(",")])
            if bcc:
                recipients.extend([email.strip() for email in bcc.split(",")])

            server.send_message(msg)
            server.quit()

            return f"Email successfully sent to {recipient_email}"
        except Exception as e:
            return f"Error sending email: {str(e)}"

    async def _arun(self, *args, **kwargs):
        """Async version."""
        return self._run(*args, **kwargs)


# ===========================
# Calendar Management Tool
# ===========================

class CalendarEventInput(BaseModel):
    """Input schema for CalendarManagementTool."""
    event_title: str = Field(description="Title of the calendar event")
    start_time: str = Field(description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS) or natural language")
    duration_minutes: int = Field(description="Duration of the event in minutes")
    description: Optional[str] = Field(default=None, description="Event description")
    attendees: Optional[str] = Field(default=None, description="Comma-separated list of attendee emails")


class CalendarManagementTool(BaseTool):
    """
    Tool to add or block time on the user's calendar.
    Now supports natural language date/time parsing!
    Configurable via environment variables:
    - CALENDAR_BACKEND: 'google', 'outlook', or 'local' (default: 'local')
    - GOOGLE_CALENDAR_CREDENTIALS: Path to Google Calendar credentials JSON
    - OUTLOOK_CLIENT_ID: Microsoft Outlook client ID
    """
    name: str = "manage_calendar"
    description: str = """
    Use this tool to add events to the calendar or block time.
    Input should include event_title, start_time, and duration_minutes.
    Optionally include description and attendees.
    Supports natural language time expressions!
    Examples:
    - "Block out two hours tomorrow morning for deep work"
    - "Add a meeting with Sarah on Friday at 2pm for 1 hour"
    - "Schedule a dentist appointment next Tuesday at 10am"
    - "Block calendar for 2-3pm tomorrow for kids pickup"
    """
    args_schema: Type[BaseModel] = CalendarEventInput

    def _run(
        self,
        event_title: str,
        start_time: str,
        duration_minutes: int,
        description: Optional[str] = None,
        attendees: Optional[str] = None,
    ) -> str:
        """Execute the calendar event creation."""
        try:
            calendar_backend = os.getenv("CALENDAR_BACKEND", "local")

            # Parse start time (handle natural language or ISO format)
            try:
                # Try parsing as ISO format first
                event_start = datetime.fromisoformat(start_time)
            except ValueError:
                # Use natural language parser
                try:
                    import dateparser
                    event_start = dateparser.parse(start_time, settings={
                        'PREFER_DATES_FROM': 'future',
                        'TIMEZONE': 'UTC'
                    })

                    if not event_start:
                        return f"Error: Could not parse start time '{start_time}'. Try formats like 'tomorrow 2pm', 'next Tuesday 10am', or ISO format."
                except ImportError:
                    return f"Error: Natural language parsing not available. Please use ISO format (YYYY-MM-DDTHH:MM:SS)."

            event_end = event_start + timedelta(minutes=duration_minutes)

            event_data = {
                "title": event_title,
                "start": event_start.isoformat(),
                "end": event_end.isoformat(),
                "description": description,
                "attendees": attendees.split(",") if attendees else []
            }

            if calendar_backend == "local":
                # Store locally in a JSON file
                calendar_file = os.getenv("CALENDAR_FILE", "calendar_events.json")
                events = []
                if os.path.exists(calendar_file):
                    with open(calendar_file, "r") as f:
                        events = json.load(f)

                events.append(event_data)

                with open(calendar_file, "w") as f:
                    json.dump(events, f, indent=2)

                return f"Calendar event '{event_title}' added successfully for {event_start.strftime('%Y-%m-%d %H:%M')} ({duration_minutes} minutes)"

            elif calendar_backend == "google":
                # Google Calendar integration (requires google-api-python-client)
                return "Google Calendar integration requires setup. See config.py for details."

            elif calendar_backend == "outlook":
                # Outlook integration (requires msal)
                return "Outlook Calendar integration requires setup. See config.py for details."

            else:
                return f"Unknown calendar backend: {calendar_backend}"

        except Exception as e:
            return f"Error adding calendar event: {str(e)}"

    async def _arun(self, *args, **kwargs):
        """Async version."""
        return self._run(*args, **kwargs)


# ===========================
# File Operations Tool
# ===========================

class FileOperationInput(BaseModel):
    """Input schema for FileOperationsTool."""
    operation: str = Field(description="Operation to perform: 'read', 'write', 'append', 'delete', 'list'")
    file_path: str = Field(description="Path to the file or directory")
    content: Optional[str] = Field(default=None, description="Content to write (for write/append operations)")


class FileOperationsTool(BaseTool):
    """
    Tool for file system operations.
    Allows reading, writing, appending, deleting files.
    """
    name: str = "file_operations"
    description: str = """
    Use this tool to perform file operations.
    Supported operations: read, write, append, delete, list
    Examples:
    - "Read the contents of notes.txt"
    - "Write 'Hello World' to output.txt"
    - "List all files in the documents folder"
    """
    args_schema: Type[BaseModel] = FileOperationInput

    def _run(
        self,
        operation: str,
        file_path: str,
        content: Optional[str] = None,
    ) -> str:
        """Execute the file operation."""
        try:
            base_dir = os.getenv("FILE_OPERATIONS_BASE_DIR", os.getcwd())
            full_path = os.path.join(base_dir, file_path)

            if operation == "read":
                if not os.path.exists(full_path):
                    return f"Error: File '{file_path}' does not exist."
                with open(full_path, "r") as f:
                    return f.read()

            elif operation == "write":
                if content is None:
                    return "Error: Content is required for write operation."
                with open(full_path, "w") as f:
                    f.write(content)
                return f"Successfully wrote to '{file_path}'"

            elif operation == "append":
                if content is None:
                    return "Error: Content is required for append operation."
                with open(full_path, "a") as f:
                    f.write(content)
                return f"Successfully appended to '{file_path}'"

            elif operation == "delete":
                if not os.path.exists(full_path):
                    return f"Error: File '{file_path}' does not exist."
                os.remove(full_path)
                return f"Successfully deleted '{file_path}'"

            elif operation == "list":
                if not os.path.exists(full_path):
                    return f"Error: Directory '{file_path}' does not exist."
                files = os.listdir(full_path)
                return f"Files in '{file_path}':\n" + "\n".join(files)

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            return f"Error performing file operation: {str(e)}"

    async def _arun(self, *args, **kwargs):
        """Async version."""
        return self._run(*args, **kwargs)


# ===========================
# Web Search Tool
# ===========================

class WebSearchInput(BaseModel):
    """Input schema for WebSearchTool."""
    query: str = Field(description="Search query")
    num_results: int = Field(default=5, description="Number of results to return")


class WebSearchTool(BaseTool):
    """
    Tool for web search operations.
    Configurable via environment variables:
    - SEARCH_API_KEY: API key for search service
    - SEARCH_ENGINE_ID: Custom search engine ID
    """
    name: str = "web_search"
    description: str = """
    Use this tool to search the web for information.
    Provide a search query and optionally the number of results.
    Examples:
    - "Search for latest AI news"
    - "Find information about Python async programming"
    """
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(
        self,
        query: str,
        num_results: int = 5,
    ) -> str:
        """Execute the web search."""
        try:
            # Placeholder implementation
            # In production, integrate with Google Custom Search, Bing API, or SerpAPI
            return f"Web search for '{query}' would return {num_results} results. (Integration required)"
        except Exception as e:
            return f"Error performing web search: {str(e)}"

    async def _arun(self, *args, **kwargs):
        """Async version."""
        return self._run(*args, **kwargs)


# ===========================
# Reminder Tool
# ===========================

class ReminderInput(BaseModel):
    """Input schema for ReminderTool."""
    message: str = Field(description="What to remind about")
    reminder_time: str = Field(description="When to remind (natural language or ISO format)")
    recipient: str = Field(default="self", description="Who to remind (default: self)")
    notification_method: str = Field(default="log", description="Notification method: log, email, browser")


class ReminderTool(BaseTool):
    """
    Tool to set reminders and notifications.
    Supports natural language time expressions.
    """
    name: str = "set_reminder"
    description: str = """
    Use this tool to set reminders for tasks or events.
    Supports natural language time expressions.
    Examples:
    - "Remind me at 8pm to call Mr. A for interview"
    - "Set reminder for tomorrow 9am to review project"
    - "Remind me in 30 minutes to take a break"
    """
    args_schema: Type[BaseModel] = ReminderInput

    def _run(
        self,
        message: str,
        reminder_time: str,
        recipient: str = "self",
        notification_method: str = "log",
    ) -> str:
        """Execute the reminder creation."""
        try:
            # Parse reminder time
            try:
                # Try ISO format first
                parsed_time = datetime.fromisoformat(reminder_time)
            except ValueError:
                # Use natural language parser
                try:
                    import dateparser
                    parsed_time = dateparser.parse(reminder_time, settings={
                        'PREFER_DATES_FROM': 'future',
                        'TIMEZONE': 'UTC'
                    })

                    if not parsed_time:
                        return f"Error: Could not parse reminder time '{reminder_time}'. Try 'tomorrow 8pm', 'in 30 minutes', etc."
                except ImportError:
                    return "Error: Natural language parsing not available."

            # Check if time is in the future
            if parsed_time <= datetime.now():
                return f"Error: Reminder time must be in the future. You specified: {parsed_time}"

            # Create reminder using reminder system
            try:
                from services.reminder_system import get_reminder_system

                reminder_system = get_reminder_system()
                reminder = reminder_system.add_reminder(
                    message=message,
                    reminder_time=parsed_time,
                    recipient=recipient,
                    notification_method=notification_method
                )

                return f"Reminder set successfully for {parsed_time.strftime('%Y-%m-%d %H:%M')}. Message: {message}"

            except Exception as e:
                return f"Error creating reminder: {str(e)}"

        except Exception as e:
            return f"Error setting reminder: {str(e)}"

    async def _arun(self, *args, **kwargs):
        """Async version."""
        return self._run(*args, **kwargs)


# ===========================
# Tool Registry
# ===========================

def get_all_tools() -> list:
    """
    Returns all available tools for the agent.
    This makes the system extensible - add new tools here.
    """
    return [
        SendEmailTool(),
        CalendarManagementTool(),
        ReminderTool(),
        FileOperationsTool(),
        WebSearchTool(),
    ]
