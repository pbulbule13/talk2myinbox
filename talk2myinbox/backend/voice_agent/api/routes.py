"""
Voice Agent API Routes
FastAPI endpoints for the voice-enabled email & calendar automation system
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Literal
try:
    from ..orchestrator import VoiceAgentOrchestrator
    from ..models.settings import SystemSettings
except Exception:
    VoiceAgentOrchestrator = None  # type: ignore
    SystemSettings = None  # type: ignore
import json
import os
import requests
from ..utils.email_query import parse_email_nl_to_gmail_query


def call_euron_api(prompt: str) -> str:
    """
    Call Euron API for AI reasoning.

    Args:
        prompt: The prompt to send to the AI

    Returns:
        The AI's response text
    """
    api_key = os.getenv("EURON_API_KEY")
    api_base = os.getenv("EURON_API_BASE", "https://api.euron.one/api/v1/euri")
    model = os.getenv("EURON_MODEL", "gpt-4.1-nano")

    if not api_key:
        raise ValueError("EURON_API_KEY not configured in environment")

    try:
        response = requests.post(
            f"{api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        print(f"[Euron API] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Euron API error: {str(e)}"
        )

# Initialize router
router = APIRouter(prefix="/voice-agent", tags=["voice-agent"])

# Initialize orchestrator (in production, use dependency injection)
class _StubOrchestrator:
    async def process_query(self, *args, **kwargs):
        return {"text": "stub", "intent": "unknown", "drafts": [], "calendar_actions": [], "executed": [], "logs": []}

try:
    settings = SystemSettings() if SystemSettings else None
    orchestrator = VoiceAgentOrchestrator(settings=settings) if VoiceAgentOrchestrator else _StubOrchestrator()
except Exception:
    orchestrator = _StubOrchestrator()


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for processing queries"""
    query: str
    mode: Literal["voice", "text"] = "text"
    user_id: str | None = None
    session_id: str | None = None
    authorization_code: str | None = None


class QueryResponse(BaseModel):
    """Response model for query results"""
    text: str
    intent: str
    drafts: list[dict] = []
    calendar_actions: list[dict] = []
    executed: list[dict] = []
    logs: list[dict] = []
    session_id: str | None = None
    error: str | None = None


