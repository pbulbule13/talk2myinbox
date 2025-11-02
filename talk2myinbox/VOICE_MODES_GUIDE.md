# Voice Interaction Modes Guide

Your **talk2myinbox** application now supports three distinct interaction modes for managing your emails and calendar through voice and text.

---

## 🎯 Three Interaction Modes

### 1. **Text Mode** ⌨️

**How it works:**
- Type your query in the text input
- Click "Send" or press Enter
- Receive text response
- No audio involved

**Best for:**
- Quiet environments
- Quick queries
- When you prefer reading
- Desktop/mobile text interaction

**Example queries:**
```
"Show me unread emails"
"What meetings do I have today?"
"Draft a reply to John's email about the project"
"Search for emails from recruiters"
```

---

### 2. **Semi-Voice Mode** 🔊

**How it works:**
- Type your query (same as Text Mode)
- AI processes the request
- **Response is spoken aloud via ElevenLabs TTS**
- Also displayed as text

**Best for:**
- Multitasking (hear responses while doing other work)
- Accessibility
- Hands-busy situations
- Learning/improving listening comprehension

**Requirements:**
- ElevenLabs API key in `.env`
- Working speakers/headphones
- Internet connection

**Controls:**
- Click "🔊 Stop" to stop audio playback
- Responses also appear in chat history

---

### 3. **Full-Voice Mode** 🎤

**How it works:**
- Click the "🎤 Speak" button
- **Speak your query** into the microphone
- Speech converted to text (Web Speech API)
- AI processes the request
- **Response is spoken back to you**
- Completely hands-free!

**Best for:**
- Driving/commuting
- Hands-free operation
- Voice-first workflows
- Accessibility needs

**Requirements:**
- Microphone access (browser will prompt)
- ElevenLabs API key for TTS
- Chrome, Edge, or Safari browser (Web Speech API support)
- Internet connection

**How to use:**
1. Click "🎤 Speak" button
2. Allow microphone access when prompted
3. Speak clearly: *"Show me urgent emails"*
4. Button changes to "⏹️ Stop" while listening
5. Speech is transcribed and displayed
6. AI responds with voice + text

**Tips:**
- Speak naturally at normal pace
- Use clear pronunciation
- Wait for beep/indicator before speaking
- Click stop to end recording early

---

## 🔧 Setup Instructions

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure ElevenLabs (for voice modes):**

   Add to your `.env` file:
   ```bash
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Optional: use default voice
   ```

   Get your API key: https://elevenlabs.io/

3. **Browser requirements for Full-Voice:**
   - **Recommended:** Google Chrome, Microsoft Edge, Safari
   - **Required:** Microphone access permission
   - **Note:** Web Speech API may not work in Firefox or older browsers

---

## 🎬 Getting Started

### Quick Start

1. **Start the server:**
   ```bash
   cd backend
   python server.py
   ```

2. **Open browser:**
   Navigate to http://localhost:8000

3. **Choose your mode:**
   - Click **⌨️ Text** for text-only
   - Click **🔊 Semi-Voice** for typed input + spoken output
   - Click **🎤 Full-Voice** for complete voice interaction

4. **Try it out:**

   **Text Mode:**
   - Type: "What emails do I have?"
   - Read the response

   **Semi-Voice Mode:**
   - Type: "Read my calendar for tomorrow"
   - Hear the AI speak the response

   **Full-Voice Mode:**
   - Click 🎤 Speak
   - Say: "Show me emails from this week"
   - Hear the AI respond

---

## 📊 Features Comparison

| Feature | Text Mode | Semi-Voice | Full-Voice |
|---------|-----------|------------|------------|
| Input Method | Keyboard | Keyboard | Microphone |
| Output Method | Text only | Text + Audio | Text + Audio |
| Hands-free | ❌ | ⚠️ Partial | ✅ Yes |
| Requires ElevenLabs | ❌ | ✅ | ✅ |
| Requires Microphone | ❌ | ❌ | ✅ |
| Browser Requirements | Any | Any | Chrome/Edge/Safari |
| Internet Required | ✅ | ✅ | ✅ |
| Best for | Desktop work | Multitasking | Hands-free |

---

## 🎤 Voice Commands Examples

### Email Management
```
"Show me unread emails"
"Search for emails from recruiters"
"What emails did I receive today?"
"Show urgent emails"
"Display emails about the project"
```

### Calendar Queries
```
"What's on my calendar today?"
"Do I have any meetings tomorrow?"
"Show me next week's schedule"
"What time is my next meeting?"
```

### Email Actions
```
"Draft a reply to Sarah's email"
"Mark John's email as read"
"Archive promotional emails"
"Delete spam emails"
```

### Combinations
```
"Check my emails and calendar for tomorrow"
"Show me unread work emails and today's meetings"
```

---

## 🔍 Troubleshooting

### Semi-Voice Mode Issues

**Problem:** No audio playback
- ✅ Check ElevenLabs API key in `.env`
- ✅ Verify speakers/headphones are working
- ✅ Check browser console for errors
- ✅ Try refreshing the page

