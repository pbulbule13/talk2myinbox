# Talk2MyInbox - AI Email & Calendar Assistant

An intelligent email and calendar management system with voice capabilities, powered by AI.

## 🚀 Features

### Email Management
- ✅ **30 Emails Display** with pagination (10 per page)
- ✅ **Smart Detection** - Human vs Automated email classification
- ✅ **Thread Grouping** - Conversations with >2 messages automatically grouped
- ✅ **Job Application Tracking** - Automatically detects and prioritizes job-related emails
- ✅ **Follow-up Indicators** - Visual badges for threads needing attention
- ✅ **Thread Viewer** - View full conversation history in a modal

### Calendar Integration
- ✅ **Auto-Detect Calendar Invites** - Automatically finds meeting invitations in emails
- ✅ **Automatic Calendar Blocking** - Creates calendar events from detected invites
- ✅ **Manual Time Blocking** - API to block specific time slots (e.g., kids' school)
- ✅ **Week/Day View** - View events for today or the entire week

### AI Features
- ✅ **Inbox Overview** - AI-powered summary of important emails
- ✅ **Interview Counter** - Counts upcoming interviews for the week
- ✅ **Voice-Enabled** - Text-to-speech for inbox overviews
- ✅ **Smart Prioritization** - AI reasoning for email importance

## 📋 Prerequisites

- Python 3.11 or higher
- Gmail API credentials (optional - runs in mock mode without)
- Google Calendar API credentials (optional - runs in mock mode without)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pbulbule13/talk2myinbox.git
cd talk2myinbox
```

### 2. Set Up Python Virtual Environment

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)

Create a `.env` file in the `backend` directory:

```env
# Gmail API (Optional - app works without these)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# AI Provider (Optional)
EURON_API_KEY=your_euron_api_key
EURON_API_BASE=https://api.euron.one/api/v1/euri
EURON_MODEL=gpt-4.1-nano

# Server Configuration
PORT=8000
HOST=0.0.0.0
```

**Note:** The application runs in **mock mode** if Gmail credentials are not configured. You'll see sample emails and calendar events.

## 🎯 Running the Application

### Method 1: Direct Python Run (Recommended)

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Run the server
python server.py
```

### Method 2: Using Uvicorn Directly

```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Accessing the Application

Once the server starts, you'll see:

```
========================================
Communications App Server Starting
========================================
Server: http://0.0.0.0:8000
API Docs: http://0.0.0.0:8000/docs
Health: http://0.0.0.0:8000/health
========================================
```

**Open your browser and navigate to:**
- **Main App:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🎨 Using the Features

### 1. Email Management

**View Emails:**
- Emails load automatically on page load
- Use pagination controls at the bottom (← Prev / Next →)
- Filter by category using the tabs at the top

**Email Badges:**
- 👤 **Human** - Email from a real person
- 🤖 **Auto** - Automated/system email
- 💬 **X msgs** - Number of messages in thread
- 💼 **Job App** - Job application related
- ⚠️ **Follow-up** - Needs your attention

**Thread Viewer:**
- Click "👁️ View Thread" on conversations with multiple messages
- See all messages in chronological order
- Reply directly from the thread viewer

### 2. Calendar Features

**View Calendar:**
- Calendar events display automatically
- Switch between Day and Week view

**Manual Calendar Blocking:**
Open browser console (F12) and run:
```javascript
// Block 1 hour for kids' school
blockCalendarTime('Kids School', '2025-01-27T15:00:00', 60)
```

### 3. AI Inbox Overview

Open browser console (F12) and run:
```javascript
// Get AI-powered inbox overview
getInboxOverview()
```

This will show:
- Important emails to review
- Interview count for the week
- Short, crisp summary
- Click 🔊 **Speak** button to hear it read aloud

## 📁 Project Structure

```
talk2myinbox/
├── backend/
│   ├── server.py                 # Main FastAPI server
│   ├── requirements.txt          # Python dependencies
│   ├── voice_agent/
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   ├── adapters/
│   │   │   ├── email/           # Gmail adapter
│   │   │   └── calendar/        # Calendar adapter
│   │   ├── agents/              # AI agents (8 total)
│   │   ├── graph/               # LangGraph workflow
│   │   ├── models/              # Pydantic models
│   │   └── utils/               # Utilities
│   └── tests/                   # Comprehensive test suite
│       ├── unit/                # Unit tests
│       ├── integration/         # Integration tests
│       └── e2e/                 # End-to-end tests
│
└── frontend/
    ├── index.html               # Main UI
    ├── communications_enhanced.js  # Core app logic
    ├── voice_module.js          # Voice controls
    └── support.js               # Support features
```

## 🔍 API Endpoints

### Email Endpoints
- `GET /voice-agent/emails` - Get email list
- `POST /voice-agent/email/send` - Send email
- `POST /voice-agent/emails/search` - Search emails
- `POST /voice-agent/email/mark-read` - Mark as read

### Calendar Endpoints
- `GET /voice-agent/calendar` - Get calendar events
- `POST /voice-agent/calendar/event` - Create calendar event
- `PUT /voice-agent/calendar/event/{id}` - Update event
- `DELETE /voice-agent/calendar/event/{id}` - Delete event

### AI Endpoints
- `POST /voice-agent/query` - Process AI query
- `POST /voice-agent/tts` - Text-to-speech

**Full API documentation:** http://localhost:8000/docs

## 🧪 Running Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test suites
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/unit/test_orchestrator.py  # Specific test file

# Run with coverage
pytest --cov=voice_agent tests/
```

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
cd backend
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Emails not loading

**Solution:**
1. Check server logs for errors
2. The app works in **mock mode** without Gmail credentials
3. If using real Gmail, ensure credentials are correct in `.env`
4. Check browser console (F12) for JavaScript errors

### Issue: Calendar errors

**Solution:**
- Calendar works in mock mode by default
- Check that `/voice-agent/calendar` endpoint returns data
- Visit http://localhost:8000/docs to test API directly

### Issue: Port 8000 already in use

**Solution:**
```bash
# Windows: Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Or use a different port
PORT=8080 python server.py
```

## 📊 Features Breakdown

### Email Detection Algorithm
- **Scoring System** for human vs automated detection
- **Personal Domain Recognition** (Gmail, Yahoo, etc.)
- **Reply/Forward Pattern Analysis**
- **Conversation Indicators** (greetings, questions, requests)
- **Automated Pattern Recognition** (newsletters, notifications)

### Thread Grouping
- Groups emails by participants + subject
- Removes Re:/Fwd: prefixes for accurate grouping
- Tracks message count and unread status
- Prioritizes threads with >2 messages
- Special handling for job applications

### Calendar Auto-Detection
- Scans email content for meeting keywords
- Extracts time and date patterns
- Creates calendar events automatically
- No authorization required (as requested)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with FastAPI, LangChain, and LangGraph
- Uses Gmail and Google Calendar APIs
- AI-powered by Euron API / OpenAI / Anthropic Claude
- Frontend styled with Tailwind CSS

---

## 🆘 Need Help?

- **Issues:** https://github.com/pbulbule13/talk2myinbox/issues
- **Documentation:** Check the `/docs` endpoint when server is running
- **API Testing:** Use http://localhost:8000/docs for interactive API testing

**Made with ❤️ and AI assistance**
