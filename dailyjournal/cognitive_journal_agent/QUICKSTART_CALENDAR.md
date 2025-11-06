# Quick Start Guide - Multi-Calendar Integration

## Your Event Has Been Added! 🎉

**Data Science Salon SF: GenAI and Intelligent Agents**
- **Date**: November 6, 2025 (Thursday)
- **Time**: 9:00 AM - 5:00 PM PST
- **Location**: AWS Builder Loft, San Francisco
- **Status**: Registered ✓

Your event is now in the calendar system and ready to view!

---

## Option 1: View Your Event via Web UI (Recommended)

### Step 1: Start the Server

```bash
# Option A: Using the batch file
start_server.bat

# Option B: Using Python directly
python main.py api
```

The server will start on `http://localhost:8000`

### Step 2: Open the Calendar UI

Open `web/calendar.html` in your browser, or navigate to:
```
http://localhost:8000/
```

### Step 3: View Your Event

1. Click on the **"Unified Events"** tab
2. Set the date range:
   - Start Date: `2025-11-01`
   - End Date: `2025-11-30`
3. Click **"Load Events"**
4. You'll see your Data Science Salon event displayed!

---

## Option 2: View via API

### Get All Events

```bash
curl http://localhost:8000/calendar/events?start_date=2025-11-01&end_date=2025-11-30
```

### Get Event Details as JSON

```bash
curl http://localhost:8000/calendar/events | python -m json.tool
```

---

## What You Can Do Now

### 1. Add More Calendar Sources

**Connect Google Calendar:**
1. Go to Import Calendar tab
2. Enter your Gmail address
3. Complete OAuth flow
4. Your Google events sync automatically

**Connect Outlook/Microsoft 365:**
1. Go to Import Calendar tab
2. Click "Connect Microsoft Calendar"
3. Complete OAuth in browser
4. Events sync automatically

**Import Calendar from Image:**
1. Take a screenshot of any calendar
2. Upload to Import Calendar tab
3. AI extracts events automatically

**Import iCal Files:**
1. Export .ics file from any calendar app
2. Upload to Import Calendar tab
3. Events are imported instantly

### 2. Detect Conflicts

The system automatically detects:
- Overlapping events
- Back-to-back meetings
- Double bookings

Any conflicts with your Data Science Salon event will be highlighted in red!

### 3. Find Free Time

**Via UI:**
1. Go to Unified Events tab
2. Use the date picker
3. See all your free time slots

**Via API:**
```bash
curl "http://localhost:8000/calendar/events/free-slots?start_date=2025-11-06T00:00:00&end_date=2025-11-06T23:59:59&min_duration_minutes=60&work_hours_only=true"
```

### 4. View Analytics

1. Go to Analytics tab
2. Select November 6, 2025
3. See:
   - Total events
   - Scheduled hours
   - Free time
   - Busiest hours

---

## Adding More Events

### Method 1: Run the Example Script Again

Edit `add_event_example.py` and change the event details:

```python
event = UnifiedEvent(
    event_id=f"manual_events_{uuid.uuid4().hex[:12]}",
    source_id="manual_events",
    title="Your Event Name",
    description="Event description",
    location="Event Location",
    start_time=datetime(2025, 11, 15, 14, 0, 0),  # Nov 15, 2:00 PM
    end_time=datetime(2025, 11, 15, 16, 0, 0),    # Nov 15, 4:00 PM
    all_day=False,
    timezone="America/Los_Angeles",
    # ... rest of the fields
)
```

Then run:
```bash
python add_event_example.py
```

### Method 2: Via API

```bash
curl -X POST "http://localhost:8000/calendar/sources" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "manual",
    "display_name": "My Events",
    "color": "#4285F4"
  }'
```

### Method 3: Connect Real Calendars

Follow the OAuth flows to sync Google Calendar or Outlook!

---

## Current Setup

### Calendar Sources Created:
- ✓ **My Events** (Manual) - Color: #FF6B6B

### Events Stored:
- ✓ **Data Science Salon SF: GenAI and Intelligent Agents**
  - November 6, 2025, 9:00 AM - 5:00 PM
  - AWS Builder Loft, San Francisco

### Data Location:
All your calendar data is stored in:
```
data/calendar_sources.json
data/unified_events.json
data/calendar_connections.json
```

---

## Viewing Your Event Right Now

### Option A: Check the JSON Files Directly

```bash
# View your event
python -m json.tool data/unified_events.json

# View your calendar sources
python -m json.tool data/calendar_sources.json
```

### Option B: Quick Python Script

Create `view_events.py`:
```python
import json
from pathlib import Path

events_file = Path("data/unified_events.json")
if events_file.exists():
    with open(events_file) as f:
        events = json.load(f)
        print(f"\nYou have {len(events)} event(s):\n")
        for event in events:
            print(f"- {event['title']}")
            print(f"  {event['start_time']} to {event['end_time']}")
            print(f"  Location: {event['location']}\n")
```

Run it:
```bash
python view_events.py
```

---

## Preparing for Your Event

### Things to Add to Your Calendar:

**Before the Event:**
- Travel time to AWS Builder Loft (consider SF traffic!)
- Prep time (review agenda, prepare questions)
- Follow-up tasks after the event

**During the Event:**
- Networking opportunities
- Specific sessions you want to attend
- Breaks

**After the Event:**
- Follow-up time to process notes
- Connect with people you met on LinkedIn
- Apply learnings to your projects

### Add Travel Time:

```python
# Add to add_event_example.py
travel_event = UnifiedEvent(
    event_id=f"manual_events_{uuid.uuid4().hex[:12]}",
    source_id="manual_events",
    title="Travel to Data Science Salon",
    location="En route to AWS Builder Loft",
    start_time=datetime(2025, 11, 6, 8, 0, 0),  # 8:00 AM
    end_time=datetime(2025, 11, 6, 9, 0, 0),    # 9:00 AM
    timezone="America/Los_Angeles",
    # ... rest of fields
)
```

---

## Troubleshooting

### Event Not Showing in UI?

1. Make sure the server is running
2. Check the date range includes November 6, 2025
3. Click "Load Events" button
4. Clear browser cache and refresh

### API Not Working?

1. Check if server is running: `curl http://localhost:8000/health`
2. Verify port 8000 is not in use by another app
3. Check the console for errors

### Want to Delete the Test Event?

Events are stored in `data/unified_events.json`. You can:
1. Delete the file to start fresh
2. Edit the JSON file directly
3. Use the API to delete (coming soon)

---

## Next Steps

1. **✓ Event Added** - Your Data Science Salon event is in the system
2. **→ Start Server** - Run `python main.py api`
3. **→ View UI** - Open `web/calendar.html`
4. **→ Add More Sources** - Connect Google Calendar or Outlook
5. **→ Import Other Calendars** - Upload images or .ics files
6. **→ Check Conflicts** - Make sure your schedule is clear for Nov 6

---

## Full Documentation

For complete details, see:
- **Complete Guide**: `docs/MULTI_CALENDAR_GUIDE.md`
- **Feature README**: `CALENDAR_FEATURE_README.md`
- **API Docs**: http://localhost:8000/docs (when server running)

---

## Support

Questions? Issues?
1. Check the comprehensive guide: `docs/MULTI_CALENDAR_GUIDE.md`
2. Review API documentation at http://localhost:8000/docs
3. Check the example scripts in the project

---

**Enjoy your Data Science Salon event! 🤖**

Have a great time learning about GenAI and Intelligent Agents!
