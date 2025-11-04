# Cognitive Journal Agent (CJA) - Architecture Design Document

**Version**: 1.0.0
**Last Updated**: 2025-11-03
**Author**: CJA Development Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Patterns](#architecture-patterns)
4. [System Architecture](#system-architecture)
5. [Component Architecture](#component-architecture)
6. [Data Architecture](#data-architecture)
7. [LangGraph Workflow Architecture](#langgraph-workflow-architecture)
8. [API Architecture](#api-architecture)
9. [Security Architecture](#security-architecture)
10. [Deployment Architecture](#deployment-architecture)
11. [Scalability & Performance](#scalability--performance)
12. [Integration Architecture](#integration-architecture)
13. [Design Decisions & Rationale](#design-decisions--rationale)
14. [Future Architecture Considerations](#future-architecture-considerations)

---

## 1. Executive Summary

The Cognitive Journal Agent (CJA) is a **multimodal, agentic personal assistant** built on a **LangGraph state machine** architecture. It provides intelligent journal management, automated task extraction, and daily summarization capabilities.

### Key Architectural Characteristics

- **Event-Driven State Machine**: LangGraph-based workflow orchestration
- **Microservices-Inspired**: Modular node-based processing pipeline
- **Multi-Backend Support**: Pluggable storage, LLM, and TTS providers
- **Fault-Tolerant**: Graceful degradation with fallback mechanisms
- **API-First**: REST API with CLI wrapper
- **Cloud-Native Ready**: Containerizable, scalable, observable

---

## 2. System Overview

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL ACTORS                               │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   User   │  │  Email   │  │ Calendar │  │   Web    │            │
│  │ (CLI/API)│  │  Server  │  │ Service  │  │ Search   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │             │             │              │                   │
└───────┼─────────────┼─────────────┼──────────────┼───────────────────┘
        │             │             │              │
        ▼             ▼             ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                COGNITIVE JOURNAL AGENT (CJA)                         │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                  API/CLI INTERFACE LAYER                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │    │
│  │  │  FastAPI     │  │  CLI Shell   │  │  Webhooks    │     │    │
│  │  │  REST API    │  │  Interface   │  │  (Future)    │     │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │    │
│  └─────────┼──────────────────┼──────────────────┼────────────┘    │
│            │                  │                  │                   │
│  ┌─────────▼──────────────────▼──────────────────▼────────────┐    │
│  │              LANGGRAPH ORCHESTRATION LAYER                  │    │
│  │                    (State Machine)                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │  Router  │  │Ingestion │  │Processing│  │ Storage  │   │    │
│  │  │   Node   │─▶│   Node   │─▶│   Node   │─▶│   Node   │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  │                                                             │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │    │
│  │  │  Agent   │  │Reporting │  │   TTS    │                 │    │
│  │  │   Node   │  │   Node   │  │   Node   │                 │    │
│  │  └──────────┘  └──────────┘  └──────────┘                 │    │
│  └─────────────────────────────────────────────────────────────    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  SERVICE LAYER                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │ Multimodal│  │   LLM    │  │  Tool    │  │  Storage │    │   │
│  │  │ Processor │  │ Service  │  │Executor  │  │ Manager  │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                 │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  OpenAI  │  │Anthropic │  │ElevenLabs│  │Firestore │            │
│  │   API    │  │   API    │  │   API    │  │   DB     │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 High-Level Architecture Principles

1. **Separation of Concerns**: Each node handles a single responsibility
2. **Loose Coupling**: Nodes communicate via state, not direct calls
3. **High Cohesion**: Related functionality grouped in modules
4. **Dependency Inversion**: Abstractions over concrete implementations
5. **Open/Closed Principle**: Open for extension, closed for modification
6. **Configuration Over Code**: Environment-driven behavior

---

## 3. Architecture Patterns

### 3.1 Primary Patterns

#### **State Machine Pattern (LangGraph)**
```
State → Transition → New State → Transition → ...
```
- Explicit state management
- Predictable state transitions
- Easy debugging and monitoring

#### **Pipeline Pattern**
```
Input → Process 1 → Process 2 → ... → Output
```
- Sequential data transformation
- Clear data flow
- Easy to add/remove stages

#### **Strategy Pattern**
```
Context → [Strategy A | Strategy B | Strategy C] → Result
```
- Interchangeable algorithms (LLM vs Rule-based)
- Runtime selection
- Easy A/B testing

#### **Repository Pattern**
```
Service → Repository Interface → [JSON | SQLite | Firestore]
```
- Abstract data access
- Swap storage backends
- Testable data layer

#### **Command Pattern (Tools)**
```
Agent → Tool Interface → [Email | Calendar | File | Search]
```
- Encapsulate actions as objects
- Extensible tool system
- Undo/redo capability (future)

### 3.2 Architectural Styles

- **Event-Driven Architecture**: State transitions trigger processing
- **Hexagonal Architecture**: Core logic isolated from external dependencies
- **Microkernel Architecture**: Core + plugins (tools, processors)
- **Layered Architecture**: API → Orchestration → Service → Data

---

## 4. System Architecture

### 4.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: PRESENTATION LAYER                                     │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│ │  FastAPI    │  │ CLI (REPL)  │  │  Webhooks   │             │
│ │  Endpoints  │  │  Interface  │  │  (Future)   │             │
│ └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: ORCHESTRATION LAYER (LangGraph)                        │
│ ┌─────────────────────────────────────────────────────────┐    │
│ │  State Management                                        │    │
│ │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │    │
│ │  │  Router  │  │  Nodes   │  │  Edges   │              │    │
│ │  └──────────┘  └──────────┘  └──────────┘              │    │
│ └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: BUSINESS LOGIC LAYER                                   │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │  Multimodal  │  │     LLM      │  │    Tool      │          │
│ │  Ingestion   │  │  Processing  │  │  Execution   │          │
│ └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │   Storage    │  │   Reporting  │  │     TTS      │          │
│ │   Manager    │  │  Generator   │  │   Output     │          │
│ └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: DATA ACCESS LAYER                                      │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │     JSON     │  │    SQLite    │  │  Firestore   │          │
│ │   Storage    │  │   Database   │  │   Database   │          │
│ └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 5: EXTERNAL SERVICES LAYER                                │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │  LLM APIs    │  │   TTS APIs   │  │  Tool APIs   │          │
│ │ OpenAI, etc. │  │ ElevenLabs   │  │ SMTP, etc.   │          │
│ └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Module Dependency Graph

```
┌────────────┐
│   main.py  │ ◄─── Entry Point
└─────┬──────┘
      │
      ├──────────────────────────────────────┐
      │                                       │
      ▼                                       ▼
┌────────────┐                        ┌─────────────┐
│  config.py │                        │ graph/      │
└────────────┘                        │ agent_graph │
                                      └──────┬──────┘
                                             │
                    ┌────────────────────────┼────────────────────┐
                    │                        │                    │
                    ▼                        ▼                    ▼
            ┌───────────────┐       ┌───────────────┐    ┌──────────────┐
            │ nodes/        │       │ tools/        │    │ data_models/ │
            │ - ingestion   │       │ external_tools│    │ schemas      │
            │ - processing  │       └───────────────┘    └──────────────┘
            │ - storage     │
            │ - reporting   │
            │ - output      │
            │ - agent       │
            └───────────────┘

Dependencies Flow: main → graph → nodes → data_models
                         └─────→ tools → data_models
                         └─────→ config
```

---

## 5. Component Architecture

### 5.1 Core Components

#### **A. LangGraph State Machine**

```python
┌─────────────────────────────────────────────────────────────┐
│                    AgentState (TypedDict)                    │
├─────────────────────────────────────────────────────────────┤
│  Input:                                                      │
│  - user_input: str                                           │
│  - input_data: Dict[str, Any]                                │
│                                                               │
│  Processing:                                                  │
│  - new_entry: JournalEntry                                   │
│  - all_entries: List[JournalEntry]                           │
│  - pending_actions: List[ActionItem]                         │
│                                                               │
│  Output:                                                      │
│  - final_report: FinalAgentReport                            │
│  - audio_output_path: str                                    │
│  - tool_response: str                                        │
└─────────────────────────────────────────────────────────────┘

        │
        ▼

┌─────────────────────────────────────────────────────────────┐
│                    Workflow Graph                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│     ┌─────────┐                                              │
│     │ START   │                                              │
│     └────┬────┘                                              │
│          │                                                    │
│          ▼                                                    │
│     ┌─────────┐                                              │
│     │ ROUTER  │ (conditional entry point)                    │
│     └────┬────┘                                              │
│          │                                                    │
│     ┌────┴──────────────┬─────────────────┐                 │
│     │                   │                 │                  │
│     ▼                   ▼                 ▼                  │
│ ┌────────┐      ┌────────────┐    ┌──────────┐             │
│ │ Agent  │      │ Ingestion  │    │Reporting │             │
│ │  Node  │      │    Node    │    │   Node   │             │
│ └───┬────┘      └─────┬──────┘    └────┬─────┘             │
│     │                 │                 │                    │
│     ▼                 ▼                 ▼                    │
│ [Optional]     ┌──────────┐      ┌─────────┐               │
│  Log Entry     │Processing│      │   TTS   │               │
│     │          │   Node   │      │  Node   │               │
│     └──────┐   └────┬─────┘      └────┬────┘               │
│            │        │                  │                    │
│            ▼        ▼                  │                    │
│          ┌──────────┐                 │                    │
│          │ Storage  │                 │                    │
│          │   Node   │                 │                    │
│          └────┬─────┘                 │                    │
│               │                       │                    │
│               ▼                       ▼                    │
│            ┌─────┐                 ┌─────┐                │
│            │ END │                 │ END │                │
│            └─────┘                 └─────┘                │
└─────────────────────────────────────────────────────────────┘
```

#### **B. Ingestion Component**

```
┌────────────────────────────────────────────────────────────┐
│              MultimodalIngest Processor                     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌───────────────────────┐          │
│  │ Input Type   │──────▶│  Processor Router     │          │
│  │ Detection    │      └───────┬───────────────┘          │
│  └──────────────┘              │                           │
│                                 │                           │
│         ┌───────────────────────┼────────────────┐         │
│         │           │           │       │        │         │
│         ▼           ▼           ▼       ▼        ▼         │
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌────┐ ┌──────┐      │
│    │  Text  │ │ Voice  │ │  OCR   │ │PDF │ │Email │      │
│    │Process │ │  STT   │ │Process │ │Proc│ │Parse │      │
│    └───┬────┘ └───┬────┘ └───┬────┘ └─┬──┘ └──┬───┘      │
│        │          │          │         │      │           │
│        └──────────┴──────────┴─────────┴──────┘           │
│                          │                                 │
│                          ▼                                 │
│                 ┌─────────────────┐                        │
│                 │  JournalEntry   │                        │
│                 │   Creation      │                        │
│                 └─────────────────┘                        │
│                                                             │
│  Supported Types:                                          │
│  • text_note                                               │
│  • voice_memo                                              │
│  • photo_ocr                                               │
│  • pdf_document                                            │
│  • code_snippet                                            │
│  • email                                                   │
│  • calendar_event                                          │
└────────────────────────────────────────────────────────────┘
```

#### **C. Processing Component**

```
┌────────────────────────────────────────────────────────────┐
│                Processing Architecture                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │ Configuration   │                                       │
│  │ USE_LLM_PROC=?  │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│     ┌─────┴─────┐                                          │
│     │           │                                          │
│     ▼           ▼                                          │
│ ┌────────┐  ┌──────────┐                                  │
│ │  LLM   │  │  Simple  │                                  │
│ │Process │  │ Process  │                                  │
│ └───┬────┘  └────┬─────┘                                  │
│     │            │                                         │
│     └────┬───────┘                                         │
│          │                                                 │
│          ▼                                                 │
│  ┌───────────────────────────────────────────┐            │
│  │        Extract & Annotate:                │            │
│  │  • Contextual Tags                        │            │
│  │    [Work, Personal, Task, Urgent, etc.]   │            │
│  │  • Action Items                           │            │
│  │    ["Email John", "Schedule meeting"]     │            │
│  │  • Emotional Tone                         │            │
│  │    [High Focus, Stressed, Reflective]     │            │
│  │  • Priority Score (1-10)                  │            │
│  │  • Key Entities                           │            │
│  │    [People, Places, Projects, Dates]      │            │
│  └───────────────────────────────────────────┘            │
│                                                             │
│  LLM Processor:                                            │
│  ┌────────────────────────────────────┐                   │
│  │ Prompt Template                    │                   │
│  │   ↓                                │                   │
│  │ LLM (OpenAI/Anthropic)             │                   │
│  │   ↓                                │                   │
│  │ Pydantic Output Parser             │                   │
│  │   ↓                                │                   │
│  │ ProcessedContent (Validated)       │                   │
│  └────────────────────────────────────┘                   │
│                                                             │
│  Simple Processor (Fallback):                              │
│  ┌────────────────────────────────────┐                   │
│  │ Rule-Based Analysis                │                   │
│  │ • Keyword matching                 │                   │
│  │ • Pattern recognition              │                   │
│  │ • Heuristic tagging                │                   │
│  └────────────────────────────────────┘                   │
└────────────────────────────────────────────────────────────┘
```

#### **D. Storage Component**

```
┌────────────────────────────────────────────────────────────┐
│              Storage Manager Architecture                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐                                      │
│  │ StorageManager   │                                      │
│  │   (Facade)       │                                      │
│  └────────┬─────────┘                                      │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────┐                                      │
│  │ Backend Selector │                                      │
│  │ (STORAGE_BACKEND)│                                      │
│  └────────┬─────────┘                                      │
│           │                                                 │
│     ┌─────┼─────┬─────────┐                                │
│     │     │     │         │                                │
│     ▼     ▼     ▼         ▼                                │
│  ┌────┐┌──────┐┌────────┐┌────────┐                       │
│  │JSON││SQLite││Firestore││Custom  │                       │
│  │Stor││  DB  ││ Cloud  ││Backend │                       │
│  └──┬─┘└───┬──┘└───┬────┘└───┬────┘                       │
│     │      │       │         │                             │
│     └──────┴───────┴─────────┘                             │
│            │                                                │
│            ▼                                                │
│  ┌─────────────────────┐                                   │
│  │  Storage Interface  │                                   │
│  │  - save_entry()     │                                   │
│  │  - get_entries()    │                                   │
│  │  - save_actions()   │                                   │
│  │  - get_actions()    │                                   │
│  └─────────────────────┘                                   │
│                                                             │
│  JSON Storage:                                              │
│  ┌──────────────────────────────────┐                     │
│  │ ./data/journal_entries.json      │                     │
│  │ ./data/action_items.json         │                     │
│  │                                  │                     │
│  │ Format: Array of objects         │                     │
│  │ Pros: Simple, portable           │                     │
│  │ Cons: No indexing, limited scale │                     │
│  └──────────────────────────────────┘                     │
│                                                             │
│  SQLite Storage:                                            │
│  ┌──────────────────────────────────┐                     │
│  │ ./data/journal.db                │                     │
│  │                                  │                     │
│  │ Tables:                          │                     │
│  │  - journal_entries               │                     │
│  │  - action_items                  │                     │
│  │                                  │                     │
│  │ Pros: Indexed, queryable         │                     │
│  │ Cons: Single-file, limited scale │                     │
│  └──────────────────────────────────┘                     │
│                                                             │
│  Firestore Storage:                                         │
│  ┌──────────────────────────────────┐                     │
│  │ Cloud Firestore                  │                     │
│  │                                  │                     │
│  │ Collections:                     │                     │
│  │  users/{userId}/journal_entries  │                     │
│  │  users/{userId}/action_items     │                     │
│  │                                  │                     │
│  │ Pros: Scalable, real-time, cloud│                     │
│  │ Cons: Network latency, cost      │                     │
│  └──────────────────────────────────┘                     │
└────────────────────────────────────────────────────────────┘
```

#### **E. Tool Execution Component**

```
┌────────────────────────────────────────────────────────────┐
│            Tool Execution Agent Architecture                │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────┐              │
│  │      User Command (Natural Language)    │              │
│  │   "Send email to John about project"    │              │
│  └──────────────────┬──────────────────────┘              │
│                     │                                      │
│                     ▼                                      │
│  ┌─────────────────────────────────────────┐              │
│  │       LangChain Agent Executor          │              │
│  │                                         │              │
│  │  ┌────────────────────────────────┐    │              │
│  │  │  ReAct/Functions Agent         │    │              │
│  │  │  - Reasoning                   │    │              │
│  │  │  - Tool Selection              │    │              │
│  │  │  - Parameter Extraction        │    │              │
│  │  │  - Execution                   │    │              │
│  │  └────────────┬───────────────────┘    │              │
│  └───────────────┼────────────────────────┘              │
│                  │                                         │
│                  ▼                                         │
│  ┌─────────────────────────────────────────┐              │
│  │         Tool Registry                   │              │
│  │     get_all_tools() → [tools]          │              │
│  └──────────────────┬──────────────────────┘              │
│                     │                                      │
│     ┌───────────────┼───────────────┬─────────┐           │
│     │               │               │         │           │
│     ▼               ▼               ▼         ▼           │
│ ┌────────┐     ┌─────────┐    ┌────────┐ ┌───────┐      │
│ │ Email  │     │Calendar │    │  File  │ │Search │      │
│ │  Tool  │     │  Tool   │    │  Tool  │ │ Tool  │      │
│ └───┬────┘     └────┬────┘    └───┬────┘ └───┬───┘      │
│     │               │              │          │           │
│     ▼               ▼              ▼          ▼           │
│ ┌────────┐     ┌─────────┐    ┌────────┐ ┌───────┐      │
│ │  SMTP  │     │Google/  │    │  File  │ │Search │      │
│ │ Server │     │Outlook/ │    │ System │ │  API  │      │
│ │        │     │ Local   │    │        │ │       │      │
│ └────────┘     └─────────┘    └────────┘ └───────┘      │
│                                                           │
│  Tool Interface (BaseTool):                              │
│  ┌──────────────────────────────────┐                    │
│  │ class MyTool(BaseTool):          │                    │
│  │   name: str                      │                    │
│  │   description: str               │                    │
│  │   args_schema: BaseModel         │                    │
│  │   def _run(...) -> str           │                    │
│  └──────────────────────────────────┘                    │
└────────────────────────────────────────────────────────────┘
```

#### **F. Reporting Component**

```
┌────────────────────────────────────────────────────────────┐
│              Reporting & Summarization                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────┐                     │
│  │  Input: List[JournalEntry]       │                     │
│  │         List[ActionItem]         │                     │
│  └─────────────┬────────────────────┘                     │
│                │                                           │
│                ▼                                           │
│  ┌──────────────────────────────────┐                     │
│  │  Reporter Selection              │                     │
│  │  (USE_LLM_REPORTING)             │                     │
│  └─────────────┬────────────────────┘                     │
│                │                                           │
│         ┌──────┴──────┐                                   │
│         │             │                                   │
│         ▼             ▼                                   │
│  ┌───────────┐  ┌──────────┐                             │
│  │   LLM     │  │  Simple  │                             │
│  │ Reporter  │  │ Reporter │                             │
│  └─────┬─────┘  └────┬─────┘                             │
│        │             │                                    │
│        └──────┬──────┘                                    │
│               │                                           │
│               ▼                                           │
│  ┌───────────────────────────────────────┐               │
│  │    FinalAgentReport Generation        │               │
│  │                                       │               │
│  │  1. DailySummaryOutput:               │               │
│  │     • Daily Theme (1-sentence)        │               │
│  │     • Key Decisions & Learnings       │               │
│  │     • Journal Narrative (2-3 para)    │               │
│  │                                       │               │
│  │  2. Pending Actions:                  │               │
│  │     • Organized by Priority           │               │
│  │     • P1 (Urgent) first               │               │
│  │     • Deduplicated                    │               │
│  │                                       │               │
│  │  3. Suggested First Task:             │               │
│  │     • Highest priority + impact       │               │
│  │     • Motivational framing            │               │
│  └───────────────────────────────────────┘               │
│                                                            │
│  LLM Reporter Pipeline:                                   │
│  ┌──────────────────────────────────────┐                │
│  │  1. Format Entries                   │                │
│  │  2. Create Prompt (System + User)    │                │
│  │  3. LLM Call (GPT-4/Claude)          │                │
│  │  4. Parse with Pydantic              │                │
│  │  5. Validate & Return                │                │
│  └──────────────────────────────────────┘                │
│                                                            │
│  Simple Reporter Pipeline:                                │
│  ┌──────────────────────────────────────┐                │
│  │  1. Count & Categorize Entries       │                │
│  │  2. Extract Tags & Emotions          │                │
│  │  3. Generate Basic Statistics        │                │
│  │  4. Create Template Summary          │                │
│  │  5. Prioritize Actions               │                │
│  └──────────────────────────────────────┘                │
└────────────────────────────────────────────────────────────┘
```

---

## 6. Data Architecture

### 6.1 Data Model

```
┌────────────────────────────────────────────────────────────┐
│                    Core Data Models                         │
├────────────────────────────────────────────────────────────┤

┌─────────────────────────────────────────────────────────┐
│                    JournalEntry                          │
├─────────────────────────────────────────────────────────┤
│ timestamp: datetime         # When captured             │
│ input_type: str            # text, voice, email, etc.   │
│ raw_content: str           # Original content           │
│ source_id: str             # Unique identifier          │
│ ─────────────────────────────────────────────────────── │
│ contextual_tags: List[str] # Work, Personal, Task, etc. │
│ extracted_action_items: List[str]  # Action phrases     │
│ inferred_emotion: str      # High Focus, Stressed, etc. │
└─────────────────────────────────────────────────────────┘
              │
              │ 1:N relationship
              ▼
┌─────────────────────────────────────────────────────────┐
│                    ActionItem                            │
├─────────────────────────────────────────────────────────┤
│ task_id: str               # Unique task ID             │
│ task_description: str      # What to do                 │
│ priority: str              # P1, P2, P3                 │
│ source_entry_id: str       # FK to JournalEntry         │
│ due_date: datetime         # Optional deadline          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                DailySummaryOutput                        │
├─────────────────────────────────────────────────────────┤
│ date: str                  # Summary date               │
│ daily_theme: str           # One-line theme             │
│ key_decisions_and_learnings: List[str]  # Top insights  │
│ journal_narrative: str     # 2-3 paragraph story        │
└─────────────────────────────────────────────────────────┘
              │
              │ 1:1 relationship
              ▼
┌─────────────────────────────────────────────────────────┐
│                FinalAgentReport                          │
├─────────────────────────────────────────────────────────┤
│ summary: DailySummaryOutput                             │
│ pending_actions: List[ActionItem]                       │
│ suggested_first_task: str                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   AgentState                             │
├─────────────────────────────────────────────────────────┤
│ user_input: str                                         │
│ input_data: Dict[str, Any]                              │
│ new_entry: JournalEntry                                 │
│ all_entries: List[JournalEntry]                         │
│ pending_actions: List[ActionItem]                       │
│ final_report: FinalAgentReport                          │
│ audio_output_path: str                                  │
│ tool_response: str                                      │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Data Flow Diagram

```
┌────────────────────────────────────────────────────────────┐
│                     Data Flow Pipeline                      │
└────────────────────────────────────────────────────────────┘

1. INPUT STAGE
   User Input (Text/Voice/Image/etc.)
         │
         ▼
   ┌─────────────┐
   │  Raw Data   │
   └──────┬──────┘
          │
          ▼
2. INGESTION STAGE
   ┌──────────────────┐
   │ MultimodalIngest │  → Converts to unified format
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  JournalEntry    │  (raw_content populated)
   │  - timestamp     │
   │  - input_type    │
   │  - raw_content   │
   │  - source_id     │
   └────────┬─────────┘
            │
            ▼
3. PROCESSING STAGE
   ┌──────────────────┐
   │   LLM/Rules      │  → Extract metadata
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  JournalEntry    │  (enriched)
   │  + tags          │
   │  + actions       │
   │  + emotion       │
   └────────┬─────────┘
            │
            ▼
4. STORAGE STAGE
   ┌──────────────────┐
   │  StorageManager  │  → Persist to backend
   └────────┬─────────┘
            │
     ┌──────┴──────┐
     ▼             ▼
┌─────────┐   ┌─────────────┐
│ Entries │   │ActionItems  │
│  Store  │   │    Store    │
└─────────┘   └─────────────┘
     │             │
     └──────┬──────┘
            │
            ▼
5. REPORTING STAGE (On Demand)
   ┌────────────────────────┐
   │  Load all_entries      │
   │  Load pending_actions  │
   └──────────┬─────────────┘
              │
              ▼
   ┌──────────────────┐
   │  DailyReporter   │  → Synthesize insights
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ FinalAgentReport │
   │  - summary       │
   │  - actions       │
   │  - suggestions   │
   └────────┬─────────┘
            │
            ▼
6. OUTPUT STAGE
   ┌──────────────────┐
   │   TTS Engine     │  → Convert to audio
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Audio File      │
   │  (MP3)           │
   └──────────────────┘
```

### 6.3 Database Schema (SQLite/Firestore)

#### **SQLite Schema**

```sql
-- Journal Entries Table
CREATE TABLE journal_entries (
    source_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    input_type TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    contextual_tags TEXT,        -- JSON array
    extracted_action_items TEXT, -- JSON array
    inferred_emotion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timestamp ON journal_entries(timestamp DESC);
CREATE INDEX idx_input_type ON journal_entries(input_type);

-- Action Items Table
CREATE TABLE action_items (
    task_id TEXT PRIMARY KEY,
    task_description TEXT NOT NULL,
    priority TEXT NOT NULL,
    source_entry_id TEXT NOT NULL,
    due_date TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_entry_id) REFERENCES journal_entries(source_id)
);

CREATE INDEX idx_priority ON action_items(priority);
CREATE INDEX idx_status ON action_items(status);
CREATE INDEX idx_due_date ON action_items(due_date);
```

#### **Firestore Schema**

```
users/
  {userId}/
    journal_entries/
      {entryId}/
        - timestamp: Timestamp
        - input_type: String
        - raw_content: String
        - contextual_tags: Array<String>
        - extracted_action_items: Array<String>
        - inferred_emotion: String

    action_items/
      {taskId}/
        - task_description: String
        - priority: String
        - source_entry_id: String
        - due_date: Timestamp
        - status: String
```

---

## 7. LangGraph Workflow Architecture

### 7.1 State Machine Diagram

```
                    ┌─────────────────┐
                    │  INITIAL STATE  │
                    │  user_input=""  │
                    │  all_entries=[] │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ CONDITIONAL     │
                    │ ENTRY POINT     │
                    │ (route_input)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌────────────────┐   ┌──────────────┐
│ JOURNAL PATH  │   │  ACTION PATH   │   │SUMMARY PATH  │
└───────┬───────┘   └────────┬───────┘   └──────┬───────┘
        │                    │                   │
        ▼                    ▼                   │
┌───────────────┐   ┌────────────────┐          │
│  INGESTION    │   │     AGENT      │          │
│     NODE      │   │  (Tool Exec)   │          │
└───────┬───────┘   └────────┬───────┘          │
        │                    │                   │
        ▼                    │                   │
┌───────────────┐            │                   │
│  PROCESSING   │            │                   │
│     NODE      │            │                   │
└───────┬───────┘            │                   │
        │                    │                   │
        ▼                    │                   │
┌───────────────┐            │                   │
│   STORAGE     │◄───────────┘                   │
│     NODE      │      (optional log)            │
└───────┬───────┘                                │
        │                                        │
        ▼                                        ▼
┌───────────────┐                       ┌────────────────┐
│      END      │                       │   REPORTING    │
└───────────────┘                       │      NODE      │
                                        └────────┬───────┘
                                                 │
                                                 ▼
                                        ┌────────────────┐
                                        │  TTS NODE      │
                                        │  (optional)    │
                                        └────────┬───────┘
                                                 │
                                                 ▼
                                        ┌────────────────┐
                                        │      END       │
                                        └────────────────┘
```

### 7.2 Node Specifications

#### **Router (Conditional Entry Point)**

```yaml
Type: Conditional Entry Point
Function: route_input(state) -> str
Logic:
  - Check for summary keywords → return "reporting"
  - Check for action keywords → return "agent"
  - Default → return "ingestion"
Output: Node name (string)
```

#### **Ingestion Node**

```yaml
Type: Processing Node
Function: ingestion_node(state) -> state
Input: state.user_input, state.input_data
Logic:
  1. Detect input type
  2. Route to appropriate processor
  3. Create JournalEntry object
Output: state.new_entry populated
Side Effects: None
```

#### **Processing Node**

```yaml
Type: Processing Node
Function: processing_node(state) -> state
Input: state.new_entry (with raw_content)
Logic:
  1. Select processor (LLM vs Simple)
  2. Extract tags, actions, emotion
  3. Update JournalEntry object
Output: state.new_entry enriched
Side Effects: LLM API calls (if enabled)
```

#### **Storage Node**

```yaml
Type: Processing Node
Function: storage_node(state) -> state
Input: state.new_entry
Logic:
  1. Save entry to backend
  2. Extract & save action items
  3. Reload all_entries and pending_actions
Output:
  - state.all_entries updated
  - state.pending_actions updated
Side Effects: Database writes
```

#### **Agent Node**

```yaml
Type: Processing Node
Function: agent_node(state) -> state
Input: state.user_input
Logic:
  1. Initialize LangChain Agent
  2. Execute with tools
  3. Capture result
Output: state.tool_response populated
Side Effects: Tool executions (emails, calendar, etc.)
```

#### **Reporting Node**

```yaml
Type: Processing Node
Function: reporting_node(state) -> state
Input: state.all_entries, state.pending_actions
Logic:
  1. Select reporter (LLM vs Simple)
  2. Generate FinalAgentReport
  3. Format output
Output: state.final_report populated
Side Effects: LLM API calls (if enabled)
```

#### **TTS Node**

```yaml
Type: Processing Node
Function: tts_node(state) -> state
Input: state.final_report
Logic:
  1. Format report for speech
  2. Call TTS service
  3. Save audio file
Output: state.audio_output_path populated
Side Effects: File writes, API calls
```

### 7.3 Edge Definitions

```python
# Journal Path
ingestion → processing → storage → END

# Action Path
agent → [conditional]
  if tool_response exists: → ingestion (to log)
  else: → END

# Summary Path
reporting → [conditional]
  if TTS_ENABLED: → tts → END
  else: → END
```

---

## 8. API Architecture

### 8.1 REST API Design

#### **Endpoint Structure**

```
Base URL: http://localhost:8000

┌─────────────────────────────────────────────────────────┐
│                     API Endpoints                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET  /                                                  │
│    → System information                                  │
│                                                          │
│  GET  /health                                            │
│    → Health check status                                 │
│                                                          │
│  POST /journal                                           │
│    → Create new journal entry                            │
│    Request: JournalRequest                               │
│    Response: JournalResponse                             │
│                                                          │
│  GET  /entries                                           │
│    → Retrieve all journal entries                        │
│    Response: List[JournalEntry]                          │
│                                                          │
│  GET  /entries/{entry_id}                                │
│    → Get specific entry (future)                         │
│                                                          │
│  GET  /actions                                           │
│    → Get pending action items                            │
│    Response: List[ActionItem]                            │
│                                                          │
│  POST /actions/{action_id}/complete                      │
│    → Mark action as complete (future)                    │
│                                                          │
│  POST /summarize                                         │
│    → Generate daily summary                              │
│    Response: FinalAgentReport                            │
│                                                          │
│  GET  /audio/{report_id}                                 │
│    → Download audio report (future)                      │
│                                                          │
│  WS   /stream                                            │
│    → WebSocket for real-time updates (future)            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### **Request/Response Models**

```python
# POST /journal
Request:
{
  "user_input": "Had a great meeting today",
  "input_data": {  # Optional
    "type": "text_note",
    "metadata": {...}
  }
}

Response:
{
  "success": true,
  "message": "Journal entry recorded",
  "data": {
    "type": "journal_entry",
    "entry_id": "text_abc123",
    "tags": ["Work", "Meeting"],
    "action_items": ["Send follow-up email"]
  }
}

# GET /entries
Response:
{
  "success": true,
  "count": 42,
  "entries": [
    {
      "source_id": "text_abc123",
      "timestamp": "2024-01-15T10:30:00",
      "input_type": "text_note",
      "raw_content": "...",
      "contextual_tags": ["Work"],
      "extracted_action_items": ["..."],
      "inferred_emotion": "High Focus"
    },
    ...
  ]
}

# POST /summarize
Response:
{
  "success": true,
  "report": {
    "summary": {
      "date": "2024-01-15",
      "daily_theme": "...",
      "key_decisions_and_learnings": [...],
      "journal_narrative": "..."
    },
    "pending_actions": [...],
    "suggested_first_task": "..."
  },
  "audio_path": "./audio_output/report_2024-01-15.mp3"
}
```

### 8.2 API Layer Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Client Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   Web    │  │  Mobile  │  │   CLI    │            │
│  │   App    │  │   App    │  │  Client  │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│               API Gateway / Load Balancer               │
│                      (Future)                           │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Application                     │
│  ┌──────────────────────────────────────────────┐     │
│  │         Middleware Stack                      │     │
│  │  ┌────────────┐  ┌────────────┐             │     │
│  │  │   CORS     │  │  Auth      │             │     │
│  │  │ Middleware │  │ (Future)   │             │     │
│  │  └────────────┘  └────────────┘             │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │          Route Handlers                       │     │
│  │  ┌────────┐  ┌────────┐  ┌────────┐         │     │
│  │  │Journal │  │Entries │  │Summary │         │     │
│  │  │Handler │  │Handler │  │Handler │         │     │
│  │  └───┬────┘  └───┬────┘  └───┬────┘         │     │
│  └──────┼───────────┼───────────┼───────────────┘     │
└─────────┼───────────┼───────────┼─────────────────────┘
          │           │           │
          └───────────┴───────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│              LangGraph Orchestration                    │
│              (See Section 7)                            │
└────────────────────────────────────────────────────────┘
```

---

## 9. Security Architecture

### 9.1 Security Layers

```
┌────────────────────────────────────────────────────────┐
│                 Security Architecture                   │
├────────────────────────────────────────────────────────┤

LAYER 1: API Security
┌─────────────────────────────────────────────────────┐
│ • CORS Configuration                                 │
│   - Allowed origins configurable                     │
│   - Credentials handling                             │
│                                                       │
│ • Rate Limiting (Future)                             │
│   - Per-IP throttling                                │
│   - API key quotas                                   │
│                                                       │
│ • Authentication (Future)                            │
│   - JWT tokens                                       │
│   - OAuth2 integration                               │
│   - API key management                               │
│                                                       │
│ • Input Validation                                   │
│   - Pydantic model validation                        │
│   - SQL injection prevention                         │
│   - XSS prevention                                   │
└─────────────────────────────────────────────────────┘

LAYER 2: Data Security
┌─────────────────────────────────────────────────────┐
│ • Encryption at Rest (Future)                        │
│   - Database encryption                              │
│   - Encrypted file storage                           │
│                                                       │
│ • Encryption in Transit                              │
│   - HTTPS/TLS for API                                │
│   - Encrypted external API calls                     │
│                                                       │
│ • Data Privacy                                       │
│   - User data isolation                              │
│   - PII handling                                     │
│   - GDPR compliance ready                            │
└─────────────────────────────────────────────────────┘

LAYER 3: Secrets Management
┌─────────────────────────────────────────────────────┐
│ • Environment Variables                              │
│   - .env file (development)                          │
│   - Never committed to repo                          │
│                                                       │
│ • Secrets Vault (Production)                         │
│   - AWS Secrets Manager                              │
│   - HashiCorp Vault                                  │
│   - Azure Key Vault                                  │
│                                                       │
│ • API Key Rotation                                   │
│   - Regular key rotation policies                    │
│   - Audit logging                                    │
└─────────────────────────────────────────────────────┘

LAYER 4: Application Security
┌─────────────────────────────────────────────────────┐
│ • Dependency Scanning                                │
│   - pip-audit                                        │
│   - Dependabot alerts                                │
│                                                       │
│ • Code Analysis                                      │
│   - Static analysis (bandit)                         │
│   - Linting (flake8, mypy)                          │
│                                                       │
│ • Sandboxing                                         │
│   - Tool execution limits                            │
│   - Resource constraints                             │
└─────────────────────────────────────────────────────┘

LAYER 5: Infrastructure Security
┌─────────────────────────────────────────────────────┐
│ • Network Security                                   │
│   - Firewall rules                                   │
│   - VPC configuration                                │
│                                                       │
│ • Container Security                                 │
│   - Non-root users                                   │
│   - Minimal base images                              │
│   - Vulnerability scanning                           │
│                                                       │
│ • Monitoring & Logging                               │
│   - Access logs                                      │
│   - Error tracking                                   │
│   - Anomaly detection                                │
└─────────────────────────────────────────────────────┘
```

### 9.2 Authentication Flow (Future)

```
┌────────────┐                 ┌────────────┐
│   Client   │                 │   Server   │
└─────┬──────┘                 └─────┬──────┘
      │                              │
      │ 1. Login Request             │
      │  (username, password)        │
      │─────────────────────────────▶│
      │                              │
      │                              │ 2. Validate Credentials
      │                              │    (bcrypt hash check)
      │                              │
      │ 3. JWT Token                 │
      │  (access + refresh)          │
      │◄─────────────────────────────│
      │                              │
      │ 4. API Request               │
      │  (Authorization: Bearer JWT) │
      │─────────────────────────────▶│
      │                              │
      │                              │ 5. Validate Token
      │                              │    (signature, expiry)
      │                              │
      │ 6. Response                  │
      │◄─────────────────────────────│
      │                              │
```

---

## 10. Deployment Architecture

### 10.1 Deployment Options

#### **Option A: Local Deployment**

```
┌────────────────────────────────────────────┐
│           Local Machine                     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Python Environment              │     │
│  │  - Python 3.9+                   │     │
│  │  - Virtual Environment           │     │
│  │  - Dependencies from requirements│     │
│  └──────────────────────────────────┘     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Application                     │     │
│  │  - main.py (CLI/API)             │     │
│  │  - Config from .env              │     │
│  └──────────────────────────────────┘     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Local Storage                   │     │
│  │  - ./data/                       │     │
│  │  - ./audio_output/               │     │
│  └──────────────────────────────────┘     │
└────────────────────────────────────────────┘
```

#### **Option B: Docker Deployment**

```
┌────────────────────────────────────────────┐
│           Docker Container                  │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Base Image                      │     │
│  │  - python:3.11-slim              │     │
│  └──────────────────────────────────┘     │
│                 │                          │
│                 ▼                          │
│  ┌──────────────────────────────────┐     │
│  │  Dependencies Layer              │     │
│  │  - pip install -r requirements   │     │
│  └──────────────────────────────────┘     │
│                 │                          │
│                 ▼                          │
│  ┌──────────────────────────────────┐     │
│  │  Application Layer               │     │
│  │  - COPY cognitive_journal_agent/ │     │
│  │  - EXPOSE 8000                   │     │
│  │  - CMD ["python", "main.py"]     │     │
│  └──────────────────────────────────┘     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Volume Mounts                   │     │
│  │  - /app/data (persistent)        │     │
│  │  - /app/audio_output             │     │
│  └──────────────────────────────────┘     │
└────────────────────────────────────────────┘
```

#### **Option C: Cloud Deployment (AWS)**

```
┌──────────────────────────────────────────────────────────┐
│                    AWS Cloud Architecture                 │
└──────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │  Route 53       │
                    │  (DNS)          │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  CloudFront     │
                    │  (CDN)          │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  ALB            │
                    │  (Load Balancer)│
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐        ┌───────────────┐
        │  ECS Fargate  │        │  ECS Fargate  │
        │  (Container 1)│        │  (Container 2)│
        └───────┬───────┘        └───────┬───────┘
                │                        │
                └────────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐        ┌───────────────┐
        │  RDS          │        │  S3           │
        │  (PostgreSQL) │        │  (File Store) │
        └───────────────┘        └───────────────┘
                │                        │
                └────────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Secrets Manager │
                    │ (API Keys)      │
                    └─────────────────┘
```

### 10.2 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY cognitive_journal_agent/ ./cognitive_journal_agent/
COPY .env.template .env

# Create directories
RUN mkdir -p /app/data /app/audio_output /app/temp_ingestion

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "-m", "cognitive_journal_agent.main", "api"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=openai
      - STORAGE_BACKEND=json
      - TTS_ENABLED=true
    volumes:
      - ./data:/app/data
      - ./audio_output:/app/audio_output
    env_file:
      - .env
    restart: unless-stopped

  # Future: PostgreSQL database
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: journal
  #     POSTGRES_USER: journal_user
  #     POSTGRES_PASSWORD: ${DB_PASSWORD}
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 10.3 Kubernetes Deployment (Future)

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cognitive-journal-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cja
  template:
    metadata:
      labels:
        app: cja
    spec:
      containers:
      - name: cja
        image: cja:latest
        ports:
        - containerPort: 8000
        env:
        - name: STORAGE_BACKEND
          value: "firestore"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: cja-secrets
              key: openai-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: cja-service
spec:
  selector:
    app: cja
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 11. Scalability & Performance

### 11.1 Scalability Strategy

```
┌────────────────────────────────────────────────────────┐
│              Scalability Dimensions                     │
├────────────────────────────────────────────────────────┤

HORIZONTAL SCALING
┌─────────────────────────────────────────────────────┐
│ • Stateless API Servers                              │
│   - Deploy multiple FastAPI instances                │
│   - Load balancer distribution                       │
│   - Auto-scaling based on CPU/memory                 │
│                                                       │
│ • Database Sharding (Future)                         │
│   - Shard by user_id                                 │
│   - Read replicas for queries                        │
│                                                       │
│ • Cache Layer (Future)                               │
│   - Redis for session data                           │
│   - Cached LLM responses                             │
└─────────────────────────────────────────────────────┘

VERTICAL SCALING
┌─────────────────────────────────────────────────────┐
│ • Resource Optimization                              │
│   - Efficient data structures                        │
│   - Connection pooling                               │
│   - Async I/O where possible                         │
│                                                       │
│ • Hardware Upgrades                                  │
│   - More CPU for LLM processing                      │
│   - More RAM for in-memory caching                   │
└─────────────────────────────────────────────────────┘

FUNCTIONAL SCALING
┌─────────────────────────────────────────────────────┐
│ • Microservices Architecture (Future)                │
│   - Separate ingestion service                       │
│   - Separate processing service                      │
│   - Separate reporting service                       │
│                                                       │
│ • Queue-Based Processing                             │
│   - Async job queue (Celery/RQ)                     │
│   - Background workers                               │
└─────────────────────────────────────────────────────┘
```

### 11.2 Performance Optimization

```
┌────────────────────────────────────────────────────────┐
│           Performance Optimization Strategy             │
├────────────────────────────────────────────────────────┤

DATABASE LAYER
• Indexing Strategy
  - Primary key indexes
  - Timestamp indexes for queries
  - Composite indexes for common queries

• Query Optimization
  - SELECT only required fields
  - Pagination for large result sets
  - Prepared statements

• Connection Pooling
  - Reuse database connections
  - Configurable pool size

CACHING STRATEGY (Future)
• Multi-Level Cache
  L1: In-memory LRU cache (functools.lru_cache)
  L2: Redis distributed cache
  L3: CDN for static assets

• Cache Keys
  - entries:{user_id}:{date}
  - summary:{user_id}:{date}
  - actions:{user_id}

• Cache Invalidation
  - Time-based (TTL)
  - Event-based (on write)

API LAYER
• Response Compression
  - gzip compression for responses
  - Brotli for modern clients

• Async Processing
  - FastAPI async endpoints
  - Async database drivers
  - Concurrent LLM calls

• Rate Limiting
  - Per-user quotas
  - IP-based throttling

LLM OPTIMIZATION
• Batch Processing
  - Combine multiple entries in one LLM call
  - Parallel processing where possible

• Model Selection
  - Use smaller models for simple tasks
  - GPT-3.5 for tagging, GPT-4 for summaries

• Prompt Optimization
  - Shorter, more focused prompts
  - Few-shot examples

• Response Caching
  - Cache LLM responses
  - Reuse similar inputs
```

### 11.3 Performance Benchmarks

```
Target Performance Metrics:

API Response Times:
- POST /journal: < 500ms (without LLM)
                 < 3s (with LLM)
- GET  /entries: < 100ms
- POST /summarize: < 5s (for 50 entries)

Throughput:
- 100 requests/second (single instance)
- 1000 requests/second (with load balancing)

Resource Usage:
- Memory: < 512MB per instance
- CPU: < 50% under normal load
- Disk: Dependent on data volume

LLM Processing:
- Entry processing: < 2s
- Daily summary: < 5s
- Batch processing: < 10s for 100 entries
```

---

## 12. Integration Architecture

### 12.1 External Integrations

```
┌────────────────────────────────────────────────────────┐
│                 Integration Map                         │
└────────────────────────────────────────────────────────┘

LLM PROVIDERS
┌─────────────────────────────────────────────────────┐
│ OpenAI                                               │
│  - API: https://api.openai.com/v1                   │
│  - Models: GPT-4, GPT-3.5-turbo                     │
│  - Auth: Bearer token                                │
│  - Rate Limits: Tier-based                          │
│                                                       │
│ Anthropic                                            │
│  - API: https://api.anthropic.com                   │
│  - Models: Claude 3.5, Claude 3                     │
│  - Auth: x-api-key header                           │
│  - Rate Limits: Request-based                       │
└─────────────────────────────────────────────────────┘

TEXT-TO-SPEECH
┌─────────────────────────────────────────────────────┐
│ ElevenLabs                                           │
│  - API: https://api.elevenlabs.io/v1               │
│  - Voices: 50+ pre-built voices                     │
│  - Auth: xi-api-key header                          │
│  - Format: MP3 output                               │
│                                                       │
│ Local TTS (pyttsx3)                                  │
│  - No API required                                   │
│  - Offline capability                                │
│  - Cross-platform                                    │
└─────────────────────────────────────────────────────┘

EMAIL & CALENDAR
┌─────────────────────────────────────────────────────┐
│ SMTP (Email)                                         │
│  - Protocols: SMTP, STARTTLS                        │
│  - Providers: Gmail, Outlook, Custom                │
│  - Auth: Username/password or OAuth2                │
│                                                       │
│ Google Calendar                                      │
│  - API: Google Calendar API v3                      │
│  - Auth: OAuth 2.0                                  │
│  - Scope: calendar.events                           │
│                                                       │
│ Microsoft Outlook                                    │
│  - API: Microsoft Graph API                         │
│  - Auth: MSAL (OAuth 2.0)                           │
│  - Scope: Calendars.ReadWrite                       │
└─────────────────────────────────────────────────────┘

STORAGE
┌─────────────────────────────────────────────────────┐
│ Google Cloud Firestore                               │
│  - API: Firestore REST/gRPC API                     │
│  - Auth: Service account credentials                │
│  - Collections: journal_entries, action_items       │
└─────────────────────────────────────────────────────┘
```

### 12.2 Integration Patterns

#### **API Client Pattern**

```python
class ExternalServiceClient:
    """Base class for external service integrations."""

    def __init__(self):
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.session = self._create_session()

    def _get_api_key(self) -> str:
        """Retrieve API key from config."""
        pass

    def _create_session(self):
        """Create HTTP session with retry logic."""
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.3)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with error handling."""
        try:
            response = self.session.request(
                method, f"{self.base_url}{endpoint}", **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
```

#### **Circuit Breaker Pattern (Future)**

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_llm_api(prompt):
    """
    Call LLM API with circuit breaker.
    If 5 failures occur, circuit opens for 60 seconds.
    """
    return llm_client.generate(prompt)
```

---

## 13. Design Decisions & Rationale

### 13.1 Key Architectural Decisions

#### **Decision 1: LangGraph for Orchestration**

**Choice**: LangGraph state machine
**Alternatives Considered**: Custom workflow, Apache Airflow, Prefect

**Rationale**:
- ✅ Built specifically for LLM workflows
- ✅ First-class state management
- ✅ Conditional edges for complex routing
- ✅ Easy debugging and visualization
- ✅ Integrates seamlessly with LangChain tools
- ❌ Newer framework (less mature than alternatives)

**Trade-offs**:
- Learning curve for LangGraph-specific patterns
- Framework lock-in (but benefits outweigh)

---

#### **Decision 2: Pydantic for Data Validation**

**Choice**: Pydantic v2
**Alternatives Considered**: Dataclasses, Marshmallow, attrs

**Rationale**:
- ✅ Type safety and validation
- ✅ Automatic JSON schema generation
- ✅ Native LangChain integration
- ✅ Fast (C bindings)
- ✅ IDE support (autocomplete, type hints)

**Trade-offs**:
- Slightly more verbose than dataclasses
- Migration path from v1 to v2 has deprecations

---

#### **Decision 3: Multi-Backend Storage**

**Choice**: Repository pattern with JSON/SQLite/Firestore
**Alternatives Considered**: Single backend (PostgreSQL), MongoDB

**Rationale**:
- ✅ Flexibility for different deployment scenarios
- ✅ JSON for quick start (no setup required)
- ✅ SQLite for local production use
- ✅ Firestore for cloud scalability
- ✅ Easy to add new backends

**Trade-offs**:
- More code to maintain (3 implementations)
- Testing complexity (test all backends)

---

#### **Decision 4: LLM with Fallback**

**Choice**: LLM processing with rule-based fallback
**Alternatives Considered**: LLM-only, Rule-based only

**Rationale**:
- ✅ Graceful degradation (no API key required)
- ✅ Cost optimization (can disable LLM)
- ✅ Development without API costs
- ✅ Better user experience (always works)

**Trade-offs**:
- Two code paths to maintain
- Rule-based is less accurate

---

#### **Decision 5: TypedDict for State vs Pydantic**

**Choice**: TypedDict for LangGraph state
**Alternatives Considered**: Pydantic BaseModel

**Rationale**:
- ✅ LangGraph compatibility
- ✅ Lighter weight (no validation overhead)
- ✅ Mutable state (LangGraph requirement)
- ❌ Less type safety than Pydantic

**Trade-offs**:
- No runtime validation on state updates
- Type hints only (not enforced)

---

### 13.2 Design Pattern Usage

| Pattern | Usage | Benefit |
|---------|-------|---------|
| State Machine | LangGraph workflow | Predictable state transitions |
| Repository | Storage backends | Abstract data access |
| Strategy | LLM vs Rules | Runtime algorithm selection |
| Factory | Tool creation | Centralized object creation |
| Facade | StorageManager | Simplified interface |
| Command | LangChain tools | Encapsulate actions |
| Observer | Future: WebSocket | Real-time updates |
| Singleton | Config object | Single source of truth |

---

## 14. Future Architecture Considerations

### 14.1 Planned Enhancements

#### **Phase 1: Core Improvements** (3-6 months)

```
┌─────────────────────────────────────────────────┐
│ • Authentication & Authorization                 │
│   - JWT-based auth                               │
│   - Multi-user support                           │
│   - Role-based access control                    │
│                                                   │
│ • Advanced Storage                               │
│   - PostgreSQL backend                           │
│   - Full-text search (Elasticsearch)             │
│   - Vector embeddings for semantic search        │
│                                                   │
│ • Enhanced Reporting                             │
│   - Weekly/monthly summaries                     │
│   - Trend analysis                               │
│   - Goal tracking                                │
└─────────────────────────────────────────────────┘
```

#### **Phase 2: Advanced Features** (6-12 months)

```
┌─────────────────────────────────────────────────┐
│ • Real-time Capabilities                         │
│   - WebSocket support                            │
│   - Live entry updates                           │
│   - Collaborative journaling                     │
│                                                   │
│ • Advanced AI Features                           │
│   - Sentiment analysis over time                 │
│   - Anomaly detection (mood changes)             │
│   - Predictive insights                          │
│   - Custom trained models                        │
│                                                   │
│ • Mobile Integration                             │
│   - Native mobile apps                           │
│   - Push notifications                           │
│   - Voice-first interface                        │
└─────────────────────────────────────────────────┘
```

#### **Phase 3: Enterprise Features** (12+ months)

```
┌─────────────────────────────────────────────────┐
│ • Multi-tenancy                                  │
│   - Organization accounts                        │
│   - Team collaboration                           │
│   - Admin dashboards                             │
│                                                   │
│ • Advanced Integrations                          │
│   - Slack/Teams integration                      │
│   - CRM integration (Salesforce)                 │
│   - Project management (Jira, Asana)             │
│                                                   │
│ • Enterprise Security                            │
│   - SSO (SAML, OAuth)                            │
│   - Audit logging                                │
│   - Compliance (HIPAA, SOC 2)                    │
└─────────────────────────────────────────────────┘
```

### 14.2 Microservices Evolution

```
Current Monolith → Future Microservices

┌─────────────────────────────────────────────────┐
│              Current Architecture                │
│                                                   │
│  ┌─────────────────────────────────────────┐   │
│  │         Single Application              │   │
│  │  (All nodes in one process)             │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘

                    ↓  Evolution  ↓

┌─────────────────────────────────────────────────┐
│           Future Microservices                   │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Ingestion │  │Processing│  │ Storage  │      │
│  │ Service  │  │ Service  │  │ Service  │      │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘      │
│        │             │              │           │
│        └─────────────┴──────────────┘           │
│                      │                          │
│              ┌───────┴────────┐                 │
│              │ Message Queue  │                 │
│              │  (RabbitMQ)    │                 │
│              └────────────────┘                 │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Reporting │  │   TTS    │  │   API    │      │
│  │ Service  │  │ Service  │  │ Gateway  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

### 14.3 AI/ML Enhancements

```
┌────────────────────────────────────────────────────────┐
│            Advanced AI Architecture (Future)            │
├────────────────────────────────────────────────────────┤

EMBEDDING & SEMANTIC SEARCH
┌─────────────────────────────────────────────────────┐
│ • Vector Database (Pinecone/Weaviate)                │
│   - Semantic search across entries                   │
│   - Similar entry recommendations                    │
│   - Automatic clustering                            │
│                                                       │
│ • RAG (Retrieval Augmented Generation)               │
│   - Context-aware summarization                      │
│   - Cross-entry insights                            │
└─────────────────────────────────────────────────────┘

CUSTOM MODELS
┌─────────────────────────────────────────────────────┐
│ • Fine-tuned Classification                          │
│   - Personal tag taxonomy                            │
│   - Custom emotion detection                         │
│   - Priority prediction                              │
│                                                       │
│ • User-specific Models                               │
│   - Learn individual writing patterns                │
│   - Personalized suggestions                         │
└─────────────────────────────────────────────────────┘

ANALYTICS & INSIGHTS
┌─────────────────────────────────────────────────────┐
│ • Time Series Analysis                               │
│   - Mood trends over time                            │
│   - Productivity patterns                            │
│   - Topic evolution                                  │
│                                                       │
│ • Predictive Analytics                               │
│   - Burnout detection                                │
│   - Goal achievement likelihood                      │
│   - Optimal task scheduling                          │
└─────────────────────────────────────────────────────┘
```

---

## Conclusion

The Cognitive Journal Agent represents a modern, production-ready architecture that balances:

1. **Flexibility**: Multiple backends, LLM providers, and deployment options
2. **Reliability**: Fallback mechanisms, error handling, graceful degradation
3. **Scalability**: Horizontal scaling, caching, async processing
4. **Maintainability**: Modular design, clear separation of concerns
5. **Extensibility**: Plugin architecture for tools, easy to add features

The architecture is designed to evolve from a single-user CLI tool to a multi-tenant SaaS platform while maintaining backward compatibility and minimizing technical debt.

**Key Strengths**:
- LangGraph provides robust state management
- Pydantic ensures data integrity
- Multi-backend design supports various use cases
- Comprehensive security considerations
- Cloud-native ready

**Areas for Future Work**:
- Microservices decomposition
- Advanced AI/ML features
- Real-time collaboration
- Enterprise-grade security
- Mobile-first experience

---

**Document Revision History**:
- v1.0.0 (2025-11-03): Initial architecture design
