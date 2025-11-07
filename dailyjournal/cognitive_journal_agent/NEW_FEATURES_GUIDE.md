# 🚀 NEW FEATURES GUIDE - Personal Assistant Upgrade

## Overview

Your Cognitive Journal Agent has been transformed into a **complete personal assistant** with natural language understanding, voice commands, smart reminders, and multi-calendar consolidation!

---

## 🎯 What's New

### 1. **Natural Language Date/Time Parsing** ✨

No more ISO format headaches! The system now understands natural language:

**Examples:**
- "tomorrow 2pm"
- "next Tuesday at 10am"
- "in 30 minutes"
- "Friday afternoon"
- "8pm today"
- "next week"

**Where it works:**
- Calendar blocking
- Event scheduling
- Reminder setting
- Any time-related command

---

### 2. **Live Voice Commands** 🎤

Speak naturally to the app using your browser's microphone!

**How to use:**
1. Go to web UI → Voice tab
2. Click "Start Listening"
3. Speak your command
4. System processes and executes automatically

**Supported Commands:**

#### Calendar Management
```
"Block calendar for 2-3 tomorrow for kids pickup"
"Schedule 5 minutes tomorrow for interview prep"
"Add to calendar: meeting with John on Friday at 2pm"
```

#### Reminders
```
"Remind me at 8pm to call Mr. A for interview"
"Set reminder for tomorrow 9am to review project"
"Remind me in 30 minutes to take a break"
```

#### Notes & Tasks
```
"Add note: ensure we finish production deployment of talk to inbox"
"Need to complete the project report by Friday"
"Take note: Mindtree and Matlabs interviews in progress"
```

#### Journal Entries
```
"Had a great meeting with the team today"
"Feeling productive and energized"
"Great idea: add automation to the workflow"
```

---

### 3. **Smart Reminder System** ⏰

Background reminder system that actually reminds you!

**Features:**
- One-time and recurring reminders
- Multiple notification methods (console, email, browser)
- Natural language time parsing
- Graceful handling of missed reminders

**How to use:**

**Via Voice:**
```
"Remind me at 8pm to prepare for tomorrow's meeting"
```

**Via API:**
```bash
curl -X POST http://localhost:7000/voice-command \
  -H "Content-Type: application/json" \
  -d '{"command": "remind me at 8pm to call client"}'
```

**View Reminders:**
```bash
curl http://localhost:7000/reminders
```

**Cancel Reminder:**
```bash
curl -X DELETE http://localhost:7000/reminders/{reminder_id}
```

---

### 4. **Calendar Consolidation** 📅

Visual unified view of all your calendars!

**Access:** Open `http://localhost:7000/web/calendar_consolidated.html`

**Features:**
- Multi-source calendar aggregation
- Timeline and list views
- Conflict detection with alerts
- Free time slot finder
- Color-coded by source
- Interactive date picker

**Supported Sources:**
- Google Calendar (via OAuth)
- Microsoft Outlook (via OAuth)
- Apple Calendar
- iCal/ICS files
- OCR from calendar screenshots
- Manual entry

**How to use:**

1. **Add Calendar Source:**
```bash
curl -X POST http://localhost:7000/calendar/sources \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "google",
    "display_name": "Work Calendar",
    "color": "#4285F4"
  }'
```

2. **Upload Calendar Screenshot:**
   - Go to Calendar UI
   - Click "Add Source" → "From Image"
   - Upload screenshot
   - System extracts events via OCR + LLM

3. **View Consolidated Events:**
   - Select date
   - Toggle between Timeline/List view
   - See conflicts highlighted
   - View free time slots

---

### 5. **Intent Detection & Smart Routing** 🧠

The system now understands what you want to do and routes commands automatically:

**Detected Intents:**
- `calendar_block` - Blocking time
- `calendar_schedule` - Scheduling events
- `reminder` - Setting reminders
- `note` - Taking notes
- `task` - Creating action items
- `journal` - Regular journaling

**Example Flow:**

**You say:** "Block calendar for 2-3 tomorrow for kids pickup"

**System:**
1. Detects intent: `calendar_block`
2. Extracts entities:
   - Time: 2-3pm tomorrow
   - Title: "kids pickup"
3. Creates calendar event
4. Confirms: "Calendar event 'kids pickup' added successfully for 2025-01-08 14:00 (60 minutes)"

---

## 📋 Complete Feature Matrix

| Feature | Voice | Text | API | Web UI |
|---------|-------|------|-----|--------|
| Calendar Blocking | ✅ | ✅ | ✅ | ✅ |
| Event Scheduling | ✅ | ✅ | ✅ | ✅ |
| Reminders | ✅ | ✅ | ✅ | 🔄 |
| Notes/Tasks | ✅ | ✅ | ✅ | ✅ |
| Screenshot OCR | ❌ | ❌ | ✅ | ✅ |
| Calendar Consolidation | ❌ | ❌ | ✅ | ✅ |
| Daily Summary | ✅ | ✅ | ✅ | ✅ |
| Action Items | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 Your Specific Use Cases - NOW SUPPORTED!

### ✅ Screenshot to Summary
**How:** Upload any screenshot (slides, events, notes) → OCR extracts text → Adds to daily summary
```bash
# Upload via web UI Image tab, or:
curl -X POST http://localhost:7000/upload \
  -F "file=@screenshot.png" \
  -F "input_type=image"
```