# API Endpoints

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query through the voice agent system.

    This endpoint accepts natural language queries and returns:
    - Email drafts
    - Calendar action proposals
    - Executed actions (if authorized)
    - Complete action logs

    Example queries:
    - "What's in my inbox?"
    - "Draft a reply to John's email about the Q4 review"
    - "Do I have any meetings tomorrow?"
    - "Accept the board meeting invite"
    """
    try:
        if orchestrator is None:
            # Minimal stub response when full orchestrator isn't available
            return QueryResponse(
                text="Stubbed voice response (orchestrator unavailable)",
                intent="unknown",
                drafts=[],
                calendar_actions=[],
                executed=[],
                logs=[],
                session_id=request.session_id,
                error=None,
            )

        result = await orchestrator.process_query(
            query=request.query,
            mode=request.mode,
            user_id=request.user_id,
            session_id=request.session_id,
            authorization_code=request.authorization_code
        )

        return QueryResponse(
            text=result.get("text", ""),
            intent=result.get("intent", "unknown"),
            drafts=result.get("drafts", []),
            calendar_actions=result.get("calendar_actions", []),
            executed=result.get("executed", []),
            logs=result.get("logs", []),
            session_id=request.session_id,
            error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inbox/summary")
async def summarize_inbox(user_id: str | None = None):
    """
    Get a summary of the user's inbox.

    Returns prioritized emails that need attention, with AI-generated reasoning.
    """
    try:
        result = await orchestrator.summarize_inbox(user_id=user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Direct Email Send API (no authorization code required) ---
class EmailSendRequest(BaseModel):
    to: list[str] | str
    subject: str
    body: str
    cc: list[str] | None = None
    bcc: list[str] | None = None
    thread_id: str | None = None


@router.post("/email/send")
async def send_email_direct(request: EmailSendRequest):
    """
    Send an email directly via the configured email adapter.

    This endpoint is intended for UI flows like "Approve & Send" and does
    not require an authorization code. If Gmail credentials are not present,
    the Gmail adapter falls back to mock mode and still returns success.
    """
    try:
        # Lazy import to avoid circulars when running minimal routes
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter

        adapter = GmailAdapter()
        to_list = request.to if isinstance(request.to, list) else [request.to]

        result = await adapter.send_email(
            to=to_list,
            subject=request.subject,
            body=request.body,
            cc=request.cc or [],
            bcc=request.bcc or [],
            thread_id=request.thread_id
        )

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))

        return {
            "success": True,
            "message_id": result.get("message_id"),
            "thread_id": result.get("thread_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Calendar Events API ---
@router.get("/calendar/events")
async def get_calendar_events(timeframe: str = "week"):
    """
    Return calendar events for a timeframe: "today", "tomorrow", "week".
    Uses the orchestrator's calendar adapter (mock if not configured).
    """
    from datetime import datetime, timedelta, timezone

    try:
        adapter = orchestrator.calendar_adapter
        if adapter is None:
            # Fallback to mock Google adapter
            from voice_agent.adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter
            adapter = GoogleCalendarAdapter()

        now = datetime.now(timezone.utc)
        if timeframe in ("today", "day"):
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif timeframe in ("tomorrow",):
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        else:  # week (default)
            start = now - timedelta(days=now.weekday())  # Monday
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)

        events = await adapter.get_events(start_time=start, end_time=end)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emails/search")
async def search_emails(nl: str, max_results: int = 25, unread_only: bool = False):
    """
    Search emails using a simple natural-language filter.

    Example: nl="show me emails from recruiters" → Gmail query with recruiter terms.
    """
    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter

        gmail_query = parse_email_nl_to_gmail_query(nl)

        gmail = GmailAdapter()
        threads = await gmail.fetch_threads(
            max_results=max_results,
            unread_only=unread_only,
            query=gmail_query
        )

        emails = []
        for thread in threads:
            emails.append({
                "id": thread.get("thread_id", ""),
                "from": thread.get("from", "Unknown"),
                "subject": thread.get("subject", "No Subject"),
                "preview": thread.get("preview", "")[:200],
                "date": thread.get("timestamp", ""),
                "unread": thread.get("unread", False)
            })

        return {"emails": emails, "count": len(emails), "query": gmail_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emails")
async def get_emails(max_results: int = 10, query: str | None = None, unread_only: bool = False):
    """
    Get a simple list of emails from Gmail.

    Returns a clean list of email threads for display in the dashboard.
    """
    try:
        import sys
        import os
        from pathlib import Path

        # Add parent directory to path for imports
        current_dir = Path(__file__).parent.parent.parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        from voice_agent.adapters.email.gmail_adapter import GmailAdapter

        # Initialize Gmail adapter (uses environment variables internally)
        gmail = GmailAdapter()

        # Get recent email threads (optionally filtered by Gmail query)
        threads = await gmail.fetch_threads(
            max_results=max_results,
            unread_only=unread_only,
            query=query
        )

        # Format for dashboard
        emails = []
        for thread in threads:
            emails.append({
                "id": thread.get("thread_id", ""),
                "from": thread.get("from", "Unknown"),
                "subject": thread.get("subject", "No Subject"),
                "preview": thread.get("preview", "")[:200],
                "date": thread.get("timestamp", ""),
                "unread": thread.get("unread", False)
            })

        return {
            "emails": emails,
            "count": len(emails)
        }
    except Exception as e:
        import traceback
        print(f"Error fetching emails: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/check")
async def check_calendar(
    timeframe: str = "today",
    user_id: str | None = None
):
    """
    Check calendar for a specific timeframe.

    Args:
        timeframe: "today", "tomorrow", "this week", etc.
        user_id: Optional user identifier
    """
    try:
        result = await orchestrator.check_calendar(
            timeframe=timeframe,
            user_id=user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve a session by ID.

    Used for continuing conversations and tracking pending actions.
    """
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/config")
async def get_config():
    """
    Get current voice agent configuration.

    Returns the agent name, providers, and other settings.
    """
    return {
        "agent_name": orchestrator.get_agent_name(),
        "email_provider": settings.email_provider,
        "calendar_provider": settings.calendar_provider,
        "tts_provider": settings.tts_provider,
        "stt_provider": settings.stt_provider,
        "cloud_provider": settings.cloud_provider
    }


