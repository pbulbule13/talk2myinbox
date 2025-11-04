# Cognitive Journal Agent - Functional Specification

**Version**: 1.0.0
**Date**: 2025-11-03
**Status**: Production Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Product Overview](#product-overview)
3. [User Personas](#user-personas)
4. [User Stories](#user-stories)
5. [Use Cases](#use-cases)
6. [Feature Specifications](#feature-specifications)
7. [User Workflows](#user-workflows)
8. [Business Logic Rules](#business-logic-rules)
9. [Acceptance Criteria](#acceptance-criteria)
10. [Non-Functional Requirements](#non-functional-requirements)
11. [Future Features](#future-features)

---

## Executive Summary

The Cognitive Journal Agent (CJA) is an AI-powered personal assistant that captures, processes, and organizes multimodal inputs (text, voice, images, documents) to help users manage their daily activities, tasks, and reflections. The system uses LangGraph for orchestration, LangChain for agentic capabilities, and supports multiple storage backends.

**Key Value Propositions:**
- **Multimodal Input**: Accept 7 different input types (text, voice, photos, PDFs, code, email, calendar)
- **Intelligent Processing**: LLM-based analysis extracts action items, tags, emotions, and priorities
- **Agentic Execution**: Perform actions like sending emails, managing calendar, file operations
- **Daily Insights**: Generate comprehensive daily summaries and suggested priorities
- **Flexible Deployment**: Local, Docker, cloud (AWS, GCP), or Kubernetes

---

## Product Overview

### What is CJA?

CJA is a personal cognitive assistant that:
1. **Captures** multimodal inputs throughout the day
2. **Processes** them using AI to extract actionable insights
3. **Stores** structured journal entries and action items
4. **Reports** daily summaries with prioritized tasks
5. **Acts** on user requests through integrated tools (email, calendar, files, web)

### Target Audience

- **Knowledge Workers**: Professionals who need to capture meeting notes, action items, and ideas
- **Content Creators**: Writers, developers, researchers who want to organize thoughts and references
- **Personal Productivity Enthusiasts**: Individuals seeking to optimize their daily workflows
- **Teams**: Small teams needing shared task tracking and knowledge management

---

## User Personas

### Persona 1: Sarah - Product Manager

**Background:**
- Age: 32, Tech Industry Product Manager
- Works remotely, attends 5-7 meetings daily
- Needs to capture action items from multiple sources

**Goals:**
- Quickly capture meeting notes via voice memos
- Automatically extract action items from notes
- Get daily summary of all tasks with priorities
- Send follow-up emails directly from the system

**Pain Points:**
- Loses track of verbal commitments in meetings
- Manual task entry is time-consuming
- Difficulty prioritizing when overwhelmed

**How CJA Helps:**
- Voice memo transcription captures meeting notes
- LLM extracts action items automatically
- Daily summary shows prioritized tasks
- Email tool sends follow-ups without leaving system

---

### Persona 2: Alex - Software Developer

**Background:**
- Age: 28, Full-Stack Developer
- Juggles multiple projects and bug fixes
- Captures code snippets and technical notes

**Goals:**
- Save code snippets with context
- Track bugs and feature ideas
- Search past technical decisions
- Integrate with calendar for sprint planning

**Pain Points:**
- Scattered notes across multiple tools
- Loses context on why decisions were made
- Forgets to follow up on technical debt

**How CJA Helps:**
- Code snippet input type preserves syntax
- Contextual tagging makes search easy
- Calendar integration tracks sprint milestones
- File operations tool manages documentation

---

### Persona 3: Maria - Researcher

**Background:**
- Age: 45, Academic Researcher
- Reads 10-20 papers weekly
- Needs to organize findings and citations

**Goals:**
- Extract key insights from PDFs
- Organize research by themes
- Track paper citations and references
- Generate literature review summaries

**Pain Points:**
- Manual PDF annotation is tedious
- Difficult to connect ideas across papers
- Citation management is time-consuming

**How CJA Helps:**
- PDF input processing extracts text
- LLM identifies key entities and themes
- Contextual tags link related research
- Daily summaries highlight research patterns

---

## User Stories

### Epic 1: Input Capture

**US-01: Text Note Entry**
- **As a** user
- **I want to** quickly enter text notes via CLI or API
- **So that** I can capture thoughts without switching tools
- **Acceptance Criteria:**
  - Text input accepted via CLI command
  - Text input accepted via API endpoint
  - Entry created with timestamp and unique ID
  - Entry stored in configured backend

**US-02: Voice Memo Transcription**
- **As a** user
- **I want to** record voice memos that are automatically transcribed
- **So that** I can capture ideas hands-free
- **Acceptance Criteria:**
  - WAV/MP3 audio files accepted
  - Speech-to-text transcription using Google Speech Recognition
  - Transcribed text stored in journal entry
  - Original audio file optionally retained

**US-03: Image OCR Processing**
- **As a** user
- **I want to** upload photos of whiteboards or documents
- **So that** text content is extracted and searchable
- **Acceptance Criteria:**
  - JPG/PNG images accepted
  - OCR extraction using Tesseract
  - Extracted text stored in journal entry
  - Image file optionally retained

**US-04: PDF Document Processing**
- **As a** user
- **I want to** upload PDF documents for content extraction
- **So that** I can journal about research papers or reports
- **Acceptance Criteria:**
  - PDF files accepted
  - Text extraction using PyPDF2
  - Extracted text stored with PDF metadata
  - Page numbers and structure preserved

**US-05: Code Snippet Capture**
- **As a** developer
- **I want to** save code snippets with language and context
- **So that** I can reference solutions later
- **Acceptance Criteria:**
  - Code input with optional language specification
  - Syntax preserved in storage
  - Contextual tags include programming language
  - Searchable by language or keywords

**US-06: Email Integration**
- **As a** user
- **I want to** forward emails to the system for processing
- **So that** important email content is journaled
- **Acceptance Criteria:**
  - Email forwarding address configured
  - Subject, body, sender, and timestamp extracted
  - Email content stored as journal entry
  - Attachments optionally processed

**US-07: Calendar Event Capture**
- **As a** user
- **I want to** sync calendar events to the journal
- **So that** I have context for meeting notes
- **Acceptance Criteria:**
  - Google Calendar integration
  - Event title, time, attendees, and location stored
  - Calendar events linked to related notes
  - Automatic retrieval of today's events

---

### Epic 2: Intelligent Processing

**US-08: Automatic Tagging**
- **As a** user
- **I want to** have my entries automatically tagged
- **So that** I can find related entries easily
- **Acceptance Criteria:**
  - LLM extracts contextual tags (3-7 per entry)
  - Tags include topics, projects, people, locations
  - Tags stored in entry metadata
  - Tag-based search supported

**US-09: Action Item Extraction**
- **As a** user
- **I want to** have action items automatically identified
- **So that** I don't miss commitments buried in notes
- **Acceptance Criteria:**
  - LLM identifies actionable phrases ("need to", "should", "must")
  - Action items stored with priority (high/medium/low)
  - Due dates inferred from context when possible
  - Action items linked to source journal entry

**US-10: Emotion Detection**
- **As a** user
- **I want to** track my emotional state over time
- **So that** I can identify stress patterns
- **Acceptance Criteria:**
  - LLM infers emotion from entry content
  - Emotions categorized (happy, stressed, neutral, excited, frustrated)
  - Emotion stored in entry metadata
  - Emotion trends shown in daily summaries

**US-11: Priority Scoring**
- **As a** user
- **I want to** have entries scored by importance
- **So that** critical items are highlighted
- **Acceptance Criteria:**
  - LLM assigns priority score (1-10)
  - Scoring considers urgency keywords, deadlines, sentiment
  - High-priority entries (8+) flagged in summaries
  - Priority scores influence task ordering

**US-12: Entity Recognition**
- **As a** user
- **I want to** have people, companies, and projects identified
- **So that** I can track interactions and context
- **Acceptance Criteria:**
  - LLM extracts named entities (people, organizations, projects)
  - Entities stored in structured format
  - Entity-based search supported
  - Entity co-occurrence tracked for relationship mapping

---

### Epic 3: Storage & Retrieval

**US-13: Multi-Backend Storage**
- **As a** user
- **I want to** choose between local and cloud storage
- **So that** I can control where my data lives
- **Acceptance Criteria:**
  - JSON file storage supported (local development)
  - SQLite storage supported (local production)
  - Firestore storage supported (cloud deployment)
  - Backend selection via environment variable

**US-14: Entry Search**
- **As a** user
- **I want to** search my journal by keywords, tags, or dates
- **So that** I can find past entries quickly
- **Acceptance Criteria:**
  - Full-text search across entry content
  - Tag-based filtering
  - Date range filtering
  - Search results ranked by relevance

**US-15: Action Item Management**
- **As a** user
- **I want to** view, update, and complete action items
- **So that** I can track my progress
- **Acceptance Criteria:**
  - List all pending action items
  - Mark action items as complete
  - Update action item details (description, due date, priority)
  - View completed action items history

**US-16: Data Export**
- **As a** user
- **I want to** export my journal data
- **So that** I can use it in other tools or for backup
- **Acceptance Criteria:**
  - Export to JSON format
  - Export to CSV format
  - Export date range selection
  - Export includes all metadata (tags, action items, emotions)

---

### Epic 4: Reporting & Insights

**US-17: Daily Summary Generation**
- **As a** user
- **I want to** receive a daily summary of my journal entries
- **So that** I can reflect on my day
- **Acceptance Criteria:**
  - Summary generated on demand or scheduled
  - Includes entry count, key themes, emotion overview
  - Lists all action items with priorities
  - Suggests first task for next day

**US-18: Voice Summary Output**
- **As a** user
- **I want to** have my daily summary read aloud
- **So that** I can listen while doing other tasks
- **Acceptance Criteria:**
  - ElevenLabs TTS integration (cloud)
  - Local pyttsx3 TTS (fallback)
  - Audio file saved for later playback
  - Voice selection configurable

**US-19: Weekly Review**
- **As a** user
- **I want to** receive a weekly review of accomplishments
- **So that** I can track progress on goals
- **Acceptance Criteria:**
  - Weekly summary includes entry trends
  - Action item completion rate calculated
  - Emotion trends visualized (text description)
  - Key achievements highlighted

**US-20: Trend Analysis**
- **As a** user
- **I want to** see trends in my journaling patterns
- **So that** I can identify productivity insights
- **Acceptance Criteria:**
  - Entry frequency by day of week
  - Most common tags and themes
  - Emotion distribution over time
  - Peak productivity times identified

---

### Epic 5: Agentic Actions

**US-21: Email Sending**
- **As a** user
- **I want to** send emails based on action items
- **So that** I can act on commitments without leaving the system
- **Acceptance Criteria:**
  - Email sending via SMTP (Gmail, Outlook, custom)
  - Recipient, subject, body specified in request
  - Email marked as sent in action item
  - Error handling for failed sends

**US-22: Calendar Management**
- **As a** user
- **I want to** create and update calendar events
- **So that** I can schedule action items
- **Acceptance Criteria:**
  - Create events in Google Calendar
  - Update existing event details
  - Delete events
  - List events for date range

**US-23: File Operations**
- **As a** user
- **I want to** perform file operations via agent
- **So that** I can manage documents from journal context
- **Acceptance Criteria:**
  - Read file contents
  - Write new files
  - Append to existing files
  - Delete files
  - File path validation and security checks

**US-24: Web Search**
- **As a** user
- **I want to** search the web for information related to entries
- **So that** I can enrich my journal with external context
- **Acceptance Criteria:**
  - Web search via API (DuckDuckGo or similar)
  - Search results returned with titles and snippets
  - Results stored as new journal entry
  - Search queries logged for context

**US-25: Custom Agent Actions**
- **As a** user
- **I want to** define custom agent actions
- **So that** I can extend the system's capabilities
- **Acceptance Criteria:**
  - Custom tool definition via LangChain tool interface
  - Tool registration in agent executor
  - Tool invocation via natural language
  - Tool results returned to user

---

## Use Cases

### Use Case 1: Morning Planning Routine

**Actor:** Sarah (Product Manager)

**Preconditions:**
- User has journal entries from previous day
- System has calendar access

**Main Flow:**
1. User requests daily summary: "Show me yesterday's summary"
2. System retrieves all entries from previous day
3. System generates summary with:
   - Entry count and types
   - Key themes and topics
   - Pending action items
   - Suggested first task
4. System reads summary aloud via TTS
5. User reviews and decides on first task

**Postconditions:**
- User has clear understanding of priorities
- First task is identified

**Alternative Flows:**
- **No entries from previous day**: System returns "No entries found for yesterday"
- **TTS unavailable**: System displays text summary only

---

### Use Case 2: Meeting Notes Capture

**Actor:** Sarah (Product Manager)

**Preconditions:**
- User is in a meeting or immediately after
- Voice recording device available

**Main Flow:**
1. User records voice memo during/after meeting
2. User uploads audio file: `cja-cli voice_memo meeting_notes.wav`
3. System transcribes audio using speech recognition
4. System processes transcription:
   - Extracts action items
   - Identifies participants (from context)
   - Determines priority
   - Assigns contextual tags
5. System stores journal entry
6. System confirms: "Journal entry created. 3 action items extracted."

**Postconditions:**
- Meeting notes stored as journal entry
- Action items available for follow-up

**Alternative Flows:**
- **Transcription fails**: System prompts for manual text entry
- **No action items found**: System stores entry without action items

---

### Use Case 3: Research Paper Processing

**Actor:** Maria (Researcher)

**Preconditions:**
- User has PDF of research paper
- PDF contains extractable text

**Main Flow:**
1. User uploads PDF: `cja-cli pdf_document research_paper.pdf`
2. System extracts text from all pages
3. System processes content:
   - Identifies key entities (authors, methods, findings)
   - Extracts potential citations
   - Assigns research topic tags
   - Calculates relevance score
4. System stores journal entry with PDF metadata
5. System responds: "Paper processed. Key themes: machine learning, NLP, transformers. 5 citations extracted."

**Postconditions:**
- Paper content searchable in journal
- Citations available for reference management

**Alternative Flows:**
- **PDF encrypted or image-based**: System attempts OCR, prompts if fails
- **Processing timeout**: System stores raw text, defers detailed analysis

---

### Use Case 4: Action Item Execution

**Actor:** Alex (Developer)

**Preconditions:**
- User has pending action items
- Required tools configured (email, calendar)

**Main Flow:**
1. User reviews action items: "Show my pending tasks"
2. System displays prioritized action list
3. User selects action: "Send follow-up email to John about API design"
4. System uses agent to compose email:
   - Retrieves context from related journal entries
   - Drafts email body
   - Confirms with user
5. User approves: "Send it"
6. System sends email via SMTP
7. System marks action item as complete
8. System confirms: "Email sent to john@example.com. Action item completed."

**Postconditions:**
- Email sent
- Action item marked complete
- User's task list updated

**Alternative Flows:**
- **Email send fails**: System retries, notifies user if persistent failure
- **User cancels**: Action item remains pending

---

### Use Case 5: Code Snippet Archiving

**Actor:** Alex (Developer)

**Preconditions:**
- User finds useful code snippet
- User wants to save for future reference

**Main Flow:**
1. User saves snippet: `cja-cli code_snippet --language python`
2. System prompts for code input (multi-line)
3. User pastes code and adds context: "JWT token validation helper"
4. System processes:
   - Detects programming language (Python)
   - Extracts function names
   - Assigns tags: python, security, jwt, authentication
5. System stores entry with code formatting preserved
6. System confirms: "Code snippet saved. Tags: python, security, jwt."

**Postconditions:**
- Code snippet stored with syntax preservation
- Searchable by language and tags

**Alternative Flows:**
- **Invalid code syntax**: System stores anyway, adds note
- **Language not specified**: System attempts auto-detection

---

## Feature Specifications

### Feature 1: Multimodal Input Processing

**Feature ID:** F-001
**Priority:** P0 (Critical)
**Status:** Implemented

**Description:**
System accepts 7 input types and converts them to structured journal entries.

**Input Types:**
1. **text_note**: Plain text input via CLI or API
2. **voice_memo**: Audio files (WAV, MP3) transcribed via speech recognition
3. **photo_ocr**: Images (JPG, PNG) processed via Tesseract OCR
4. **pdf_document**: PDF files with text extraction
5. **code_snippet**: Code with language specification
6. **email**: Email forwarding integration
7. **calendar_event**: Calendar sync integration

**Technical Implementation:**
- Class: `MultimodalIngest` in `nodes/ingestion.py`
- Method per input type: `process_text_note()`, `process_voice_memo()`, etc.
- Dependencies: SpeechRecognition, Tesseract, PyPDF2, Pillow
- Fallback: If optional dependency missing, graceful error message

**Validation Rules:**
- All input types must generate valid `JournalEntry` Pydantic model
- `timestamp` automatically generated if not provided
- `source_id` must be unique (UUID generated if not provided)
- `raw_content` must be non-empty string

**Error Handling:**
- Invalid file formats: Return error message with supported formats
- File not found: Return descriptive error
- Processing failure: Store entry with error flag, continue operation

---

### Feature 2: LLM-Based Content Analysis

**Feature ID:** F-002
**Priority:** P0 (Critical)
**Status:** Implemented

**Description:**
System uses LLMs (OpenAI GPT-4, Anthropic Claude) to extract structured insights from journal entries.

**Extracted Information:**
1. **Contextual Tags**: 3-7 tags describing topics, projects, people, locations
2. **Action Items**: Task descriptions with inferred priorities
3. **Emotion**: Inferred emotional state (happy, stressed, neutral, excited, frustrated)
4. **Priority Score**: 1-10 urgency/importance rating
5. **Key Entities**: Named entities (people, organizations, projects)

**Technical Implementation:**
- Class: `ProcessEntry` in `nodes/processing.py`
- LLM Provider: Configurable (OpenAI, Anthropic, or local)
- Output Parsing: Pydantic `ProcessedContent` model
- Prompt Engineering: Few-shot examples for consistent output
- Fallback: Rule-based processing if LLM unavailable

**LLM Configuration:**
```python
llm:
  provider: openai  # or anthropic, local
  model: gpt-4-turbo-preview
  temperature: 0.3  # Lower for consistency
  max_tokens: 1000
  fallback_to_rules: true
```

**Rule-Based Fallback:**
- Tags: Keyword extraction via NLTK/spaCy
- Action items: Regex patterns for action verbs
- Emotion: Sentiment analysis via TextBlob
- Priority: Keyword-based heuristics
- Entities: Basic NER via spaCy

**Validation Rules:**
- Tags must be lowercase, alphanumeric + hyphen
- Action items must have non-empty description
- Emotion must be from predefined set
- Priority score must be 1-10 integer

---

### Feature 3: Multi-Backend Storage

**Feature ID:** F-003
**Priority:** P0 (Critical)
**Status:** Implemented

**Description:**
System supports multiple storage backends via repository pattern, selectable via configuration.

**Supported Backends:**
1. **JSON**: Local file storage (development)
2. **SQLite**: Local database (production)
3. **Firestore**: Google Cloud NoSQL (cloud production)

**Technical Implementation:**
- Abstract Interface: `StorageBackend` protocol
- Implementations: `JSONStorage`, `SQLiteStorage`, `FirestoreStorage`
- Facade: `StorageManager` selects backend based on environment
- Configuration: `STORAGE_BACKEND` environment variable

**Storage Operations:**
- `save_journal_entry(entry: JournalEntry)`: Store new entry
- `get_journal_entry(entry_id: str)`: Retrieve by ID
- `query_entries(filters: dict)`: Search entries
- `save_action_item(item: ActionItem)`: Store action item
- `get_pending_actions()`: Retrieve incomplete action items
- `mark_action_complete(task_id: str)`: Update action item status

**Data Persistence:**
- JSON: `data/journal_entries.json`, `data/action_items.json`
- SQLite: `data/cja_database.db` (tables: journal_entries, action_items)
- Firestore: Collections: `journal_entries`, `action_items`

**Migration Support:**
- Export from any backend to JSON
- Import JSON to any backend
- Migration scripts in `utils/migrate_data.py`

---

### Feature 4: Daily Summary Reports

**Feature ID:** F-004
**Priority:** P1 (High)
**Status:** Implemented

**Description:**
System generates comprehensive daily summaries with prioritized action items and insights.

**Summary Components:**
1. **Metadata**: Date, total entries, input type distribution
2. **Key Themes**: Most common tags (top 5)
3. **Emotion Overview**: Dominant emotion and distribution
4. **Action Items**: All pending tasks, sorted by priority
5. **Suggested First Task**: Highest priority or most urgent
6. **Notable Insights**: LLM-generated reflections (optional)

**Technical Implementation:**
- Class: `ReportGenerator` in `nodes/reporting.py`
- Aggregation: Query storage for date range
- LLM Summarization: Optional for insights section
- Output: `DailySummaryOutput` Pydantic model

**Generation Triggers:**
- User request: "Show today's summary"
- Scheduled: Daily at configured time (cron job)
- API call: `POST /api/summary` with date parameter

**Output Formats:**
- Text: Formatted string for CLI display
- JSON: Structured data for API responses
- Audio: TTS-generated speech file (MP3)

**Example Output:**
```
Daily Summary for 2025-11-03
============================

Total Entries: 12
Input Types: 5 voice memos, 4 text notes, 2 PDFs, 1 code snippet

Key Themes: product-management, api-design, team-meetings, documentation, deadlines

Emotion Overview: Stressed (40%), Focused (30%), Neutral (30%)

Pending Action Items (7):
  [HIGH] Follow up with John on API design decisions (Due: Today)
  [HIGH] Review PR #245 before EOD (Due: Today)
  [MED] Update sprint planning doc (Due: 2025-11-04)
  [MED] Schedule 1:1 with Sarah (Due: This week)
  [LOW] Research GraphQL alternatives (Due: Next week)

Suggested First Task: Follow up with John on API design decisions

Notable Insights: Today showed high stress related to approaching deadlines.
Consider delegating the GraphQL research task to reduce cognitive load.
```

---

### Feature 5: Agentic Tool Execution

**Feature ID:** F-005
**Priority:** P1 (High)
**Status:** Implemented

**Description:**
System uses LangChain agent executor to perform actions based on user requests or action items.

**Available Tools:**
1. **SendEmailTool**: Send emails via SMTP
2. **CalendarManagementTool**: Create/update/delete calendar events
3. **FileOperationsTool**: Read, write, append, delete files
4. **WebSearchTool**: Search the web for information

**Technical Implementation:**
- Class: `AgentExecutor` in `nodes/agent.py`
- Framework: LangChain's `create_react_agent` with GPT-4
- Tool Definitions: LangChain `BaseTool` subclasses in `tools/external_tools.py`
- Error Handling: Retry logic with exponential backoff

**Agent Prompt:**
```
You are a helpful personal assistant. Use the available tools to help the user
complete tasks based on their journal entries and action items. Always confirm
actions with the user before performing operations that send emails or modify
external systems.
```

**Tool Input Validation:**
- Pydantic schemas for each tool's arguments
- Schema enforcement via `args_schema` attribute
- Invalid input returns error message to agent

**Security Considerations:**
- File operations restricted to allowed directories (configurable)
- Email sending rate limited
- Calendar operations require valid authentication
- Web search queries sanitized

---

### Feature 6: Voice Output (TTS)

**Feature ID:** F-006
**Priority:** P2 (Medium)
**Status:** Implemented

**Description:**
System converts daily summaries and reports to speech audio files.

**TTS Providers:**
1. **ElevenLabs**: Cloud-based, high-quality voices (primary)
2. **pyttsx3**: Local, offline TTS (fallback)

**Technical Implementation:**
- Class: `VoiceOutput` in `nodes/output.py`
- Cloud: ElevenLabs API with voice selection
- Local: pyttsx3 with system voices
- Output: MP3 audio files saved to `data/audio/`

**Voice Configuration:**
```python
tts:
  provider: elevenlabs  # or local
  elevenlabs:
    api_key: ${ELEVENLABS_API_KEY}
    voice_id: ${ELEVENLABS_VOICE_ID}
    model_id: eleven_monolingual_v1
  local:
    rate: 150  # Words per minute
    volume: 0.9
```

**Usage:**
- Automatic: TTS generated when summary requested
- On-demand: User can request specific text be converted
- Playback: Audio file path returned for user playback

---

## User Workflows

### Workflow 1: Daily Journal Entry Flow

```
[User] --text/voice/image--> [System: Ingestion]
                                      |
                                      v
                            [System: Processing]
                                      |
                          +-----------+------------+
                          |                        |
                    [Extract Tags]          [Extract Actions]
                          |                        |
                          v                        v
                    [Apply Rules]            [Calculate Priority]
                          |                        |
                          +------------+-----------+
                                       |
                                       v
                              [System: Storage]
                                       |
                                       v
                              [Confirm to User]
```

**Step Details:**
1. User provides input (any of 7 types)
2. Ingestion node converts to `JournalEntry`
3. Processing node enriches with LLM analysis
4. Storage node persists to configured backend
5. User receives confirmation with extracted insights

**Time Estimate:** 2-10 seconds (depending on input type and LLM)

---

### Workflow 2: Daily Summary Generation Flow

```
[User Request] --> [System: Check Cache]
                          |
                    Cache Miss?
                          |
                          v
                [System: Query Storage]
                          |
                          v
                [Aggregate Entries by Date]
                          |
                          v
                [LLM: Generate Summary]
                          |
                          v
                [Format Output (Text/JSON)]
                          |
                   +------+------+
                   |             |
            [Display]      [Generate TTS]
                                 |
                                 v
                          [Save Audio File]
                                 |
                                 v
                          [Return Audio Path]
```

**Step Details:**
1. User requests summary (CLI or API)
2. System checks if summary cached for date
3. If not cached, query storage for all entries in date range
4. Aggregate statistics (count, themes, emotions)
5. LLM generates narrative summary
6. Format output based on request type
7. Optionally generate TTS audio
8. Return summary to user

**Time Estimate:** 5-15 seconds (first generation), <1 second (cached)

---

### Workflow 3: Action Item Execution Flow

```
[User: "Send email to X"] --> [System: Agent Router]
                                      |
                                      v
                              [LangChain Agent]
                                      |
                              [Select Tool: SendEmail]
                                      |
                                      v
                              [Extract Parameters]
                                      |
                           (recipient, subject, body)
                                      |
                                      v
                              [Validate Parameters]
                                      |
                                  Valid?
                                      |
                         +------------+------------+
                         |                         |
                       Yes                        No
                         |                         |
                         v                         v
                  [Execute Tool]          [Request Clarification]
                         |
                +--------+--------+
                |                 |
             Success           Failure
                |                 |
                v                 v
        [Update Action Item] [Log Error, Retry]
                |
                v
        [Confirm to User]
```

**Step Details:**
1. User requests action (natural language)
2. Agent router determines appropriate tool
3. Agent extracts parameters from context
4. Parameters validated via Pydantic schema
5. Tool executed with error handling
6. Result returned to user
7. Related action item marked complete

**Time Estimate:** 3-30 seconds (depending on tool and external API latency)

---

## Business Logic Rules

### Rule 1: Priority Calculation

**Rule ID:** BR-001

**Condition:** When processing a journal entry or action item

**Logic:**
```python
priority_score = 5  # Default: Medium

# +3 points for urgency keywords
if any(keyword in content.lower() for keyword in ["urgent", "asap", "critical", "emergency"]):
    priority_score += 3

# +2 points for deadline mentions
if any(keyword in content.lower() for keyword in ["today", "eod", "deadline", "due"]):
    priority_score += 2

# +1 point for negative emotion
if emotion in ["stressed", "frustrated", "anxious"]:
    priority_score += 1

# -1 point for future tense
if any(keyword in content.lower() for keyword in ["eventually", "someday", "later"]):
    priority_score -= 1

# Clamp to 1-10 range
priority_score = max(1, min(10, priority_score))
```

**Output:** Integer from 1 (lowest) to 10 (highest)

---

### Rule 2: Action Item Classification

**Rule ID:** BR-002

**Condition:** When extracting action items from text

**Logic:**
```python
action_patterns = [
    r"(need|needs) to \w+",
    r"(should|must|have to) \w+",
    r"(will|going to) \w+",
    r"(todo|TODO): .+",
    r"(action item|task): .+"
]

for pattern in action_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    for match in matches:
        action_items.append({
            "description": match,
            "priority": calculate_priority(match),
            "source": entry_id
        })
```

**Output:** List of `ActionItem` objects

---

### Rule 3: Tag Relevance Filtering

**Rule ID:** BR-003

**Condition:** When LLM generates more than 7 tags

**Logic:**
```python
if len(tags) > 7:
    # Filter by relevance score (TF-IDF or frequency)
    scored_tags = [(tag, calculate_relevance(tag, content)) for tag in tags]
    scored_tags.sort(key=lambda x: x[1], reverse=True)
    tags = [tag for tag, score in scored_tags[:7]]
```

**Output:** Maximum 7 most relevant tags

---

### Rule 4: Emotion Override

**Rule ID:** BR-004

**Condition:** When user explicitly states emotion

**Logic:**
```python
explicit_emotions = {
    "i feel": r"i feel (\w+)",
    "i am": r"i am (feeling )?([\w]+)",
    "feeling": r"feeling (very )?([\w]+)"
}

for pattern_name, pattern in explicit_emotions.items():
    match = re.search(pattern, content.lower())
    if match:
        emotion = match.group(-1)  # Last capture group
        if emotion in VALID_EMOTIONS:
            return emotion  # Override LLM inference
```

**Output:** User-stated emotion takes precedence over LLM inference

---

### Rule 5: Duplicate Entry Prevention

**Rule ID:** BR-005

**Condition:** Before saving a new journal entry

**Logic:**
```python
# Check for duplicate within 5-minute window
recent_entries = query_entries(
    timestamp_after=current_time - timedelta(minutes=5)
)

for existing in recent_entries:
    similarity = calculate_similarity(new_entry.raw_content, existing.raw_content)
    if similarity > 0.9:  # 90% similar
        return {"status": "duplicate", "existing_id": existing.entry_id}

# Not a duplicate, proceed with save
save_entry(new_entry)
```

**Output:** Prevent accidental duplicate submissions

---

## Acceptance Criteria

### AC-1: Input Processing

**Feature:** Multimodal Input (F-001)

**Criteria:**
- [ ] All 7 input types accepted without errors
- [ ] Invalid input types return descriptive error messages
- [ ] File uploads validate file size (max 10MB default)
- [ ] Processing time < 10 seconds for standard inputs
- [ ] Invalid files (corrupted, wrong format) handled gracefully
- [ ] Successful processing returns entry ID confirmation

**Test Verification:**
- Unit tests: `tests/test_ingestion.py` (7/7 passing)
- Integration tests: `tests/test_integration.py`

---

### AC-2: LLM Processing

**Feature:** LLM-Based Content Analysis (F-002)

**Criteria:**
- [ ] Tags extracted with 80%+ relevance (manual review)
- [ ] Action items detected with 90%+ accuracy (benchmark dataset)
- [ ] Emotion inference correlates with sentiment (80%+ agreement)
- [ ] Priority scores consistent with human ratings (Pearson r > 0.7)
- [ ] Fallback to rule-based processing when LLM unavailable
- [ ] Processing time < 5 seconds for entries < 1000 words

**Test Verification:**
- Unit tests: `tests/test_processing.py`
- Benchmark: 100 manually-labeled entries

---

### AC-3: Storage Reliability

**Feature:** Multi-Backend Storage (F-003)

**Criteria:**
- [ ] All CRUD operations succeed for each backend
- [ ] Data consistency maintained (write-read verification)
- [ ] Concurrent writes handled without data loss
- [ ] Query operations return correct results
- [ ] Backend failure triggers graceful degradation
- [ ] Data migration between backends preserves all fields

**Test Verification:**
- Unit tests: `tests/test_storage.py` (9/9 passing)
- Load tests: 1000 concurrent writes

---

### AC-4: Summary Accuracy

**Feature:** Daily Summary Reports (F-004)

**Criteria:**
- [ ] Summary includes all entries for specified date
- [ ] Statistics calculated correctly (counts, distributions)
- [ ] Action items sorted by priority
- [ ] Suggested first task aligns with priorities
- [ ] TTS audio matches text summary content
- [ ] Generated summary readable (Flesch score > 60)

**Test Verification:**
- Unit tests: `tests/test_reporting.py`
- Manual review: 20 sample summaries

---

### AC-5: Agent Actions

**Feature:** Agentic Tool Execution (F-005)

**Criteria:**
- [ ] Agent correctly selects appropriate tool (95%+ accuracy)
- [ ] Tool parameters extracted from natural language
- [ ] Invalid parameters trigger user clarification
- [ ] Tool execution errors handled with retry logic
- [ ] Successful actions update related entries
- [ ] User confirmation required for destructive operations

**Test Verification:**
- Integration tests: `tests/test_agent_integration.py`
- Manual testing: 50 sample commands

---

## Non-Functional Requirements

### NFR-1: Performance

**Requirement ID:** NFR-001
**Priority:** P0

**Specifications:**
- **Input Processing**: < 10 seconds for standard inputs (text, voice < 2min)
- **LLM Processing**: < 5 seconds for entries < 1000 words
- **Storage Operations**: < 100ms for writes, < 50ms for reads (local)
- **API Response Time**: p95 < 500ms for standard requests
- **Concurrent Users**: Support 100 concurrent API requests
- **Throughput**: Process 1000 entries/hour on standard hardware

**Measurement:**
- Performance benchmarks in `tests/performance/`
- Monitoring via Prometheus metrics
- Load testing with Locust

---

### NFR-2: Scalability

**Requirement ID:** NFR-002
**Priority:** P1

**Specifications:**
- **Data Volume**: Support 10,000+ journal entries per user
- **User Growth**: Horizontally scalable to 10,000+ users (cloud deployment)
- **Storage Growth**: Linear performance degradation with data size
- **LLM Caching**: Cache common processing results to reduce API calls
- **Rate Limiting**: Configurable per-user rate limits

**Approach:**
- Firestore for cloud scalability
- LLM response caching (Redis)
- Async processing for long-running tasks
- Read replicas for query scaling

---

### NFR-3: Reliability

**Requirement ID:** NFR-003
**Priority:** P0

**Specifications:**
- **Uptime**: 99.9% availability (cloud deployment)
- **Data Durability**: 99.99999% (Firestore guarantees)
- **Error Rate**: < 0.1% of requests result in errors
- **Fallback Mechanisms**: All LLM dependencies have rule-based fallbacks
- **Graceful Degradation**: Reduced functionality better than total failure

**Approach:**
- Health check endpoints (`/health`, `/ready`)
- Retry logic with exponential backoff
- Circuit breakers for external API calls
- Backup storage in multiple zones

---

### NFR-4: Security

**Requirement ID:** NFR-004
**Priority:** P0

**Specifications:**
- **Authentication**: API key or OAuth 2.0 for API access
- **Encryption**: Data encrypted at rest (AES-256) and in transit (TLS 1.3)
- **Secrets Management**: Environment variables or secret manager (AWS SSM, GCP Secret Manager)
- **Input Validation**: All user inputs sanitized and validated
- **File Operations**: Restricted to allowed directories
- **Rate Limiting**: Prevent abuse (100 requests/minute per user)

**Approach:**
- FastAPI dependency injection for auth
- Firestore encryption by default
- Parameterized queries (SQLite)
- Input validation via Pydantic

---

### NFR-5: Usability

**Requirement ID:** NFR-005
**Priority:** P1

**Specifications:**
- **CLI Intuitiveness**: Commands follow standard conventions
- **Error Messages**: Clear, actionable error descriptions
- **Documentation**: Comprehensive docs for all features
- **Onboarding**: New user can create first entry in < 5 minutes
- **Help System**: `--help` flag for all commands

**Approach:**
- Consistent CLI interface (argparse)
- Interactive prompts for complex inputs
- Example usage in help text
- Quickstart guide in README

---

### NFR-6: Maintainability

**Requirement ID:** NFR-006
**Priority:** P1

**Specifications:**
- **Code Quality**: Type hints, docstrings, linting (Ruff)
- **Test Coverage**: > 80% code coverage
- **Modularity**: Loosely coupled components
- **Configuration**: Externalized via environment variables
- **Logging**: Structured logging (JSON format) at multiple levels

**Approach:**
- Pydantic for type safety
- Repository pattern for storage abstraction
- Strategy pattern for LLM vs rule-based processing
- Comprehensive unit and integration tests

---

### NFR-7: Observability

**Requirement ID:** NFR-007
**Priority:** P2

**Specifications:**
- **Logging**: INFO level for operations, DEBUG for development
- **Metrics**: Prometheus-compatible metrics (request counts, latencies)
- **Tracing**: Distributed tracing for multi-service deployments (OpenTelemetry)
- **Alerting**: Notifications for critical errors or performance degradation

**Approach:**
- Structured logging via Python `logging` module
- Custom metrics via Prometheus client
- OpenTelemetry instrumentation for FastAPI
- Integration with monitoring platforms (Datadog, Grafana)

---

## Future Features

### FF-1: Mobile App

**Description:** Native iOS/Android apps with voice recording and photo capture

**Priority:** P2
**Timeline:** Q2 2026

**User Stories:**
- US-26: As a mobile user, I want to capture voice memos on the go
- US-27: As a mobile user, I want to photograph whiteboards and process them

**Technical Approach:**
- React Native for cross-platform development
- Direct integration with CJA REST API
- Offline mode with sync when connected

---

### FF-2: Collaborative Journaling

**Description:** Share journal entries and action items with team members

**Priority:** P2
**Timeline:** Q3 2026

**User Stories:**
- US-28: As a team lead, I want to share meeting notes with my team
- US-29: As a team member, I want to see shared action items

**Technical Approach:**
- Multi-user authentication
- Permission-based access control
- Real-time updates via WebSockets

---

### FF-3: Advanced Analytics

**Description:** Visualizations and insights dashboard

**Priority:** P3
**Timeline:** Q4 2026

**User Stories:**
- US-30: As a user, I want to see my productivity trends over time
- US-31: As a user, I want to visualize emotion patterns

**Technical Approach:**
- React dashboard with Chart.js
- Time-series analysis of entry patterns
- Correlation analysis (emotion vs. productivity)

---

### FF-4: Third-Party Integrations

**Description:** Integrate with Slack, Notion, Todoist, etc.

**Priority:** P2
**Timeline:** Q1 2027

**User Stories:**
- US-32: As a Slack user, I want to send messages to CJA via Slack bot
- US-33: As a Notion user, I want to sync entries to Notion database

**Technical Approach:**
- OAuth integrations with each platform
- Webhook receivers for event-driven updates
- Plugin architecture for extensibility

---

### FF-5: Voice Command Interface

**Description:** Natural language voice commands for all operations

**Priority:** P3
**Timeline:** Q2 2027

**User Stories:**
- US-34: As a user, I want to say "Show me today's summary" and hear it
- US-35: As a user, I want to say "Send email to X about Y" hands-free

**Technical Approach:**
- Wake word detection (e.g., "Hey CJA")
- Full voice interface with TTS feedback
- Integration with smart speakers (Alexa, Google Home)

---

## Appendix A: Glossary

**Terms:**

- **Journal Entry**: Single instance of captured content with metadata
- **Action Item**: Extracted task from journal entries
- **Contextual Tag**: Topic or theme label for categorization
- **Priority Score**: 1-10 rating of urgency/importance
- **Storage Backend**: Underlying persistence layer (JSON, SQLite, Firestore)
- **LangGraph**: Framework for building stateful, multi-actor LLM applications
- **LangChain**: Framework for building applications with LLMs
- **Pydantic**: Data validation library using Python type hints
- **TTS**: Text-to-Speech synthesis
- **OCR**: Optical Character Recognition
- **Agent**: LLM-powered executor that selects and uses tools

---

## Appendix B: Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-03 | CJA Team | Initial release |

---

**Document Status:** Production Ready
**Next Review Date:** 2026-02-01
**Owner:** Product Management Team
**Contact:** product@cja.example.com

---
