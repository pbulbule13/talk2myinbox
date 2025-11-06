# Multi-Calendar Integration Feature

## Overview

This feature allows you to combine multiple calendar sources into a single unified view, ensuring you never miss an event. It supports OAuth-based calendar sync (Google, Outlook), file imports (iCal), and even AI-powered OCR extraction from calendar images.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_calendar.txt
```

### 2. Set Up Environment Variables

Copy the example below to your `.env` file:

```env
# LLM Configuration (for OCR parsing)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key

# Google Calendar (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Microsoft Calendar (optional)
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
```

### 3. Start the Server

```bash
python main.py api
```

### 4. Access the Calendar UI

Open your browser and navigate to:
```
web/calendar.html
```

Or use the API directly at:
```
http://localhost:8000/docs
```

## Features

### 🔗 Multiple Calendar Sources
- **Google Calendar** - OAuth 2.0 integration
- **Microsoft Outlook/365** - OAuth 2.0 integration
- **iCal/ICS Files** - Standard calendar file import
- **OCR Image Import** - Extract events from calendar screenshots
- **Manual Entry** - Direct event creation via API

### 🔍 Smart Features
- **Conflict Detection** - Automatically identify scheduling conflicts
- **Event Deduplication** - Remove duplicate events across sources
- **Free Time Finder** - Identify available time slots
- **Calendar Analytics** - Daily insights and statistics

### 🎨 Beautiful UI
- Responsive web interface
- Color-coded calendar sources
- Visual conflict indicators
- Real-time sync status

## Usage Examples

### Connect Google Calendar

1. Navigate to the "Import Calendar" tab
2. Enter your Gmail address
3. Click "Connect Google Calendar"
4. Complete OAuth flow
5. Events sync automatically

### Import Calendar from Image

1. Navigate to the "Import Calendar" tab
2. Upload a calendar screenshot
3. Select target calendar source
4. Wait for AI processing (OCR + LLM parsing)
5. Review extracted events

### Import iCal File

1. Navigate to the "Import Calendar" tab
2. Upload .ics file
3. Select target calendar source
4. Events are imported instantly

### View Unified Calendar

1. Navigate to the "Unified Events" tab
2. Set date range
3. Click "Load Events"
4. See all events from all sources
5. Conflicts are highlighted in red

### View Analytics

1. Navigate to the "Analytics" tab
2. Select a date
3. View:
   - Total events
   - Scheduled hours
   - Free time
   - Busiest hours
   - Event breakdown by source

## API Endpoints

### Calendar Sources
- `POST /calendar/sources` - Add calendar source
- `GET /calendar/sources` - List sources
- `DELETE /calendar/sources/{id}` - Delete source

### Events
- `GET /calendar/events` - Get unified events
- `GET /calendar/events/free-slots` - Find free time

### Sync
- `POST /calendar/sync/{source_id}` - Sync specific source
- `POST /calendar/sync/all` - Sync all sources

### Import
- `POST /calendar/import/ocr` - Import from image
- `POST /calendar/import/ical` - Import iCal file

### Analytics
- `GET /calendar/analytics/daily` - Daily analytics

## File Structure

```
cognitive_journal_agent/
├── data_models/
│   └── pydantic_schemas.py       # Calendar data models
├── nodes/
│   └── calendar_storage.py       # Storage layer (JSON/SQLite/Firestore)
├── services/
│   ├── calendar_sync.py          # Google/Microsoft/iCal sync
│   └── calendar_ocr.py           # OCR processing & conflict detection
├── api/
│   └── calendar_routes.py        # FastAPI endpoints
├── web/
│   └── calendar.html             # Web UI
├── docs/
│   └── MULTI_CALENDAR_GUIDE.md   # Complete documentation
├── requirements_calendar.txt     # Calendar dependencies
└── CALENDAR_FEATURE_README.md    # This file
```

## Architecture

```
┌─────────────┐
│   Web UI    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI Server             │
│  (calendar_routes.py)           │
└────────┬───────────┬────────────┘
         │           │
         ▼           ▼