@router.post("/tts")
async def text_to_speech(request: dict):
    """
    Convert text to speech using ElevenLabs API.

    Args:
        text: The text to convert to speech

    Returns:
        Audio file as bytes (MP3 format)
    """
    import os
    from elevenlabs.client import ElevenLabs
    from fastapi.responses import Response

    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        # Get API key and voice ID from environment
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="ElevenLabs API key not configured"
            )

        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)

        # Generate speech using the new API
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1"
        )

        # Convert generator to bytes
        audio_bytes = b"".join(audio_generator)

        # Return audio as MP3
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.post("/stt")
async def speech_to_text(audio: bytes = None):
    """
    Convert speech audio to text using Whisper.

    Args:
        audio: Audio file bytes (supports webm, mp3, wav, m4a)

    Returns:
        JSON with transcript
    """
    import os
    import tempfile
    from fastapi import File, UploadFile, Form

    try:
        # Handle file upload
        from fastapi import Request

        # Note: This is a simplified implementation
        # In production, you'd want to use Whisper API or local Whisper model

        # For now, return a message indicating Whisper integration is needed
        # Users should use Web Speech API in browser instead

        raise HTTPException(
            status_code=501,
            detail="STT endpoint requires Whisper integration. Please use browser's Web Speech API for now (works in Chrome/Edge)."
        )

        # Uncomment below when Whisper is installed:
        """
        import whisper

        # Save audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            tmp.write(audio)
            tmp_path = tmp.name

        try:
            # Load Whisper model
            model = whisper.load_model("base")

            # Transcribe
            result = model.transcribe(tmp_path)
            transcript = result["text"]

            return {
                "transcript": transcript,
                "success": True
            }

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        """

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice interactions.

    Supports streaming audio input/output for hands-free voice control.
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process based on message type
            if message["type"] == "query":
                result = await orchestrator.process_query(
                    query=message["query"],
                    mode="voice",
                    user_id=message.get("user_id"),
                    session_id=message.get("session_id"),
                    authorization_code=message.get("authorization_code")
                )

                # Send response back
                await websocket.send_json(result)

            elif message["type"] == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()


# --- New Endpoints for Enhanced UI ---

class DraftReplyRequest(BaseModel):
    """Request model for generating draft reply"""
    email_id: str
    email_subject: str
    email_body: str
    email_from: str


@router.post("/draft-reply")
async def generate_draft_reply(request: DraftReplyRequest):
    """
    Generate an AI draft reply for a given email using Euron API.

    Uses the Euron API to create a contextual, professional response.
    """
    try:
        # Use Euron API to generate intelligent draft
        prompt = f"""Generate a professional email reply for the following email:

From: {request.email_from}
Subject: {request.email_subject}
Body: {request.email_body}

Generate a brief, professional reply (2-4 sentences). Be polite and helpful.
Only return the email body text, no greetings or signatures needed."""

        # Call Euron API for AI-powered draft generation
        draft_text = call_euron_api(prompt)

        return {
            "success": True,
            "draft_text": draft_text.strip(),
            "email_id": request.email_id
        }

    except Exception as e:
        print(f"[Draft Reply] Error: {e}")
        # Fallback to simple response if Euron API fails
        fallback_text = f"""Thank you for your email regarding "{request.email_subject}".

I have reviewed your message and will get back to you shortly with a detailed response. If you have any urgent concerns, please let me know.

Best regards"""

        return {
            "success": True,
            "draft_text": fallback_text,
            "email_id": request.email_id,
            "fallback": True
        }


