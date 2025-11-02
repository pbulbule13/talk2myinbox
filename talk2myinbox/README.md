# Communications App

A standalone email and calendar management application with AI-powered voice agent integration.

## Features

- 📧 **Email Management**: Connect to Gmail and manage your inbox
- 📅 **Calendar Integration**: View and manage Google Calendar events
- 🤖 **AI Assistant**: Smart email categorization and draft generation
- 🎙️ **Voice Interface**: Three interaction modes - Text, Semi-Voice, and Full-Voice
  - ⌨️ **Text Mode**: Type queries, read responses
  - 🔊 **Semi-Voice Mode**: Type queries, hear AI responses
  - 🎤 **Full-Voice Mode**: Speak queries, hear responses (hands-free!)
- 📝 **Draft Approval**: Review and approve AI-generated email responses
- 👤 **Human Escalation**: Escalate complex items for human review
- 🔐 **Secure OAuth**: Secure Gmail and Calendar authentication

## Project Structure

```
communications-app/
├── frontend/               # Frontend files
│   ├── index.html         # Main HTML page
│   ├── communications_enhanced.js  # Core JavaScript
│   └── communications_tab_enhanced.html  # Original tab component
├── backend/               # Backend API
│   ├── server.py         # FastAPI server
│   └── voice_agent/      # Voice agent system
│       ├── api/          # API routes
│       ├── adapters/     # Email/Calendar adapters
│       ├── agents/       # AI agents
│       ├── config/       # Configuration
│       ├── models/       # Data models
│       ├── utils/        # Utilities
│       └── orchestrator.py
├── config/               # Configuration files (created at runtime)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Prerequisites

- Python 3.10 or higher
- Gmail account with API access (optional for demo mode)
- Google Calendar API access (optional for demo mode)
- OpenAI/Anthropic/Google API key for LLM
- ElevenLabs API key (optional for voice features)

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# At minimum, you need one LLM API key (OpenAI, Anthropic, or Google)
```

### 3. Gmail Setup (Optional - can run in mock mode)

If you want to connect to real Gmail:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON and save as `config/gmail_credentials.json`
6. Run the app - it will prompt for OAuth authorization on first run

**OR** run in mock/demo mode by setting in `.env`:
```
EMAIL_MOCK_MODE=true
CALENDAR_MOCK_MODE=true
```

### 4. Run the Server

```bash
# Navigate to backend directory
cd backend

# Run the server
python server.py
```

The server will start on `http://localhost:8000`

### 5. Access the Application

Open your browser and navigate to:
- **App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Required**:
- At least one LLM API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)

**Optional**:
- Gmail/Calendar credentials (or use mock mode)
- ElevenLabs for voice features
- Custom port and host settings

### Mock Mode

For testing without real Gmail/Calendar access:

```bash
# In .env
EMAIL_MOCK_MODE=true
CALENDAR_MOCK_MODE=true
```

This will generate sample emails and calendar events for demo purposes.

## API Endpoints

### Voice Agent
- `POST /voice-agent/query` - Process natural language queries
- `GET /voice-agent/inbox/summary` - Get inbox summary
- `POST /voice-agent/email/send` - Send email
- `GET /voice-agent/emails` - Get email list
- `GET /voice-agent/emails/search` - Search emails
- `GET /voice-agent/calendar/events` - Get calendar events
- `POST /voice-agent/tts` - Text-to-speech conversion
- `WebSocket /voice-agent/ws` - Real-time voice interaction

### Application
- `GET /` - Main application page
- `GET /health` - Health check
- `GET /docs` - API documentation

## Voice Interaction Modes

The application supports three distinct interaction modes:

### ⌨️ Text Mode
- Type your queries in plain English
- Read AI responses as text
- Perfect for quiet environments

### 🔊 Semi-Voice Mode
- Type your queries
- AI responses are spoken aloud via ElevenLabs TTS
- Great for multitasking

### 🎤 Full-Voice Mode
- Speak your queries hands-free
- AI responds with voice + text
- Uses Web Speech API for recognition
- Completely hands-free operation

**See [VOICE_MODES_GUIDE.md](VOICE_MODES_GUIDE.md) for detailed instructions.**

## Features in Detail

### Email Categories

Emails are automatically categorized into:
- 🚨 **Urgent**: Time-sensitive emails
- 💼 **Work**: Professional correspondence
- 👤 **Personal**: Personal emails
- 🎁 **Promotions**: Marketing and offers
- 👥 **Social**: Social media notifications

### AI Draft Generation

The AI assistant can:
- Generate intelligent email responses
- Maintain context across conversations
- Suggest appropriate tone and content
- Require human approval before sending

### Human Escalation

When AI encounters complex scenarios:
- User can manually escalate any email
- Add notes for human reviewer
- Track escalation status
- Get expert human response

## Development

### Running in Development Mode

```bash
cd backend
python server.py
```

The server runs with hot-reload enabled by default.

### Testing

```bash
# Run tests
pytest backend/voice_agent/tests/

# Run with coverage
pytest --cov=voice_agent backend/voice_agent/tests/
```

### Project Dependencies

The project uses:
- **FastAPI**: Modern web framework
- **LangChain/LangGraph**: AI orchestration
- **Google APIs**: Gmail and Calendar integration
- **ElevenLabs**: Voice synthesis (optional)
- **Anthropic/OpenAI/Google**: LLM providers

## Troubleshooting

### Gmail Connection Issues

1. Check credentials file exists: `config/gmail_credentials.json`
2. Verify OAuth scopes include Gmail access
3. Try deleting `config/gmail_token.json` and re-authenticating
4. Use mock mode for testing: `EMAIL_MOCK_MODE=true`

### Calendar Issues

1. Enable Google Calendar API in Cloud Console
2. Verify credentials have Calendar scope
3. Use mock mode for testing: `CALENDAR_MOCK_MODE=true`

### Voice Features Not Working

1. Check ElevenLabs API key in `.env`
2. Voice features are optional - app works without them
3. Comment out voice libraries in requirements.txt if causing issues

### Port Already in Use

```bash
# Change port in .env
PORT=8001
```

## Security Notes

- Never commit `.env` file or credentials to version control
- Keep API keys secure and rotate regularly
- Use OAuth tokens instead of passwords
- Review Gmail API permissions carefully
- Enable 2FA on Google account

## License

This project is provided as-is for personal use.

## Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation at `/docs`
3. Check server logs for error details
4. Ensure all environment variables are set correctly

## Deployment

### Local Deployment

Already configured for local deployment - just follow Quick Start.

### Cloud Deployment (Optional)

For production deployment:

1. Set environment variables in cloud platform
2. Configure OAuth redirect URIs
3. Use production-grade WSGI server
4. Enable HTTPS
5. Set proper CORS origins
6. Use secrets management service

## Roadmap

Future enhancements:
- [ ] Multi-account email support
- [ ] Advanced email search and filters
- [ ] Email templates library
- [ ] Scheduled email sending
- [ ] Integration with more email providers
- [ ] Mobile app version
- [ ] Team collaboration features

## Version

Current version: 1.0.0

## Credits

Built with FastAPI, LangChain, Google APIs, and modern web technologies.