### ✅ Calendar Screenshot Consolidation
**How:** Upload calendar screenshots → OCR + LLM extracts events → Adds to consolidated calendar
```bash
curl -X POST http://localhost:7000/calendar/import/ocr \
  -F "file=@calendar.png" \
  -F "source_id=work_calendar"
```

### ✅ Meeting Notes/Transcripts
**How:** Copy/paste text → Auto-analyzes → Extracts action items
```
Just paste into the text box or say:
"Add note: In today's meeting we discussed Q4 goals and decided to launch by March"
```

### ✅ Voice Commands - ALL YOUR EXAMPLES!
```
✅ "Block calendar for 2-3 tomorrow for kids pickup"
✅ "Remind me at 8pm to call Mr. A for interview"
✅ "Add note: finish production deployment of talk to inbox"
✅ "Schedule 5 minutes tomorrow for Mindtree interview prep"
✅ "Note: Matlabs and OneSource interviews in progress"
```

### ✅ Daily Summary with All Sources
- Screenshots converted to text ✅
- Calendar events ✅
- Voice notes transcribed ✅
- Meeting notes ✅
- Action items extracted ✅
- Emotional tone analyzed ✅

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd cognitive_journal_agent
python main.py api
```

### 2. Open Web UI
```
http://localhost:7000/web_ui.html
```

### 3. Try Voice Commands
1. Click Voice tab
2. Click "Start Listening"
3. Say: "Block calendar for 3pm today for team meeting"

### 4. View Calendar Consolidation
```
http://localhost:7000/web/calendar_consolidated.html
```

### 5. Check Reminders
```bash
curl http://localhost:7000/reminders
```

---

## 📚 API Endpoints Reference

### Voice Commands
```
POST /voice-command
Body: {"command": "your natural language command"}
```

### Reminders
```
GET  /reminders                    # List all
POST /reminders                    # Create (via voice-command)
DELETE /reminders/{id}             # Cancel
GET  /notifications/browser        # Get pending notifications
POST /notifications/browser/{id}/read  # Mark as read
```

### Calendar
```
GET  /calendar/events              # Get events
POST /calendar/sync/all            # Sync all sources
POST /calendar/import/ocr          # Upload calendar screenshot
GET  /calendar/events/free-slots   # Find free time
```

### Journal (Existing)
```
POST /journal                      # Create entry
GET  /entries                      # List all
GET  /actions                      # Get action items
POST /summarize                    # Generate summary
POST /upload                       # Upload files
```

---

## 🎨 Example Workflows

### Morning Routine
```
1. Say: "What's on my calendar today?"
2. System shows consolidated calendar
3. Say: "Block 9-10am for morning planning"
4. Say: "Remind me at 5pm to review daily summary"
```

### After Meeting
```
1. Copy meeting transcript
2. Paste into text box
3. System extracts:
   - Key discussion points
   - Action items
   - Mentions of people
   - Deadlines
4. Automatically adds to daily summary
```

### Screenshot Processing
```
1. Take screenshot of presentation
2. Upload via Image tab
3. OCR extracts text
4. LLM analyzes content
5. Adds to summary with tags
```

---

## 🔧 Configuration

### Enable Email Reminders
```bash
# In .env file
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Add Google Calendar
```bash
# Get OAuth credentials from Google Cloud Console
# Add to .env:
GOOGLE_CALENDAR_CREDENTIALS=/path/to/credentials.json
```

### Customize NLP Parser
Edit `services/nlp_parser.py` to add custom intent patterns.

---

## ⚡ Performance Tips

1. **Voice Recognition:** Works best in Chrome/Edge browsers
2. **Calendar Sync:** Run sync manually first time, then automatic
3. **OCR Quality:** Use high-resolution screenshots
4. **Reminders:** Browser notifications require polling (every 30s)

---

## 🐛 Troubleshooting

### Voice not working?
- Check microphone permissions in browser
- Use Chrome or Edge (best support)
- Check console for errors

### Reminders not triggering?
- Check reminder system is running (starts with API server)
- Verify time is in the future
- Check `data/reminders.json` for scheduled reminders

### Calendar not showing events?
- Sync calendar sources first
- Check date range selection
- Verify source is active

### Natural language parsing issues?
- Be specific with times ("2pm" not "afternoon")
- Include date context ("tomorrow" not "later")
- Check logs for parsing errors

---

## 🎓 Advanced Features

### Custom Voice Commands
Edit `services/nlp_parser.py` to add patterns:
```python
self.intent_patterns[CommandIntent.CUSTOM] = [
    r'my custom pattern',
]
```

### Recurring Reminders
```python
reminder_system.add_reminder(
    message="Daily standup",
    reminder_time=datetime.now().replace(hour=9, minute=0),
    recurring=True,
    recurrence_pattern="daily"
)
```

### Calendar OCR with Custom LLM
Modify `services/calendar_ocr.py` to use different LLM model.

---

## 📈 Next Steps

1. **Set up your calendar sources**
2. **Try voice commands**
3. **Upload some screenshots to test OCR**
4. **Set a few reminders**
5. **Generate your first daily summary with ALL sources**

---

## 🎉 You're All Set!

Your Personal Assistant is ready to:
- ✅ Understand natural language
- ✅ Execute voice commands
- ✅ Manage your calendar intelligently
- ✅ Send you reminders
- ✅ Process screenshots and documents
- ✅ Consolidate everything into daily summaries

**Start by saying:** "Block calendar for 2-3 tomorrow for kids pickup" 🚀

---

**Need Help?** Check the logs or open an issue on GitHub!

**Version:** 2.0.0 - Personal Assistant Edition
**Last Updated:** 2025-01-07
