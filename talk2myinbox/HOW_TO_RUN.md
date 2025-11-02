# 🚀 How to Run talk2myinbox

**Complete step-by-step guide to run your AI-powered email & calendar app**

---

## 📋 Prerequisites

Before running the app, ensure you have:

- ✅ Python 3.9+ installed
- ✅ Git installed (if cloning)
- ✅ Internet connection
- ✅ API keys (or use mock mode for testing)

---

## ⚡ Quick Start (5 Minutes)

### Option 1: Run in Demo Mode (No API Keys Required)

```bash
# 1. Navigate to project
cd talk2myinbox

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env - Set mock mode to true
# Open .env and change:
EMAIL_MOCK_MODE=true
CALENDAR_MOCK_MODE=true

# 5. Run the server
cd backend
python server.py

# 6. Open browser
# Go to: http://localhost:8000
```

### Option 2: Run with Real APIs

```bash
# 1-3. Same as above

# 4. Add your API keys to .env
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here

ELEVENLABS_API_KEY=your_key_here  # For voice features

EMAIL_MOCK_MODE=false
CALENDAR_MOCK_MODE=false

# 5-6. Same as above
```

---

## 🔧 Detailed Setup Instructions

### Step 1: Check Python Version

```bash
python --version
# Should show: Python 3.9.0 or higher
```

If not installed, download from: https://www.python.org/downloads/

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# This installs:
# - FastAPI (web framework)
# - LangChain (AI orchestration)
# - Google API clients (Gmail, Calendar)
# - ElevenLabs (text-to-speech)
# - And more...
```

Expected output:
```
Installing collected packages: fastapi, uvicorn, langgraph...
Successfully installed fastapi-0.115.0 uvicorn-0.30.0 ...
```

### Step 4: Configure Environment Variables

```bash
# Copy the template
cp .env.example .env

# Open .env in your editor
# Windows:
notepad .env

# macOS/Linux:
nano .env
# or
code .env  # if using VS Code
```

**Minimum Configuration (Demo Mode):**
```env
# Server
HOST=0.0.0.0
PORT=8000

# Mock mode (no API keys needed)
EMAIL_MOCK_MODE=true
CALENDAR_MOCK_MODE=true

# Add at least one LLM key (or use mock)
OPENAI_API_KEY=test_key
```

**Full Configuration (Production):**
```env
# LLM Provider (choose one)
OPENAI_API_KEY=sk-proj-your-key-here

# Voice (optional)
ELEVENLABS_API_KEY=your-key-here

# Email & Calendar (optional, use mock mode if not set)
EMAIL_MOCK_MODE=false
CALENDAR_MOCK_MODE=false
```

### Step 5: Get API Keys (If Using Real Services)

#### OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-`)
5. Paste in `.env`: `OPENAI_API_KEY=sk-proj-...`

#### Anthropic API Key (Alternative)
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Create API key
4. Paste in `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

#### ElevenLabs API Key (For Voice Features)
1. Go to: https://elevenlabs.io/
2. Sign up or log in
3. Get your API key
4. Paste in `.env`: `ELEVENLABS_API_KEY=...`

#### Gmail API Setup (Optional)
1. Go to: https://console.cloud.google.com/
2. Create a new project
3. Enable Gmail API and Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON
6. Save as: `config/gmail_credentials.json`

**OR** use mock mode: `EMAIL_MOCK_MODE=true`

### Step 6: Run the Server

```bash
# Navigate to backend directory
cd backend

# Run the server
python server.py
```

**Expected Output:**
```
========================================
Communications App Server Starting
========================================
Server: http://0.0.0.0:8000
API Docs: http://0.0.0.0:8000/docs
Health: http://0.0.0.0:8000/health
========================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 7: Open the Application

Open your web browser and go to:

```
http://localhost:8000
```

---

## 🖥️ What You'll See

### 1. Voice Interaction Panel (Top)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎙️ AI Voice Assistant                                           │
│ Manage your inbox with text, semi-voice, or full-voice         │
│                                                                 │
│ [⌨️ Text] [🔊 Semi-Voice] [🎤 Full-Voice]                       │
│                                                                 │
│ ┌───────────────────────────────────────────────┐ [Send →]    │
│ │ Type your query here...                       │             │
│ └───────────────────────────────────────────────┘             │
│                                                                 │
│ ℹ️ Type your query and click Send                              │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ Chat history appears here...                            │   │
│ └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Text Mode**: Type queries, read responses
- **Semi-Voice Mode**: Type queries, hear AI speak responses
- **Full-Voice Mode**: Speak queries, hear responses (hands-free!)

