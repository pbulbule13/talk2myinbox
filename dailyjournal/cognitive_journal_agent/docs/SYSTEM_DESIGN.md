# System Design Overview - Cognitive Journal Agent

**Version**: 1.0.0
**Last Updated**: 2025-11-03

---

## Executive Summary

This document provides a comprehensive system design overview of the Cognitive Journal Agent (CJA), including detailed diagrams, component interactions, and data flows.

---

## Table of Contents

1. [System Context](#1-system-context)
2. [Container Diagram](#2-container-diagram)
3. [Component Diagram](#3-component-diagram)
4. [Sequence Diagrams](#4-sequence-diagrams)
5. [Data Flow Diagrams](#5-data-flow-diagrams)
6. [State Machine Diagrams](#6-state-machine-diagrams)
7. [Class Diagrams](#7-class-diagrams)
8. [Infrastructure Diagrams](#8-infrastructure-diagrams)

---

## 1. System Context

### 1.1 Context Diagram (C4 Level 1)

```
                    ┌─────────────────────────────────┐
                    │          Users                  │
                    │  • Individual Users             │
                    │  • Teams (Future)               │
                    │  • Enterprise (Future)          │
                    └──────────┬──────────────────────┘
                               │
                               │ HTTP/CLI
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│                  COGNITIVE JOURNAL AGENT                          │
│                                                                   │
│  A multimodal, agentic personal assistant for intelligent        │
│  journal management, task extraction, and daily summarization.   │
│                                                                   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│   LLM Services  │ │  TTS Service │ │  Storage     │
│  • OpenAI       │ │  • ElevenLabs│ │  • Firestore │
│  • Anthropic    │ │  • Local TTS │ │  • SQLite    │
└─────────────────┘ └──────────────┘ └──────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│ External Tools  │ │Email/Calendar│ │   Backup     │
│  • Web Search   │ │  • SMTP      │ │  • S3/GCS    │
│  • File Ops     │ │  • Google    │ │              │
└─────────────────┘ └──────────────┘ └──────────────┘
```

### 1.2 User Interactions

```
┌─────────────┐                    ┌─────────────┐
│     User    │                    │     CJA     │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │ 1. Input (Text/Voice/Image)      │
       │─────────────────────────────────▶│
       │                                  │
       │                                  │ 2. Process & Analyze
       │                                  │──────────┐
       │                                  │          │
       │                                  │◀─────────┘
       │                                  │
       │ 3. Acknowledgment                │
       │◀─────────────────────────────────│
       │                                  │
       │ 4. Request Summary               │
       │─────────────────────────────────▶│
       │                                  │
       │                                  │ 5. Generate Report
       │                                  │──────────┐
       │                                  │          │
       │                                  │◀─────────┘
       │                                  │
       │ 6. Daily Summary + Audio         │
       │◀─────────────────────────────────│
       │                                  │
       │ 7. Execute Action (e.g., Email)  │
       │─────────────────────────────────▶│
       │                                  │
       │                                  │ 8. Use Tools
       │                                  │──────────┐
       │                                  │          │
       │                                  │◀─────────┘
       │                                  │
       │ 9. Confirmation                  │
       │◀─────────────────────────────────│
       │                                  │
```

---

## 2. Container Diagram

### 2.1 Container Architecture (C4 Level 2)

```
┌───────────────────────────────────────────────────────────────┐
│                      User Devices                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Browser │  │   CLI    │  │  Mobile  │  │ Webhooks │     │
│  │   (Web)  │  │Terminal  │  │   App    │  │ (Future) │     │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘     │
└────────┼─────────────┼─────────────┼─────────────┼───────────┘
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                       │
                       │ HTTPS/HTTP
                       ▼
┌───────────────────────────────────────────────────────────────┐
│                API Gateway / Load Balancer                     │
│                       (AWS ALB / NGINX)                        │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│              Web Application Container                         │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           FastAPI Application                            │ │
│  │  • REST API Endpoints                                    │ │
│  │  • Request validation                                    │ │
│  │  • Response formatting                                   │ │
│  │  • CORS handling                                         │ │
│  │  • Health checks                                         │ │
│  └──────────────────────┬──────────────────────────────────┘ │
│                         │                                     │
│  ┌──────────────────────▼──────────────────────────────────┐ │
│  │         LangGraph Orchestration Engine                   │ │
│  │  • State machine management                              │ │
│  │  • Node execution                                        │ │
│  │  • Conditional routing                                   │ │
│  │  • Error handling                                        │ │
│  └──────────────────────┬──────────────────────────────────┘ │
│                         │                                     │
│  ┌──────────────────────▼──────────────────────────────────┐ │
│  │              Business Logic Layer                        │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │ │
│  │  │Ingestion  │ │Processing │ │  Storage  │             │ │
│  │  │  Module   │ │  Module   │ │  Module   │             │ │
│  │  └───────────┘ └───────────┘ └───────────┘             │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │ │
│  │  │Reporting  │ │    TTS    │ │   Agent   │             │ │
│  │  │  Module   │ │  Module   │ │  Module   │             │ │
│  │  └───────────┘ └───────────┘ └───────────┘             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  Technology: Python 3.11, FastAPI, LangChain, LangGraph       │
└───────────────┬────────────────────────────────────────┬──────┘
                │                                        │
    ┌───────────┴────────────┐              ┌────────────┴────────────┐
    │                        │              │                         │
    ▼                        ▼              ▼                         ▼
┌─────────┐          ┌─────────────┐  ┌──────────┐          ┌──────────┐
│Database │          │File Storage │  │LLM APIs  │          │Tool APIs │
│Container│          │  Container  │  │Container │          │Container │
├─────────┤          ├─────────────┤  ├──────────┤          ├──────────┤
│• SQLite │          │• Local FS   │  │• OpenAI  │          │• SMTP    │
│• Postgres│          │• S3/GCS    │  │• Anthropic│          │• Calendar│
│• Firestore│         │• Audio     │  │• Cached  │          │• Search  │
└─────────┘          └─────────────┘  └──────────┘          └──────────┘
```

---

## 3. Component Diagram

### 3.1 Detailed Component View (C4 Level 3)

```
┌──────────────────────────────────────────────────────────────────┐
│                     CJA Application Components                    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      API Layer                                    │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │  FastAPI   │  │   CORS     │  │   Auth     │                 │
│  │   Router   │  │ Middleware │  │ (Future)   │                 │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘                 │
└─────────┼────────────────┼────────────────┼───────────────────────┘
          │                │                │
          └────────────────┴────────────────┘
                           │
┌──────────────────────────▼────────────────────────────────────────┐
│                  Orchestration Layer                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LangGraph State Machine                     │    │
│  │                                                          │    │
│  │  State = {                                               │    │
│  │    user_input, input_data,                              │    │
│  │    new_entry, all_entries, pending_actions,             │    │
│  │    final_report, audio_output_path, tool_response       │    │
│  │  }                                                       │    │
│  │                                                          │    │
│  │  ┌──────────┐     ┌──────────┐     ┌──────────┐        │    │
│  │  │  Router  │────▶│Ingestion │────▶│Processing│        │    │
│  │  │   Node   │     │   Node   │     │   Node   │        │    │
│  │  └──────────┘     └──────────┘     └──────────┘        │    │
│  │       │                                   │             │    │
│  │       │            ┌──────────┐           │             │    │
│  │       └───────────▶│  Storage │◀──────────┘             │    │
│  │                    │   Node   │                         │    │
│  │                    └──────────┘                         │    │
│  │                                                          │    │
│  │  ┌──────────┐     ┌──────────┐     ┌──────────┐        │    │
│  │  │  Agent   │     │Reporting │     │   TTS    │        │    │
│  │  │   Node   │     │   Node   │     │   Node   │        │    │
│  │  └──────────┘     └──────────┘     └──────────┘        │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼────────────────────────────────────────┐
│                    Service Layer                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Multimodal Ingestion Service                    │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │   │
│  │  │  Text   │ │  Voice  │ │   OCR   │ │   PDF   │        │   │
│  │  │Processor│ │   STT   │ │Processor│ │Processor│        │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │   │
│  │  ┌─────────┐ ┌─────────┐                                 │   │
│  │  │  Email  │ │Calendar │                                 │   │
│  │  │  Parser │ │ Parser  │                                 │   │
│  │  └─────────┘ └─────────┘                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LLM Processing Service                       │   │
│  │  ┌──────────────────┐         ┌──────────────────┐       │   │
│  │  │   LLM Processor  │         │Simple Processor  │       │   │
│  │  │                  │         │   (Fallback)     │       │   │
│  │  │ ┌──────────────┐ │         │ ┌──────────────┐ │       │   │
│  │  │ │Prompt Engine │ │         │ │Rule Engine   │ │       │   │
│  │  │ └──────────────┘ │         │ └──────────────┘ │       │   │
│  │  │ ┌──────────────┐ │         │ ┌──────────────┐ │       │   │
│  │  │ │  LLM Client  │ │         │ │Pattern Match │ │       │   │
│  │  │ │ (OpenAI/etc) │ │         │ │   Engine     │ │       │   │
│  │  │ └──────────────┘ │         │ └──────────────┘ │       │   │
│  │  │ ┌──────────────┐ │         │                  │       │   │
│  │  │ │Output Parser │ │         │                  │       │   │
│  │  │ │  (Pydantic)  │ │         │                  │       │   │
│  │  │ └──────────────┘ │         │                  │       │   │
│  │  └──────────────────┘         └──────────────────┘       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Storage Management Service                   │   │
│  │  ┌──────────────────────────────────────────────────┐    │   │
│  │  │        StorageManager (Facade Pattern)           │    │   │
│  │  └─────────────┬────────────────────────────────────┘    │   │
│  │                │                                          │   │
│  │    ┌───────────┼───────────┬──────────────┐              │   │
│  │    │           │           │              │              │   │
│  │    ▼           ▼           ▼              ▼              │   │
│  │ ┌──────┐  ┌─────────┐ ┌──────────┐  ┌─────────┐        │   │
│  │ │ JSON │  │ SQLite  │ │Firestore │  │ Custom  │        │   │
│  │ │Backend│  │ Backend │ │ Backend  │  │ Backend │        │   │
│  │ └──────┘  └─────────┘ └──────────┘  └─────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Tool Execution Service                         │   │
│  │  ┌──────────────────────────────────────────────────┐    │   │
│  │  │      LangChain Agent Executor                    │    │   │
│  │  │  ┌─────────────────────────────────────────┐     │    │   │
│  │  │  │         Tool Registry                   │     │    │   │
│  │  │  └─────────────────────────────────────────┘     │    │   │
│  │  └──────────────────┬───────────────────────────────┘    │   │
│  │                     │                                     │   │
│  │       ┌─────────────┼─────────────┬──────────────┐       │   │
│  │       │             │             │              │       │   │
│  │       ▼             ▼             ▼              ▼       │   │
│  │  ┌────────┐   ┌─────────┐   ┌────────┐   ┌─────────┐   │   │
│  │  │ Email  │   │Calendar │   │  File  │   │  Search │   │   │
│  │  │  Tool  │   │  Tool   │   │  Tool  │   │   Tool  │   │   │
│  │  └────────┘   └─────────┘   └────────┘   └─────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │             Reporting Service                             │   │
│  │  ┌──────────────┐         ┌──────────────┐               │   │
│  │  │ LLM Reporter │         │Simple Reporter│               │   │
│  │  │              │         │  (Fallback)   │               │   │
│  │  │• Synthesizer │         │• Statistics   │               │   │
│  │  │• Formatter   │         │• Templates    │               │   │
│  │  └──────────────┘         └──────────────┘               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              TTS Output Service                           │   │
│  │  ┌───────────────┐        ┌───────────────┐              │   │
│  │  │  ElevenLabs   │        │   Local TTS   │              │   │
│  │  │    Client     │        │   (pyttsx3)   │              │   │
│  │  └───────────────┘        └───────────────┘              │   │
│  │  ┌───────────────┐                                        │   │
│  │  │Text Formatter │                                        │   │
│  │  │  (for speech) │                                        │   │
│  │  └───────────────┘                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼────────────────────────────────────────┐
│                   Data Access Layer                               │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ Pydantic Models  │  │ Type Definitions │                     │
│  │  • JournalEntry  │  │  • AgentState    │                     │
│  │  • ActionItem    │  │  • TypedDict     │                     │
│  │  • Report Models │  │                  │                     │
│  └──────────────────┘  └──────────────────┘                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Sequence Diagrams

### 4.1 Journal Entry Creation

```
User          API          Router       Ingestion    Processing    Storage      Database
 │             │             │             │             │             │             │
 │  POST       │             │             │             │             │             │
 │ /journal    │             │             │             │             │             │
 ├────────────▶│             │             │             │             │             │
 │             │             │             │             │             │             │
 │             │ Initialize  │             │             │             │             │
 │             │   State     │             │             │             │             │
 │             ├────────────▶│             │             │             │             │
 │             │             │             │             │             │             │
 │             │             │  Route to   │             │             │             │
 │             │             │  Ingestion  │             │             │             │
 │             │             ├────────────▶│             │             │             │
 │             │             │             │             │             │             │
 │             │             │             │ Convert to  │             │             │
 │             │             │             │JournalEntry │             │             │
 │             │             │             ├───────┐     │             │             │
 │             │             │             │       │     │             │             │
 │             │             │             │◀──────┘     │             │             │
 │             │             │             │             │             │             │
 │             │             │             │  Process    │             │             │
 │             │             │             │   Entry     │             │             │
 │             │             │             ├────────────▶│             │             │
 │             │             │             │             │             │             │
 │             │             │             │             │   Extract   │             │
 │             │             │             │             │ Tags/Actions│             │
 │             │             │             │             ├──────┐      │             │
 │             │             │             │             │      │      │             │
 │             │             │             │             │◀─────┘      │             │
 │             │             │             │             │             │             │
 │             │             │             │             │  Save Entry │             │
 │             │             │             │             │             │             │
 │             │             │             │             ├────────────▶│             │
 │             │             │             │             │             │             │
 │             │             │             │             │             │  Write to   │
 │             │             │             │             │             │     DB      │
 │             │             │             │             │             ├────────────▶│
 │             │             │             │             │             │             │
 │             │             │             │             │             │    OK       │
 │             │             │             │             │             │◀────────────│
 │             │             │             │             │             │             │
 │             │             │             │             │  Return     │             │
 │             │             │             │             │   State     │             │
 │             │             │             │             │◀────────────│             │
 │             │             │             │◀────────────│             │             │
 │             │             │◀────────────│             │             │             │
 │             │◀────────────│             │             │             │             │
 │             │             │             │             │             │             │
 │  Response   │             │             │             │             │             │
 │◀────────────│             │             │             │             │             │
 │             │             │             │             │             │             │
```

### 4.2 Daily Summary Generation

```
User      API      Router    Storage    Reporting    LLM API    TTS Service
 │         │         │          │           │           │            │
 │  POST   │         │          │           │           │            │
 │/summarize│        │          │           │           │            │
 ├────────▶│         │          │           │           │            │
 │         │         │          │           │           │            │
 │         │ Route   │          │           │           │            │
 │         │   to    │          │           │           │            │
 │         │Reporting│          │           │           │            │
 │         ├────────▶│          │           │           │            │
 │         │         │          │           │           │            │
 │         │         │  Load    │           │           │            │
 │         │         │ Entries  │           │           │            │
 │         │         ├─────────▶│           │           │            │
 │         │         │          │           │           │            │
 │         │         │  Return  │           │           │            │
 │         │         │ Entries  │           │           │            │
 │         │         │◀─────────│           │           │            │
 │         │         │          │           │           │            │
 │         │         │ Generate │           │           │            │
 │         │         │  Report  │           │           │            │
 │         │         ├─────────────────────▶│           │            │
 │         │         │          │           │           │            │
 │         │         │          │           │  Format   │            │
 │         │         │          │           │  Prompt   │            │
 │         │         │          │           ├──────┐    │            │
 │         │         │          │           │      │    │            │
 │         │         │          │           │◀─────┘    │            │
 │         │         │          │           │           │            │
 │         │         │          │           │   LLM     │            │
 │         │         │          │           │   Call    │            │
 │         │         │          │           ├──────────▶│            │
 │         │         │          │           │           │            │
 │         │         │          │           │  Report   │            │
 │         │         │          │           │   JSON    │            │
 │         │         │          │           │◀──────────│            │
 │         │         │          │           │           │            │
 │         │         │          │           │  Parse &  │            │
 │         │         │          │           │ Validate  │            │
 │         │         │          │           ├──────┐    │            │
 │         │         │          │           │      │    │            │
 │         │         │          │           │◀─────┘    │            │
 │         │         │          │           │           │            │
 │         │         │  Report  │           │           │            │
 │         │         │ Generated│           │           │            │
 │         │         │◀─────────────────────│           │            │
 │         │         │          │           │           │            │
 │         │         │ Convert  │           │           │            │
 │         │         │ to Audio │           │           │            │
 │         │         ├──────────────────────────────────────────────▶│
 │         │         │          │           │           │            │
 │         │         │          │           │           │   Generate │
 │         │         │          │           │           │    Audio   │
 │         │         │          │           │           │◀───────┐   │
 │         │         │          │           │           │        │   │
 │         │         │          │           │           │────────┘   │
 │         │         │          │           │           │            │
 │         │         │ Audio    │           │           │            │
 │         │         │  Path    │           │           │            │
 │         │         │◀──────────────────────────────────────────────│
 │         │         │          │           │           │            │
 │         │◀────────│          │           │           │            │
 │         │         │          │           │           │            │
 │Response │         │          │           │           │            │
 │◀────────│         │          │           │           │            │
 │         │         │          │           │           │            │
```

---

## 5. Data Flow Diagrams

### 5.1 End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Input Stage                                   │
└─────────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        Text Input    Voice Input    Image Input
              │             │             │
              ▼             ▼             ▼
         [Plain Text]   [Audio File]  [Image File]
              │             │             │
              │             ▼             ▼
              │        [STT Engine]   [OCR Engine]
              │             │             │
              └─────────────┴─────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Ingestion & Normalization                        │
│                                                                  │
│  Input → MultimodalIngest → JournalEntry(raw_content)          │
│                                                                  │
│  Data: {                                                        │
│    timestamp: DateTime,                                         │
│    input_type: "text_note" | "voice_memo" | "photo_ocr",      │
│    raw_content: String,                                         │
│    source_id: UUID                                              │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Processing & Enrichment                         │
│                                                                  │
│  JournalEntry → ProcessEntry → EnrichedJournalEntry            │
│                                                                  │
│  LLM Processing:                                                │
│    • Prompt: "Analyze: {raw_content}"                           │
│    • LLM Response: ProcessedContent(Pydantic)                   │
│    • Extract: tags, actions, emotion                            │
│                                                                  │
│  Data: {                                                        │
│    ...previous_fields,                                          │
│    contextual_tags: ["Work", "Task", "Urgent"],                │
│    extracted_action_items: ["Email John"],                     │
│    inferred_emotion: "High Focus"                               │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Storage & Persistence                           │
│                                                                  │
│  EnrichedJournalEntry → StorageManager → Database              │
│                                                                  │
│  Operations:                                                    │
│    1. Save entry                                                │
│    2. Extract & save action items                               │
│    3. Update aggregates                                         │
│                                                                  │
│  Storage Format (JSON):                                         │
│  {                                                               │
│    "source_id": "text_abc123",                                  │
│    "timestamp": "2024-01-15T10:30:00",                          │
│    "raw_content": "...",                                        │
│    "contextual_tags": ["Work"],                                 │
│    "extracted_action_items": ["..."],                           │
│    "inferred_emotion": "High Focus"                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ (On demand)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Aggregation & Reporting                         │
│                                                                  │
│  Load: all_entries[] + pending_actions[]                        │
│    ↓                                                             │
│  DailyReporter → FinalAgentReport                              │
│                                                                  │
│  LLM Processing:                                                │
│    • Context: All entries from today                            │
│    • Prompt: "Synthesize daily summary"                         │
│    • Output: Structured report (Pydantic)                       │
│                                                                  │
│  Data: {                                                        │
│    summary: {                                                   │
│      date: "2024-01-15",                                        │
│      daily_theme: "Productive project work",                    │
│      key_decisions_and_learnings: [...],                        │
│      journal_narrative: "..."                                   │
│    },                                                            │
│    pending_actions: [...],                                      │
│    suggested_first_task: "..."                                  │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Output Generation                               │
│                                                                  │
│  FinalAgentReport → TTSService → Audio File                    │
│                                                                  │
│  Text Formatting:                                               │
│    "Good morning! Here's your daily summary for {date}..."      │
│                                                                  │
│  TTS Processing:                                                │
│    • Format for natural speech                                  │
│    • Call ElevenLabs API                                        │
│    • Save MP3 file                                              │
│                                                                  │
│  Output: ./audio_output/report_2024-01-15.mp3                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. State Machine Diagrams

### 6.1 LangGraph State Transitions

```
                     [START]
                        │
                        ▼
              ┌─────────────────┐
              │ INITIAL_STATE   │
              │                 │
              │ user_input: ""  │
              │ new_entry: null │
              │ all_entries: [] │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ ROUTE_INPUT     │
              │                 │
              │ Determine path  │
              │ based on input  │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ PATH:      │  │ PATH:      │  │ PATH:      │
│ JOURNAL    │  │ ACTION     │  │ SUMMARY    │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      ▼               ▼               │
┌────────────┐  ┌────────────┐       │
│ INGESTING  │  │ EXECUTING  │       │
│            │  │   TOOLS    │       │
│ State:     │  │            │       │
│ +input_data│  │ State:     │       │
└─────┬──────┘  │+tool_resp  │       │
      │         └─────┬──────┘       │
      ▼               │               │
┌────────────┐        │               │
│PROCESSING  │        │               │
│            │        │               │
│ State:     │        │               │
│ +new_entry │        │               │
│  (enriched)│        │               │
└─────┬──────┘        │               │
      │               │               │
      ▼               ▼               │
┌────────────┐  ┌────────────┐       │
│  STORING   │  │  LOGGING   │       │
│            │  │ (Optional) │       │
│ State:     │  │            │       │
│+all_entries│  │            │       │
│ +actions   │  │            │       │
└─────┬──────┘  └─────┬──────┘       │
      │               │               │
      ▼               ▼               │
    [END]           [END]             │
                                      │
                                      ▼
                              ┌────────────┐
                              │ REPORTING  │
                              │            │
                              │ State:     │
                              │+final_rep  │
                              └─────┬──────┘
                                    │
                              ┌─────▼──────┐
                              │ TTS_ENABLED│
                              │   CHECK    │
                              └─────┬──────┘
                                    │
                              ┌─────┴──────┐
                              │            │
                              ▼            ▼
                        ┌──────────┐  ┌────────┐
                        │GENERATING│  │  SKIP  │
                        │   AUDIO  │  │  AUDIO │
                        │          │  └───┬────┘
                        │ State:   │      │
                        │ +audio   │      │
                        │  _path   │      │
                        └─────┬────┘      │
                              │           │
                              └─────┬─────┘
                                    │
                                    ▼
                                  [END]
```

### 6.2 State Transitions Matrix

| From State | Event | To State | Actions |
|------------|-------|----------|---------|
| INITIAL | user_input | ROUTING | Parse input |
| ROUTING | is_journal | INGESTING | Create entry |
| ROUTING | is_action | EXECUTING | Initialize agent |
| ROUTING | is_summary | REPORTING | Load entries |
| INGESTING | entry_created | PROCESSING | Extract metadata |
| PROCESSING | processed | STORING | Save to DB |
| STORING | saved | END | Return response |
| EXECUTING | tool_done | LOGGING | Create log entry |
| LOGGING | logged | END | Return response |
| REPORTING | report_generated | TTS_CHECK | Check config |
| TTS_CHECK | enabled | GENERATING_AUDIO | Call TTS API |
| TTS_CHECK | disabled | END | Return report |
| GENERATING_AUDIO | audio_created | END | Return with audio |

---

## 7. Class Diagrams

### 7.1 Core Domain Models

```
┌──────────────────────────────────────┐
│         JournalEntry                  │
├──────────────────────────────────────┤
│ - timestamp: datetime                │
│ - input_type: str                    │
│ - raw_content: str                   │
│ - source_id: str                     │
│ - contextual_tags: List[str]         │
│ - extracted_action_items: List[str]  │
│ - inferred_emotion: Optional[str]    │
├──────────────────────────────────────┤
│ + __init__(...)                      │
│ + dict() -> dict                     │
│ + model_dump() -> dict               │
└──────────────────────────────────────┘
                │
                │ 1:N
                ▼
┌──────────────────────────────────────┐
│           ActionItem                  │
├──────────────────────────────────────┤
│ - task_id: str                       │
│ - task_description: str              │
│ - priority: str                      │
│ - source_entry_id: str               │
│ - due_date: Optional[datetime]       │
├──────────────────────────────────────┤
│ + __init__(...)                      │
│ + is_urgent() -> bool                │
│ + is_overdue() -> bool               │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│      DailySummaryOutput               │
├──────────────────────────────────────┤
│ - date: str                          │
│ - daily_theme: str                   │
│ - key_decisions_and_learnings:       │
│   List[str]                          │
│ - journal_narrative: str             │
└──────────────────────────────────────┘
                │
                │ 1:1
                ▼
┌──────────────────────────────────────┐
│       FinalAgentReport                │
├──────────────────────────────────────┤
│ - summary: DailySummaryOutput        │
│ - pending_actions: List[ActionItem]  │
│ - suggested_first_task: str          │
├──────────────────────────────────────┤
│ + to_text() -> str                   │
│ + to_audio() -> str                  │
└──────────────────────────────────────┘
```

### 7.2 Service Layer Classes

```
┌──────────────────────────────────────┐
│     <<interface>>                    │
│     StorageBackend                   │
├──────────────────────────────────────┤
│ + save_entry(entry) -> bool         │
│ + get_entries(date) -> List[Entry]  │
│ + save_action_items(items) -> bool  │
│ + get_pending_actions() -> List[]   │
└──────────────┬───────────────────────┘
               │
        ┌──────┴──────┬──────────────┐
        │             │              │
        ▼             ▼              ▼
┌───────────┐ ┌───────────┐  ┌────────────┐
│   JSON    │ │  SQLite   │  │ Firestore  │
│  Storage  │ │  Storage  │  │  Storage   │
├───────────┤ ├───────────┤  ├────────────┤
│+save_     │ │+save_     │  │+save_      │
│ entry()   │ │ entry()   │  │ entry()    │
│+get_      │ │+get_      │  │+get_       │
│ entries() │ │ entries() │  │ entries()  │
└───────────┘ └───────────┘  └────────────┘

┌──────────────────────────────────────┐
│      StorageManager                  │
│      (Facade Pattern)                │
├──────────────────────────────────────┤
│ - backend: StorageBackend            │
├──────────────────────────────────────┤
│ + __init__(backend_type)             │
│ + save_entry(entry) -> bool         │
│ + get_entries() -> List[Entry]      │
└──────────────────────────────────────┘
```

---

## 8. Infrastructure Diagrams

### 8.1 AWS Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                         Internet                            │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    AWS Cloud                                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               Route 53 (DNS)                         │    │
│  │  • cja.yourdomain.com → CloudFront                   │    │
│  └──────────────────┬──────────────────────────────────┘    │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          CloudFront (CDN)                            │    │
│  │  • Global edge locations                             │    │
│  │  • SSL/TLS termination                               │    │
│  │  • DDoS protection                                   │    │
│  └──────────────────┬──────────────────────────────────┘    │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Application Load Balancer (ALB)                     │    │
│  │  • Health checks                                     │    │
│  │  • SSL offloading                                    │    │
│  │  • Path-based routing                                │    │
│  └──────────────────┬──────────────────────────────────┘    │
│                     │                                        │
│           ┌─────────┴─────────┐                              │
│           │                   │                              │
│           ▼                   ▼                              │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │  ECS Fargate   │  │  ECS Fargate   │                     │
│  │  Container 1   │  │  Container 2   │  (Auto-scaling)     │
│  │                │  │                │                     │
│  │  ┌──────────┐  │  │  ┌──────────┐  │                     │
│  │  │   CJA    │  │  │  │   CJA    │  │                     │
│  │  │   App    │  │  │  │   App    │  │                     │
│  │  └──────────┘  │  │  └──────────┘  │                     │
│  └────────┬───────┘  └────────┬───────┘                     │
│           │                   │                              │
│           └─────────┬─────────┘                              │
│                     │                                        │
│        ┌────────────┼────────────┬─────────────┐            │
│        │            │            │             │            │
│        ▼            ▼            ▼             ▼            │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   RDS   │ │   S3     │ │ Secrets  │ │CloudWatch│       │
│  │(Postgres│ │(Storage) │ │ Manager  │ │ (Logs)   │       │
│  └─────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                               │
│  VPC:                                                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Private Subnet: 10.0.1.0/24                        │     │
│  │ Public Subnet:  10.0.2.0/24                        │     │
│  │ Security Groups: ALB, ECS, RDS                     │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
                     │
                     │ (External APIs)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│           External Services                                   │
│  ┌──────────┐  ┌────────────┐  ┌───────────┐               │
│  │ OpenAI   │  │ ElevenLabs │  │   SMTP    │               │
│  │   API    │  │    API     │  │  Server   │               │
│  └──────────┘  └────────────┘  └───────────┘               │
└──────────────────────────────────────────────────────────────┘
```

### 8.2 Kubernetes Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                         │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │            Ingress Controller (NGINX)               │   │
│  │  • cja.yourdomain.com                               │   │
│  │  • SSL/TLS termination (cert-manager)               │   │
│  └──────────────────┬─────────────────────────────────┘   │
│                     │                                      │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Service (LoadBalancer)                 │   │
│  │  • External IP                                      │   │
│  │  • Port 80 → 8000                                   │   │
│  └──────────────────┬─────────────────────────────────┘   │
│                     │                                      │
│                     │ Load balance across pods            │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │           Deployment (cja-deployment)               │   │
│  │  replicas: 3                                        │   │
│  │                                                      │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐      │   │
│  │  │   Pod 1   │  │   Pod 2   │  │   Pod 3   │      │   │
│  │  │           │  │           │  │           │      │   │
│  │  │ ┌───────┐ │  │ ┌───────┐ │  │ ┌───────┐ │      │   │
│  │  │ │  CJA  │ │  │ │  CJA  │ │  │ │  CJA  │ │      │   │
│  │  │ │ App   │ │  │ │ App   │ │  │ │ App   │ │      │   │
│  │  │ └───────┘ │  │ └───────┘ │  │ └───────┘ │      │   │
│  │  │           │  │           │  │           │      │   │
│  │  │ Resources:│  │ Resources:│  │ Resources:│      │   │
│  │  │ CPU: 500m │  │ CPU: 500m │  │ CPU: 500m │      │   │
│  │  │ RAM: 512M │  │ RAM: 512M │  │ RAM: 512M │      │   │
│  │  └───────────┘  └───────────┘  └───────────┘      │   │
│  └────────────────────────────────────────────────────┘   │
│                     │                                      │
│                     │ Mount ConfigMaps/Secrets            │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │           Configuration                             │   │
│  │                                                      │   │
│  │  ┌─────────────┐        ┌─────────────┐           │   │
│  │  │ ConfigMap   │        │   Secret    │           │   │
│  │  │ cja-config  │        │ cja-secrets │           │   │
│  │  │             │        │             │           │   │
│  │  │ • ENV vars  │        │ • API keys  │           │   │
│  │  │ • Config    │        │ • Passwords │           │   │
│  │  └─────────────┘        └─────────────┘           │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Persistent Storage                          │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  PersistentVolumeClaim (PVC)                │   │   │
│  │  │  • data-volume                               │   │   │
│  │  │  • audio-volume                              │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Monitoring & Logging                        │   │
│  │                                                      │   │
│  │  ┌───────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │Prometheus │  │  Grafana   │  │  FluentD   │    │   │
│  │  │ (Metrics) │  │(Dashboard) │  │  (Logs)    │    │   │
│  │  └───────────┘  └────────────┘  └────────────┘    │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

This system design document provides comprehensive visual representations of the Cognitive Journal Agent architecture across multiple dimensions:

- **Context**: How the system fits into the broader ecosystem
- **Containers**: High-level deployment structure
- **Components**: Detailed internal architecture
- **Sequences**: Step-by-step interaction flows
- **Data**: How information moves through the system
- **State**: Workflow state transitions
- **Classes**: Object-oriented design
- **Infrastructure**: Cloud deployment patterns

These diagrams serve as:
1. **Communication Tool**: For stakeholders and developers
2. **Documentation**: Reference for implementation
3. **Design Guide**: Blueprint for future enhancements
4. **Onboarding**: New team member orientation

For additional details, refer to:
- `ARCHITECTURE.md`: Full architecture specification
- `DEPLOYMENT_GUIDE.md`: Deployment instructions
- `README.md`: Usage and getting started guide
