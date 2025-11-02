# Voice Agent System - Agentic Email & Calendar Automation

## Overview

This is a production-grade **voice-enabled email and calendar automation system** built entirely in Python. The system acts as an executive assistant that can:

- ✅ **Triage and prioritize** your inbox intelligently
- ✅ **Draft human-quality email replies** in your tone
- ✅ **Manage calendar** scheduling, accepts, declines, and proposals
- ✅ **Track follow-ups** and remind you of pending items
- ✅ **Operate via voice or text** - hands-free or keyboard-driven
- ✅ **Require authorization codes** before taking irreversible actions (gotoHuman-style human-in-the-loop)
- ✅ **Log everything** for complete audit trail and dashboard visibility

**Default Agent Name:** "Vinegar" (fully customizable in settings)

## 🏗️ Architecture

### Technology Stack

- **LangGraph** - Agent orchestration and state machine
- **Pydantic** - Strongly typed models and validation
- **FastAPI** - REST API and WebSocket endpoints
- **LangChain + OpenAI** - LLM reasoning and draft generation
- **Gmail API / Google Calendar API** - Email and calendar integration (pluggable adapters)
- **ElevenLabs + Whisper** - Text-to-speech and speech-to-text (pluggable)

### System Flow

```
User Query (Voice/Text)
    ↓
[Intent Classification] → Determine what user wants
    ↓
[Context Retrieval] → Fetch emails, calendar, history
    ↓
[Reasoning] → Assess priority, decide best action
    ↓
[Draft Generation] → Create email drafts or calendar proposals
    ↓
[Authorization] → Request 4-digit code if action requires it
    ↓
[Execution] → Send email, accept meeting, etc. (ONLY if authorized)
    ↓
[Logging] → Record everything for audit trail
    ↓
Response to User + Dashboard Update
```

### Key Design Principles

1. **Human-in-the-Loop**: Never send emails or modify calendar without explicit authorization
2. **Authorization Codes**: 4-digit one-time codes required for irreversible actions
3. **Full Audit Trail**: Every decision and action is logged with reasoning
4. **Cloud-Agnostic**: Default GCP, but runs on AWS, Azure, or on-prem with just config changes
5. **Pluggable Adapters**: Swap email/calendar providers without touching core logic
6. **Voice-First**: Designed for hands-free operation but works equally well with text

## 📁 Directory Structure

```
voice_agent/
├── models/                    # Pydantic models
│   ├── email_models.py       # EmailDraft, EmailThread, EmailCategory
│   ├── calendar_models.py    # CalendarEvent, CalendarAction
│   ├── action_models.py      # ActionLog, FollowUpTask
│   ├── auth_models.py        # AuthorizationCode, AuthSession
│   └── settings.py           # SystemSettings (configuration)
├── agents/                    # LangGraph agent nodes
│   ├── intent_agent.py       # Classify user intent
│   ├── context_agent.py      # Retrieve email/calendar context
│   ├── reasoning_agent.py    # Assess priority and recommend action
│   ├── draft_agent.py        # Generate email drafts and calendar proposals
│   ├── authorization_agent.py # Manage auth codes
│   ├── execution_agent.py    # Execute authorized actions
│   └── logging_agent.py      # Record all actions to audit trail
├── graph/                     # LangGraph orchestration
│   ├── state.py              # VoiceAgentState (shared state)
│   └── graph_builder.py      # Build the LangGraph workflow
├── adapters/                  # Provider integrations
│   ├── email/
│   │   ├── base.py           # BaseEmailAdapter (abstract interface)
│   │   └── gmail_adapter.py  # Gmail API implementation
│   └── calendar/
│       ├── base.py           # BaseCalendarAdapter
│       └── google_calendar_adapter.py  # Google Calendar API
├── api/                       # FastAPI endpoints
│   └── routes.py             # REST and WebSocket endpoints
├── orchestrator.py            # Main VoiceAgentOrchestrator
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
# Voice Agent Configuration
VOICE_AGENT_voice_agent_name=Vinegar
VOICE_AGENT_cloud_provider=gcp

# LLM
OPENAI_API_KEY=your_openai_key_here

# Email
VOICE_AGENT_email_provider=gmail_api
VOICE_AGENT_gmail_credentials_path=./config/gmail_credentials.json

# Calendar
VOICE_AGENT_calendar_provider=google_calendar
VOICE_AGENT_calendar_credentials_path=./config/calendar_credentials.json

# Voice
VOICE_AGENT_tts_provider=elevenlabs
VOICE_AGENT_elevenlabs_api_key=your_elevenlabs_key_here
VOICE_AGENT_stt_provider=whisper
```

