# Talk2MyInbox - Architecture Documentation

## System Architecture Overview

Talk2MyInbox is a modern, microservices-inspired application built with a clean separation of concerns. The system follows a **3-tier architecture** with a presentation layer (frontend), business logic layer (backend API + agents), and data layer (Gmail/Calendar APIs).

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Browser)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   HTML/CSS   │  │  JavaScript  │  │  Voice Module   │  │
│  │  (Tailwind)  │  │   (Vanilla)  │  │ (Web Speech API)│  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI Server)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Layer (FastAPI)                  │  │
│  │  • /voice-agent/emails     • /voice-agent/calendar   │  │
│  │  • /voice-agent/query      • /voice-agent/tts        │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │          Orchestrator (Coordinator)                   │  │
│  │  • Session Management  • Query Processing             │  │
│  │  • Agent Coordination  • State Management             │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │      LangGraph Workflow (State Machine)              │  │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌──────┐      │  │
│  │  │Intent│→│Context│→│Reason│→│Draft│→│Author│→...   │  │
│  │  └─────┘  └─────┘  └─────┘  └─────┘  └──────┘      │  │
│  │  8-stage pipeline with conditional routing            │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              Agents Layer                             │  │
│  │  • IntentAgent      • ReasoningAgent                  │  │
│  │  • ContextAgent     • DraftAgent                      │  │
│  │  • AuthAgent        • ExecutionAgent                  │  │
│  │  • ResponseAgent    • LoggingAgent                    │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │            Adapters Layer                             │  │
│  │  ┌──────────────┐           ┌──────────────┐         │  │
│  │  │ Email Adapter│           │Calendar Adapt│         │  │
│  │  │  (Abstract)  │           │  (Abstract)  │         │  │
│  │  └──────┬───────┘           └──────┬───────┘         │  │
│  │         │                           │                  │  │
│  │  ┌──────▼───────┐           ┌──────▼───────┐         │  │
│  │  │Gmail Adapter │           │GCal Adapter  │         │  │
│  │  └──────────────┘           └──────────────┘         │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               External Services Layer                        │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────┐      │
│  │ Gmail API  │  │ Calendar API │  │   AI APIs     │      │
│  │ (Google)   │  │   (Google)   │  │(Euron/OpenAI) │      │
│  └────────────┘  └──────────────┘  └───────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer

**Technology Stack:**
- Vanilla JavaScript (ES6+)
- Tailwind CSS (CDN)
- Web Speech API
- Fetch API for HTTP requests

**Components:**
- `communications_enhanced.js` - Main email/calendar UI logic
- `voice_module.js` - Voice recognition and synthesis
- `support.js` - Help and support features
- `index.html` - Single-page application

**Key Features:**
- Responsive design with mobile support
- Real-time updates via polling (60s intervals)
- Client-side email categorization
- Thread grouping and pagination
- Voice interaction capabilities

### 2. Backend Layer

#### 2.1 FastAPI Server

**File:** `backend/server.py`

**Responsibilities:**
- HTTP request routing
- Static file serving
- CORS handling
- Health check endpoints

**Configuration:**
- Host: `0.0.0.0` (configurable)
- Port: `8000` (configurable)
- Auto-reload in development
- Uvicorn ASGI server

#### 2.2 API Router

**File:** `backend/voice_agent/api/routes.py`

**Endpoints:**

**Email Endpoints:**
```
GET  /voice-agent/emails              - List emails
POST /voice-agent/email/send          - Send email
POST /voice-agent/emails/search       - Search emails
POST /voice-agent/email/mark-read     - Mark as read
POST /voice-agent/email/archive       - Archive email
POST /voice-agent/email/delete        - Delete email
```

**Calendar Endpoints:**
```
GET    /voice-agent/calendar           - Get events
GET    /voice-agent/calendar/events    - List events
POST   /voice-agent/calendar/event     - Create event
PUT    /voice-agent/calendar/event/:id - Update event
DELETE /voice-agent/calendar/event/:id - Delete event
GET    /voice-agent/calendar/check     - Check availability
```