### 2. Email Categories (Left Column)

```
┌─────────────────────────────────┐
│ 📂 Categories                   │
│                                 │
│ [All 25] [🚨Urgent 3]          │
│ [💼Work 15] [👤Personal 5]     │
│ [🎁Promo 2] [👥Social 0]       │
└─────────────────────────────────┘
```

### 3. Inbox List (Left Column)

```
┌─────────────────────────────────┐
│ 📨 Inbox                        │
│ Connected to Gmail ✓            │
├─────────────────────────────────┤
│ 🚨 sender@company.com           │
│ Urgent: Project Deadline        │
│ Need your review by EOD...      │
│ [Unread] [Urgent]          2h   │
├─────────────────────────────────┤
│ 💼 client@business.com          │
│ Meeting Tomorrow                │
│ Confirming our 2pm meeting...   │
│ [Work]                     5h   │
├─────────────────────────────────┤
│ 👤 friend@personal.com          │
│ Dinner this weekend?            │
│ Are you free on Saturday...     │
│ [Personal]              Yesterday│
└─────────────────────────────────┘
```

### 4. Pending Drafts (Middle Column)

```
┌─────────────────────────────────┐
│ ✍️ Pending Drafts               │
│ AI Generated                    │
├─────────────────────────────────┤
│ To: client@business.com         │
│ Re: Meeting Tomorrow            │
│ Thank you for confirming...     │
│ [Pending]                       │
│ [View & Edit] [✓ Approve]      │
│ [✗ Reject]                      │
├─────────────────────────────────┤
│ To: sender@company.com          │
│ Re: Project Deadline            │
│ I've reviewed the documents...  │
│ [Pending]                       │
│ [View & Edit] [✓ Approve]      │
│ [✗ Reject]                      │
└─────────────────────────────────┘
```

### 5. Calendar Widget (Middle Column)

```
┌─────────────────────────────────┐
│ 📅 Today's Calendar             │
│ [This Week ▼]                   │
├─────────────────────────────────┤
│ 10:00 AM  Team Standup          │
│           Conference Room A     │
├─────────────────────────────────┤
│ 02:00 PM  Client Meeting        │
│           Zoom                  │
├─────────────────────────────────┤
│ 04:30 PM  Project Review        │
│           Building B            │
└─────────────────────────────────┘
```

### 6. AI Status & Actions (Right Column)

```
┌─────────────────────────────────┐
│ 🤖 AI Assistant Status          │
├─────────────────────────────────┤
│ Gmail:          ✓ Connected     │
│ Voice Agent:    ✓ Active        │
│ Calendar:       ✓ Synced        │
│ Drafts Pending: 2               │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ ⚡ Quick Actions                │
├─────────────────────────────────┤
│ [🔄 Refresh Inbox]              │
│ [✍️ Compose New]                │
│ [👤 Get Human Help]             │
│ [🤖 Auto-Draft Replies]         │
└─────────────────────────────────┘
```

---

## 🎯 How to Use

### Example 1: Text Mode Query

**Step 1:** Click **⌨️ Text** mode

**Step 2:** Type in the input box:
```
Show me my unread emails
```

**Step 3:** Click **Send →**

**What Happens:**
```
┌─────────────────────────────────┐
│ You:                            │
│ Show me my unread emails        │
│                                 │
│ AI Assistant:                   │
│ You have 5 unread emails:       │
│ 1. Urgent: Project Deadline     │
│ 2. Meeting Tomorrow             │
│ 3. Weekly Report Due            │
│ 4. Team Update                  │
│ 5. New Feature Request          │
└─────────────────────────────────┘
```

The email list on the left updates to show only unread emails.

### Example 2: Semi-Voice Mode

**Step 1:** Click **🔊 Semi-Voice** mode

**Step 2:** Type:
```
What's on my calendar today?
```

**Step 3:** Click **Send →**

