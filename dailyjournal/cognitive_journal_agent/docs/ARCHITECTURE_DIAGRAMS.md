# Cognitive Journal Agent - Architecture Diagrams

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Component Interaction Diagram](#component-interaction-diagram)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Sequence Diagrams](#sequence-diagrams)
5. [Deployment Architecture](#deployment-architecture)

---

## High-Level Architecture

### System Overview
```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│                    COGNITIVE JOURNAL AGENT                                │
│              AI-Powered Personal Assistant System                         │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────┐
                            │    USER     │
                            └──────┬──────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ↓                             ↓
            ┌───────────────┐           ┌────────────────┐
            │   WEB UI      │           │  MOBILE APP    │
            │  (Browser)    │           │   (Future)     │
            └───────┬───────┘           └────────┬───────┘
                    │                            │
                    └──────────────┬─────────────┘
                                   │ HTTP/REST
                                   ↓
            ┌──────────────────────────────────────────┐
            │          API GATEWAY (FastAPI)           │
            │            Port 7000                     │
            └──────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ↓                          ↓                          ↓
┌───────────────┐        ┌───────────────┐        ┌──────────────┐
│   INGESTION   │        │   ANALYSIS    │        │   STORAGE    │
│    LAYER      │        │    LAYER      │        │    LAYER     │
├───────────────┤        ├───────────────┤        ├──────────────┤
│               │        │               │        │              │
│ • Text        │───────>│ • LangChain   │───────>│ • Events     │
│ • Voice       │        │ • OpenAI      │        │ • Entries    │
│ • Image (OCR) │        │ • Gemini      │        │ • Actions    │
│ • PDF         │        │               │        │              │
│ • Code        │        │               │        │              │
│ • Calendar    │        │               │        │              │
│               │        │               │        │              │
└───────────────┘        └───────────────┘        └──────────────┘
        │                        │                        │
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                                 ↓
                    ┌────────────────────────┐
                    │   EXTERNAL SERVICES    │
                    ├────────────────────────┤
                    │ • Google Gemini 2.5    │
                    │ • OpenAI GPT-4o-mini   │
                    │ • Tesseract OCR        │
                    │ • Whisper STT          │
                    │ • ElevenLabs TTS       │
                    └────────────────────────┘
```

---

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COMPONENT INTERACTION MAP                        │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │                    WEB UI LAYER                          │
    │                 web_ui_compact_v2.html                   │
    └───────────────────────┬──────────────────────────────────┘
                            │
                   JavaScript API Calls
                            │
    ┌───────────────────────┴──────────────────────────────────┐
    │                                                           │
    │                   FASTAPI APPLICATION                     │
    │                       (main.py)                           │
    │                                                           │
    │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
    │   │  /upload    │  │  /journal   │  │ /calendar   │    │
    │   │  endpoint   │  │  endpoint   │  │ /events     │    │
    │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
    │          │                 │                 │           │
    └──────────┼─────────────────┼─────────────────┼───────────┘
               │                 │                 │
               │                 │                 │
    ┌──────────▼─────────────────▼─────────────────▼───────────┐
    │              PROCESSING NODES LAYER                       │
    ├───────────────────────────────────────────────────────────┤
    │                                                           │
    │  ┌─────────────────────────────────────────────────────┐ │
    │  │         nodes/ingestion.py                          │ │
    │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │ │
    │  │  │ process_   │  │ process_   │  │ process_   │   │ │
    │  │  │   text()   │  │  voice()   │  │ photo_ocr()│   │ │
    │  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘   │ │
    │  │        │               │               │           │ │
    │  │        └───────────────┼───────────────┘           │ │
    │  │                        │                           │ │
    │  └────────────────────────┼───────────────────────────┘ │
    │                           │                             │
    │                           ↓                             │
    │  ┌─────────────────────────────────────────────────────┐ │
    │  │       nodes/calendar_storage.py                     │ │
    │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │ │
    │  │  │  save_     │  │  get_      │  │  detect_   │   │ │
    │  │  │ events()   │  │ events()   │  │ conflicts()│   │ │
    │  │  └────────────┘  └────────────┘  └────────────┘   │ │
    │  └─────────────────────────────────────────────────────┘ │
    │                                                           │
    └───────────────────────────┬───────────────────────────────┘
                                │
                                ↓
    ┌───────────────────────────────────────────────────────────┐
    │               AI SERVICES LAYER                           │
    ├───────────────────────────────────────────────────────────┤
    │                                                           │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │   services/gemini_multimodal.py                  │   │
    │  │                                                   │   │
    │  │   class GeminiMultimodalProcessor:               │   │
    │  │     ├─ extract_text_from_image()                 │   │
    │  │     ├─ extract_calendar_events()                 │   │
    │  │     ├─ analyze_image()                           │   │
    │  │     └─ is_calendar_image()                       │   │
    │  │                                                   │   │
    │  │   Uses: Gemini 2.5 Flash API                     │   │
    │  └──────────────────────────────────────────────────┘   │
    │                                                           │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │   services/gemini_calendar.py                    │   │
    │  │                                                   │   │
    │  │   class GeminiCalendarExtractor:                 │   │
    │  │     └─ extract_events_from_image()               │   │
    │  │                                                   │   │
    │  │   class CalendarAnalyzer:                        │   │
    │  │     ├─ summarize_day()                           │   │
    │  │     ├─ identify_free_time()                      │   │
    │  │     └─ get_longest_free_block()                  │   │
    │  └──────────────────────────────────────────────────┘   │
    │                                                           │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │   LangChain Agent                                │   │
    │  │     • AgentExecutor                              │   │
    │  │     • OpenAI GPT-4o-mini                         │   │
    │  │     • Tool orchestration                         │   │
    │  └──────────────────────────────────────────────────┘   │
    │                                                           │
    └───────────────────────────┬───────────────────────────────┘
                                │
                                ↓
    ┌───────────────────────────────────────────────────────────┐
    │                   DATA LAYER                              │
    ├───────────────────────────────────────────────────────────┤
    │                                                           │
    │   ./data/                                                │
    │   ├── unified_events.json        (99 events)            │
    │   ├── journal_entries.json       (journal data)         │
    │   ├── action_items.json          (tasks)                │
    │   ├── calendar_sources.json      (configs)              │
    │   ├── calendar_connections.json  (OAuth)                │
    │   └── reminders.json             (scheduled)            │
    │                                                           │
    └───────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. Calendar Image Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│         CALENDAR IMAGE PROCESSING DATA FLOW                      │
└─────────────────────────────────────────────────────────────────┘

USER
  │
  │ 1. Upload calendar image
  │    (drag & drop or file select)
  ↓
┌──────────────────────────┐
│  WEB UI                  │
│  • Validate file type    │
│  • Create FormData       │
│  • POST /upload          │
└───────────┬──────────────┘
            │
            │ 2. HTTP POST with file
            ↓
┌──────────────────────────────────────────┐
│  FastAPI main.py                         │
│  @app.post("/upload")                    │
│                                          │
│  • Receive multipart/form-data          │
│  • Save to temp file                    │
│  • Check input_type == 'image'          │
└───────────┬──────────────────────────────┘
            │
            │ 3. Invoke Gemini processing
            ↓
┌───────────────────────────────────────────────────┐
│  services/gemini_multimodal.py                    │
│  GeminiMultimodalProcessor                        │
│                                                   │
│  extract_calendar_events(image_path)              │
│    │                                              │
│    ├─ 4. Read & encode image to base64           │
│    ├─ 5. Build structured prompt                 │
│    ├─ 6. Call Gemini 2.5 Flash API               │
│    │       ↓                                      │
│    │   ┌─────────────────────────────┐           │
│    │   │  GEMINI 2.5 FLASH API       │           │
│    │   │  • Vision analysis          │           │
│    │   │  • Calendar grid detection  │           │
│    │   │  • Event extraction         │           │
│    │   │  • JSON formatting          │           │
│    │   └─────────────┬───────────────┘           │
│    │                 │                            │
│    ├─ 7. Return JSON array of events             │
│    │    [                                         │
│    │      {                                       │
│    │        "title": "Team Meeting",              │
│    │        "date": "2025-11-07",                 │
│    │        "start_time": "10:00",                │
│    │        "end_time": "11:00",                  │
│    │        "location": "Office"                  │
│    │      }                                       │
│    │    ]                                         │
│    │                                              │
│    └─ 8. Parse JSON response                     │
└───────────┬───────────────────────────────────────┘
            │
            │ 9. Convert to UnifiedEvent objects
            ↓
┌─────────────────────────────────────────────────┐
│  main.py (continued)                            │
│                                                 │
│  for event_data in events_data:                │
│    unified_event = UnifiedEvent(               │
│      event_id=generate_id(),                   │
│      source_id=source_id,                      │
│      title=event_data['title'],                │
│      start_time=parse_datetime(...),           │
│      end_time=parse_datetime(...),             │
│      location=event_data.get('location'),      │
│      ...                                       │
│    )                                           │
└───────────┬─────────────────────────────────────┘
            │
            │ 10. Save events to storage
            ↓
┌──────────────────────────────────────────────┐
│  nodes/calendar_storage.py                   │
│  CalendarStorageManager                      │
│                                              │
│  save_events(unified_events)                 │
│    │                                         │
│    ├─ 11. Load existing events              │
│    ├─ 12. Merge new events                  │
│    ├─ 13. Detect conflicts                  │
│    │       ↓                                 │
│    │   ConflictDetector                      │
│    │     • Check time overlaps               │
│    │     • Categorize conflicts              │
│    │     • Mark conflicting events           │
│    │                                         │
│    └─ 14. Write to unified_events.json      │
└───────────┬──────────────────────────────────┘
            │
            │ 15. Return success response
            ↓
┌──────────────────────────────┐
│  FastAPI Response            │
│  {                           │
│    "success": true,          │
│    "message": "Extracted     │
│                30 events",   │
│    "events_count": 30        │
│  }                           │
└───────────┬──────────────────┘
            │
            │ 16. Update UI
            ↓
┌──────────────────────────────────────────┐
│  WEB UI                                  │
│  • Show success message                 │
│  • Refresh loadCalendar()               │
│  • Update stats (events count)          │
│  • Display events in Calendar Summary   │
│  • Highlight conflicts                  │
└──────────────────────────────────────────┘
```

### 2. Journal Entry Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│            JOURNAL ENTRY PROCESSING DATA FLOW                    │
└─────────────────────────────────────────────────────────────────┘

USER
  │
  │ 1. Enter text in Text tab
  │    "Today I completed the project..."
  ↓
┌──────────────────────────┐
│  WEB UI                  │
│  submitText()            │
│  • Validate input        │
│  • POST /journal         │
└───────────┬──────────────┘
            │
            │ 2. HTTP POST { "user_input": "..." }
            ↓
┌──────────────────────────────────────┐
│  FastAPI main.py                     │
│  @app.post("/journal")               │
│  • Receive JSON payload              │
└───────────┬──────────────────────────┘
            │
            │ 3. Invoke ingestion
            ↓
┌───────────────────────────────────────────────────┐
│  nodes/ingestion.py                               │
│  IngestionNode                                    │
│                                                   │
│  process_text(user_input)                         │
│    │                                              │
│    ├─ 4. Create base journal entry               │
│    ├─ 5. Invoke LangChain agent                  │
│    │       ↓                                      │
│    │   ┌──────────────────────────────┐          │
│    │   │  LangChain AgentExecutor     │          │
│    │   │                              │          │
│    │   │  Agent Tools:                │          │
│    │   │  • TagExtractor              │          │
│    │   │  • SentimentAnalyzer         │          │
│    │   │  • ActionItemDetector        │          │
│    │   │  • EntityRecognizer          │          │
│    │   │                              │          │
│    │   │  LLM: OpenAI GPT-4o-mini     │          │
│    │   └───────────┬──────────────────┘          │
│    │               │                              │
│    ├─ 6. Receive analysis results                │
│    │    {                                         │
│    │      tags: ["work", "project"],              │
│    │      emotions: {                             │
│    │        sentiment: "positive",                │
│    │        mood: "accomplished"                  │
│    │      },                                      │
│    │      action_items: [                         │
│    │        "Review code",                        │
│    │        "Deploy to prod"                      │
│    │      ]                                       │
│    │    }                                         │
│    │                                              │
│    └─ 7. Create enriched JournalEntry            │
└───────────┬───────────────────────────────────────┘
            │
            │ 8. Save to storage
            ↓
┌──────────────────────────────────────────────┐
│  Data Storage                                │
│                                              │
│  ├─ Save to journal_entries.json            │
│  │   {                                      │
│  │     entry_id: "uuid",                    │
│  │     timestamp: "2025-11-09T10:00:00",    │
│  │     input_type: "text",                  │
│  │     raw_content: "...",                  │
│  │     tags: [...],                         │
│  │     emotions: {...},                     │
│  │     action_items: [...]                  │
│  │   }                                      │
│  │                                          │
│  └─ Extract & save to action_items.json    │
│      [                                      │
│        {                                    │
│          action_id: "uuid",                 │
│          description: "Review code",        │
│          priority_level: "P1",              │
│          source_entry_id: "uuid"            │
│        }                                    │
│      ]                                      │
└───────────┬──────────────────────────────────┘
            │
            │ 9. Return response
            ↓
┌──────────────────────────────┐
│  FastAPI Response            │
│  {                           │
│    "success": true,          │
│    "entry": {...}            │
│  }                           │
└───────────┬──────────────────┘
            │
            │ 10. Update UI
            ↓
┌──────────────────────────────────────────┐
│  WEB UI                                  │
│  • Show success message                 │
│  • Clear input field                    │
│  • Refresh loadRecent()                 │
│  • Refresh loadActions()                │
│  • Update Overall Summary               │
└──────────────────────────────────────────┘
```

---

## Sequence Diagrams

### Calendar Consolidation Sequence

```
┌──────┐  ┌─────────┐  ┌─────────┐  ┌────────┐  ┌─────────┐  ┌──────────┐
│ User │  │ Web UI  │  │ FastAPI │  │ Gemini │  │ Storage │  │ Conflict │
│      │  │         │  │         │  │  API   │  │ Manager │  │ Detector │
└──┬───┘  └────┬────┘  └────┬────┘  └───┬────┘  └────┬────┘  └────┬─────┘
   │           │            │            │            │            │
   │ 1. Upload │            │            │            │            │
   │  Calendar │            │            │            │            │
   │   Images  │            │            │            │            │
   ├──────────>│            │            │            │            │
   │           │            │            │            │            │
   │           │ 2. POST    │            │            │            │
   │           │   /upload  │            │            │            │
   │           ├───────────>│            │            │            │
   │           │            │            │            │            │
   │           │            │ 3. Extract │            │            │
   │           │            │  calendar  │            │            │
   │           │            │   events   │            │            │
   │           │            ├───────────>│            │            │
   │           │            │            │            │            │
   │           │            │ 4. Vision  │            │            │
   │           │            │  Analysis  │            │            │
   │           │            │<───────────┤            │            │
   │           │            │  (JSON)    │            │            │
   │           │            │            │            │            │
   │           │            │ 5. Save    │            │            │
   │           │            │   events   │            │            │
   │           │            ├────────────┼───────────>│            │
   │           │            │            │            │            │
   │           │            │            │            │ 6. Detect  │
   │           │            │            │            │  conflicts │
   │           │            │            │            ├───────────>│
   │           │            │            │            │            │
   │           │            │            │            │ 7. Marked  │
   │           │            │            │            │   events   │
   │           │            │            │            │<───────────┤
   │           │            │            │            │            │
   │           │            │ 8. Success │            │            │
   │           │            │<───────────┼────────────┤            │
   │           │            │            │            │            │
   │           │ 9. Response│            │            │            │
   │           │   (30 evts)│            │            │            │
   │           │<───────────┤            │            │            │
   │           │            │            │            │            │
   │ 10. Show  │            │            │            │            │
   │  Success  │            │            │            │            │
   │<──────────┤            │            │            │            │
   │           │            │            │            │            │
   │ 11. Click │            │            │            │            │
   │ Consolid. │            │            │            │            │
   ├──────────>│            │            │            │            │
   │           │            │            │            │            │
   │           │ 12. GET    │            │            │            │
   │           │ /calendar/ │            │            │            │
   │           │   events   │            │            │            │
   │           ├───────────>│            │            │            │
   │           │            │            │            │            │
   │           │            │ 13. Fetch  │            │            │
   │           │            │    all     │            │            │
   │           │            ├────────────┼───────────>│            │
   │           │            │            │            │            │
   │           │            │ 14. Events │            │            │
   │           │            │  + confls  │            │            │
   │           │            │<───────────┼────────────┤            │
   │           │            │            │            │            │
   │           │ 15. JSON   │            │            │            │
   │           │  (99 evts) │            │            │            │
   │           │<───────────┤            │            │            │
   │           │            │            │            │            │
   │ 16. Render│            │            │            │            │
   │   Calendar│            │            │            │            │
   │   Summary │            │            │            │            │
   │<──────────┤            │            │            │            │
   │           │            │            │            │            │
```

---

## Deployment Architecture

### Local Development

```
┌─────────────────────────────────────────────────────────────┐
│              LOCAL DEVELOPMENT ENVIRONMENT                   │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Developer PC    │
│  Windows/Mac     │
├──────────────────┤
│                  │
│  ┌────────────┐  │
│  │ Python 3.10│  │
│  │   venv     │  │
│  └────────────┘  │
│        │         │
│        ↓         │
│  ┌────────────┐  │
│  │  FastAPI   │  │
│  │  Server    │  │
│  │  Port 7000 │  │
│  └────────────┘  │
│        │         │
│        ↓         │
│  ┌────────────┐  │
│  │   ./data/  │  │
│  │  JSON files│  │
│  └────────────┘  │
│                  │
└──────────────────┘
        │
        │ localhost:7000
        ↓
┌──────────────────┐
│   Browser        │
│  Chrome/Firefox  │
└──────────────────┘
```

### Production Deployment (Docker)

```
┌─────────────────────────────────────────────────────────────────┐
│                 PRODUCTION DEPLOYMENT (DOCKER)                   │
└─────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │    USERS     │
                        └──────┬───────┘
                               │
                               │ HTTPS
                               ↓
                    ┌──────────────────┐
                    │   Load Balancer  │
                    │   (nginx/Caddy)  │
                    └──────────┬───────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ↓              ↓              ↓
        ┌─────────────┐┌─────────────┐┌─────────────┐
        │  Container  ││  Container  ││  Container  │
        │      1      ││      2      ││      3      │
        ├─────────────┤├─────────────┤├─────────────┤
        │             ││             ││             │
        │  FastAPI    ││  FastAPI    ││  FastAPI    │
        │  App        ││  App        ││  App        │
        │  Port 7000  ││  Port 7000  ││  Port 7000  │
        │             ││             ││             │
        └──────┬──────┘└──────┬──────┘└──────┬──────┘
               │              │              │
               └──────────────┼──────────────┘
                              │
                              ↓
                    ┌──────────────────┐
                    │   Shared Volume  │
                    │     ./data/      │
                    │  (persistent)    │
                    └──────────────────┘
                              │
                              ↓
                    ┌──────────────────┐
                    │  Backup Service  │
                    │  (daily snapshots│
                    └──────────────────┘

External Services (API Calls):
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Gemini    │  │   OpenAI    │  │ ElevenLabs  │
│  2.5 Flash  │  │ GPT-4o-mini │  │     TTS     │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Cloud Deployment (GCP)

```
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE CLOUD PLATFORM DEPLOYMENT                    │
└─────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │    USERS     │
                        └──────┬───────┘
                               │
                               │ HTTPS
                               ↓
                    ┌──────────────────────┐
                    │  Cloud Load Balancer │
                    │   (Global HTTPS)     │
                    └──────────┬───────────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │    Cloud Run         │
                    │  (Serverless)        │
                    ├──────────────────────┤
                    │                      │
                    │  Auto-scaling        │
                    │  0-100 instances     │
                    │                      │
                    │  FastAPI Container   │
                    │  Port 8080           │
                    │                      │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ↓              ↓              ↓
        ┌─────────────┐┌─────────────┐┌─────────────┐
        │   Cloud     ││  Cloud      ││  Secret     │
        │   Storage   ││  Firestore  ││  Manager    │
        ├─────────────┤├─────────────┤├─────────────┤
        │             ││             ││             │
        │ • Files     ││ • Events    ││ • API Keys  │
        │ • Uploads   ││ • Entries   ││ • Tokens    │
        │ • Backups   ││ • Actions   ││             │
        │             ││             ││             │
        └─────────────┘└─────────────┘└─────────────┘

                    ┌──────────────────────┐
                    │  Cloud Monitoring    │
                    │  • Logs              │
                    │  • Metrics           │
                    │  • Alerts            │
                    └──────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                            │
└─────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  NETWORK LAYER                                             │
├────────────────────────────────────────────────────────────┤
│  • HTTPS/TLS 1.3                                          │
│  • CORS configuration                                     │
│  • Rate limiting                                          │
│  • DDoS protection (CloudFlare/Cloud Armor)              │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                         │
├────────────────────────────────────────────────────────────┤
│  • Input validation (Pydantic)                            │
│  • File type validation                                   │
│  • Size limits (10MB max)                                 │
│  • SQL injection prevention (no SQL used)                 │
│  • XSS prevention (sanitize outputs)                      │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                │
├────────────────────────────────────────────────────────────┤
│  • File permission restrictions                            │
│  • Temp file auto-cleanup                                 │
│  • API key environment variables                          │
│  • No credentials in code                                 │
│  • Data encryption at rest (future)                       │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│  EXTERNAL API SECURITY                                     │
├────────────────────────────────────────────────────────────┤
│  • API key rotation policy                                │
│  • Request signing                                         │
│  • Error handling (no leak sensitive info)                │
│  • Timeout configurations                                 │
└────────────────────────────────────────────────────────────┘
```

---

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│               OBSERVABILITY ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │ APPLICATION  │
                    │   main.py    │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   LOGGING    │  │   METRICS    │  │   TRACING    │
├──────────────┤  ├──────────────┤  ├──────────────┤
│              │  │              │  │              │
│ • Python     │  │ • Request    │  │ • Distributed│
│   logging    │  │   count      │  │   tracing    │
│ • Structured │  │ • Response   │  │ • Latency    │
│   JSON       │  │   times      │  │   breakdown  │
│ • Log levels │  │ • Error rate │  │ • Service    │
│              │  │ • API usage  │  │   deps       │
│              │  │              │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ↓
              ┌──────────────────────┐
              │  Monitoring Backend  │
              │  (Cloud Logging,     │
              │   Prometheus, etc)   │
              └──────────┬───────────┘
                         │
                         ↓
              ┌──────────────────────┐
              │   Dashboards         │
              │  • Grafana           │
              │  • Cloud Console     │
              │  • Custom UI         │
              └──────────────────────┘
```

---

**Document Version**: 1.0
**Last Updated**: November 9, 2025
**Author**: Cognitive Journal Agent Team
