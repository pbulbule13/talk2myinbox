# Cognitive Journal Agent (CJA)

A multimodal, agentic personal assistant built on LangGraph for intelligent journal management, task extraction, and daily summarization.

## Features

### Core Capabilities

- **Multimodal Input Processing**: Text, voice, images (OCR), PDFs, code snippets, emails, calendar events
- **Intelligent Processing**: LLM-powered contextual tagging, action item extraction, and emotional tone detection
- **Flexible Storage**: JSON, SQLite, or Firestore backends
- **Daily Summaries**: AI-generated daily narratives with key insights and learnings
- **Action Planning**: Automatic extraction and prioritization of actionable tasks
- **Text-to-Speech**: High-quality audio reports via ElevenLabs or local TTS
- **Agentic Tools**: Email, calendar management, file operations, web search
- **API & CLI**: FastAPI server and interactive command-line interface

### Architecture

Built on a production-grade LangGraph state machine with the following workflow:

```
User Input → Router → [Ingestion, Agent, or Reporting]
                 ↓
         [Processing → Storage]
                 ↓
         [Reporting → TTS → End]
```

## Installation

### Prerequisites

- Python 3.9+
- API keys (optional but recommended):
  - OpenAI or Anthropic (for LLM processing)
  - ElevenLabs (for high-quality TTS)
  - Google Cloud (for Firestore storage)

### Quick Start

1. **Clone and install dependencies**:
```bash
cd cognitive_journal_agent
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
# Generate template
python config.py

# Copy and edit
cp .env.template .env
# Edit .env with your API keys
```

3. **Run the agent**:
```bash
# Interactive CLI
python main.py cli

# API server
python main.py api

# Demo mode
python main.py demo

# Single command
python main.py -c "Had a productive meeting today"
```

## Configuration

All settings are configurable via environment variables or `.env` file:

### LLM Configuration
```bash
LLM_PROVIDER=openai              # openai, anthropic
LLM_MODEL_NAME=gpt-4
LLM_TEMPERATURE=0.3
OPENAI_API_KEY=your_key_here
USE_LLM_PROCESSING=true          # Use LLM for processing (false = rule-based)
USE_LLM_REPORTING=true           # Use LLM for reports (false = simple summary)
```

### Storage Configuration
```bash
STORAGE_BACKEND=json             # json, sqlite, firestore
STORAGE_DIR=./data
# For Firestore:
# GOOGLE_CLOUD_CREDENTIALS=/path/to/credentials.json
```

### TTS Configuration
```bash
TTS_BACKEND=elevenlabs           # elevenlabs, local, none
TTS_ENABLED=true
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### Email & Calendar
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

CALENDAR_BACKEND=local           # local, google, outlook
```

## Usage

### CLI Mode

```bash
python main.py cli
```

Interactive mode with commands:
- Type journal entries, thoughts, or notes
- Use action commands: "send email to...", "schedule meeting..."
- Type "summarize" or "report" for daily summary
- Type "quit" to exit

### API Mode

```bash
python main.py api
```

Then access:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

API Endpoints:
- `POST /journal` - Create journal entry
- `GET /entries` - Retrieve all entries
- `GET /actions` - Get pending action items
- `POST /summarize` - Generate daily summary

Example API request:
```bash
curl -X POST "http://localhost:8000/journal" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Had a great meeting today"}'
```

### Programmatic Usage

```python
from graph.agent_graph import run_agent, AgentWithMemory

# Single execution
result = run_agent("Today I learned about LangGraph")

# With memory (multi-turn)
agent = AgentWithMemory()
agent.execute("First journal entry")
agent.execute("Second journal entry")
agent.execute("Generate summary")
```

## Multimodal Input Examples

### Text Note
```python
result = run_agent("Had a productive day working on the ML project")
```

### Code Snippet
```python
result = run_agent(
    user_input="",
    input_data={
        "type": "code_snippet",
        "content": "def hello(): return 'world'",
        "language": "python"
    }
)
```