**AI/Voice Endpoints:**
```
POST /voice-agent/query    - Process AI query
POST /voice-agent/tts      - Text-to-speech
WS   /voice-agent/ws       - WebSocket for streaming
```

**Support Endpoints:**
```
GET  /voice-agent/help           - Get help info
POST /voice-agent/support/ticket - Create support ticket
```

#### 2.3 Orchestrator

**File:** `backend/voice_agent/orchestrator.py`

**Purpose:** Central coordinator for all operations

**Key Methods:**
- `process_query(query, user_id, mode)` - Main entry point
- `summarize_inbox(user_id)` - Inbox summary
- `draft_reply(thread_id, instructions)` - Draft email
- `check_calendar(timeframe)` - Calendar query
- `create_session(user_id)` - Session management
- `get_session(session_id)` - Retrieve session
- `update_session(session_id, updates)` - Update session
- `delete_session(session_id)` - Delete session

**State Management:**
- Session-based (in-memory)
- No persistent database
- Automatic cleanup of expired sessions

#### 2.4 LangGraph Workflow

**File:** `backend/voice_agent/graph/graph_builder.py`

**State:** `backend/voice_agent/graph/state.py`

**8-Stage Pipeline:**

1. **Intent Classification** (`intent_agent.py`)
   - Input: User query
   - Output: Intent type + confidence
   - Intents: triage_inbox, draft_reply, schedule_meeting, check_calendar, follow_up, summarize, manage_communications, send_email, archive_email, prioritize_inbox, config, unknown

2. **Context Retrieval** (`context_agent.py`)
   - Input: Intent + query
   - Output: Relevant emails, calendar events, sender history
   - Operations: Fetch emails, get calendar, retrieve context

3. **Reasoning** (`reasoning_agent.py`)
   - Input: Intent + context
   - Output: Priority assessment, recommended action
   - Features: LLM-powered with cascading fallback (OpenAI → Anthropic → Google → Euron)

4. **Draft Generation** (`draft_agent.py`)
   - Input: Intent + context + reasoning
   - Output: Email drafts, calendar proposals
   - Features: Tone adjustment, template-based generation

5. **Authorization** (`authorization_agent.py`)
   - Input: Drafts + actions
   - Output: Authorization requirement + code
   - Logic: Determines if human approval needed

6. **Execution** (`execution_agent.py`)
   - Input: Authorized actions
   - Output: Executed actions + results
   - Operations: Send emails, create events, update calendar

7. **Response Generation** (`response_agent.py`)
   - Input: All previous outputs
   - Output: Formatted response (text/voice)
   - Features: Mode-specific formatting (text vs voice)

8. **Logging** (`logging_agent.py`)
   - Input: Complete workflow state
   - Output: Audit trail
   - Purpose: Debugging, compliance, analytics

**Conditional Routing:**
- Read-only operations skip draft/authorization/execution
- Failed operations trigger error handling
- Authorization blocks execution until approved

#### 2.5 Adapters Layer

**Email Adapter:**

**Files:**
- `backend/voice_agent/adapters/email/base.py` - Abstract interface
- `backend/voice_agent/adapters/email/gmail_adapter.py` - Gmail implementation
- `backend/voice_agent/adapters/email/factory.py` - Factory pattern
- `backend/voice_agent/adapters/email/gmail_oauth.py` - OAuth flow
- `backend/voice_agent/adapters/email/gmail_adapter_helpers.py` - Utilities

**Methods:**
```python
async def fetch_threads(max_results, unread_only, query) -> List[Dict]
async def get_thread(thread_id) -> Dict
async def send_email(to, subject, body, cc, bcc, thread_id) -> Dict
async def mark_read(message_id) -> Dict
async def mark_unread(message_id) -> Dict
async def archive(message_id) -> Dict
async def delete(message_id) -> Dict
```