┌──────────────┐  ┌──────────────┐
│ Calendar     │  │   OCR        │
│ Sync         │  │ Processor    │
│ Services     │  │ (AI-powered) │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   Calendar Storage Manager      │
│  (JSON/SQLite/Firestore)        │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│    Conflict Detector            │
└─────────────────────────────────┘
```

## Data Models

### CalendarSource
```python
{
  "source_id": "google_abc123",
  "source_type": "google|outlook|ical|ocr|manual",
  "display_name": "Work Calendar",
  "color": "#4285F4",
  "is_active": true,
  "sync_frequency_minutes": 60
}
```

### UnifiedEvent
```python
{
  "event_id": "google_abc123_event456",
  "source_id": "google_abc123",
  "title": "Team Meeting",
  "start_time": "2025-01-16T14:00:00",
  "end_time": "2025-01-16T15:00:00",
  "location": "Conference Room A",
  "has_conflict": false,
  "conflicting_event_ids": []
}
```

## Configuration

### OAuth Setup

#### Google Calendar
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials JSON
5. Save to `config/google_calendar_credentials.json`

#### Microsoft Calendar
1. Register app in [Azure Portal](https://portal.azure.com/)
2. Add `Calendars.Read` permission
3. Create client secret
4. Configure redirect URI: `http://localhost:8000/auth/microsoft/callback`
5. Add credentials to `.env`

### OCR Setup

1. Install Tesseract:
   ```bash
   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   # Mac: brew install tesseract
   # Linux: sudo apt-get install tesseract-ocr
   ```

2. Configure LLM API key in `.env`:
   ```env
   OPENAI_API_KEY=your_key
   # OR
   ANTHROPIC_API_KEY=your_key
   ```

## Troubleshooting

### Google Calendar Not Syncing
- Verify credentials file exists at `config/google_calendar_credentials.json`
- Re-run OAuth flow to refresh tokens
- Check Calendar API is enabled in Google Cloud Console

### Microsoft Calendar Authentication Failed
- Ensure redirect URI matches exactly in Azure Portal
- Verify `Calendars.Read` permission is granted
- Check client ID and secret in `.env`

### OCR Not Extracting Events
- Ensure Tesseract is installed and in PATH
- Use high-quality, clear images
- Provide a reference date for better parsing
- Check LLM API key is configured

### No Events Showing
- Sync calendar sources first
- Check date range covers your events
- Verify calendar source is active

## Advanced Usage

### Custom Sync Intervals
```python
{
  "sync_frequency_minutes": 15  # Sync every 15 minutes
}
```

### Filter Events by Source
```bash
curl "http://localhost:8000/calendar/events?source_ids=google_abc,outlook_xyz"
```

### Find Focus Time (2+ hour blocks)
```bash
curl "http://localhost:8000/calendar/events/free-slots?start_date=2025-01-16T00:00:00&end_date=2025-01-16T23:59:59&min_duration_minutes=120&work_hours_only=true"
```

## Security Best Practices

1. **Never commit** credentials or tokens to version control
2. **Use environment variables** for all sensitive data
3. **Rotate OAuth tokens** regularly
4. **Encrypt storage** if using Firestore or external databases
5. **Validate inputs** on all API endpoints
6. **Use HTTPS** in production

## Performance Tips

1. **Adjust sync intervals** based on calendar update frequency
2. **Use appropriate date ranges** to limit event fetching
3. **Enable caching** for frequently accessed data
4. **Run conflict detection** asynchronously for large datasets
5. **Optimize OCR images** (resize, crop) before uploading

## Future Enhancements

- [ ] Two-way calendar sync (create/edit events)
- [ ] Smart meeting scheduling with AI suggestions
- [ ] Mobile app integration
- [ ] Real-time notifications for conflicts
- [ ] CalDAV server support
- [ ] Apple Calendar direct integration
- [ ] Natural language event creation
- [ ] Automatic event categorization

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Documentation

For complete documentation, see:
- **Full Guide**: `docs/MULTI_CALENDAR_GUIDE.md`
- **API Docs**: `http://localhost:8000/docs` (when server is running)
- **Main README**: `README.md`

## Support

- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- API Documentation: http://localhost:8000/docs
- Questions: Check the full guide in `docs/MULTI_CALENDAR_GUIDE.md`

## License

This feature is part of the Cognitive Journal Agent project and follows the same license.

---

Built with ❤️ for the Cognitive Journal Agent
