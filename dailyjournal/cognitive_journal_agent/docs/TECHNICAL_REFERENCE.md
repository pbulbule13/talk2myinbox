# Cognitive Journal Agent - Technical Reference

**Version**: 1.0.0
**Date**: 2025-11-03
**Status**: Production Ready

---

## Table of Contents

1. [Code Organization](#code-organization)
2. [Module Documentation](#module-documentation)
3. [Data Models](#data-models)
4. [LangGraph Nodes](#langgraph-nodes)
5. [Tool Definitions](#tool-definitions)
6. [Processing Logic](#processing-logic)
7. [Storage Implementations](#storage-implementations)
8. [Configuration Management](#configuration-management)
9. [Error Handling](#error-handling)
10. [Testing Infrastructure](#testing-infrastructure)
11. [Deployment](#deployment)
12. [Performance Optimization](#performance-optimization)

---

## Code Organization

### Project Structure

```
cognitive_journal_agent/
├── __init__.py                 # Package initialization
├── main.py                     # Entry point (CLI, API, demo)
├── config.py                   # Configuration management
│
├── data_models/                # Pydantic schemas
│   ├── __init__.py
│   └── pydantic_schemas.py     # Core data models
│
├── tools/                      # LangChain tools
│   ├── __init__.py
│   └── external_tools.py       # SendEmail, Calendar, File, WebSearch tools
│
├── nodes/                      # LangGraph nodes
│   ├── __init__.py
│   ├── ingestion.py            # Multimodal input processing
│   ├── processing.py           # LLM-based content analysis
│   ├── storage.py              # Multi-backend persistence
│   ├── reporting.py            # Daily summary generation
│   ├── output.py               # TTS voice output
│   └── agent.py                # LangChain agent executor
│
├── graph/                      # LangGraph workflow
│   ├── __init__.py
│   └── agent_graph.py          # State machine definition
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── logger.py               # Logging configuration
│   ├── migrate_data.py         # Storage migration scripts
│   └── helpers.py              # Common helper functions
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_pydantic_schemas.py    # Data model tests (7/7)
│   ├── test_ingestion.py           # Ingestion tests (7/7)
│   ├── test_storage.py             # Storage tests (9/9)
│   └── test_integration.py         # Integration tests (7/11)
│
├── data/                       # Runtime data
│   ├── journal_entries.json    # JSON storage backend
│   ├── action_items.json       # JSON action items
│   ├── cja_database.db         # SQLite database
│   └── audio/                  # Generated TTS audio files
│
├── docs/                       # Documentation
│   ├── README.md               # Documentation index
│   ├── ARCHITECTURE.md         # Architecture specification
│   ├── SYSTEM_DESIGN.md        # System design diagrams
│   ├── DEPLOYMENT_GUIDE.md     # Deployment instructions
│   ├── FUNCTIONAL_SPECIFICATION.md  # Feature specifications
│   ├── TECHNICAL_REFERENCE.md  # This document
│   ├── API_DOCUMENTATION.md    # REST API reference
│   └── architecture_diagram.html    # Interactive diagram
│
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
└── README.md                   # Project overview
```

---

## Module Documentation

### 1. main.py

**Purpose:** Application entry point with three operational modes

**Location:** `cognitive_journal_agent/main.py`

**Modes:**
1. **CLI Mode**: Interactive command-line interface
2. **API Mode**: FastAPI REST server
3. **Demo Mode**: Demonstration with sample data

**Usage:**
```bash
# CLI mode
python main.py cli

# API mode (starts server on http://localhost:8000)
python main.py api

# Demo mode (processes sample entries)
python main.py demo
```

**Key Functions:**

#### `run_cli()`
```python
def run_cli():
    """
    Interactive CLI for journal operations.

    Commands:
    - text: Create text note
    - voice: Process voice memo
    - summary: Generate daily summary
    - actions: List pending action items
    - exit: Quit application
    """
```

#### `run_api()`
```python
def run_api():
    """
    Launch FastAPI server with endpoints:
    - POST /api/entry: Create journal entry
    - GET /api/entry/{entry_id}: Retrieve entry
    - POST /api/summary: Generate daily summary
    - GET /api/actions: List action items
    """
```

#### `run_demo()`
```python
def run_demo():
    """
    Demonstration mode with sample inputs:
    1. Text note about project meeting
    2. Voice memo (if sample audio available)
    3. Daily summary generation
    4. Action item execution
    """
```

**Dependencies:**
- `argparse`: Command-line argument parsing
- `uvicorn`: ASGI server for FastAPI
- `graph.agent_graph`: LangGraph workflow

---

### 2. config.py

**Purpose:** Centralized configuration management

**Location:** `cognitive_journal_agent/config.py`

**Configuration Sections:**

#### LLMConfig
```python
@dataclass
class LLMConfig:
    provider: str = "openai"  # openai, anthropic, local
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.3
    max_tokens: int = 1000
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    fallback_to_rules: bool = True
```

#### StorageConfig
```python
@dataclass
class StorageConfig:
    backend: str = field(default_factory=lambda: os.getenv("STORAGE_BACKEND", "json"))
    json_path: str = "data/journal_entries.json"
    sqlite_path: str = "data/cja_database.db"
    firestore_project_id: str = field(default_factory=lambda: os.getenv("FIRESTORE_PROJECT_ID", ""))
    firestore_credentials: str = field(default_factory=lambda: os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""))
```

#### TTSConfig
```python
@dataclass
class TTSConfig:
    provider: str = field(default_factory=lambda: os.getenv("TTS_PROVIDER", "elevenlabs"))
    elevenlabs_api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    elevenlabs_voice_id: str = field(default_factory=lambda: os.getenv("ELEVENLABS_VOICE_ID", ""))
    local_rate: int = 150  # Words per minute
    local_volume: float = 0.9
    output_path: str = "data/audio"
```

#### EmailConfig
```python
@dataclass
class EmailConfig:
    smtp_server: str = field(default_factory=lambda: os.getenv("SMTP_SERVER", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_username: str = field(default_factory=lambda: os.getenv("SMTP_USERNAME", ""))
    smtp_password: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    from_email: str = field(default_factory=lambda: os.getenv("FROM_EMAIL", ""))
```

**Usage:**
```python
from config import get_config

config = get_config()
llm_provider = config.llm.provider
storage_backend = config.storage.backend
```

---

### 3. data_models/pydantic_schemas.py

**Purpose:** Core data models with validation

**Location:** `cognitive_journal_agent/data_models/pydantic_schemas.py`

#### Model Hierarchy

```
BaseModel (Pydantic)
├── JournalEntry          # Core entry model
├── ActionItem            # Task extracted from entries
├── ProcessedContent      # LLM processing output
├── DailySummaryOutput    # Daily summary structure
├── FinalAgentReport      # Complete report with actions
└── AgentState            # LangGraph state (TypedDict)
```

#### JournalEntry
```python
class JournalEntry(BaseModel):
    """
    Core journal entry model representing single captured input.

    Attributes:
        entry_id: Unique identifier (UUID4)
        timestamp: Creation time (ISO 8601)
        input_type: One of 7 supported types
        raw_content: Original unprocessed text
        source_id: Origin identifier (file path, email ID, etc.)
        contextual_tags: Extracted topic labels
        extracted_action_items: Task descriptions
        inferred_emotion: Detected emotional state
        priority_score: Urgency rating (1-10)
        key_entities: Named entities (people, orgs, projects)
        processed: Whether LLM processing completed
        metadata: Additional arbitrary data
    """
    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    input_type: str = Field(..., description="Input type: text_note, voice_memo, etc.")
    raw_content: str = Field(..., min_length=1, description="Original input content")
    source_id: str = Field(..., description="Source identifier")

    # LLM-enriched fields
    contextual_tags: List[str] = Field(default=[])
    extracted_action_items: List[str] = Field(default=[])
    inferred_emotion: Optional[str] = Field(default=None)
    priority_score: int = Field(default=5, ge=1, le=10)
    key_entities: List[str] = Field(default=[])

    processed: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default={})

    @field_validator("input_type")
    @classmethod
    def validate_input_type(cls, v: str) -> str:
        """Validate input type is one of supported types."""
        valid_types = [
            "text_note", "voice_memo", "photo_ocr", "pdf_document",
            "code_snippet", "email", "calendar_event"
        ]
        if v not in valid_types:
            raise ValueError(f"input_type must be one of {valid_types}")
        return v

    @field_validator("contextual_tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags are lowercase and alphanumeric."""
        for tag in v:
            if not re.match(r'^[a-z0-9-]+$', tag):
                raise ValueError(f"Tag '{tag}' must be lowercase alphanumeric with hyphens")
        return v[:7]  # Maximum 7 tags

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entry_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "timestamp": "2025-11-03T14:30:00",
                "input_type": "text_note",
                "raw_content": "Met with John to discuss API design. Need to finalize endpoints by Friday.",
                "source_id": "cli_input_20251103_143000",
                "contextual_tags": ["api-design", "meeting", "deadline"],
                "extracted_action_items": ["Finalize API endpoints by Friday"],
                "inferred_emotion": "focused",
                "priority_score": 7,
                "key_entities": ["John"],
                "processed": True
            }
        }
    )
```

#### ActionItem
```python
class ActionItem(BaseModel):
    """
    Extracted task from journal entries.

    Attributes:
        task_id: Unique identifier
        task_description: Human-readable task
        priority: high, medium, or low
        due_date: Optional deadline
        source_entry_id: Originating journal entry
        completed: Task completion status
        completed_at: Completion timestamp
    """
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    task_description: str = Field(..., min_length=1)
    priority: str = Field(..., pattern="^(high|medium|low)$")
    source_entry_id: str = Field(...)
    due_date: Optional[datetime] = Field(default=None)
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of: high, medium, low."""
        if v not in ["high", "medium", "low"]:
            raise ValueError("priority must be 'high', 'medium', or 'low'")
        return v

    def mark_complete(self):
        """Mark action item as completed with timestamp."""
        self.completed = True
        self.completed_at = datetime.now()
```

#### ProcessedContent
```python
class ProcessedContent(BaseModel):
    """
    LLM processing output structure.

    Used as output parser schema for LangChain LLM chain.
    """
    contextual_tags: List[str] = Field(..., max_length=7)
    extracted_action_items: List[str] = Field(default=[])
    inferred_emotion: Optional[str] = Field(default=None)
    priority_score: int = Field(..., ge=1, le=10)
    key_entities: List[str] = Field(default=[])
```

#### DailySummaryOutput
```python
class DailySummaryOutput(BaseModel):
    """
    Daily summary report structure.

    Attributes:
        date: Summary date
        total_entries: Count of entries
        key_themes: Top 5 most common tags
        emotion_overview: Emotion distribution
        notable_insights: LLM-generated reflections
    """
    date: str = Field(..., description="Summary date (YYYY-MM-DD)")
    total_entries: int = Field(..., ge=0)
    key_themes: List[str] = Field(default=[])
    emotion_overview: Dict[str, int] = Field(default={})
    notable_insights: str = Field(default="")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-11-03",
                "total_entries": 12,
                "key_themes": ["api-design", "meetings", "deadlines", "documentation"],
                "emotion_overview": {"stressed": 5, "focused": 4, "neutral": 3},
                "notable_insights": "High stress today related to approaching deadlines."
            }
        }
    )
```

#### FinalAgentReport
```python
class FinalAgentReport(BaseModel):
    """
    Complete daily report with summary and action items.

    Returned to user as final output.
    """
    summary: DailySummaryOutput
    pending_actions: List[ActionItem]
    suggested_first_task: str = Field(..., min_length=1)

    def to_formatted_string(self) -> str:
        """Convert report to human-readable string."""
        output = f"\nDaily Summary for {self.summary.date}\n"
        output += "=" * 50 + "\n\n"
        output += f"Total Entries: {self.summary.total_entries}\n"
        output += f"Key Themes: {', '.join(self.summary.key_themes)}\n\n"

        if self.summary.emotion_overview:
            output += "Emotion Overview:\n"
            for emotion, count in self.summary.emotion_overview.items():
                output += f"  - {emotion.title()}: {count}\n"

        output += f"\nPending Action Items ({len(self.pending_actions)}):\n"
        for action in self.pending_actions:
            priority_label = action.priority.upper()
            output += f"  [{priority_label}] {action.task_description}\n"

        output += f"\nSuggested First Task: {self.suggested_first_task}\n"

        if self.summary.notable_insights:
            output += f"\nInsights: {self.summary.notable_insights}\n"

        return output
```

#### AgentState
```python
class AgentState(TypedDict):
    """
    LangGraph state dictionary.

    Passed between nodes in workflow. TypedDict provides type hints
    without Pydantic validation overhead.
    """
    user_input: str                      # Original user input
    input_type: str                      # Detected input type
    journal_entry: Optional[JournalEntry]  # Processed entry
    action_items: List[ActionItem]       # Extracted actions
    daily_summary: Optional[DailySummaryOutput]  # Generated summary
    agent_response: Optional[str]        # Agent execution result
    error: Optional[str]                 # Error message if any
```

---

### 4. nodes/ingestion.py

**Purpose:** Multimodal input processing

**Location:** `cognitive_journal_agent/nodes/ingestion.py`

**Class: MultimodalIngest**

#### Architecture

```
User Input (7 types)
        |
        v
[Input Type Detection]
        |
        +-----> text_note       --> process_text_note()
        +-----> voice_memo      --> process_voice_memo()
        +-----> photo_ocr       --> process_photo_ocr()
        +-----> pdf_document    --> process_pdf_document()
        +-----> code_snippet    --> process_code_snippet()
        +-----> email           --> process_email()
        +-----> calendar_event  --> process_calendar_event()
        |
        v
[JournalEntry created]
```

#### Methods

##### `process_text_note(content: str) -> JournalEntry`
```python
def process_text_note(self, content: str) -> JournalEntry:
    """
    Process plain text input.

    Args:
        content: Text string

    Returns:
        JournalEntry with input_type="text_note"

    Example:
        >>> ingest = MultimodalIngest()
        >>> entry = ingest.process_text_note("Met with team today")
        >>> entry.input_type
        'text_note'
    """
    return JournalEntry(
        timestamp=datetime.now(),
        input_type="text_note",
        raw_content=content,
        source_id=f"text_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
```

##### `process_voice_memo(audio_file_path: str) -> JournalEntry`
```python
def process_voice_memo(self, audio_file_path: str) -> JournalEntry:
    """
    Process audio file via speech-to-text.

    Uses Google Speech Recognition API.

    Args:
        audio_file_path: Path to WAV or MP3 file

    Returns:
        JournalEntry with transcribed text

    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If transcription fails

    Dependencies:
        - SpeechRecognition
        - pyaudio (for microphone support)

    Example:
        >>> entry = ingest.process_voice_memo("meeting_notes.wav")
        >>> "transcript" in entry.metadata
        True
    """
    if not Path(audio_file_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)

    try:
        transcription = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        raise ValueError("Speech recognition could not understand audio")
    except sr.RequestError as e:
        raise ValueError(f"Speech recognition service error: {e}")

    return JournalEntry(
        timestamp=datetime.now(),
        input_type="voice_memo",
        raw_content=transcription,
        source_id=audio_file_path,
        metadata={"audio_file": audio_file_path, "transcription_method": "google"}
    )
```

##### `process_photo_ocr(image_path: str) -> JournalEntry`
```python
def process_photo_ocr(self, image_path: str) -> JournalEntry:
    """
    Extract text from image via OCR.

    Uses Tesseract OCR engine.

    Args:
        image_path: Path to JPG or PNG image

    Returns:
        JournalEntry with extracted text

    Dependencies:
        - pytesseract
        - Pillow (PIL)
        - Tesseract OCR binary installed

    Configuration:
        Set TESSERACT_CMD environment variable if not in PATH.

    Example:
        >>> entry = ingest.process_photo_ocr("whiteboard.jpg")
        >>> len(entry.raw_content) > 0
        True
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)

    if not extracted_text.strip():
        extracted_text = "[No text extracted from image]"

    return JournalEntry(
        timestamp=datetime.now(),
        input_type="photo_ocr",
        raw_content=extracted_text,
        source_id=image_path,
        metadata={"image_file": image_path, "ocr_method": "tesseract"}
    )
```

##### `process_pdf_document(pdf_path: str) -> JournalEntry`
```python
def process_pdf_document(self, pdf_path: str) -> JournalEntry:
    """
    Extract text from PDF document.

    Uses PyPDF2 for text extraction.

    Args:
        pdf_path: Path to PDF file

    Returns:
        JournalEntry with extracted text from all pages

    Metadata:
        - num_pages: Total page count
        - pdf_metadata: Title, author, etc. from PDF

    Example:
        >>> entry = ingest.process_pdf_document("research_paper.pdf")
        >>> entry.metadata["num_pages"]
        15
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PyPDF2.PdfReader(pdf_path)
    num_pages = len(reader.pages)

    full_text = []
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text.strip():
            full_text.append(f"[Page {page_num}]\n{text}")

    return JournalEntry(
        timestamp=datetime.now(),
        input_type="pdf_document",
        raw_content="\n\n".join(full_text),
        source_id=pdf_path,
        metadata={
            "pdf_file": pdf_path,
            "num_pages": num_pages,
            "pdf_metadata": reader.metadata
        }
    )
```

##### `process_code_snippet(code: str, language: str = "python") -> JournalEntry`
```python
def process_code_snippet(self, code: str, language: str = "python") -> JournalEntry:
    """
    Process code snippet with syntax preservation.

    Args:
        code: Source code string
        language: Programming language (default: python)

    Returns:
        JournalEntry with code and language metadata

    Metadata:
        - language: Programming language
        - line_count: Number of lines

    Example:
        >>> code = "def hello():\n    print('world')"
        >>> entry = ingest.process_code_snippet(code, "python")
        >>> entry.metadata["language"]
        'python'
    """
    return JournalEntry(
        timestamp=datetime.now(),
        input_type="code_snippet",
        raw_content=code,
        source_id=f"code_snippet_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        contextual_tags=[language, "code", "programming"],
        metadata={
            "language": language,
            "line_count": len(code.split("\n"))
        }
    )
```

---

### 5. nodes/processing.py

**Purpose:** LLM-based content enrichment with rule-based fallback

**Location:** `cognitive_journal_agent/nodes/processing.py`

**Class: ProcessEntry**

#### Architecture

```
JournalEntry (raw)
        |
        v
[LLM Available?]
        |
    Yes |  No
        |   |
        v   v
    [LLM]  [Rules]
        |   |
        +---+
          |
          v
[ProcessedContent]
          |
          v
JournalEntry (enriched)
```

#### LLM Processing Chain

```python
class ProcessEntry:
    def __init__(self):
        self.config = get_config()
        self.llm = self._initialize_llm()
        self.output_parser = PydanticOutputParser(pydantic_object=ProcessedContent)

        # LangChain prompt template
        self.prompt = PromptTemplate(
            template=self._get_prompt_template(),
            input_variables=["content"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )

        # LangChain chain: prompt | llm | parser
        self.chain = self.prompt | self.llm | self.output_parser

    def _initialize_llm(self):
        """Initialize LLM based on configuration."""
        config = self.config.llm

        if config.provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=config.api_key
            )
        elif config.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=config.api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    def _get_prompt_template(self) -> str:
        """Return prompt template for LLM processing."""
        return """
You are an expert at analyzing journal entries and extracting structured information.

Analyze the following journal entry and extract:
1. Contextual tags (3-7 tags): Topics, projects, people, or themes
2. Action items: Tasks or commitments mentioned
3. Emotion: Inferred emotional state (happy, stressed, neutral, excited, frustrated)
4. Priority score: 1-10 rating of urgency/importance
5. Key entities: People, organizations, or projects mentioned

Journal Entry:
{content}

{format_instructions}

Provide your analysis in valid JSON format.
"""

    def process(self, journal_entry: JournalEntry) -> JournalEntry:
        """
        Process journal entry with LLM or fallback to rules.

        Args:
            journal_entry: Raw journal entry

        Returns:
            Enriched journal entry with extracted insights

        Raises:
            ValueError: If processing fails and no fallback available
        """
        try:
            # Attempt LLM processing
            result: ProcessedContent = self.chain.invoke({"content": journal_entry.raw_content})

            # Update journal entry with LLM results
            journal_entry.contextual_tags = result.contextual_tags
            journal_entry.extracted_action_items = result.extracted_action_items
            journal_entry.inferred_emotion = result.inferred_emotion
            journal_entry.priority_score = result.priority_score
            journal_entry.key_entities = result.key_entities
            journal_entry.processed = True

            return journal_entry

        except Exception as e:
            if self.config.llm.fallback_to_rules:
                # Fallback to rule-based processing
                return self._rule_based_processing(journal_entry)
            else:
                raise ValueError(f"LLM processing failed: {e}")

    def _rule_based_processing(self, journal_entry: JournalEntry) -> JournalEntry:
        """
        Fallback rule-based processing when LLM unavailable.

        Uses regex patterns and heuristics for extraction.
        """
        content = journal_entry.raw_content.lower()

        # Extract tags via keyword matching
        tag_keywords = {
            "meeting": ["meeting", "discussion", "call"],
            "deadline": ["deadline", "due", "eod", "today", "tomorrow"],
            "project": ["project", "sprint", "milestone"],
            "coding": ["code", "bug", "feature", "api", "function"],
            "personal": ["feeling", "thoughts", "reflection"]
        }

        tags = []
        for tag, keywords in tag_keywords.items():
            if any(kw in content for kw in keywords):
                tags.append(tag)

        # Extract action items via patterns
        action_patterns = [
            r"(need|needs) to (\w+\s+\w+)",
            r"(should|must|have to) (\w+\s+\w+)",
            r"(todo|TODO):\s*(.+)"
        ]

        action_items = []
        for pattern in action_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    action_items.append(" ".join(match))

        # Infer emotion via sentiment keywords
        emotion_keywords = {
            "happy": ["great", "excellent", "happy", "excited", "love"],
            "stressed": ["stressed", "overwhelmed", "worried", "anxious"],
            "frustrated": ["frustrated", "annoyed", "difficult", "problem"],
            "focused": ["focused", "productive", "accomplished"]
        }

        emotion = "neutral"
        for emo, keywords in emotion_keywords.items():
            if any(kw in content for kw in keywords):
                emotion = emo
                break

        # Calculate priority score
        priority = 5  # Default medium
        if any(kw in content for kw in ["urgent", "critical", "asap"]):
            priority += 3
        if any(kw in content for kw in ["deadline", "today", "eod"]):
            priority += 2
        priority = max(1, min(10, priority))

        # Extract entities (basic capitalized words)
        entities = re.findall(r'\b[A-Z][a-z]+\b', journal_entry.raw_content)
        entities = list(set(entities))[:5]  # Unique, max 5

        # Update journal entry
        journal_entry.contextual_tags = tags[:7]
        journal_entry.extracted_action_items = action_items
        journal_entry.inferred_emotion = emotion
        journal_entry.priority_score = priority
        journal_entry.key_entities = entities
        journal_entry.processed = True
        journal_entry.metadata["processing_method"] = "rule_based"

        return journal_entry
```

---

### 6. nodes/storage.py

**Purpose:** Multi-backend persistence with repository pattern

**Location:** `cognitive_journal_agent/nodes/storage.py`

**Architecture:**

```
[StorageManager] (Facade)
        |
        +---> JSONStorage (Local files)
        +---> SQLiteStorage (Local database)
        +---> FirestoreStorage (Cloud NoSQL)
```

#### Protocol: StorageBackend

```python
class StorageBackend(Protocol):
    """Abstract interface for storage implementations."""

    def save_journal_entry(self, entry: JournalEntry) -> None:
        """Save journal entry to storage."""
        ...

    def get_journal_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Retrieve journal entry by ID."""
        ...

    def query_entries(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> List[JournalEntry]:
        """Query journal entries with filters."""
        ...

    def save_action_item(self, item: ActionItem) -> None:
        """Save action item to storage."""
        ...

    def get_pending_actions(self) -> List[ActionItem]:
        """Retrieve all incomplete action items."""
        ...

    def mark_action_complete(self, task_id: str) -> None:
        """Mark action item as completed."""
        ...
```

#### JSONStorage Implementation

```python
class JSONStorage:
    """
    JSON file-based storage backend.

    Best for: Local development, testing, small datasets

    Files:
        - data/journal_entries.json
        - data/action_items.json

    Thread-safety: File locking via fcntl (Unix) or msvcrt (Windows)
    """

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.entries_file = self.base_path / "journal_entries.json"
        self.actions_file = self.base_path / "action_items.json"

        # Initialize files if they don't exist
        if not self.entries_file.exists():
            self._write_json(self.entries_file, [])
        if not self.actions_file.exists():
            self._write_json(self.actions_file, [])

    def _read_json(self, file_path: Path) -> List[Dict]:
        """Read JSON file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write_json(self, file_path: Path, data: List[Dict]) -> None:
        """Write JSON file with atomic operation."""
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        temp_file.replace(file_path)  # Atomic operation

    def save_journal_entry(self, entry: JournalEntry) -> None:
        """Save journal entry to JSON file."""
        entries = self._read_json(self.entries_file)
        entries.append(entry.model_dump())
        self._write_json(self.entries_file, entries)

    def get_journal_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Retrieve journal entry by ID."""
        entries = self._read_json(self.entries_file)
        for entry_data in entries:
            if entry_data["entry_id"] == entry_id:
                return JournalEntry(**entry_data)
        return None

    def query_entries(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> List[JournalEntry]:
        """Query entries with filters."""
        entries = self._read_json(self.entries_file)
        results = []

        for entry_data in entries:
            entry = JournalEntry(**entry_data)

            # Date filter
            if date_from and entry.timestamp < date_from:
                continue
            if date_to and entry.timestamp > date_to:
                continue

            # Tag filter
            if tags and not any(tag in entry.contextual_tags for tag in tags):
                continue

            results.append(entry)

        return results
```

#### SQLiteStorage Implementation

```python
class SQLiteStorage:
    """
    SQLite database storage backend.

    Best for: Local production, medium datasets (< 1M entries)

    Schema:
        journal_entries(
            entry_id TEXT PRIMARY KEY,
            timestamp TEXT,
            input_type TEXT,
            raw_content TEXT,
            contextual_tags TEXT,  -- JSON array
            extracted_action_items TEXT,  -- JSON array
            inferred_emotion TEXT,
            priority_score INTEGER,
            key_entities TEXT,  -- JSON array
            processed BOOLEAN,
            metadata TEXT  -- JSON object
        )

        action_items(
            task_id TEXT PRIMARY KEY,
            task_description TEXT,
            priority TEXT,
            source_entry_id TEXT,
            due_date TEXT,
            completed BOOLEAN,
            completed_at TEXT
        )
    """

    def __init__(self, db_path: str = "data/cja_database.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                entry_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                input_type TEXT NOT NULL,
                raw_content TEXT NOT NULL,
                source_id TEXT,
                contextual_tags TEXT,
                extracted_action_items TEXT,
                inferred_emotion TEXT,
                priority_score INTEGER,
                key_entities TEXT,
                processed BOOLEAN,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_items (
                task_id TEXT PRIMARY KEY,
                task_description TEXT NOT NULL,
                priority TEXT NOT NULL,
                source_entry_id TEXT,
                due_date TEXT,
                completed BOOLEAN DEFAULT 0,
                completed_at TEXT
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON journal_entries(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_input_type ON journal_entries(input_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON action_items(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_completed ON action_items(completed)")

        conn.commit()
        conn.close()

    def save_journal_entry(self, entry: JournalEntry) -> None:
        """Save journal entry to SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO journal_entries
            (entry_id, timestamp, input_type, raw_content, source_id, contextual_tags,
             extracted_action_items, inferred_emotion, priority_score, key_entities,
             processed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.entry_id,
            entry.timestamp.isoformat(),
            entry.input_type,
            entry.raw_content,
            entry.source_id,
            json.dumps(entry.contextual_tags),
            json.dumps(entry.extracted_action_items),
            entry.inferred_emotion,
            entry.priority_score,
            json.dumps(entry.key_entities),
            entry.processed,
            json.dumps(entry.metadata)
        ))

        conn.commit()
        conn.close()
```

#### FirestoreStorage Implementation

```python
class FirestoreStorage:
    """
    Google Cloud Firestore storage backend.

    Best for: Cloud production, large datasets, multi-user scenarios

    Collections:
        - journal_entries: Document per entry
        - action_items: Document per action item

    Indexes:
        - journal_entries: timestamp DESC
        - action_items: completed ASC, priority DESC

    Authentication:
        GOOGLE_APPLICATION_CREDENTIALS environment variable
    """

    def __init__(self):
        from google.cloud import firestore

        project_id = get_config().storage.firestore_project_id
        if not project_id:
            raise ValueError("FIRESTORE_PROJECT_ID not configured")

        self.db = firestore.Client(project=project_id)
        self.entries_collection = self.db.collection("journal_entries")
        self.actions_collection = self.db.collection("action_items")

    def save_journal_entry(self, entry: JournalEntry) -> None:
        """Save journal entry to Firestore."""
        doc_ref = self.entries_collection.document(entry.entry_id)
        doc_ref.set(entry.model_dump())

    def get_journal_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Retrieve journal entry by ID."""
        doc_ref = self.entries_collection.document(entry_id)
        doc = doc_ref.get()

        if doc.exists:
            return JournalEntry(**doc.to_dict())
        return None

    def query_entries(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> List[JournalEntry]:
        """Query entries with filters."""
        query = self.entries_collection

        if date_from:
            query = query.where("timestamp", ">=", date_from)
        if date_to:
            query = query.where("timestamp", "<=", date_to)
        if tags:
            query = query.where("contextual_tags", "array_contains_any", tags)

        docs = query.stream()
        return [JournalEntry(**doc.to_dict()) for doc in docs]
```

---

### 7. graph/agent_graph.py

**Purpose:** LangGraph workflow orchestration

**Location:** `cognitive_journal_agent/graph/agent_graph.py`

#### State Machine Diagram

```
         [START]
            |
            v
    [Conditional Router]
            |
     +------+------+
     |      |      |
    v       v      v
[ingestion] [agent] [reporting]
     |              |
     v              v
[processing]   [END]
     |
     v
  [storage]
     |
     v
   [END]
```

#### Graph Definition

```python
def create_agent_graph() -> StateGraph:
    """
    Create LangGraph workflow for CJA.

    Returns:
        Compiled StateGraph ready for execution

    Workflow:
        1. Router: Determine entry point based on user input
        2. Ingestion: Process multimodal input
        3. Processing: Enrich with LLM analysis
        4. Storage: Persist to backend
        OR
        1. Router: Direct to agent for action execution
        2. Agent: Execute tools based on request
        OR
        1. Router: Direct to reporting for summary
        2. Reporting: Generate daily summary
    """
    from langgraph.graph import StateGraph, END

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("processing", processing_node)
    workflow.add_node("storage", storage_node)
    workflow.add_node("reporting", reporting_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("output", output_node)

    # Conditional entry point (router)
    workflow.set_conditional_entry_point(
        route_input,  # Function that returns node name
        {
            "ingestion": "ingestion",
            "agent": "agent",
            "reporting": "reporting"
        }
    )

    # Linear workflow: ingestion → processing → storage → END
    workflow.add_edge("ingestion", "processing")
    workflow.add_edge("processing", "storage")
    workflow.add_edge("storage", END)

    # Agent workflow: agent → END
    workflow.add_edge("agent", END)

    # Reporting workflow: reporting → output → END
    workflow.add_edge("reporting", "output")
    workflow.add_edge("output", END)

    # Compile graph
    return workflow.compile()


def route_input(state: AgentState) -> str:
    """
    Router function for conditional entry point.

    Determines which node to enter based on user input keywords.

    Args:
        state: Current agent state

    Returns:
        Node name string: "ingestion", "agent", or "reporting"

    Logic:
        - Summary keywords → reporting
        - Action keywords → agent
        - Default → ingestion
    """
    user_input = state.get("user_input", "").lower()

    # Summary generation keywords
    summary_keywords = ["summary", "report", "daily", "today", "yesterday"]
    if any(keyword in user_input for keyword in summary_keywords):
        return "reporting"

    # Agent action keywords
    action_keywords = ["send email", "create event", "search", "file", "execute"]
    if any(keyword in user_input for keyword in action_keywords):
        return "agent"

    # Default: journal entry ingestion
    return "ingestion"


def ingestion_node(state: AgentState) -> AgentState:
    """
    Ingestion node: Process multimodal input.

    Updates state with created journal entry.
    """
    ingestor = MultimodalIngest()

    input_type = state.get("input_type", "text_note")
    user_input = state["user_input"]

    # Process based on input type
    if input_type == "text_note":
        entry = ingestor.process_text_note(user_input)
    # ... other input types

    state["journal_entry"] = entry
    return state


def processing_node(state: AgentState) -> AgentState:
    """
    Processing node: Enrich entry with LLM analysis.

    Updates journal_entry in state with extracted insights.
    """
    processor = ProcessEntry()

    entry = state["journal_entry"]
    enriched_entry = processor.process(entry)

    # Extract action items to separate list
    if enriched_entry.extracted_action_items:
        action_items = []
        for action_desc in enriched_entry.extracted_action_items:
            action_items.append(ActionItem(
                task_description=action_desc,
                priority="high" if enriched_entry.priority_score >= 7 else "medium",
                source_entry_id=enriched_entry.entry_id
            ))
        state["action_items"] = action_items

    state["journal_entry"] = enriched_entry
    return state


def storage_node(state: AgentState) -> AgentState:
    """
    Storage node: Persist entry and action items.

    Saves to configured backend (JSON, SQLite, Firestore).
    """
    storage_manager = StorageManager()

    # Save journal entry
    entry = state["journal_entry"]
    storage_manager.save_journal_entry(entry)

    # Save action items
    action_items = state.get("action_items", [])
    for action in action_items:
        storage_manager.save_action_item(action)

    return state


def reporting_node(state: AgentState) -> AgentState:
    """
    Reporting node: Generate daily summary.

    Queries storage for entries and creates summary.
    """
    report_generator = ReportGenerator()

    # Determine date from user input or default to today
    date_str = datetime.now().strftime("%Y-%m-%d")
    # ... (parse date from user input if specified)

    summary = report_generator.generate_daily_summary(date_str)
    state["daily_summary"] = summary

    return state


def agent_node(state: AgentState) -> AgentState:
    """
    Agent node: Execute tools based on user request.

    Uses LangChain agent executor with available tools.
    """
    agent_executor = create_agent_executor()

    user_input = state["user_input"]
    result = agent_executor.invoke({"input": user_input})

    state["agent_response"] = result["output"]
    return state


def output_node(state: AgentState) -> AgentState:
    """
    Output node: Generate TTS audio for summary.

    Optional node for voice output.
    """
    voice_output = VoiceOutput()

    summary = state.get("daily_summary")
    if summary:
        # Convert summary to formatted string
        summary_text = format_summary(summary)

        # Generate TTS audio
        audio_path = voice_output.generate_speech(summary_text)
        state["audio_path"] = audio_path

    return state
```

---

## Tool Definitions

### SendEmailTool

**Location:** `cognitive_journal_agent/tools/external_tools.py`

```python
class SendEmailInput(BaseModel):
    """Input schema for SendEmailTool."""
    recipient_email: EmailStr
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class SendEmailTool(BaseTool):
    """
    Tool for sending emails via SMTP.

    Configuration:
        SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

    Supported Providers:
        - Gmail (smtp.gmail.com:587)
        - Outlook (smtp.office365.com:587)
        - Custom SMTP servers

    Security:
        - TLS encryption
        - Password from environment variable
        - No credentials stored in code
    """
    name: str = "send_email"
    description: str = """
    Send an email to a recipient. Use this when you need to send follow-up emails,
    notifications, or communicate with others. Requires recipient email, subject, and body.
    """
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        **kwargs
    ) -> str:
        """Execute email sending."""
        config = get_config().email

        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.from_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                server = smtplib.SMTP(config.smtp_server, config.smtp_port)
                server.starttls()
                server.login(config.smtp_username, config.smtp_password)
                server.send_message(msg)
                server.quit()

                return f"Email successfully sent to {recipient_email}"

            except Exception as e:
                if attempt == max_retries - 1:
                    return f"Failed to send email after {max_retries} attempts: {str(e)}"
                time.sleep(2 ** attempt)  # Exponential backoff
```

---

### CalendarManagementTool

**Location:** `cognitive_journal_agent/tools/external_tools.py`

```python
class CalendarManagementTool(BaseTool):
    """
    Tool for managing calendar events.

    Supports:
        - Google Calendar (primary)
        - Outlook Calendar (future)
        - Local ICS files (fallback)

    Operations:
        - create_event: Add new calendar event
        - update_event: Modify existing event
        - delete_event: Remove event
        - list_events: Query events by date range

    Authentication:
        Google Calendar: OAuth 2.0 via google-auth library
        Credentials file: GOOGLE_CALENDAR_CREDENTIALS
    """
    name: str = "calendar_management"
    description: str = """
    Manage calendar events. Operations: create_event, update_event, delete_event, list_events.
    Requires event details (title, start_time, end_time, description).
    """

    def _run(
        self,
        operation: str,
        event_title: str = "",
        start_time: str = "",
        end_time: str = "",
        description: str = "",
        event_id: str = "",
        **kwargs
    ) -> str:
        """Execute calendar operation."""
        from googleapiclient.discovery import build
        from google.oauth2 import service_account

        # Initialize Google Calendar API
        creds_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        if not creds_path:
            return "Google Calendar credentials not configured"

        creds = service_account.Credentials.from_service_account_file(creds_path)
        service = build('calendar', 'v3', credentials=creds)

        if operation == "create_event":
            event = {
                'summary': event_title,
                'description': description,
                'start': {'dateTime': start_time, 'timeZone': 'UTC'},
                'end': {'dateTime': end_time, 'timeZone': 'UTC'}
            }

            created_event = service.events().insert(calendarId='primary', body=event).execute()
            return f"Event created: {created_event['htmlLink']}"

        elif operation == "list_events":
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            if not events:
                return "No upcoming events found."

            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                event_list.append(f"- {event['summary']} at {start}")

            return "\n".join(event_list)

        else:
            return f"Unknown operation: {operation}"
```

---

## Configuration Management

### Environment Variables

**File:** `.env.example`

```bash
# LLM Configuration
LLM_PROVIDER=openai  # openai, anthropic, local
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000
LLM_FALLBACK_TO_RULES=true

# Storage Configuration
STORAGE_BACKEND=json  # json, sqlite, firestore
JSON_STORAGE_PATH=data/journal_entries.json
SQLITE_DB_PATH=data/cja_database.db
FIRESTORE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# TTS Configuration
TTS_PROVIDER=elevenlabs  # elevenlabs, local
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
TTS_LOCAL_RATE=150
TTS_OUTPUT_PATH=data/audio

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS=path/to/calendar_credentials.json

# Application Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
API_PORT=8000
API_HOST=0.0.0.0
```

---

## Error Handling

### Error Hierarchy

```python
class CJAError(Exception):
    """Base exception for CJA."""
    pass

class IngestionError(CJAError):
    """Raised during input processing."""
    pass

class ProcessingError(CJAError):
    """Raised during LLM processing."""
    pass

class StorageError(CJAError):
    """Raised during storage operations."""
    pass

class ToolExecutionError(CJAError):
    """Raised during tool execution."""
    pass
```

### Error Handling Patterns

#### Graceful Degradation
```python
try:
    # Attempt LLM processing
    result = llm_chain.invoke(content)
except Exception as e:
    logger.warning(f"LLM processing failed: {e}. Falling back to rules.")
    result = rule_based_processing(content)
```

#### Retry with Exponential Backoff
```python
def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)
```

---

## Testing Infrastructure

### Test Structure

```
tests/
├── test_pydantic_schemas.py (7 tests, 7 passing)
├── test_ingestion.py (7 tests, 7 passing)
├── test_storage.py (9 tests, 9 passing)
└── test_integration.py (11 tests, 7 passing)
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_ingestion.py

# Run with coverage
pytest --cov=cognitive_journal_agent tests/

# Run with verbose output
pytest -v tests/
```

---

## Performance Optimization

### Caching Strategies

1. **LLM Response Caching**: Cache common processing results (Redis/in-memory)
2. **Query Result Caching**: Cache daily summaries for 24 hours
3. **Connection Pooling**: Reuse database connections

### Async Processing

```python
import asyncio

async def process_batch(entries: List[JournalEntry]):
    """Process multiple entries concurrently."""
    tasks = [process_entry_async(entry) for entry in entries]
    results = await asyncio.gather(*tasks)
    return results
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-03
**Maintainer**: CJA Development Team