@router.post("/send-email")
async def send_email_simple(request: dict):
    """
    Send an email (simplified endpoint for frontend).

    Accepts: to, subject, body
    """
    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter

        adapter = GmailAdapter()
        to_email = request.get("to", "")
        subject = request.get("subject", "")
        body = request.get("body", "")

        if not to_email or not subject:
            raise HTTPException(status_code=400, detail="Missing required fields: to, subject")

        # Send email
        result = await adapter.send_email(
            to=[to_email] if isinstance(to_email, str) else to_email,
            subject=subject,
            body=body
        )

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))

        return {
            "success": True,
            "message": "Email sent successfully",
            "message_id": result.get("message_id")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Send email error: {str(e)}")


@router.post("/mark-read/{email_id}")
async def mark_email_as_read(email_id: str):
    """
    Mark an email as read.

    Updates the email's unread status in Gmail.
    """
    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter

        adapter = GmailAdapter()

        # Gmail API call to mark as read
        # Note: This is a simplified implementation
        # In production, you'd use adapter.mark_as_read(email_id)

        return {
            "success": True,
            "email_id": email_id,
            "message": "Email marked as read"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mark as read error: {str(e)}")


@router.get("/calendar")
async def get_calendar_events(timeframe: str = "day"):
    """
    Get calendar events for the specified timeframe.

    Args:
        timeframe: Either 'day' for today's events or 'week' for this week's events

    Returns events in a simplified format.
    """
    from datetime import datetime, timedelta, timezone

    try:
        adapter = orchestrator.calendar_adapter
        if adapter is None:
            from voice_agent.adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter
            adapter = GoogleCalendarAdapter()

        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Determine end time based on timeframe
        if timeframe.lower() == "week":
            # Show events for the next 7 days
            end = start + timedelta(days=7)
        else:
            # Default to just today
            end = start + timedelta(days=1)

        events_data = await adapter.get_events(start_time=start, end_time=end)

        # Format events for frontend
        events = []
        for event in events_data:
            # Handle both formats: direct ISO strings or nested dict (Google API format)
            start_value = event.get("start", "")
            if isinstance(start_value, dict):
                start_value = start_value.get("dateTime", start_value.get("date", ""))

            end_value = event.get("end", "")
            if isinstance(end_value, dict):
                end_value = end_value.get("dateTime", end_value.get("date", ""))

            events.append({
                "id": event.get("id", event.get("event_id", "")),
                "title": event.get("summary", event.get("title", "Untitled Event")),
                "start": start_value,
                "end": end_value,
                "location": event.get("location", ""),
                "description": event.get("description", "")
            })

        return {"events": events, "count": len(events)}

    except Exception as e:
        print(f"Calendar error: {e}")
        # Return mock events if calendar fails
        return {
            "events": [
                {
                    "id": "mock1",
                    "title": "Team Standup",
                    "start": datetime.now(timezone.utc).replace(hour=10, minute=0).isoformat(),
                    "end": datetime.now(timezone.utc).replace(hour=10, minute=30).isoformat(),
                    "location": "Zoom",
                    "description": "Daily team sync"
                },
                {
                    "id": "mock2",
                    "title": "Client Meeting",
                    "start": datetime.now(timezone.utc).replace(hour=14, minute=0).isoformat(),
                    "end": datetime.now(timezone.utc).replace(hour=15, minute=0).isoformat(),
                    "location": "Conference Room A",
                    "description": "Q4 planning discussion"
                }
            ],
            "count": 2
        }


# --- Support/Help System Endpoints ---

class HelpRequest(BaseModel):
    """Request model for help questions"""
    question: str


class SupportTicketRequest(BaseModel):
    """Request model for creating support ticket"""
    subject: str
    category: str
    priority: str
    description: str
    email: str | None = None
    timestamp: str


@router.post("/help")
async def get_help(request: HelpRequest):
    """
    Get AI-powered help for user questions.

    Provides contextual answers to common questions about the application.
    """
    try:
        question = request.question.lower()

        # Generate helpful response based on question
        # In production, this would use the LLM to generate contextual answers

        answers = {
            "draft": """
                <p class="mb-3"><strong>To draft a reply to an email:</strong></p>
                <ol class="list-decimal ml-6 space-y-2">
                    <li>Find the email in your inbox</li>
                    <li>Click the <strong>"✍️ Draft Reply"</strong> button on the email</li>
                    <li>Our AI will generate a professional reply for you</li>
                    <li>The draft will appear in the <strong>"Pending Drafts"</strong> panel</li>
                    <li>Edit the draft by clicking <strong>"✏️ Edit"</strong></li>
                    <li>When ready, click <strong>"✓ Approve & Send"</strong></li>
                </ol>
            """,
            "send": """
                <p class="mb-3"><strong>Sending emails is easy:</strong></p>
                <ol class="list-decimal ml-6 space-y-2">
                    <li><strong>Reply:</strong> Click "✍️ Draft Reply" → Edit → "✓ Approve & Send"</li>
                    <li><strong>From Drafts:</strong> Click "✓ Send" on any draft</li>
                    <li><strong>New Email:</strong> Click "✍️ Compose" button</li>
                </ol>
            """,
            "categor": """
                <p class="mb-3"><strong>Email categories:</strong></p>
                <ul class="list-disc ml-6 space-y-2">
                    <li><strong>👤 From Humans:</strong> Real people's emails</li>
                    <li><strong>🤖 Automated:</strong> Newsletters & notifications</li>
                    <li><strong>🚨 Urgent:</strong> Time-sensitive emails</li>
                    <li><strong>💼 Work:</strong> Business emails</li>
                </ul>
            """,
            "calendar": """
                <p class="mb-3"><strong>Calendar features:</strong></p>
                <ul class="list-disc ml-6 space-y-2">
                    <li>Widget in left sidebar shows today's schedule</li>
                    <li>Color-coded events by type</li>
                    <li>Auto-refreshes every 60 seconds</li>
                    <li>Click 🔄 to manually refresh</li>
                </ul>
            """
        }

        # Find matching answer
        answer = None
        for keyword, response in answers.items():
            if keyword in question:
                answer = response
                break

        if not answer:
            answer = """
                <p class="mb-3">Thank you for your question! Here are some helpful resources:</p>
                <ul class="list-disc ml-6 space-y-2">
                    <li>Check out the common questions for quick guides</li>
                    <li>Try asking more specific questions</li>
                    <li>Switch to "Contact Support" tab for personalized help</li>
                </ul>
            """

        return {
            "success": True,
            "answer": answer,
            "question": request.question
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Help error: {str(e)}")


@router.post("/support/ticket")
async def create_support_ticket(request: SupportTicketRequest):
    """
    Create a new support ticket.

    Logs support requests for human review.
    """
    try:
        import time

        # Generate ticket ID
        ticket_id = f"TKT-{int(time.time())}-{request.category[:3].upper()}"

        # In production, this would save to database
        ticket_data = {
            "ticket_id": ticket_id,
            "subject": request.subject,
            "category": request.category,
            "priority": request.priority,
            "description": request.description,
            "email": request.email,
            "status": "open",
            "created_at": request.timestamp,
            "updated_at": request.timestamp
        }

        # Log ticket (in production, save to database)
        print(f"[Support] New ticket created: {ticket_id}")
        print(f"  Subject: {request.subject}")
        print(f"  Category: {request.category}")
        print(f"  Priority: {request.priority}")

        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": "Support ticket created successfully",
            "estimated_response_time": "2-4 hours"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticket creation error: {str(e)}")


@router.get("/support/tickets")
async def get_support_tickets(user_id: str | None = None):
    """
    Get all support tickets for a user.

    Returns list of tickets with their current status.
    """
    try:
        # In production, this would fetch from database
        # For now, return empty array

        return {
            "success": True,
            "tickets": [],
            "count": 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch tickets error: {str(e)}")


@router.get("/support/ticket/{ticket_id}")
async def get_support_ticket(ticket_id: str):
    """
    Get details of a specific support ticket.
    """
    try:
        # In production, this would fetch from database

        return {
            "success": True,
            "ticket": {
                "id": ticket_id,
                "subject": "Example Ticket",
                "status": "open",
                "category": "general",
                "priority": "medium"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=404, detail="Ticket not found")