### 3. Set Up Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Gmail API** and **Google Calendar API**
4. Create OAuth 2.0 credentials
5. Download credentials JSON and save to `./config/gmail_credentials.json`
6. First run will prompt you to authorize access in browser

### 4. Start the API Server

```bash
# From the healthcare_sciences_dashboard directory
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API

```bash
curl -X POST http://localhost:8000/voice-agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What emails need my attention?",
    "mode": "text"
  }'
```

## 📖 Usage Examples

### Example 1: Triage Inbox

**User:** "Vinegar, what's in my inbox?"

**System:**
- Classifies intent as `triage_inbox`
- Fetches recent emails via Gmail API
- Assesses priority (high/medium/low) with reasoning
- Returns summary:

```
"You have 3 emails that need attention:

1. **High Priority**: John from PartnerCorp asking about Q4 review meeting
   → Reason: Key partner, time-sensitive request
   → Suggested action: Draft a reply proposing times

2. **Medium Priority**: Internal team update from Sarah
   → Reason: FYI, no action needed
   → Suggested action: Mark as read

3. **Low Priority**: Marketing newsletter
   → Reason: Bulk email
   → Suggested action: Archive

Would you like me to draft a reply to John's email?"
```

### Example 2: Draft Email Reply

**User:** "Yes, draft a warm reply saying I'm available Thursday at 2pm"

**System:**
- Classifies intent as `draft_reply`
- Generates email draft:

```
Subject: Re: Q4 Financial Review Meeting

Hi John,

Thanks for reaching out! I'd be happy to discuss Q4 numbers with you.

I'm available Thursday at 2:00 PM if that works for you. We can meet at our office or hop on a call, whatever you prefer.

Looking forward to it!

