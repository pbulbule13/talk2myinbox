# Multi-Calendar Integration Guide

## Overview

The Multi-Calendar Integration feature allows you to combine multiple calendar sources into a single unified view, ensuring you never miss an event. This feature supports various input methods including OAuth-based calendar sync, file imports, and even OCR-based extraction from calendar images.

## Table of Contents

1. [Features](#features)
2. [Supported Calendar Sources](#supported-calendar-sources)
3. [Quick Start](#quick-start)
4. [Setup and Configuration](#setup-and-configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Architecture](#architecture)
8. [Troubleshooting](#troubleshooting)

---

## Features

- **Multiple Calendar Sources**: Connect Google Calendar, Outlook/Microsoft 365, iCal files, OCR images, and manual entries
- **OAuth Integration**: Secure authentication with Google and Microsoft
- **OCR Calendar Import**: Extract events from calendar images using AI-powered OCR
- **iCal/ICS File Support**: Import standard calendar files
- **Unified Event View**: See all events from different sources in one place
- **Conflict Detection**: Automatically detect scheduling conflicts
- **Free Time Finder**: Identify available time slots
- **Calendar Analytics**: Daily insights, busiest hours, and time breakdown
- **Event Deduplication**: Automatically remove duplicate events
- **Web UI**: Beautiful, responsive interface for managing calendars

---

## Supported Calendar Sources

### 1. Google Calendar (OAuth)
- **Authentication**: OAuth 2.0
- **Features**: Read events, sync automatically
- **Requirements**: Google Cloud credentials

### 2. Microsoft Outlook/365 (OAuth)
- **Authentication**: OAuth 2.0 via Microsoft Graph API
- **Features**: Read events, sync automatically
- **Requirements**: Microsoft Azure app credentials

### 3. iCal/ICS Files
- **Format**: Standard iCalendar format (.ics)
- **Features**: Import events, recurring events support
- **Requirements**: None

### 4. OCR Image Import
- **Input**: Calendar screenshots, photos
- **Features**: AI-powered text extraction and event parsing
- **Requirements**: Tesseract OCR, OpenAI or Anthropic API

### 5. Manual Entry
- **Input**: Direct API calls or UI
- **Features**: Custom event creation
- **Requirements**: None

---

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies
pip install fastapi uvicorn pydantic

# Google Calendar
pip install google-auth google-auth-oauthlib google-api-python-client

# Microsoft Calendar
pip install msal requests

# iCal support
pip install icalendar recurring-ical-events

# OCR support
pip install pytesseract pillow

# LLM support (choose one)
pip install langchain-openai
# OR
pip install langchain-anthropic
```

### 2. Start the API Server

```bash
python main.py api
```

The server will start on `http://localhost:8000`

### 3. Open the Web UI

Navigate to:
```
http://localhost:8000/web/calendar.html
```

Or use the API documentation:
```
http://localhost:8000/docs
```

---

## Setup and Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Storage Configuration
STORAGE_BACKEND=json  # Options: json, sqlite, firestore
STORAGE_DIR=./data

# LLM Configuration (for OCR parsing)
LLM_PROVIDER=openai  # Options: openai, anthropic
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google Calendar OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_CALENDAR_CREDENTIALS=./config/google_calendar_credentials.json
GOOGLE_CALENDAR_TOKEN=./data/google_calendar_token.json

# Microsoft Calendar OAuth
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/microsoft/callback

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Google Calendar Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Calendar API

2. **Create OAuth 2.0 Credentials**:
   - Navigate to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: Desktop app
   - Download the credentials JSON file
   - Save it as `config/google_calendar_credentials.json`

3. **Configure Redirect URI**:
   - Add `http://localhost` to authorized redirect URIs

### Microsoft Calendar Setup

1. **Register an Azure App**:
   - Go to [Azure Portal](https://portal.azure.com/)
   - Navigate to "Azure Active Directory" → "App registrations"
   - Create a new registration

2. **Configure API Permissions**:
   - Add permissions: `Calendars.Read`, `Calendars.ReadWrite`
   - Grant admin consent

3. **Create Client Secret**:
   - Navigate to "Certificates & secrets"
   - Create a new client secret
   - Copy the secret value to `.env`

4. **Configure Redirect URI**:
   - Add `http://localhost:8000/auth/microsoft/callback`

---

## Usage Guide

### Using the Web UI

#### 1. Add Calendar Sources

Navigate to the **Calendar Sources** tab:

1. Select the calendar type (Google, Outlook, iCal, OCR, Manual)
2. Enter a display name (e.g., "Work Calendar")
3. Choose a color for UI display
4. Click "Add Calendar Source"

#### 2. Connect OAuth Calendars

Navigate to the **Import Calendar** tab:

**For Google Calendar:**
1. Enter your Gmail address
2. Click "Connect Google Calendar"
3. Complete the OAuth flow in the browser
4. Events will be synced automatically

**For Microsoft Calendar:**
1. Click "Connect Microsoft Calendar"
2. Complete the OAuth flow in Microsoft's login page
3. Return to the app and sync

#### 3. Import Calendar from Image

Navigate to the **Import Calendar** tab:

1. Click the "Upload calendar image" area
2. Select a calendar screenshot or photo
3. Choose the target calendar source
4. Optionally set a reference date
5. Click upload and wait for OCR processing

**Tips for best OCR results:**
- Use clear, high-resolution images
- Ensure good lighting and contrast
- Include date information in the image
- Avoid skewed or rotated images

#### 4. Import iCal Files

Navigate to the **Import Calendar** tab:

1. Click the "Upload iCal file" area
2. Select an .ics or .ical file
3. Choose the target calendar source
4. Click upload

#### 5. View Unified Events

Navigate to the **Unified Events** tab:

1. Set the date range (start and end dates)
2. Click "Load Events"
3. View all events from all sources
4. Conflicts are highlighted in red

**Sync all calendars:**
- Click "Sync All Calendars" to fetch latest events from all active sources

#### 6. View Analytics

Navigate to the **Analytics** tab:

1. Select a date
2. Click "Load Analytics"
3. View:
   - Total events for the day
   - Scheduled hours
   - Free time available
   - Busiest hours
   - Event breakdown by source
   - Number of conflicts

### Using the API

#### Add a Calendar Source

```bash
curl -X POST "http://localhost:8000/calendar/sources" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "google",
    "display_name": "Work Calendar",
    "color": "#4285F4",
    "sync_frequency_minutes": 60,
    "sync_window_days": 90
  }'
```

#### Get All Calendar Sources

```bash
curl "http://localhost:8000/calendar/sources"
```

#### Sync a Calendar Source

```bash
curl -X POST "http://localhost:8000/calendar/sync/{source_id}"
```

#### Get Unified Events

```bash
curl "http://localhost:8000/calendar/events?start_date=2025-01-01&end_date=2025-01-31"
```

#### Import Calendar via OCR

```bash
curl -X POST "http://localhost:8000/calendar/import/ocr" \
  -F "file=@calendar_image.png" \
  -F "source_id=your_source_id" \
  -F "reference_date=2025-01-15"
```

#### Import iCal File

```bash
curl -X POST "http://localhost:8000/calendar/import/ical" \
  -F "file=@calendar.ics" \
  -F "source_id=your_source_id"
```

#### Get Daily Analytics

```bash
curl "http://localhost:8000/calendar/analytics/daily?date=2025-01-15"
```

#### Find Free Time Slots

```bash
curl "http://localhost:8000/calendar/events/free-slots?start_date=2025-01-15T09:00:00&end_date=2025-01-15T17:00:00&min_duration_minutes=30&work_hours_only=true"
```

---

## API Reference

### Endpoints

#### Calendar Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calendar/sources` | Add a new calendar source |
| GET | `/calendar/sources` | Get all calendar sources |
| DELETE | `/calendar/sources/{source_id}` | Delete a calendar source |

#### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calendar/auth/google` | Authenticate with Google Calendar |
| GET | `/calendar/auth/microsoft/url` | Get Microsoft OAuth URL |
| POST | `/calendar/auth/microsoft/callback` | Handle Microsoft OAuth callback |

#### Synchronization

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calendar/sync/{source_id}` | Sync a specific calendar source |
| POST | `/calendar/sync/all` | Sync all active calendar sources |

#### Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calendar/events` | Get unified calendar events |
| GET | `/calendar/events/free-slots` | Find free time slots |

#### Import

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calendar/import/ocr` | Import calendar from image |
| POST | `/calendar/import/ical` | Import iCal/ICS file |

#### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calendar/analytics/daily` | Get daily calendar analytics |

### Data Models

#### CalendarSource

```python
{
  "source_id": "string",
  "source_type": "google|outlook|ical|ocr|manual",
  "display_name": "string",
  "is_active": boolean,
  "color": "string (#RRGGBB)",
  "requires_oauth": boolean,
  "last_sync": "datetime",
  "sync_frequency_minutes": integer,
  "sync_window_days": integer
}
```

#### UnifiedEvent

```python
{
  "event_id": "string",
  "source_id": "string",
  "title": "string",
  "description": "string",
  "location": "string",
  "start_time": "datetime",
  "end_time": "datetime",
  "all_day": boolean,
  "timezone": "string",
  "attendees": ["email1", "email2"],
  "organizer": "string",
  "is_recurring": boolean,
  "recurrence_rule": "string (RRULE format)",
  "status": "confirmed|tentative|cancelled",
  "has_conflict": boolean,
  "conflicting_event_ids": ["event_id1", "event_id2"]
}
```

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Web UI                              │
│                   (calendar.html)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│                   (calendar_routes.py)                       │
└────────┬────────────────────────┬────────────────────────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐    ┌──────────────────────────────┐
│  Calendar Sync   │    │  Calendar OCR Processor      │
│   Services       │    │   (AI-powered parsing)       │
│                  │    │                              │
│ - GoogleSync     │    └──────────────────────────────┘
│ - MicrosoftSync  │
│ - ICalSync       │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Calendar Storage Manager                    │
│           (JSON / SQLite / Firestore backend)                │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Conflict Detector                          │
│          (Detect overlaps, find free slots)                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Adding a Calendar Source**:
   ```
   User → Web UI → POST /calendar/sources → Storage
   ```

2. **OAuth Authentication**:
   ```
   User → Web UI → OAuth Endpoint → External Provider → Callback → Storage
   ```

3. **Syncing Events**:
   ```
   User → Sync Request → Calendar Sync Service → External API → UnifiedEvent → Storage
   ```

4. **OCR Import**:
   ```
   User → Upload Image → OCR Processor → Tesseract → LLM Parser → UnifiedEvent → Storage
   ```

5. **Viewing Events**:
   ```
   User → Web UI → GET /calendar/events → Storage → Conflict Detection → Response
   ```

### Storage Schema

**calendar_sources.json**:
```json
[
  {
    "source_id": "google_abc123",
    "source_type": "google",
    "display_name": "Work Calendar",
    "is_active": true,
    "color": "#4285F4",
    "last_sync": "2025-01-15T10:30:00"
  }
]
```

**unified_events.json**:
```json
[
  {
    "event_id": "google_abc123_event456",
    "source_id": "google_abc123",
    "title": "Team Meeting",
    "start_time": "2025-01-16T14:00:00",
    "end_time": "2025-01-16T15:00:00",
    "location": "Conference Room A",
    "has_conflict": false
  }
]
```

---

## Troubleshooting

### Google Calendar Authentication Fails

**Problem**: "Credentials file not found" error

**Solution**:
1. Ensure you've downloaded the credentials JSON from Google Cloud Console
2. Save it to `config/google_calendar_credentials.json`
3. Check the path in your `.env` file

**Problem**: "Access blocked: This app's request is invalid"

**Solution**:
1. Check that your Google Cloud project has Calendar API enabled
2. Verify redirect URIs include `http://localhost`
3. Make sure you're using Desktop app credentials

### Microsoft Calendar Authentication Fails

**Problem**: "Invalid redirect URI"

**Solution**:
1. In Azure Portal, ensure redirect URI matches exactly: `http://localhost:8000/auth/microsoft/callback`
2. Check that the redirect URI is registered under "Authentication" → "Platform configurations" → "Web"

**Problem**: "Insufficient permissions"

**Solution**:
1. Ensure `Calendars.Read` permission is added in Azure Portal
2. Grant admin consent for the permissions
3. Re-authenticate

### OCR Not Working

**Problem**: "No text could be extracted from the image"

**Solution**:
1. Ensure Tesseract is installed:
   ```bash
   # Windows
   Download from: https://github.com/UB-Mannheim/tesseract/wiki

   # Mac
   brew install tesseract

   # Linux
   sudo apt-get install tesseract-ocr
   ```
2. Use higher quality images
3. Ensure good contrast and lighting

**Problem**: "No calendar events could be parsed"

**Solution**:
1. Check that your LLM API key is configured
2. Verify the image actually contains calendar information
3. Try providing a reference date for better parsing

### Events Not Syncing

**Problem**: "No events fetched from calendar"

**Solution**:
1. Check that OAuth tokens are valid (re-authenticate if needed)
2. Verify the sync window covers the date range of your events
3. Check that the calendar source is marked as "active"

### Conflicts Not Detected

**Problem**: Overlapping events not showing as conflicts

**Solution**:
1. Ensure "detect_conflicts" parameter is true when fetching events
2. Check that event times are in the correct timezone
3. Sync all calendars before checking for conflicts

---

## Advanced Usage

### Custom Sync Intervals

You can configure different sync intervals for different calendar sources:

```python
{
  "sync_frequency_minutes": 15  # Sync every 15 minutes
}
```

### Filtering Events

Get events from specific sources only:

```bash
curl "http://localhost:8000/calendar/events?source_ids=google_abc123,outlook_xyz789"
```

### Finding Focus Time

Use the free slots API to find the best time for focused work:

```bash
curl "http://localhost:8000/calendar/events/free-slots?start_date=2025-01-16T00:00:00&end_date=2025-01-16T23:59:59&min_duration_minutes=120&work_hours_only=true"
```

This will return all 2-hour+ blocks during work hours (9am-5pm, M-F).

### Integrating with Journal Entries

The calendar events can be linked to journal entries through the `CalendarInsight` model, which tracks `related_journal_entries`. This allows you to:

1. See which meetings you journaled about
2. Auto-tag journal entries based on calendar events
3. Generate reports that combine calendar and journal data

---

## Best Practices

1. **Regular Syncing**: Set appropriate sync intervals (15-60 minutes) for frequently changing calendars
2. **OAuth Token Refresh**: OAuth tokens expire - implement proper refresh logic
3. **Conflict Resolution**: Review conflicts regularly and adjust schedules
4. **Privacy**: Keep OAuth credentials and tokens secure, never commit them to version control
5. **Error Handling**: Monitor sync errors and re-authenticate when needed
6. **Deduplication**: Run deduplication regularly if importing from multiple sources
7. **Timezone Awareness**: Always specify timezones for events to avoid confusion

---

## Future Enhancements

- **Two-way sync**: Create/edit events and push back to source calendars
- **Smart scheduling**: AI-powered meeting time suggestions
- **Recurring events**: Better handling of complex recurrence patterns
- **Mobile app**: Native mobile calendar integration
- **Notifications**: Real-time alerts for conflicts and upcoming events
- **CalDAV support**: Connect to any CalDAV server
- **Apple Calendar**: Direct iCloud calendar integration

---

## Support

For issues, feature requests, or questions:

1. Check the [GitHub Issues](https://github.com/your-repo/issues)
2. Review the API documentation at `http://localhost:8000/docs`
3. Consult the main README.md for general setup help

---

## License

This feature is part of the Cognitive Journal Agent project and follows the same license.