**Features:**
- OAuth 2.0 authentication
- Token refresh handling
- Mock mode for testing
- Error handling with fallback

**Calendar Adapter:**

**Files:**
- `backend/voice_agent/adapters/calendar/base.py` - Abstract interface
- `backend/voice_agent/adapters/calendar/google_calendar_adapter.py` - Google Calendar implementation

**Methods:**
```python
async def get_events(start_time, end_time, calendar_id) -> List[Dict]
async def get_event(event_id) -> Dict
async def create_event(title, start_time, end_time, attendees, description, location) -> Dict
async def update_event(event_id, updates) -> Dict
async def delete_event(event_id) -> Dict
async def accept_event(event_id) -> Dict
async def decline_event(event_id, message) -> Dict
async def propose_alternative(event_id, alternative_times) -> Dict
```

**Features:**
- Calendar API integration
- Mock mode with realistic data
- Conflict detection
- Attendee management

### 3. Data Layer

#### External APIs

**Gmail API:**
- Scope: `https://www.googleapis.com/auth/gmail.modify`
- Methods: threads.list, threads.get, messages.send, messages.modify
- Authentication: OAuth 2.0 with refresh token
- Rate limits: Handled with exponential backoff

**Google Calendar API:**
- Scope: `https://www.googleapis.com/auth/calendar`
- Methods: events.list, events.get, events.insert, events.update, events.delete
- Authentication: OAuth 2.0
- Features: Recurring events, attendees, reminders

**AI Provider APIs:**
- Euron API (primary)
- OpenAI GPT-4 (fallback)
- Anthropic Claude (fallback)
- Google Gemini (fallback)

## Design Patterns

### 1. Adapter Pattern
Abstract base classes for email and calendar with concrete implementations for different providers.

### 2. Factory Pattern
`EmailAdapterFactory` creates appropriate adapter instances based on configuration.

### 3. Observer Pattern
Frontend polls backend at intervals for updates (60s default).

### 4. State Machine Pattern
LangGraph implements a state machine for workflow orchestration.

### 5. Strategy Pattern
Multiple LLM providers with cascading fallback strategy.

### 6. Repository Pattern
Adapters abstract data access from external APIs.

## Data Flow

### Email Retrieval Flow

```
User Opens App
    ↓
Frontend: loadAllEmails()
    ↓
GET /voice-agent/emails?max_results=30
    ↓
Backend: Router → GmailAdapter.fetch_threads()
    ↓
Gmail API: threads.list()
    ↓
Backend: Format threads → Return JSON
    ↓
Frontend: categorizeEmail() → groupEmailsByThread()
    ↓
Frontend: renderEmailList() with pagination
    ↓
Display: 10 emails per page with badges
```

### AI Query Flow

```
User: "What are my important emails?"
    ↓
Frontend: POST /voice-agent/query
    ↓
Backend: Orchestrator.process_query()
    ↓
LangGraph Pipeline Start
    ↓
IntentAgent: Classify → "triage_inbox"
    ↓
ContextAgent: Fetch emails from Gmail
    ↓
ReasoningAgent: LLM analyzes → Priority list
    ↓
Skip: Draft/Authorization/Execution (read-only)
    ↓
ResponseAgent: Format response
    ↓
LoggingAgent: Record audit trail
    ↓
LangGraph Pipeline End
    ↓
Return: {"text_response": "...", "priority_emails": [...]}
    ↓
Frontend: Display in modal with TTS option
```

### Calendar Auto-Detection Flow

```
Emails Loaded
    ↓
Frontend: autoDetectCalendarInvites()
    ↓
For each email: detectCalendarInvite()
    ↓
Check: Keywords (meeting, interview, schedule)
    ↓
Check: Time patterns (2pm, tomorrow, Monday)
    ↓
If Match: extractMeetingDetails()
    ↓
Extract: title, time, date, duration
    ↓
proposeCalendarBlock()
    ↓
POST /voice-agent/calendar/event
    ↓
Backend: GoogleCalendarAdapter.create_event()
    ↓
Calendar API: events.insert()
    ↓
Success: Show notification
    ↓
Refresh: loadCalendar()
```