Best,
[Your Name]
```

**System:** "I've prepared this reply. To send it, please provide your 4-digit authorization code: **5239**"

**User:** "5239"

**System:** "Email sent successfully! I'll remind you 30 minutes before the meeting if you'd like."

### Example 3: Calendar Management

**User:** "Do I have any conflicts tomorrow afternoon?"

**System:**
- Checks calendar for tomorrow 12pm-6pm
- Returns: "You have one meeting from 2-3pm (Board Prep). You're free from 12-2pm and 3-6pm."

**User:** "Accept the 2pm meeting and block 1:30-2pm for prep time"

**System:**
- Proposes two calendar actions
- Generates authorization code
- After user confirms, executes both actions

## 🔐 Authorization & Safety

### How Authorization Works

1. **Action Detection**: System identifies if action is irreversible (send email, accept meeting, etc.)
2. **Code Generation**: Creates a 4-digit one-time code (expires in 10 minutes, 3 attempts max)
3. **User Confirmation**: Displays/speaks the code and waits for user input
4. **Validation**: Verifies code before executing action
5. **Logging**: Records whether action was authorized and executed

### Actions That Require Authorization

- ✅ Sending an email
- ✅ Accepting a calendar invite
- ✅ Declining a calendar invite
- ✅ Creating a calendar event
- ✅ Blocking calendar time

### Actions That Don't Require Authorization

- Reading/summarizing inbox
- Checking calendar
- Generating drafts (without sending)
- Setting follow-up reminders

## 📊 Action Logging & Dashboard

Every action generates an **ActionLog** entry:

```python
{
    "log_id": "log_abc123",
    "timestamp": "2025-10-27T14:30:00Z",
    "actor": "Vinegar",
    "mode": "voice",
    "object_type": "email",
    "object_ref": "Re: Q4 Financial Review",
    "action": "drafted_reply",
    "reason": "User requested reply with proposed meeting time",
    "status": {
        "status": "pending_user_auth",
        "status_message": "Awaiting authorization code"
    },
    "user_id": "ceo_user",
    "authorization_code_used": false,
    "metadata": {
        "draft_id": "draft_xyz789",
        "to": ["john.doe@partner.com"]
    }
}
```

These logs are:
- Streamed to the dashboard in real-time
- Stored in database (PostgreSQL/Firestore/SQLite)
- Queryable for audit trail
- Used for analytics and insights

## 🎤 Voice Integration

### Text-to-Speech (TTS)

Default: **ElevenLabs**

```python
# System speaks responses naturally
voice_response = "You have 3 emails that need attention..."
# → Converted to speech and played back
```

### Speech-to-Text (STT)

Default: **Whisper** (OpenAI)

```python
# User speaks command
audio_input = record_audio()  # "Vinegar, what's in my inbox?"
# → Transcribed to text and processed
```

### Wake Word

"Vinegar" (or custom name from settings)

## ⚙️ Configuration

All behavior is configurable via `SystemSettings`:

```python
class SystemSettings(BaseModel):
    # Agent Identity
    voice_agent_name: str = "Vinegar"  # Change to any name

    # Cloud/Deployment
    cloud_provider: Literal["gcp", "aws", "azure", "on_prem"] = "gcp"

    # Authorization
    auth_code_length: int = 4
    auth_code_expiry_minutes: int = 10

    # Communication
    tone_default: Literal["formal", "warm", "concise", "friendly"] = "formal"
    vip_domains: list[str] = ["partner.com", "investor.org"]

    # Providers
    email_provider: Literal["gmail_api", "imap_smtp", "outlook_graph"] = "gmail_api"
    calendar_provider: Literal["google_calendar", "caldav", "outlook_calendar"] = "google_calendar"
    tts_provider: Literal["elevenlabs", "google_tts", "azure_tts"] = "elevenlabs"
    stt_provider: Literal["whisper", "google_stt", "azure_stt"] = "whisper"
```

## 🔌 Adding New Providers

### Email Provider

1. Implement `BaseEmailAdapter` interface
2. Add to `adapters/email/`
3. Register in `orchestrator.py`

Example:

```python
# adapters/email/outlook_adapter.py
class OutlookAdapter(BaseEmailAdapter):
    async def fetch_threads(self, ...):
        # Use Microsoft Graph API
        pass

    async def send_email(self, ...):
        # Use Microsoft Graph API
        pass
```

### Calendar Provider

Same process, implement `BaseCalendarAdapter`

## 🚢 Deployment

### Google Cloud Run (Default)

```bash
# Build container
docker build -t gcr.io/your-project/voice-agent .

# Deploy
gcloud run deploy voice-agent \
  --image gcr.io/your-project/voice-agent \
  --platform managed \
  --region us-central1
```

### AWS/Azure/On-Prem

Just change `cloud_provider` in settings. No code changes needed.

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific module
pytest voice_agent/tests/test_intent_agent.py
```

## 📝 Next Steps

1. **Complete Gmail/Calendar API Setup**: Follow OAuth2 flow to get credentials
2. **Integrate with Dashboard UI**: Connect FastAPI endpoints to Communications tab
3. **Add Voice UI**: Build microphone input and audio playback in frontend
4. **Set Up Database**: Configure PostgreSQL or Firestore for persistent storage
5. **Deploy to Cloud**: Use Docker + Cloud Run/ECS/Azure Container Instances

## 🤝 Contributing

This system is modular and extensible. To add features:

1. **New Intent**: Add to `IntentClassificationAgent`
2. **New Agent**: Create in `agents/` and wire into `graph_builder.py`
3. **New Provider**: Implement adapter interface
4. **New Models**: Add to `models/` with Pydantic validation

## 📚 References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Google Calendar API Python Quickstart](https://developers.google.com/calendar/api/quickstart/python)
- [ElevenLabs API Docs](https://elevenlabs.io/docs)
- [OpenAI Whisper](https://github.com/openai/whisper)

## 📄 License

[Your License Here]

---

**Built with LangGraph, FastAPI, and Pydantic**