**Problem:** Audio cuts off
- ✅ Check internet connection
- ✅ ElevenLabs API rate limits
- ✅ Try shorter queries

### Full-Voice Mode Issues

**Problem:** Microphone not working
- ✅ Allow microphone access in browser
- ✅ Check browser permissions (chrome://settings/content/microphone)
- ✅ Test microphone in system settings
- ✅ Use Chrome or Edge (best support)

**Problem:** Speech not recognized
- ✅ Speak clearly and at normal pace
- ✅ Reduce background noise
- ✅ Check microphone is not muted
- ✅ Try rephrasing your query

**Problem:** "Speech recognition not supported"
- ✅ Switch to Chrome, Edge, or Safari
- ✅ Update browser to latest version
- ✅ Use Semi-Voice mode as alternative

### General Issues

**Problem:** "STT endpoint requires Whisper"
- ℹ️ This is expected - use browser's Web Speech API instead
- ℹ️ Full-Voice mode works without backend STT
- ℹ️ To enable backend STT, uncomment Whisper in requirements.txt

**Problem:** Lag or slow responses
- ✅ Check internet connection speed
- ✅ API rate limits (OpenAI/Anthropic/ElevenLabs)
- ✅ Try simpler queries
- ✅ Check server logs for errors

---

## 🎨 UI Indicators

### Status Messages
- **ℹ️ Blue:** Information/instructions
- **✓ Green:** Success
- **⚠️ Red:** Error or warning
- **⟳ Gray:** Loading/processing
- **🎤 Red:** Recording in progress
- **🔊 Purple:** Audio playing

### Visual Cues
- **Microphone button pulses:** Currently recording
- **Button changes to "Stop":** Active recording
- **Chat bubbles:**
  - Blue (right): Your queries
  - Gray (left): AI responses
  - Red: Error messages

---

## 🔐 Privacy & Security

### Voice Data
- **Full-Voice Mode:** Audio processed by browser's Web Speech API (Chrome/Google)
- **Semi-Voice Mode:** Text sent to ElevenLabs for speech synthesis
- **Data retention:** Check ElevenLabs and Google privacy policies
- **Local processing:** Speech recognition happens in browser when possible

### Best Practices
- Use in private environments for sensitive information
- Review AI-generated email drafts before sending
- Don't share API keys or credentials
- Clear chat history after sensitive queries

---

## 🚀 Advanced Configuration

### Custom Voice (ElevenLabs)

1. Go to https://elevenlabs.io/voice-library
2. Choose or clone a voice
3. Copy the Voice ID
4. Update `.env`:
   ```bash
   ELEVENLABS_VOICE_ID=your_custom_voice_id
   ```

### Whisper Backend (Optional)

For offline STT or better accuracy:

1. Uncomment in `requirements.txt`:
   ```bash
   openai-whisper>=20231117
   ```

2. Install dependencies:
   ```bash
   pip install openai-whisper
   ```

3. Update `routes.py` to enable Whisper endpoint (code already included, just uncomment)

**Note:** Whisper models are large downloads (140MB - 3GB)

---

## 📱 Mobile Support

### Text Mode
- ✅ Fully supported on mobile browsers

### Semi-Voice Mode
- ✅ Works on iOS Safari and Android Chrome
- ⚠️ May require headphones for best experience

### Full-Voice Mode
- ⚠️ Limited support on mobile browsers
- ✅ Works on Chrome Android (requires permissions)
- ⚠️ iOS Safari has limited Web Speech API support
- 💡 **Recommendation:** Use Semi-Voice mode on mobile

---

## 💡 Tips for Best Experience

### General
1. **Start with Text Mode** to test queries
2. **Use natural language** - no special syntax needed
3. **Be specific** - "Show urgent work emails" vs "Show emails"
4. **Check chat history** to review past queries

### Voice Modes
1. **Quiet environment** - reduces recognition errors
2. **Clear pronunciation** - speak at normal conversational pace
3. **Wait for prompt** - ensure recording started before speaking
4. **Shorter queries** - easier for AI to process accurately
5. **Use headphones** - prevents audio feedback in Full-Voice mode

### Productivity
1. **Keyboard shortcuts:** Press Enter to send in Text/Semi-Voice
2. **Clear chat regularly** to improve readability
3. **Combine with email view** - voice queries update email list
4. **Test voice in private** before using in shared spaces

---

## 🆘 Getting Help

### In-App Help
- Click the **👤 Contact Human** button for manual support
- Use **"Escalate to Human"** on any email for expert review

### Documentation
- Main README: `README.md`
- Quick Start: `QUICKSTART.md`
- This guide: `VOICE_MODES_GUIDE.md`

### Common Resources
- ElevenLabs Docs: https://docs.elevenlabs.io
- Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- FastAPI Docs: https://fastapi.tiangolo.com

---

## 🎉 Enjoy Your Voice-Enabled Inbox!

Your **talk2myinbox** is now fully voice-enabled. Choose the mode that fits your workflow and start managing your inbox hands-free!

**Happy voice commanding! 🎤📧**