**What Happens:**
1. Text response appears in chat
2. AI voice speaks the response aloud: 🔊
   *"You have 3 meetings today. At 10 AM you have Team Standup..."*
3. Calendar widget highlights today's events

### Example 3: Full-Voice Mode

**Step 1:** Click **🎤 Full-Voice** mode

**Step 2:** Click **🎤 Speak** button

**Step 3:** Speak into microphone:
```
"Draft a reply to the latest email"
```

**What Happens:**
1. Your speech is transcribed
2. AI processes the request
3. Draft appears in "Pending Drafts"
4. AI speaks: 🔊 *"I've drafted a reply for you. Would you like to review it?"*

### Example 4: Approve Draft

**Step 1:** Click **[View & Edit]** on a draft

**Step 2:** Review the draft:
```
┌─────────────────────────────────────┐
│ Review Draft Email                  │
├─────────────────────────────────────┤
│ To: client@business.com             │
│ Subject: Re: Meeting Tomorrow       │
│                                     │
│ Body:                               │
│ ┌─────────────────────────────────┐ │
│ │ Thank you for confirming our    │ │
│ │ meeting tomorrow at 2 PM. I've  │ │
│ │ prepared the agenda and will    │ │
│ │ send it shortly.                │ │
│ │                                 │ │
│ │ Looking forward to our          │ │
│ │ discussion.                     │ │
│ │                                 │ │
│ │ Best regards                    │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [✓ Approve & Send] [👤 Send to     │
│  Human Review] [✗ Reject]          │
└─────────────────────────────────────┘
```

**Step 3:** Click **[✓ Approve & Send]**

**Step 4:** Confirm: "Send email to client@business.com?"

**Result:** ✅ Email sent successfully!

---

## 🎨 Visual Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│                        🎙️ AI VOICE ASSISTANT                           │
│  [⌨️ Text] [🔊 Semi-Voice] [🎤 Full-Voice]                             │
│  ┌────────────────────────────────────┐ [Send]                        │
│  │ Type or speak your query...        │                               │
│  └────────────────────────────────────┘                               │
│  💬 Chat History:                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ User: Show my emails                                           │  │
│  │ AI: You have 25 emails. 3 urgent, 15 work-related...          │  │
│  └────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────┬──────────────────────┬────────────────────────────┐
│  📂 CATEGORIES  │   ✍️ PENDING DRAFTS  │    🤖 AI STATUS & ACTIONS │
│                 │                      │                            │
│ All     [25]    │ Draft #1             │ Gmail:     ✓ Connected    │
│ Urgent   [3]    │ To: client@...       │ Agent:     ✓ Active       │
│ Work    [15]    │ Re: Meeting          │ Calendar:  ✓ Synced       │
│ Personal [5]    │ [View] [Approve]     │ Drafts:    2 pending      │
│ Promo    [2]    │                      │                            │
│                 │ Draft #2             │ ⚡ QUICK ACTIONS          │
├─────────────────┤ To: sender@...       │ [🔄 Refresh]             │
│  📨 INBOX       │ Re: Project          │ [✍️ Compose]             │
│  Connected ✓    │ [View] [Approve]     │ [👤 Human Help]          │
├─────────────────┤                      │ [🤖 Auto-Draft]          │
│ 🚨 sender@...   │ ─────────────────    │                            │
│ Urgent Project  │ 📅 CALENDAR          │ 👤 HUMAN SUPPORT         │
│ Need review...  │ [This Week ▼]        │                            │
│ [Unread] 2h     │                      │ Response: 2-4 hours       │
├─────────────────┤ 10:00 Team Meeting   │ Available: 24/7           │
│ 💼 client@...   │ 14:00 Client Call    │ Expert Review Team        │
│ Meeting         │ 16:30 Project Review │                            │
│ Confirming...   │                      │                            │
│ [Work] 5h       │                      │                            │
├─────────────────┤                      │                            │
│ 👤 friend@...   │                      │                            │
│ Dinner weekend? │                      │                            │
│ Are you free... │                      │                            │
│ [Personal] 1d   │                      │                            │
└─────────────────┴──────────────────────┴────────────────────────────┘
```

---

## 🎬 Common Use Cases

### Use Case 1: Check Emails
```
1. Type: "Show me my emails from today"
2. Email list updates
3. Click on any email to read full content
```

### Use Case 2: Draft Response
```
1. Type: "Draft a thank you reply to John's email"
2. AI generates draft
3. Review in Pending Drafts
4. Click [Approve & Send]
```

### Use Case 3: Check Calendar
```
1. Type: "What meetings do I have tomorrow?"
2. Calendar widget updates
3. AI lists all meetings
```

### Use Case 4: Voice Search
```
1. Switch to Full-Voice mode
2. Click microphone
3. Say: "Show urgent emails from this week"
4. Listen to AI response
```

### Use Case 5: Human Escalation
```
1. Open complex email
2. Click [Escalate to Human]
3. Add notes for human reviewer
4. Submit for expert review
```

---

## 🔧 Troubleshooting

### Server Won't Start

**Problem:** `python server.py` fails

**Solutions:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt

# Check for port conflicts
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux
```

