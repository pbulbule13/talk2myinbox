# Voice Modes Testing Checklist

Use this checklist to verify all three voice modes are working correctly.

---

## Pre-Testing Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Ensure `.env` contains:
```bash
# Required for all modes
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
# OR
GOOGLE_API_KEY=your_key_here

# Required for Semi-Voice and Full-Voice modes
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Optional - for demo mode without Gmail
EMAIL_MOCK_MODE=true
CALENDAR_MOCK_MODE=true
```

### 3. Start Server
```bash
cd backend
python server.py
```

Expected output:
```
========================================
Communications App Server Starting
========================================
Server: http://0.0.0.0:8000
API Docs: http://0.0.0.0:8000/docs
Health: http://0.0.0.0:8000/health
========================================
```

### 4. Open Browser
Navigate to: http://localhost:8000

---

## Test Suite

### ✅ Text Mode Testing

#### Test 1.1: Basic Text Query
- [ ] Click "⌨️ Text" mode button
- [ ] Type in input: "What emails do I have?"
- [ ] Click "Send" or press Enter
- [ ] Verify: Response appears in chat area
- [ ] Verify: No audio plays
- [ ] Verify: Status shows "Response received"

#### Test 1.2: Email Query
- [ ] Type: "Show me unread emails"
- [ ] Verify: Email list updates (if Gmail connected)
- [ ] Verify: Chat shows user query and AI response

#### Test 1.3: Calendar Query
- [ ] Type: "What's on my calendar today?"
- [ ] Verify: Calendar events appear in response
- [ ] Verify: Calendar widget updates

#### Test 1.4: Error Handling
- [ ] Type empty query and click Send
- [ ] Verify: Error message "Please enter a query"
- [ ] Type invalid query: "asdfghjkl"
- [ ] Verify: AI responds appropriately

---

### ✅ Semi-Voice Mode Testing

#### Test 2.1: Mode Switch
- [ ] Click "🔊 Semi-Voice" button
- [ ] Verify: Button highlights (blue background)
- [ ] Verify: Text input still visible
- [ ] Verify: Placeholder says "Type your query (response will be spoken)..."

#### Test 2.2: Text Input with Audio Output
- [ ] Type: "Read my inbox summary"
- [ ] Click Send
- [ ] Verify: Text response appears in chat
- [ ] Verify: Status shows "Generating speech..."
- [ ] Verify: Audio plays automatically
- [ ] Verify: Status shows "Playing response..." with 🔊
- [ ] Verify: "🔊 Stop" button appears

#### Test 2.3: Audio Controls
- [ ] Send another query
- [ ] Click "🔊 Stop" while audio playing
- [ ] Verify: Audio stops immediately
- [ ] Verify: Status updates

#### Test 2.4: Multiple Queries
- [ ] Type: "What emails are urgent?"
- [ ] Wait for response to finish
- [ ] Type: "Check my calendar"
- [ ] Verify: Both responses play sequentially
- [ ] Verify: Chat history shows all queries

#### Test 2.5: ElevenLabs Error Handling
- [ ] Temporarily use invalid ElevenLabs API key
- [ ] Send query
- [ ] Verify: Text response still shows
- [ ] Verify: Error message about TTS failure
- [ ] Restore valid API key

---

### ✅ Full-Voice Mode Testing

#### Test 3.1: Mode Switch
- [ ] Click "🎤 Full-Voice" button
- [ ] Verify: Text input hides
- [ ] Verify: "🎤 Speak" button appears
- [ ] Verify: Instructions update

#### Test 3.2: Browser Permissions
- [ ] Click "🎤 Speak" button
- [ ] Verify: Browser prompts for microphone access
- [ ] Click "Allow"
- [ ] Verify: Button changes to "⏹️ Stop"
- [ ] Verify: Status shows "Listening... Speak now"

#### Test 3.3: Voice Recognition
- [ ] Click "🎤 Speak"
- [ ] Speak clearly: "Show me my emails"
- [ ] Wait for recognition
- [ ] Verify: Transcript appears in chat
- [ ] Verify: Status shows "Processing query..."
- [ ] Verify: AI responds with voice + text
- [ ] Verify: Audio plays automatically

#### Test 3.4: Stop Recording
- [ ] Click "🎤 Speak"
- [ ] Start speaking
- [ ] Click "⏹️ Stop" before finishing
- [ ] Verify: Recording stops
- [ ] Verify: Partial transcript processed (if any)

#### Test 3.5: Multiple Voice Queries
- [ ] Ask: "What meetings do I have tomorrow?"
- [ ] Wait for complete response
- [ ] Ask: "Show urgent emails"
- [ ] Verify: Both handled correctly
- [ ] Verify: Chat history intact

#### Test 3.6: Speech Recognition Errors
- [ ] Click "🎤 Speak"
- [ ] Don't say anything for 5 seconds
- [ ] Verify: Error "No speech detected"
- [ ] Try again with background noise
- [ ] Verify: Recognition still works or shows helpful error

#### Test 3.7: Browser Compatibility
**Chrome/Edge:**
- [ ] Full-Voice mode works
- [ ] Recognition accurate

**Safari:**
- [ ] Full-Voice mode works (may have limitations)
- [ ] Test on macOS/iOS if available

**Firefox:**
- [ ] Check if Web Speech API supported
- [ ] If not, verify helpful error message

---

### ✅ UI/UX Testing

#### Test 4.1: Mode Switching
- [ ] Switch from Text → Semi-Voice
- [ ] Verify smooth transition
- [ ] Switch from Semi-Voice → Full-Voice
- [ ] Verify UI updates correctly
- [ ] Switch back to Text
- [ ] Verify all elements reset