### Email
```python
result = run_agent(
    user_input="",
    input_data={
        "type": "email",
        "email_data": {
            "from": "john@example.com",
            "subject": "Project Update",
            "body": "Latest status...",
            "timestamp": datetime.now()
        }
    }
)
```

### Calendar Event
```python
result = run_agent(
    user_input="",
    input_data={
        "type": "calendar_event",
        "event_data": {
            "title": "Team Standup",
            "start": "2024-01-15 09:00",
            "end": "2024-01-15 09:30",
            "attendees": ["alice@example.com"]
        }
    }
)
```

## Testing

### Run All Tests
```bash
cd cognitive_journal_agent
pytest tests/ -v
```

### Run Specific Test Suite
```bash
pytest tests/test_ingestion.py -v
pytest tests/test_storage.py -v
pytest tests/test_integration.py -v
```

### Test Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Project Structure

```
cognitive_journal_agent/
├── main.py                     # Entry point (CLI, API, demo modes)
├── config.py                   # Configuration management
├── requirements.txt            # Dependencies
├── data_models/
│   └── pydantic_schemas.py     # Pydantic data models
├── tools/
│   └── external_tools.py       # LangChain tool definitions
├── nodes/
│   ├── ingestion.py            # Multimodal input processing
│   ├── processing.py           # LLM-based analysis
│   ├── storage.py              # Storage backends
│   ├── reporting.py            # Daily summaries
│   ├── output.py               # Text-to-speech
│   └── agent.py                # Tool execution agent
├── graph/
│   └── agent_graph.py          # LangGraph workflow
└── tests/
    ├── test_pydantic_schemas.py
    ├── test_ingestion.py
    ├── test_storage.py
    └── test_integration.py
```

## Advanced Features

### Custom Tools

Add new tools by extending `tools/external_tools.py`:

```python
from langchain.tools import BaseTool

class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "What this tool does"

    def _run(self, input: str) -> str:
        # Tool logic here
        return "Result"

# Add to get_all_tools()
def get_all_tools():
    return [
        SendEmailTool(),
        CalendarManagementTool(),
        MyCustomTool(),  # Add here
    ]
```

### Workflow Visualization

```bash
python main.py --visualize
```

Generates `agent_graph.png` showing the workflow structure.

### Streaming Execution

```python
from graph.agent_graph import stream_agent

async for state in stream_agent("Journal entry"):
    print(f"State update: {state}")
```

## Performance Optimization

### Without LLM APIs (Free Tier)

Set in `.env`:
```bash
USE_LLM_PROCESSING=false
USE_LLM_REPORTING=false
TTS_BACKEND=local
STORAGE_BACKEND=json
```

This uses:
- Rule-based processing (no API calls)
- Simple summaries (no LLM)
- Local TTS (pyttsx3)
- JSON storage (no cloud)

### With LLM APIs (Full Features)

```bash
USE_LLM_PROCESSING=true
USE_LLM_REPORTING=true
TTS_BACKEND=elevenlabs
STORAGE_BACKEND=firestore
```

## Troubleshooting

### Common Issues

**Import errors**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

**API key errors**: Check `.env` file has correct keys:
```bash
python config.py  # View current config
```

**Storage errors**: Ensure directories exist and have write permissions:
```bash
mkdir -p data audio_output temp_ingestion
```

**OCR not working**: Install Tesseract:
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Contributing

To extend the agent:

1. **Add new input types**: Extend `nodes/ingestion.py`
2. **Add new tools**: Extend `tools/external_tools.py`
3. **Modify workflow**: Edit `graph/agent_graph.py`
4. **Add new storage backends**: Extend `nodes/storage.py`

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) - State machine workflow
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation
- [FastAPI](https://github.com/tiangolo/fastapi) - API server
- [ElevenLabs](https://elevenlabs.io/) - Text-to-speech

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Built by**: Cognitive Journal Agent Team
**Version**: 1.0.0
**Status**: Production Ready
