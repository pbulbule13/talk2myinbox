# Cognitive Journal Agent - API Documentation

**Version**: 1.0.0
**Date**: 2025-11-03
**Status**: Production Ready
**Base URL**: `http://localhost:8000` (local) or `https://api.yourproject.com` (production)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Usage Examples](#usage-examples)
8. [WebSocket Support](#websocket-support)
9. [Webhook Support (Future)](#webhook-support-future)
10. [SDKs and Client Libraries](#sdks-and-client-libraries)

---

## Overview

The Cognitive Journal Agent (CJA) provides a RESTful API for programmatic access to journaling, processing, and reporting capabilities. The API follows REST principles and uses JSON for request/response payloads.

### Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://api.yourproject.com`

### API Version

Current version: `v1`

All endpoints are prefixed with `/api` (e.g., `/api/entry`)

### Content Type

All requests and responses use `application/json` content type.

### Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource successfully created
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Authentication

### API Key Authentication

**Header:** `X-API-Key`

```bash
curl -H "X-API-Key: your-api-key-here" \
  http://localhost:8000/api/entry
```

### OAuth 2.0 (Future)

OAuth 2.0 support planned for multi-user scenarios.

**Flow:** Authorization Code Grant

### Obtaining an API Key

API keys are generated during deployment or via admin interface.

**Local Development:** API key validation disabled by default. Set `REQUIRE_AUTH=true` in `.env` to enable.

**Production:** API keys required. Configure via environment variable:

```bash
API_KEYS=key1,key2,key3  # Comma-separated list
```

---

## API Endpoints

### 1. Create Journal Entry

**Endpoint:** `POST /api/entry`

**Description:** Create a new journal entry from various input types.

**Authentication:** Required

**Request Body:**
```json
{
  "input_type": "text_note",
  "content": "Met with team to discuss API design. Need to finalize endpoints by Friday.",
  "metadata": {
    "source": "mobile_app",
    "location": "Office"
  }
}
```

**Request Schema:**
- `input_type` (string, required): One of: `text_note`, `voice_memo`, `photo_ocr`, `pdf_document`, `code_snippet`, `email`, `calendar_event`
- `content` (string, required): Raw input content or file path
- `metadata` (object, optional): Additional arbitrary metadata

**Response:**
```json
{
  "status": "success",
  "data": {
    "entry_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2025-11-03T14:30:00Z",
    "input_type": "text_note",
    "raw_content": "Met with team to discuss API design. Need to finalize endpoints by Friday.",
    "contextual_tags": ["api-design", "meeting", "deadline"],
    "extracted_action_items": ["Finalize API endpoints by Friday"],
    "inferred_emotion": "focused",
    "priority_score": 7,
    "processed": true
  },
  "message": "Journal entry created successfully"
}
```

**Status Codes:**
- `201 Created`: Entry successfully created
- `400 Bad Request`: Invalid input type or missing content
- `500 Internal Server Error`: Processing failed

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "input_type": "text_note",
    "content": "Completed feature implementation today. Feeling productive!"
  }'
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/api/entry"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key"
}
payload = {
    "input_type": "text_note",
    "content": "Completed feature implementation today. Feeling productive!"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

---

### 2. Get Journal Entry

**Endpoint:** `GET /api/entry/{entry_id}`

**Description:** Retrieve a specific journal entry by ID.

**Authentication:** Required

**Path Parameters:**
- `entry_id` (string, required): UUID of the journal entry

**Response:**
```json
{
  "status": "success",
  "data": {
    "entry_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2025-11-03T14:30:00Z",
    "input_type": "text_note",
    "raw_content": "Met with team to discuss API design.",
    "contextual_tags": ["api-design", "meeting"],
    "extracted_action_items": ["Finalize API endpoints by Friday"],
    "inferred_emotion": "focused",
    "priority_score": 7,
    "key_entities": ["team"],
    "processed": true,
    "metadata": {}
  }
}
```

**Status Codes:**
- `200 OK`: Entry found
- `404 Not Found`: Entry ID doesn't exist

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/api/entry/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "X-API-Key: your-api-key"
```

---

### 3. Query Journal Entries

**Endpoint:** `GET /api/entries`

**Description:** Search and filter journal entries.

**Authentication:** Required

**Query Parameters:**
- `date_from` (string, optional): Start date (ISO 8601 format: `2025-11-01`)
- `date_to` (string, optional): End date (ISO 8601 format: `2025-11-03`)
- `tags` (string, optional): Comma-separated tags (e.g., `meeting,api-design`)
- `input_type` (string, optional): Filter by input type
- `limit` (integer, optional): Maximum results (default: 50, max: 100)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response:**
```json
{
  "status": "success",
  "data": {
    "entries": [
      {
        "entry_id": "...",
        "timestamp": "2025-11-03T14:30:00Z",
        "input_type": "text_note",
        "raw_content": "...",
        "contextual_tags": ["api-design"],
        "priority_score": 7
      }
    ],
    "total_count": 42,
    "limit": 50,
    "offset": 0
  }
}
```

**Status Codes:**
- `200 OK`: Query successful (returns empty array if no results)
- `400 Bad Request`: Invalid query parameters

**Example (cURL):**
```bash
curl -X GET "http://localhost:8000/api/entries?date_from=2025-11-01&tags=meeting&limit=20" \
  -H "X-API-Key: your-api-key"
```

**Example (Python):**
```python
params = {
    "date_from": "2025-11-01",
    "date_to": "2025-11-03",
    "tags": "meeting,api-design",
    "limit": 20
}
response = requests.get(
    "http://localhost:8000/api/entries",
    params=params,
    headers={"X-API-Key": "your-api-key"}
)
print(response.json())
```

---

### 4. Generate Daily Summary

**Endpoint:** `POST /api/summary`

**Description:** Generate a daily summary report for a specified date.

**Authentication:** Required

**Request Body:**
```json
{
  "date": "2025-11-03",
  "include_audio": true
}
```

**Request Schema:**
- `date` (string, required): Date in YYYY-MM-DD format
- `include_audio` (boolean, optional): Generate TTS audio file (default: false)

**Response:**
```json
{
  "status": "success",
  "data": {
    "summary": {
      "date": "2025-11-03",
      "total_entries": 12,
      "key_themes": ["api-design", "meetings", "deadlines", "documentation"],
      "emotion_overview": {
        "stressed": 5,
        "focused": 4,
        "neutral": 3
      },
      "notable_insights": "High stress today related to approaching deadlines."
    },
    "pending_actions": [
      {
        "task_id": "...",
        "task_description": "Finalize API endpoints by Friday",
        "priority": "high",
        "due_date": "2025-11-07",
        "completed": false
      }
    ],
    "suggested_first_task": "Finalize API endpoints by Friday",
    "audio_url": "/api/audio/summary_20251103.mp3"
  },
  "message": "Daily summary generated successfully"
}
```

**Status Codes:**
- `200 OK`: Summary generated
- `400 Bad Request`: Invalid date format
- `404 Not Found`: No entries for specified date

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/summary \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "date": "2025-11-03",
    "include_audio": true
  }'
```

---

### 5. List Action Items

**Endpoint:** `GET /api/actions`

**Description:** Retrieve all action items with optional filtering.

**Authentication:** Required

**Query Parameters:**
- `status` (string, optional): `pending` or `completed` (default: `pending`)
- `priority` (string, optional): `high`, `medium`, or `low`
- `limit` (integer, optional): Maximum results (default: 50)

**Response:**
```json
{
  "status": "success",
  "data": {
    "action_items": [
      {
        "task_id": "...",
        "task_description": "Finalize API endpoints by Friday",
        "priority": "high",
        "source_entry_id": "...",
        "due_date": "2025-11-07T23:59:59Z",
        "completed": false,
        "completed_at": null
      }
    ],
    "total_count": 7
  }
}
```

**Status Codes:**
- `200 OK`: Action items retrieved

**Example (cURL):**
```bash
curl -X GET "http://localhost:8000/api/actions?status=pending&priority=high" \
  -H "X-API-Key: your-api-key"
```

---

### 6. Update Action Item

**Endpoint:** `PATCH /api/actions/{task_id}`

**Description:** Update action item details or mark as complete.

**Authentication:** Required

**Path Parameters:**
- `task_id` (string, required): UUID of the action item

**Request Body:**
```json
{
  "completed": true,
  "priority": "medium",
  "due_date": "2025-11-10"
}
```

**Request Schema:**
- `completed` (boolean, optional): Mark as complete/incomplete
- `priority` (string, optional): Update priority
- `due_date` (string, optional): Update due date
- `task_description` (string, optional): Update description

**Response:**
```json
{
  "status": "success",
  "data": {
    "task_id": "...",
    "task_description": "Finalize API endpoints by Friday",
    "priority": "medium",
    "due_date": "2025-11-10T00:00:00Z",
    "completed": true,
    "completed_at": "2025-11-03T16:45:00Z"
  },
  "message": "Action item updated successfully"
}
```

**Status Codes:**
- `200 OK`: Action item updated
- `404 Not Found`: Task ID doesn't exist

**Example (cURL):**
```bash
curl -X PATCH http://localhost:8000/api/actions/task-uuid \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"completed": true}'
```

---

### 7. Execute Agent Action

**Endpoint:** `POST /api/agent/execute`

**Description:** Execute an action using the LangChain agent (send email, manage calendar, etc.).

**Authentication:** Required

**Request Body:**
```json
{
  "instruction": "Send an email to john@example.com with subject 'API Design Review' and body 'Hi John, Let's schedule time to review the API design.'",
  "confirm_before_execute": true
}
```

**Request Schema:**
- `instruction` (string, required): Natural language instruction
- `confirm_before_execute` (boolean, optional): Require confirmation before execution (default: true for destructive actions)

**Response:**
```json
{
  "status": "success",
  "data": {
    "action": "send_email",
    "parameters": {
      "recipient": "john@example.com",
      "subject": "API Design Review",
      "body": "Hi John, Let's schedule time to review the API design."
    },
    "result": "Email successfully sent to john@example.com",
    "executed_at": "2025-11-03T14:45:00Z"
  },
  "message": "Agent action executed successfully"
}
```

**Status Codes:**
- `200 OK`: Action executed successfully
- `400 Bad Request`: Invalid instruction or missing parameters
- `403 Forbidden`: Action requires confirmation
- `500 Internal Server Error`: Execution failed

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "instruction": "Create calendar event for API review meeting tomorrow at 2pm"
  }'
```

---

### 8. Upload File

**Endpoint:** `POST /api/upload`

**Description:** Upload files for processing (voice memos, PDFs, images).

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Form Parameters:**
- `file` (file, required): File to upload
- `input_type` (string, required): Type of file (`voice_memo`, `photo_ocr`, `pdf_document`)

**Response:**
```json
{
  "status": "success",
  "data": {
    "entry_id": "...",
    "file_path": "/uploads/20251103_143000_audio.wav",
    "processing_status": "completed",
    "extracted_content": "Transcribed text from audio...",
    "contextual_tags": ["meeting", "transcription"]
  },
  "message": "File uploaded and processed successfully"
}
```

**Status Codes:**
- `201 Created`: File uploaded and processed
- `400 Bad Request`: Invalid file type or size
- `413 Payload Too Large`: File exceeds size limit (default: 10MB)

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@meeting_notes.wav" \
  -F "input_type=voice_memo"
```

**Example (Python):**
```python
with open("meeting_notes.wav", "rb") as f:
    files = {"file": f}
    data = {"input_type": "voice_memo"}
    response = requests.post(
        "http://localhost:8000/api/upload",
        files=files,
        data=data,
        headers={"X-API-Key": "your-api-key"}
    )
    print(response.json())
```

---

### 9. Health Check

**Endpoint:** `GET /health`

**Description:** Check API health status.

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "checks": {
    "database": "ok",
    "llm": "ok",
    "storage": "ok"
  }
}
```

**Status Codes:**
- `200 OK`: Service healthy
- `503 Service Unavailable`: Service degraded or unhealthy

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/health
```

---

### 10. Get Audio File

**Endpoint:** `GET /api/audio/{filename}`

**Description:** Retrieve generated TTS audio file.

**Authentication:** Required

**Path Parameters:**
- `filename` (string, required): Audio file name (e.g., `summary_20251103.mp3`)

**Response:** Binary audio file (MP3 format)

**Status Codes:**
- `200 OK`: Audio file returned
- `404 Not Found`: Audio file doesn't exist

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/api/audio/summary_20251103.mp3 \
  -H "X-API-Key: your-api-key" \
  -o summary.mp3
```

---

## Request/Response Schemas

### JournalEntrySchema

```json
{
  "entry_id": "string (UUID)",
  "timestamp": "string (ISO 8601 datetime)",
  "input_type": "string (enum: text_note, voice_memo, photo_ocr, pdf_document, code_snippet, email, calendar_event)",
  "raw_content": "string",
  "source_id": "string",
  "contextual_tags": ["string"],
  "extracted_action_items": ["string"],
  "inferred_emotion": "string (enum: happy, stressed, neutral, excited, frustrated)",
  "priority_score": "integer (1-10)",
  "key_entities": ["string"],
  "processed": "boolean",
  "metadata": {}
}
```

### ActionItemSchema

```json
{
  "task_id": "string (UUID)",
  "task_description": "string",
  "priority": "string (enum: high, medium, low)",
  "source_entry_id": "string (UUID)",
  "due_date": "string (ISO 8601 datetime, nullable)",
  "completed": "boolean",
  "completed_at": "string (ISO 8601 datetime, nullable)"
}
```

### DailySummarySchema

```json
{
  "date": "string (YYYY-MM-DD)",
  "total_entries": "integer",
  "key_themes": ["string"],
  "emotion_overview": {
    "emotion_name": "integer (count)"
  },
  "notable_insights": "string"
}
```

### ErrorSchema

```json
{
  "status": "error",
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_INPUT_TYPE",
    "message": "Input type 'invalid_type' is not supported",
    "details": {
      "valid_types": ["text_note", "voice_memo", "photo_ocr", "pdf_document", "code_snippet", "email", "calendar_event"]
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT_TYPE` | 400 | Unsupported input type |
| `MISSING_CONTENT` | 400 | Required content field missing |
| `INVALID_DATE_FORMAT` | 400 | Date format not ISO 8601 |
| `INVALID_ENTRY_ID` | 400 | Entry ID not valid UUID |
| `ENTRY_NOT_FOUND` | 404 | Journal entry doesn't exist |
| `ACTION_NOT_FOUND` | 404 | Action item doesn't exist |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `PROCESSING_FAILED` | 500 | LLM or storage processing error |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Error Handling Best Practices

1. **Always check `status` field**: `"success"` or `"error"`
2. **Parse error details**: Use `error.details` for actionable information
3. **Implement retry logic**: For `429` and `500` errors with exponential backoff
4. **Log error codes**: For debugging and monitoring

**Example (Python):**
```python
response = requests.post(url, json=payload, headers=headers)
data = response.json()

if data["status"] == "error":
    error_code = data["error"]["code"]
    error_message = data["error"]["message"]
    print(f"Error {error_code}: {error_message}")

    if error_code == "RATE_LIMIT_EXCEEDED":
        # Wait and retry
        time.sleep(60)
        response = requests.post(url, json=payload, headers=headers)
else:
    # Success
    entry = data["data"]
    print(f"Entry created: {entry['entry_id']}")
```

---

## Rate Limiting

### Limits

- **Authenticated Requests**: 100 requests per minute per API key
- **Unauthenticated Requests**: 10 requests per minute per IP
- **File Uploads**: 10 files per hour per API key

### Rate Limit Headers

Response headers include current rate limit status:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699027200
```

- `X-RateLimit-Limit`: Total requests allowed per window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Handling Rate Limits

When rate limit exceeded, response:

```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "details": {
      "retry_after": 45
    }
  }
}
```

**Best Practices:**
1. Monitor `X-RateLimit-Remaining` header
2. Implement exponential backoff on `429` responses
3. Cache responses when possible
4. Batch operations to reduce request count

---

## Usage Examples

### Complete Workflow Example (Python)

```python
import requests
import time

class CJAClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }

    def create_entry(self, input_type, content):
        """Create a new journal entry."""
        url = f"{self.base_url}/api/entry"
        payload = {
            "input_type": input_type,
            "content": content
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def get_entry(self, entry_id):
        """Retrieve a journal entry by ID."""
        url = f"{self.base_url}/api/entry/{entry_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def query_entries(self, date_from=None, date_to=None, tags=None):
        """Query journal entries with filters."""
        url = f"{self.base_url}/api/entries"
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if tags:
            params["tags"] = ",".join(tags)

        response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def generate_summary(self, date, include_audio=False):
        """Generate daily summary."""
        url = f"{self.base_url}/api/summary"
        payload = {
            "date": date,
            "include_audio": include_audio
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def list_actions(self, status="pending", priority=None):
        """List action items."""
        url = f"{self.base_url}/api/actions"
        params = {"status": status}
        if priority:
            params["priority"] = priority

        response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def complete_action(self, task_id):
        """Mark action item as complete."""
        url = f"{self.base_url}/api/actions/{task_id}"
        payload = {"completed": True}
        response = requests.patch(url, json=payload, headers=self.headers)
        return response.json()

# Usage
client = CJAClient("http://localhost:8000", "your-api-key")

# Create entry
result = client.create_entry("text_note", "Finished API documentation today!")
entry_id = result["data"]["entry_id"]
print(f"Created entry: {entry_id}")

# Query entries
entries = client.query_entries(
    date_from="2025-11-01",
    tags=["api-design", "documentation"]
)
print(f"Found {entries['data']['total_count']} entries")

# Generate summary
summary = client.generate_summary("2025-11-03", include_audio=True)
print(f"Summary: {summary['data']['summary']['notable_insights']}")

# List pending actions
actions = client.list_actions(status="pending", priority="high")
for action in actions["data"]["action_items"]:
    print(f"- {action['task_description']}")

# Complete first action
if actions["data"]["action_items"]:
    first_action = actions["data"]["action_items"][0]
    client.complete_action(first_action["task_id"])
    print(f"Completed: {first_action['task_description']}")
```

---

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class CJAClient {
  constructor(baseURL, apiKey) {
    this.client = axios.create({
      baseURL: baseURL,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey
      }
    });
  }

  async createEntry(inputType, content) {
    const response = await this.client.post('/api/entry', {
      input_type: inputType,
      content: content
    });
    return response.data;
  }

  async getEntry(entryId) {
    const response = await this.client.get(`/api/entry/${entryId}`);
    return response.data;
  }

  async queryEntries(filters = {}) {
    const response = await this.client.get('/api/entries', {
      params: filters
    });
    return response.data;
  }

  async generateSummary(date, includeAudio = false) {
    const response = await this.client.post('/api/summary', {
      date: date,
      include_audio: includeAudio
    });
    return response.data;
  }

  async listActions(status = 'pending', priority = null) {
    const params = { status };
    if (priority) params.priority = priority;

    const response = await this.client.get('/api/actions', { params });
    return response.data;
  }

  async completeAction(taskId) {
    const response = await this.client.patch(`/api/actions/${taskId}`, {
      completed: true
    });
    return response.data;
  }
}

// Usage
(async () => {
  const client = new CJAClient('http://localhost:8000', 'your-api-key');

  // Create entry
  const result = await client.createEntry('text_note', 'Working on mobile app integration');
  console.log(`Created entry: ${result.data.entry_id}`);

  // Generate summary
  const summary = await client.generateSummary('2025-11-03');
  console.log(`Key themes: ${summary.data.summary.key_themes.join(', ')}`);

  // List actions
  const actions = await client.listActions('pending', 'high');
  console.log(`Pending high-priority tasks: ${actions.data.total_count}`);
})();
```

---

### cURL Examples Collection

```bash
# Create text entry
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input_type": "text_note", "content": "Meeting with product team"}'

# Upload voice memo
curl -X POST http://localhost:8000/api/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@recording.wav" \
  -F "input_type=voice_memo"

# Query entries by date and tags
curl -X GET "http://localhost:8000/api/entries?date_from=2025-11-01&tags=meeting,api" \
  -H "X-API-Key: your-api-key"

# Generate daily summary
curl -X POST http://localhost:8000/api/summary \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"date": "2025-11-03", "include_audio": true}'

# List pending high-priority actions
curl -X GET "http://localhost:8000/api/actions?status=pending&priority=high" \
  -H "X-API-Key: your-api-key"

# Complete an action
curl -X PATCH http://localhost:8000/api/actions/task-uuid \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"completed": true}'

# Execute agent action
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"instruction": "Send email to john@example.com about project status"}'

# Health check
curl -X GET http://localhost:8000/health
```

---

## WebSocket Support

### Real-Time Updates (Future)

**Endpoint:** `ws://localhost:8000/ws`

**Description:** WebSocket connection for real-time entry updates and notifications.

**Authentication:** API key via query parameter: `ws://localhost:8000/ws?api_key=your-key`

**Events:**

#### Entry Created
```json
{
  "event": "entry_created",
  "data": {
    "entry_id": "...",
    "timestamp": "2025-11-03T14:30:00Z",
    "input_type": "text_note"
  }
}
```

#### Action Item Added
```json
{
  "event": "action_added",
  "data": {
    "task_id": "...",
    "task_description": "...",
    "priority": "high"
  }
}
```

#### Processing Complete
```json
{
  "event": "processing_complete",
  "data": {
    "entry_id": "...",
    "contextual_tags": ["..."],
    "priority_score": 7
  }
}
```

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?api_key=your-key');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`Event: ${message.event}`, message.data);

  if (message.event === 'entry_created') {
    // Handle new entry
    updateUI(message.data);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Webhook Support (Future)

### Webhook Configuration

**Endpoint:** `POST /api/webhooks`

**Description:** Register webhook URLs for event notifications.

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/cja",
  "events": ["entry_created", "action_added", "summary_generated"],
  "secret": "your-webhook-secret"
}
```

**Webhook Payload:**
```json
{
  "event": "entry_created",
  "timestamp": "2025-11-03T14:30:00Z",
  "data": {
    "entry_id": "...",
    "input_type": "text_note"
  },
  "signature": "sha256=..."
}
```

**Signature Verification:**
```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature."""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

---

## SDKs and Client Libraries

### Official SDKs

- **Python SDK**: `pip install cja-sdk` (Coming soon)
- **JavaScript SDK**: `npm install @cja/sdk` (Coming soon)
- **Go SDK**: `go get github.com/yourorg/cja-go` (Coming soon)

### Community SDKs

- **Ruby**: https://github.com/community/cja-ruby
- **PHP**: https://github.com/community/cja-php

### OpenAPI Specification

Download OpenAPI 3.0 specification:
- **URL**: `http://localhost:8000/openapi.json`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Pagination

For endpoints returning lists, use pagination parameters:

```
GET /api/entries?limit=50&offset=100
```

**Response includes pagination metadata:**
```json
{
  "data": {
    "entries": [...],
    "total_count": 500,
    "limit": 50,
    "offset": 100,
    "has_more": true
  }
}
```

**Iterate through pages:**
```python
offset = 0
limit = 50
all_entries = []

while True:
    response = client.query_entries(limit=limit, offset=offset)
    entries = response["data"]["entries"]
    all_entries.extend(entries)

    if not response["data"]["has_more"]:
        break

    offset += limit
```

---

## Filtering and Sorting

### Supported Filters

- **Date Range**: `date_from`, `date_to`
- **Tags**: `tags` (comma-separated)
- **Input Type**: `input_type`
- **Priority**: `priority` (for action items)
- **Status**: `status` (for action items)

### Sorting

```
GET /api/entries?sort_by=timestamp&order=desc
```

**Supported Sort Fields:**
- `timestamp` (default)
- `priority_score`
- `input_type`

**Sort Order:**
- `asc` (ascending)
- `desc` (descending, default)

---

## Batch Operations (Future)

### Batch Create Entries

**Endpoint:** `POST /api/entries/batch`

**Request:**
```json
{
  "entries": [
    {"input_type": "text_note", "content": "Entry 1"},
    {"input_type": "text_note", "content": "Entry 2"}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "created": 2,
    "failed": 0,
    "entries": [...]
  }
}
```

---

## Versioning

API versioning via URL path (future):

- **v1**: `http://localhost:8000/api/v1/entry`
- **v2**: `http://localhost:8000/api/v2/entry`

Current version: **v1** (implicit, no version in URL)

Breaking changes will introduce new version.

---

## Support and Feedback

- **Documentation Issues**: https://github.com/yourrepo/issues
- **API Status**: https://status.yourproject.com
- **Email**: api-support@yourproject.com
- **Slack Community**: https://slack.yourproject.com

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-03
**Maintainer**: CJA API Team
**Contact**: api-team@yourproject.com

---
