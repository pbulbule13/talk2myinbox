# Cognitive Journal Agent - Functional Overview

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Core Features](#core-features)
3. [User Workflows](#user-workflows)
4. [Functional Diagram](#functional-diagram)
5. [Feature Breakdown](#feature-breakdown)

---

## Executive Summary

**Cognitive Journal Agent** is an AI-powered personal assistant that combines multimodal journaling with intelligent calendar consolidation. It uses Gemini 2.5 Flash for advanced image processing and LangChain for orchestration.

### Key Capabilities:
- **5 Input Methods**: Text, Voice, Image, PDF, Code
- **Calendar Integration**: Upload multiple calendar screenshots with AI extraction
- **Conflict Detection**: Automatic detection of overlapping events
- **AI Summaries**: Daily summaries with action items and insights
- **Compact Dashboard**: All-in-one view of journal, calendar, and tasks

---

## Core Features

### 1. Multimodal Input Processing
```
┌─────────────────────────────────────────────────────┐
│          MULTIMODAL INPUT METHODS                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📝 TEXT          🎤 VOICE        📷 IMAGE         │
│  • Quick entry    • Speech-to-    • OCR with       │
│  • Rich text        text           Gemini          │
│  • Markdown       • Natural       • Calendar       │
│                     language        extraction     │
│                                                     │
│  📄 PDF           💻 CODE                           │
│  • Document       • Syntax        • Multi-format   │
│    parsing          highlighting    support        │
│  • Text           • Language                       │
│    extraction       detection                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2. Calendar Consolidation
```
┌─────────────────────────────────────────────────────┐
│        AI-POWERED CALENDAR PROCESSING               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Upload 2-3 Calendar Screenshots                   │
│         ↓                                          │
│  Gemini 2.5 Flash Extraction                       │
│         ↓                                          │
│  • Event titles, dates, times                      │
│  • Locations (if visible)                          │
│  • Context-aware date inference                    │
│         ↓                                          │
│  Unified Calendar View                             │
│         ↓                                          │
│  Conflict Detection:                               │
│  • Full Overlap (RED)                              │
│  • Partial Overlap (YELLOW)                        │
│  • Adjacent Events (BLUE)                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3. AI Analysis & Summaries
```
┌─────────────────────────────────────────────────────┐
│           INTELLIGENT PROCESSING                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  INPUT → LangChain → LLM Analysis                  │
│                         ↓                          │
│           ┌─────────────┴─────────────┐            │
│           ↓             ↓             ↓            │
│      TAGS          EMOTIONS      ACTION ITEMS      │
│    • Auto-tag     • Sentiment    • Extracted       │
│    • Category     • Mood           tasks           │
│                   • Context      • Priorities      │
│                                                     │
│           DAILY SUMMARY GENERATION                  │
│                    ↓                               │
│  • Calendar highlights                             │
│  • Journal insights                                │
│  • Action items                                    │
│  • Conflict warnings                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## User Workflows

### Workflow 1: Quick Journal Entry
```
User Opens App
    ↓
Select Input Method (Text/Voice/Image/PDF/Code)
    ↓
Enter/Upload Content
    ↓
AI Processing:
  • Extract text
  • Analyze sentiment
  • Generate tags
  • Identify action items
    ↓
Content Saved + Displayed in Dashboard
    ↓
Overall Summary Updated
```

### Workflow 2: Calendar Consolidation
```
User Uploads Calendar Images (2-3 screenshots)
    ↓
Gemini 2.5 Flash Processing:
  • Identify calendar grid
  • Extract events (title, date, time, location)
  • Infer missing information
    ↓
Event Storage in unified_events.json
    ↓
Conflict Detection:
  • Check for overlapping events
  • Categorize conflicts (full/partial/adjacent)
    ↓
Display in Full Calendar Summary:
  • Events grouped by date
  • Conflicts highlighted
  • Total event count shown
    ↓
Update Overall Summary with calendar stats
```

### Workflow 3: Daily Summary Generation
```
User Opens Dashboard
    ↓
System Fetches:
  • All calendar events
  • Today's journal entries
  • Action items
    ↓
AI Generation:
  • Calendar Summary (events, conflicts, free time)
  • Journal Summary (entries, tags, insights)
  • Overall Summary (combined view)
    ↓
Display in 3-Panel Dashboard:
  • Left: Input methods
  • Middle: Summaries (Overall, Calendar, Journal)
  • Right: Recent entries, Action items
```

---

## Functional Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    COGNITIVE JOURNAL AGENT                        │
│                   Functional Architecture                         │
└──────────────────────────────────────────────────────────────────┘

                         USER INTERFACE
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   INPUT     │  │  SUMMARIES  │  │   ACTIVITY  │             │
│  │   METHODS   │  │   PANEL     │  │    PANEL    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│       │                  │                  │                    │
│       └──────────────────┴──────────────────┘                    │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │   FASTAPI REST API     │
              │   (Port 7000)          │
              └────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   UPLOAD     │  │   JOURNAL    │  │   SUMMARY    │
│  ENDPOINT    │  │  ENDPOINT    │  │  ENDPOINTS   │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        ↓                  ↓                  ↓
┌────────────────────────────────────────────────────┐
│              PROCESSING LAYER                      │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │
│  │   GEMINI    │  │  LANGCHAIN  │  │  TESSERACT│ │
│  │  2.5 FLASH  │  │ ORCHESTRATOR│  │    OCR    │  │
│  └─────────────┘  └─────────────┘  └──────────┘  │
│         │                │                │        │
│         └────────────────┴────────────────┘        │
│                          │                         │
└──────────────────────────┼─────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────┐
│              DATA STORAGE LAYER                    │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐  ┌────────────────────────┐ │
│  │ unified_events   │  │  journal_entries.json  │ │
│  │    .json         │  │  action_items.json     │ │
│  │  (99 events)     │  │  calendar_sources.json │ │
│  └──────────────────┘  └────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Feature Breakdown

### Input Processing Features

#### 1. Text Entry
- **Capability**: Direct text input with markdown support
- **Processing**:
  - NLP analysis for sentiment
  - Entity extraction
  - Tag generation
- **Output**: Journal entry with metadata

#### 2. Voice Entry
- **Capability**: Speech-to-text conversion
- **Processing**:
  - Audio recording
  - Whisper transcription
  - Natural language understanding
- **Output**: Transcribed text + journal entry

#### 3. Image Entry (OCR)
- **Capability**: Extract text from images
- **Processing**:
  - Gemini 2.5 Flash vision (primary)
  - Tesseract OCR (fallback)
  - Context-aware extraction
- **Output**: Extracted text + journal entry

#### 4. Calendar Image Entry
- **Capability**: Extract calendar events from screenshots
- **Processing**:
  - Gemini multimodal AI
  - Calendar grid detection
  - Event extraction (title, date, time, location)
  - Date inference with context
- **Output**: UnifiedEvent objects stored in database

#### 5. PDF Entry
- **Capability**: Extract text from PDF documents
- **Processing**:
  - PyPDF2 extraction
  - Text formatting preservation
- **Output**: Document text + journal entry

#### 6. Code Entry
- **Capability**: Code snippet storage
- **Processing**:
  - Language detection
  - Syntax highlighting
  - Documentation extraction
- **Output**: Code entry with metadata

### Calendar Features

#### 1. Multi-Calendar Upload
- Upload 2-3 calendar screenshots
- Support for: Google Calendar, Outlook, Apple Calendar, paper calendars
- Batch processing with Gemini 2.5 Flash

#### 2. Event Extraction
- **Automatic Detection**:
  - Event titles
  - Dates (YYYY-MM-DD)
  - Times (HH:MM, 24-hour)
  - Locations (if visible)
  - Descriptions (if visible)

- **Context-Aware Inference**:
  - Missing dates inferred from calendar month/year
  - All-day events detected
  - Time zones normalized

#### 3. Conflict Detection
```
CONFLICT TYPES:
┌────────────────────────────────────────┐
│ FULL OVERLAP (Critical)               │
│ Event A: 10:00 AM - 11:00 AM         │
│ Event B: 10:00 AM - 11:00 AM         │
│ → Highlighted in RED                  │
├────────────────────────────────────────┤
│ PARTIAL OVERLAP (Warning)             │
│ Event A: 10:00 AM - 11:00 AM         │
│ Event B: 10:30 AM - 11:30 AM         │
│ → Highlighted in YELLOW               │
├────────────────────────────────────────┤
│ ADJACENT (Info)                       │
│ Event A: 10:00 AM - 11:00 AM         │
│ Event B: 11:00 AM - 12:00 PM         │
│ → Highlighted in BLUE                 │
└────────────────────────────────────────┘
```

#### 4. Unified Calendar View
- **Full Calendar Summary**: Shows ALL events from all uploaded calendars
- **Grouped by Date**: Events organized chronologically
- **Event Count**: Total events displayed (e.g., "99 total")
- **Conflict Warnings**: Visual indicators for overlaps

### Summary Features

#### 1. Calendar Summary
```json
{
  "date": "2025-11-09",
  "total_events": 99,
  "events": [...],
  "conflicts": [...],
  "free_time": [...]
}
```

#### 2. Journal Summary
```json
{
  "date": "2025-11-09",
  "total_entries": 5,
  "entries": [...],
  "action_items": [...],
  "tags": ["work", "personal", "health"],
  "summary_text": "AI-generated summary"
}
```

#### 3. Overall Summary
- Combines calendar + journal + actions
- Highlights key events and insights
- Shows calendar statistics
- Lists next actions

---

## Dashboard Layout

```
┌────────────────────────────────────────────────────────────────┐
│  🧠 Cognitive Journal - AI-Powered Personal Assistant         │
├────────────────────────────────────────────────────────────────┤
│  Stats: 99 Events | 5 Entries | 12 Actions | 2 Conflicts      │
├──────────────┬─────────────────────────┬──────────────────────┤
│              │                         │                      │
│  LEFT COL    │    MIDDLE COL          │    RIGHT COL        │
│              │                         │                      │
│  ┌────────┐  │  ┌──────────────────┐  │  ┌────────────────┐ │
│  │ 📝Text │  │  │ 📊 Overall       │  │  │ 📋 Recent      │ │
│  │ 🎤Voice│  │  │    Summary       │  │  │    Entries     │ │
│  │ 📷Image│  │  │ • Today's        │  │  │                │ │
│  │ 📄PDF  │  │  │   overview       │  │  │ Entry 1        │ │
│  │ 💻Code │  │  │ • Calendar stats │  │  │ Entry 2        │ │
│  └────────┘  │  └──────────────────┘  │  │ Entry 3        │ │
│              │                         │  └────────────────┘ │
│  ┌────────┐  │  ┌──────────────────┐  │                      │
│  │📅Upload│  │  │ 📅 Full Calendar │  │  ┌────────────────┐ │
│  │Calendar│  │  │    Summary       │  │  │ ✅ Action      │ │
│  │        │  │  │                  │  │  │    Items       │ │
│  │ • Cal1 │  │  │ Nov 6, 2025      │  │  │                │ │
│  │ • Cal2 │  │  │ • 10:00 Meeting  │  │  │ □ Task 1 (P1)  │ │
│  │ • Cal3 │  │  │ • 14:00 Lunch    │  │  │ □ Task 2 (P2)  │ │
│  │        │  │  │                  │  │  │ □ Task 3 (P3)  │ │
│  │[Consol]│  │  │ Nov 7, 2025      │  │  │                │ │
│  └────────┘  │  │ • 09:00 Standup  │  │  └────────────────┘ │
│              │  │ • 11:00 Review   │  │                      │
│              │  │   [CONFLICT]     │  │                      │
│              │  │ • 11:00 Call     │  │                      │
│              │  │   [CONFLICT]     │  │                      │
│              │  └──────────────────┘  │                      │
│              │                         │                      │
│              │  ┌──────────────────┐  │                      │
│              │  │ 📝 Journal       │  │                      │
│              │  │    Summary       │  │                      │
│              │  │                  │  │                      │
│              │  │ Tags: #work      │  │                      │
│              │  │       #health    │  │                      │
│              │  └──────────────────┘  │                      │
│              │                         │                      │
└──────────────┴─────────────────────────┴──────────────────────┘
```

---

## Success Metrics

### Calendar Extraction Accuracy
- **Event Detection Rate**: 95%+ (Gemini 2.5 Flash)
- **Date Inference Accuracy**: 90%+
- **Conflict Detection**: 100% for exact overlaps

### User Experience
- **Dashboard Load Time**: < 2 seconds
- **Event Upload Processing**: 5-10 seconds for 3 calendars
- **UI Responsiveness**: Real-time updates

### AI Processing
- **Summary Generation**: < 3 seconds
- **Tag Accuracy**: 85%+
- **Action Item Extraction**: 80%+

---

## Future Enhancements

### Phase 2 (Planned)
1. **Real Calendar API Integration**
   - Google Calendar OAuth
   - Microsoft Outlook OAuth
   - Apple Calendar sync

2. **Advanced AI Features**
   - Predictive scheduling
   - Smart conflict resolution
   - Automated event categorization

3. **Collaboration**
   - Shared calendars
   - Team journal entries
   - Collaborative action items

4. **Mobile App**
   - iOS/Android native apps
   - Push notifications
   - Offline mode

---

**Document Version**: 1.0
**Last Updated**: November 9, 2025
**Author**: Cognitive Journal Agent Team