## Security Architecture

### Authentication & Authorization

**Gmail/Calendar OAuth 2.0:**
- Authorization Code Flow
- Refresh token stored securely (environment variables)
- Access token cached with auto-refresh
- Scopes: `gmail.modify`, `calendar`

**API Security:**
- CORS enabled for specified origins
- Rate limiting (planned)
- Input validation with Pydantic
- SQL injection prevention (no SQL used)
- XSS prevention (HTML escaping)

**Session Management:**
- Server-side sessions (in-memory)
- Session IDs (UUID v4)
- Automatic expiration (configurable)
- No persistent storage

**Secrets Management:**
- Environment variables (.env)
- No hardcoded credentials
- API keys not exposed to frontend

### Data Privacy

- No data stored persistently
- Email content never logged
- HTTPS required in production
- Mock mode for testing without real data

## Scalability Considerations

### Current Limitations

- Single-server deployment
- In-memory session storage (not distributed)
- Synchronous email processing
- No caching layer
- No load balancing

### Scaling Strategies

**Horizontal Scaling:**
1. Deploy multiple backend instances
2. Use Redis for shared session storage
3. Implement sticky sessions or JWT
4. Add load balancer (Nginx/HAProxy)

**Performance Optimization:**
1. Add Redis cache for email threads
2. Implement background job queue (Celery)
3. Use CDN for frontend assets
4. Compress responses (gzip)
5. Optimize database queries (if SQL added)

**High Availability:**
1. Multi-region deployment
2. Database replication
3. Failover mechanisms
4. Health checks and auto-recovery

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | HTML/CSS/JavaScript | UI |
| Styling | Tailwind CSS | Responsive design |
| Backend | FastAPI | REST API |
| Orchestration | LangGraph | Workflow engine |
| AI | LangChain | LLM integration |
| Email | Gmail API | Email operations |
| Calendar | Google Calendar API | Calendar operations |
| Voice | Web Speech API | STT/TTS |
| Server | Uvicorn | ASGI server |
| Testing | Pytest | Unit/Integration tests |
| Type Checking | Pydantic | Data validation |

## Deployment Architecture

### Development
```
Local Machine
├── Backend (Uvicorn, localhost:8000)
└── Frontend (Static files served by FastAPI)
```

### Production (Recommended)
```
Cloud Provider (AWS/GCP/Azure)
├── Application Layer
│   ├── Load Balancer (AWS ALB/GCP Load Balancer)
│   ├── Backend Instances (Auto-scaling group)
│   │   └── Docker Container (FastAPI + Uvicorn)
│   └── Frontend (CloudFront + S3 / GCS)
├── Cache Layer
│   └── Redis (ElastiCache / Memorystore)
├── Monitoring
│   ├── CloudWatch / Stackdriver
│   └── Application logs
└── Security
    ├── API Gateway
    ├── WAF (Web Application Firewall)
    └── SSL/TLS (Let's Encrypt / ACM)
```

## Future Architecture Enhancements

1. **Microservices Split:**
   - Email Service
   - Calendar Service
   - AI Service
   - User Service

2. **Message Queue:**
   - RabbitMQ / AWS SQS for async processing
   - Background jobs for long-running tasks

3. **Database Layer:**
   - PostgreSQL for user data
   - MongoDB for email metadata
   - Redis for caching

4. **Observability:**
   - Prometheus + Grafana for metrics
   - Jaeger for distributed tracing
   - ELK stack for log aggregation

5. **CI/CD Pipeline:**
   - GitHub Actions / GitLab CI
   - Automated testing
   - Container registry
   - Automated deployment

---

**Last Updated:** 2025-01-03
**Version:** 1.0.0