### Can't Access http://localhost:8000

**Problem:** Browser shows "Can't reach this page"

**Solutions:**
1. Check if server is running (look for "Uvicorn running" message)
2. Try http://127.0.0.1:8000 instead
3. Check firewall settings
4. Change port in .env: `PORT=8001`

### Voice Features Not Working

**Problem:** No audio in Semi-Voice/Full-Voice modes

**Solutions:**
1. Check `ELEVENLABS_API_KEY` in .env
2. Test with Text mode first
3. Check browser console for errors (F12)
4. Allow microphone permission in browser
5. Use Chrome or Edge (best support)

### Email/Calendar Not Loading

**Problem:** Shows "Error loading emails"

**Solutions:**
1. Set `EMAIL_MOCK_MODE=true` in .env for testing
2. Check Gmail credentials in `config/`
3. Verify API keys are correct
4. Check internet connection
5. View browser console (F12) for detailed errors

### Imports Failing

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall all dependencies
pip install -r requirements.txt

# Check pip version
pip --version

# Upgrade pip
python -m pip install --upgrade pip
```

---

## 📊 System Requirements

### Minimum Requirements
- **OS:** Windows 10, macOS 10.15, Ubuntu 20.04
- **Python:** 3.9 or higher
- **RAM:** 2 GB
- **Disk:** 500 MB free space
- **Browser:** Chrome 90+, Edge 90+, Safari 14+

### Recommended
- **Python:** 3.10 or 3.11
- **RAM:** 4 GB
- **Internet:** Broadband connection
- **Browser:** Latest Chrome or Edge

---

## 🚀 Performance Tips

1. **Use virtual environment** to avoid conflicts
2. **Close unused applications** to free memory
3. **Use Text mode** for fastest responses
4. **Enable mock mode** when testing (no API calls)
5. **Clear browser cache** if UI seems slow

---

## 📱 Access from Phone

### On Same Network:

1. Find your computer's IP:
   ```bash
   # Windows
   ipconfig
   # Look for IPv4 Address: 192.168.x.x

   # Mac/Linux
   ifconfig
   # Look for inet: 192.168.x.x
   ```

2. On phone, open browser and go to:
   ```
   http://192.168.x.x:8000
   ```

3. Features:
   - ✅ Text mode works great
   - ✅ Semi-voice mode works
   - ⚠️ Full-voice limited on mobile

---

## 🎯 Quick Reference

### Start Server
```bash
cd backend && python server.py
```

### Stop Server
```
Press CTRL+C in terminal
```

### Restart Server
```bash
# CTRL+C to stop
# Then run again:
python server.py
```

### View Logs
```bash
# Logs appear in terminal
# Or check: backend/logs/
```

### Run Tests
```bash
make test
# or
cd backend && pytest tests/
```

---

## ✅ Success Checklist

Server is running when you see:
- [x] "Application startup complete"
- [x] "Uvicorn running on http://0.0.0.0:8000"
- [x] No error messages in terminal

Browser is working when you see:
- [x] Voice interaction panel loads
- [x] Email categories visible
- [x] Calendar widget appears
- [x] Can type in text box

Ready to use when:
- [x] Server running (check above)
- [x] Browser loaded (check above)
- [x] Can send a test query
- [x] AI responds in chat

---

**You're all set! Your AI-powered inbox is ready! 🎉**

Try your first query:
- Type: "Show me my emails"
- Click: Send →
- Watch the magic happen! ✨