#### Test 4.2: Chat History
- [ ] Send 5+ queries in any mode
- [ ] Verify: All appear in chat area
- [ ] Verify: Scrollbar appears when needed
- [ ] Verify: Auto-scrolls to latest message
- [ ] Click "Clear Chat"
- [ ] Verify: Chat clears completely

#### Test 4.3: Visual Feedback
- [ ] Test each status type:
  - [ ] Info (blue ℹ️)
  - [ ] Success (green ✓)
  - [ ] Error (red ⚠️)
  - [ ] Loading (gray ⟳)
  - [ ] Recording (red 🎤)
  - [ ] Playing (purple 🔊)

#### Test 4.4: Responsive Design
- [ ] Resize browser window
- [ ] Verify: Voice panel adapts
- [ ] Test on mobile device (if available)
- [ ] Verify: All modes accessible

---

### ✅ Integration Testing

#### Test 5.1: Email Integration
- [ ] Use voice mode to query: "Show recent emails"
- [ ] Verify: Email list in main panel updates
- [ ] Click on an email
- [ ] Verify: Details modal opens

#### Test 5.2: Calendar Integration
- [ ] Ask: "What's my schedule today?"
- [ ] Verify: Calendar widget updates
- [ ] Verify: Events listed correctly

#### Test 5.3: Draft Generation
- [ ] Ask: "Draft a reply to the latest email"
- [ ] Verify: Draft appears in "Pending Drafts"
- [ ] Verify: Can view and edit draft
- [ ] Verify: Can approve or reject

#### Test 5.4: Human Escalation
- [ ] Ask: "I need human help with this email"
- [ ] Verify: Escalation modal appears
- [ ] Verify: Can add notes
- [ ] Verify: Submission works

---

### ✅ Performance Testing

#### Test 6.1: Response Times
- [ ] Send text query
- [ ] Time: Should respond in < 5 seconds
- [ ] Send voice query (Full-Voice)
- [ ] Time: Total (recognition + processing + TTS) < 15 seconds

#### Test 6.2: Audio Quality
- [ ] Test TTS with long response (200+ words)
- [ ] Verify: Audio quality consistent
- [ ] Verify: No cutoffs or stuttering
- [ ] Verify: Natural-sounding voice

#### Test 6.3: Concurrent Operations
- [ ] Start voice query
- [ ] While AI responding, try clicking email
- [ ] Verify: No conflicts
- [ ] Verify: Both operations complete

---

### ✅ Error Handling Testing

#### Test 7.1: Network Errors
- [ ] Disconnect internet
- [ ] Try sending query
- [ ] Verify: Helpful error message
- [ ] Reconnect
- [ ] Verify: Works again

#### Test 7.2: API Errors
- [ ] Use invalid LLM API key
- [ ] Send query
- [ ] Verify: Error displayed clearly
- [ ] Restore valid key

#### Test 7.3: Microphone Errors
- [ ] Deny microphone permission
- [ ] Try Full-Voice mode
- [ ] Verify: Error "Microphone access denied"
- [ ] Verify: Suggestion to allow access

---

## Test Results Summary

### Pass Criteria
- [ ] All three modes functional
- [ ] Mode switching smooth
- [ ] Text queries work correctly
- [ ] Audio playback works in Semi/Full-Voice
- [ ] Voice recognition works in Full-Voice
- [ ] UI feedback clear and helpful
- [ ] Error handling graceful
- [ ] Integration with email/calendar works
- [ ] Performance acceptable
- [ ] Documentation accurate

### Known Issues
Document any issues found:

1. Issue:
   - Severity:
   - Workaround:

2. Issue:
   - Severity:
   - Workaround:

### Browser Compatibility
- [ ] Chrome/Edge: ✅ Fully supported
- [ ] Safari: ✅ Works with minor limitations
- [ ] Firefox: ⚠️ Limited (no Web Speech API)
- [ ] Mobile Chrome: ✅ Works
- [ ] Mobile Safari: ⚠️ Limited voice support

---

## Production Readiness Checklist

Before deploying:

### Security
- [ ] API keys not exposed in frontend
- [ ] CORS configured properly
- [ ] OAuth tokens stored securely
- [ ] HTTPS enabled in production

### Performance
- [ ] Audio files cached appropriately
- [ ] Rate limiting implemented
- [ ] Error logging configured
- [ ] Monitoring set up

### Documentation
- [ ] README updated
- [ ] Voice guide complete
- [ ] API docs accurate
- [ ] User instructions clear

### User Experience
- [ ] Loading states clear
- [ ] Error messages helpful
- [ ] Instructions visible
- [ ] Feedback immediate

---

## Quick Test Commands

Test queries to use:

**Email:**
- "Show me unread emails"
- "What emails did I get today?"
- "Search for emails from recruiters"
- "Show urgent work emails"

**Calendar:**
- "What's on my calendar today?"
- "Do I have meetings tomorrow?"
- "Show next week's schedule"

**Actions:**
- "Draft a reply to the latest email"
- "Mark all as read"
- "Archive promotional emails"

**Combined:**
- "Check my emails and calendar for tomorrow"
- "What do I need to do today?"

---

## Testing Complete! 🎉

Date Tested: _________________

Tester: _________________

Build Version: 1.0.0

Status: ⬜ Pass | ⬜ Pass with Issues | ⬜ Fail

Notes:
______________________________________
______________________________________
______________________________________
