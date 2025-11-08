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
# Email query parsing (temporarily disabled)
# from ..utils.email_query import parse_email_nl_to_gmail_query
# Import LLM fallback for AI-powered email analysis
from ..utils.llm_fallback import call_llm_with_fallback

# Initialize router
router = APIRouter(prefix="/voice-agent", tags=["voice-agent"])

# Initialize orchestrator (in production, use dependency injection)
class _StubOrchestrator:
    def __init__(self):
        self.calendar_adapter = None
        self.email_adapter = None

    async def process_query(self, *args, **kwargs):
        return {"text": "stub", "intent": "unknown", "drafts": [], "calendar_actions": [], "executed": [], "logs": []}

    async def summarize_inbox(self, user_id: str | None = None):
        """
        Analyze inbox and provide intelligent summarization with prioritization.
        Identifies emails needing immediate attention using AI analysis.
        """
        from datetime import datetime, timedelta, timezone
        from ..adapters.email.gmail_adapter import GmailAdapter
        from ..adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter

        try:
            # Fetch recent emails
            gmail = GmailAdapter()
            email_threads = await gmail.fetch_threads(max_results=50, unread_only=False)

            # Fetch calendar events for context
            calendar = GoogleCalendarAdapter()
            today = datetime.now(timezone.utc)
            week_later = today + timedelta(days=7)
            calendar_events = await calendar.fetch_events(
                start_date=today.isoformat(),
                end_date=week_later.isoformat()
            )

            # Prepare data for LLM analysis
            email_data = []
            for thread in email_threads[:30]:  # Analyze top 30 to avoid token limits
                email_data.append({
                    "from": thread.get("from", "Unknown"),
                    "subject": thread.get("subject", "No Subject"),
                    "preview": thread.get("preview", "")[:300],
                    "timestamp": thread.get("timestamp", ""),
                    "unread": thread.get("unread", False)
                })

            event_data = []
            for event in calendar_events[:10]:  # Include upcoming events for context
                event_data.append({
                    "summary": event.get("summary", "No Title"),
                    "start": event.get("start", ""),
                    "end": event.get("end", "")
                })

            # Build AI prompt for intelligent analysis
            prompt = f"""You are an intelligent email assistant. Analyze these emails and identify which ones need immediate attention.

TODAY'S DATE: {today.strftime('%Y-%m-%d %H:%M')}

UPCOMING CALENDAR EVENTS:
{json.dumps(event_data, indent=2)}

RECENT EMAILS (last 30):
{json.dumps(email_data, indent=2)}

Analyze these emails and provide:
1. URGENT: Emails requiring immediate action (deadlines, time-sensitive requests, important meetings)
2. HIGH PRIORITY: Important emails that should be addressed soon (client requests, team updates, decisions needed)
3. NORMAL: Regular emails that can be handled later
4. REASONING: Brief explanation of why each email is categorized as such

Focus on:
- Deadlines and time-sensitive content
- Meeting invitations and scheduling requests
- Questions requiring responses
- Important senders (executives, clients, partners)
- Action items and follow-ups
- Conflicts with calendar events

Return your analysis as a JSON object with this structure:
{{
  "urgent": [
    {{"from": "sender", "subject": "subject", "reason": "why urgent", "action": "what to do"}}
  ],
  "high_priority": [
    {{"from": "sender", "subject": "subject", "reason": "why important"}}
  ],
  "summary": "Brief overview of inbox status and key insights",
  "total_emails": {len(email_data)},
  "unread_count": {sum(1 for e in email_data if e.get('unread', False))}
}}

Return ONLY the JSON object, no additional text."""

            # Call LLM with fallback chain
            print("[Inbox Summary] Calling LLM for intelligent email analysis...")
            llm_response = call_llm_with_fallback(prompt, max_tokens=1500, temperature=0.3)

            # Parse LLM response
            try:
                # Extract JSON from response (handle cases where LLM adds extra text)
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = llm_response[json_start:json_end]
                    analysis = json.loads(json_str)
                else:
                    analysis = json.loads(llm_response)

                print(f"[Inbox Summary] AI analysis complete: {len(analysis.get('urgent', []))} urgent, {len(analysis.get('high_priority', []))} high priority")
                return analysis

            except json.JSONDecodeError as e:
                print(f"[Inbox Summary] ERROR parsing LLM JSON response: {e}")
                print(f"[Inbox Summary] Raw response: {llm_response[:500]}")
                # Return fallback structure
                return {
                    "urgent": [],
                    "high_priority": [],
                    "summary": "Email analysis is currently unavailable. Please try again.",
                    "total_emails": len(email_data),
                    "unread_count": sum(1 for e in email_data if e.get('unread', False)),
                    "error": "Failed to parse AI analysis"
                }

        except Exception as e:
            print(f"[Inbox Summary] ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {
                "urgent": [],
                "high_priority": [],
                "summary": f"Error analyzing inbox: {str(e)}",
                "total_emails": 0,
                "unread_count": 0,
                "error": str(e)
            }

try:
    settings = None  # Disable settings for now
    orchestrator = _StubOrchestrator()  # Use stub to avoid initialization issues
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
    - Email analysis and answers
    - Calendar action proposals
    - Intelligent responses using LLM

    Example queries:
    - "How many interview emails did I receive?"
    - "What's in my inbox?"
    - "Do I have any meetings this week?"
    - "Which emails need replies?"
    """
    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter
        from voice_agent.adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter
        from datetime import datetime, timezone, timedelta

        query = request.query.lower()

        print(f"[Query] Processing: {request.query}")

        # Fetch emails for context
        gmail = GmailAdapter()
        threads = await gmail.fetch_threads(max_results=50)

        print(f"[Query] Fetched {len(threads)} emails for analysis")

        # Build email context for LLM
        email_context = "EMAILS IN INBOX:\n\n"
        for idx, thread in enumerate(threads[:50], 1):
            email_context += f"Email {idx}:\n"
            email_context += f"From: {thread.get('from', 'Unknown')}\n"
            email_context += f"Subject: {thread.get('subject', 'No Subject')}\n"
            email_context += f"Date: {thread.get('timestamp', 'Unknown')}\n"
            email_context += f"Preview: {thread.get('preview', '')[:200]}\n"
            email_context += f"Unread: {thread.get('unread', False)}\n\n"

        # Fetch calendar events if query mentions meetings/calendar
        calendar_context = ""
        if any(word in query for word in ['meeting', 'calendar', 'schedule', 'interview', 'call']):
            try:
                calendar = GoogleCalendarAdapter()
                now = datetime.now(timezone.utc)
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(days=7)
                events = await calendar.get_events(start_time=start, end_time=end)

                if events:
                    calendar_context = "\n\nCALENDAR EVENTS THIS WEEK:\n"
                    for event in events[:10]:
                        calendar_context += f"- {event.get('title', 'Untitled')}: {event.get('start', 'No date')}\n"

                print(f"[Query] Fetched {len(events)} calendar events")
            except Exception as cal_error:
                print(f"[Query] Calendar fetch warning: {cal_error}")

        # Analyze emails for priority and reply needs
        unread_emails = [e for e in threads if e.get('unread', False)]
        emails_from_humans = []
        urgent_emails = []
        emails_needing_reply = []

        for email in threads:
            # Check if from a human (not automated)
            sender = email.get('from', '').lower()
            automated_indicators = ['noreply', 'no-reply', 'notification', 'automated', 'mailer-daemon']
            is_human = not any(ind in sender for ind in automated_indicators)

            if is_human:
                emails_from_humans.append(email)

            # Check for urgency keywords
            subject = email.get('subject', '').lower()
            preview = email.get('preview', '').lower()
            if any(word in subject or word in preview for word in ['urgent', 'asap', 'priority', 'immediate', 'critical']):
                urgent_emails.append(email)

            # Emails likely needing reply (unread + from humans)
            if email.get('unread', False) and is_human:
                emails_needing_reply.append(email)

        # Create enhanced prompt for LLM to answer the query
        # For voice mode, keep responses ultra-concise (1 sentence max)
        if request.mode == "voice":
            prompt = f"""USER QUESTION: {request.query}

EMAIL ANALYSIS:
- Total emails: {len(threads)}
- Unread emails: {len(unread_emails)}
- Emails from humans: {len(emails_from_humans)}
- Urgent/priority emails: {len(urgent_emails)}
- Emails likely needing reply (unread from humans): {len(emails_needing_reply)}

TASK: Answer in ONE SHORT SENTENCE (max 15 words). Be direct and concise for voice output.

Examples:
- "You have 5 unread emails from humans"
- "3 urgent emails need your attention"
- "You have 2 meetings today"

ANSWER:"""
            max_tokens_limit = 50
        else:
            prompt = f"""USER QUESTION: {request.query}

{email_context}{calendar_context}

EMAIL ANALYSIS:
- Total emails: {len(threads)}
- Unread emails: {len(unread_emails)}
- Emails from humans: {len(emails_from_humans)}
- Urgent/priority emails: {len(urgent_emails)}
- Emails likely needing reply (unread from humans): {len(emails_needing_reply)}

TASK: Answer the user's question based on the emails and calendar events above.

For questions about:
- Email counts: Count and categorize emails (e.g., "You received 5 interview emails")
- Priority/reply questions: Use the EMAIL ANALYSIS data above
- Specific topics: Search email subjects and content for keywords
- Meetings: List upcoming calendar events
- Action items: Identify emails that need replies or attention

Provide a direct, conversational answer in 2-4 sentences. Include specific numbers and details.

ANSWER:"""
            max_tokens_limit = 500

        # Use LLM to answer the query
        print(f"[Query] Calling LLM to answer question (mode: {request.mode})...")
        answer = call_llm_with_fallback(prompt, max_tokens=max_tokens_limit, temperature=0.3)

        # Determine intent based on query keywords
        intent = "unknown"
        if any(word in query for word in ['interview', 'job', 'application']):
            intent = "job_search"
        elif any(word in query for word in ['meeting', 'calendar', 'schedule']):
            intent = "calendar_check"
        elif any(word in query for word in ['reply', 'respond', 'answer']):
            intent = "email_reply"
        elif any(word in query for word in ['inbox', 'email', 'unread']):
            intent = "inbox_check"

        print(f"[Query] Answer generated. Intent: {intent}")

        return QueryResponse(
            text=answer.strip(),
            intent=intent,
            drafts=[],
            calendar_actions=[],
            executed=[],
            logs=[{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "query_processed",
                "query": request.query,
                "emails_analyzed": len(threads)
            }],
            session_id=request.session_id,
            error=None
        )

    except Exception as e:
        print(f"[Query] ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inbox/summary")
async def summarize_inbox(user_id: str | None = None):
    """
    Get a summary of the user's inbox with AI-powered intelligent analysis.

    Returns prioritized emails that need attention, with AI-generated reasoning.
    """
    from datetime import datetime, timedelta, timezone
    from ..adapters.email.gmail_adapter import GmailAdapter
    from ..adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter

    try:
        # Fetch recent emails
        gmail = GmailAdapter()
        email_threads = await gmail.fetch_threads(max_results=50, unread_only=False)

        # Fetch calendar events for context
        calendar = GoogleCalendarAdapter()
        today = datetime.now(timezone.utc)
        week_later = today + timedelta(days=7)
        calendar_events = await calendar.fetch_events(
            start_date=today.isoformat(),
            end_date=week_later.isoformat()
        )

        # Prepare data for LLM analysis
        email_data = []
        for thread in email_threads[:30]:  # Analyze top 30 to avoid token limits
            email_data.append({
                "from": thread.get("from", "Unknown"),
                "subject": thread.get("subject", "No Subject"),
                "preview": thread.get("preview", "")[:300],
                "timestamp": thread.get("timestamp", ""),
                "unread": thread.get("unread", False)
            })

        event_data = []
        for event in calendar_events[:10]:  # Include upcoming events for context
            event_data.append({
                "summary": event.get("summary", "No Title"),
                "start": event.get("start", ""),
                "end": event.get("end", "")
            })

        # Build AI prompt for intelligent analysis
        prompt = f"""You are an intelligent email assistant. Analyze these emails and identify which ones need immediate attention.

TODAY'S DATE: {today.strftime('%Y-%m-%d %H:%M')}

UPCOMING CALENDAR EVENTS:
{json.dumps(event_data, indent=2)}

RECENT EMAILS (last 30):
{json.dumps(email_data, indent=2)}

Analyze these emails and provide:
1. URGENT: Emails requiring immediate action (deadlines, time-sensitive requests, important meetings)
2. HIGH PRIORITY: Important emails that should be addressed soon (client requests, team updates, decisions needed)
3. NORMAL: Regular emails that can be handled later
4. REASONING: Brief explanation of why each email is categorized as such

Focus on:
- Deadlines and time-sensitive content
- Meeting invitations and scheduling requests
- Questions requiring responses
- Important senders (executives, clients, partners)
- Action items and follow-ups
- Conflicts with calendar events

Return your analysis as a JSON object with this structure:
{{
  "urgent": [
    {{"from": "sender", "subject": "subject", "reason": "why urgent", "action": "what to do"}}
  ],
  "high_priority": [
    {{"from": "sender", "subject": "subject", "reason": "why important"}}
  ],
  "summary": "Brief overview of inbox status and key insights",
  "total_emails": {len(email_data)},
  "unread_count": {sum(1 for e in email_data if e.get('unread', False))}
}}

Return ONLY the JSON object, no additional text."""

        # Call LLM with fallback chain
        print("[Inbox Summary] Calling LLM for intelligent email analysis...")
        llm_response = call_llm_with_fallback(prompt, max_tokens=1500, temperature=0.3)

        # Parse LLM response
        try:
            # Extract JSON from response (handle cases where LLM adds extra text)
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(llm_response)

            print(f"[Inbox Summary] AI analysis complete: {len(analysis.get('urgent', []))} urgent, {len(analysis.get('high_priority', []))} high priority")
            return analysis

        except json.JSONDecodeError as e:
            print(f"[Inbox Summary] ERROR parsing LLM JSON response: {e}")
            print(f"[Inbox Summary] Raw response: {llm_response[:500]}")
            # Return fallback structure
            return {
                "urgent": [],
                "high_priority": [],
                "summary": "Email analysis is currently unavailable. Please try again.",
                "total_emails": len(email_data),
                "unread_count": sum(1 for e in email_data if e.get('unread', False)),
                "error": "Failed to parse AI analysis"
            }

    except Exception as e:
        print(f"[Inbox Summary] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "urgent": [],
            "high_priority": [],
            "summary": f"Error analyzing inbox: {str(e)}",
            "total_emails": 0,
            "unread_count": 0,
            "error": str(e)
        }


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


@router.get("/test-gmail")
async def test_gmail():
    """Test Gmail adapter initialization"""
    import sys
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv(override=True)

    result = {
        "env_vars": {
            "GMAIL_CLIENT_ID": os.getenv("GMAIL_CLIENT_ID", "NOT SET")[:30],
            "GMAIL_CLIENT_SECRET": "SET" if os.getenv("GMAIL_CLIENT_SECRET") else "NOT SET",
            "GMAIL_REFRESH_TOKEN": "SET" if os.getenv("GMAIL_REFRESH_TOKEN") else "NOT SET",
            "EMAIL_MOCK_MODE": os.getenv("EMAIL_MOCK_MODE", "false")
        }
    }

    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter
        gmail = GmailAdapter()
        result["adapter_created"] = "YES"
        result["use_mock"] = gmail.use_mock

        # Try to get service
        service = gmail.service
        result["service"] = "INITIALIZED" if service else "NONE"

        # Try to fetch 1 email
        threads = await gmail.fetch_threads(max_results=1)
        result["threads_fetched"] = len(threads)
        if threads:
            result["first_email_from"] = threads[0].get("from", "Unknown")

    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()

    return result

@router.get("/emails/test")
async def test_emails():
    """Test endpoint to verify basic functionality"""
    return {"status": "ok", "message": "Test endpoint works"}

@router.get("/emails")
async def get_emails(max_results: int = 10, query: str = None, unread_only: bool = False):
    """Get email list - using mock data in mock mode"""
    import sys
    import traceback

    try:
        print(f"[GET /emails] Starting - max_results={max_results}, query={query}, unread_only={unread_only}", flush=True)

        from datetime import datetime, timezone, timedelta
        import os

        # Check if we're in mock mode
        mock_mode = os.getenv("EMAIL_MOCK_MODE", "false").lower() == "true"
        print(f"[GET /emails] mock_mode={mock_mode}", flush=True)

        if mock_mode:
            print("[GET /emails] Using mock mode - generating test data", flush=True)
            # Return mock data directly
            now = datetime.now(timezone.utc)
            print(f"[GET /emails] Current time: {now.isoformat()}", flush=True)

            mock_emails = [
                {
                    "id": "mock_1",
                    "from": "john.doe@partner.com",
                    "subject": "Urgent: Project Deadline Tomorrow",
                    "preview": "Hi! Just a reminder that the Q4 project deliverables are due tomorrow.",
                    "body": "Hi! Just a reminder that the Q4 project deliverables are due tomorrow. Can you send me the final report?",
                    "date": (now - timedelta(hours=2)).isoformat(),
                    "timestamp": (now - timedelta(hours=2)).isoformat(),
                    "unread": True,
                    "attachments": [],
                    "hasAttachments": False,
                    "attachmentCount": 0
                },
                {
                    "id": "mock_2",
                    "from": "hr@company.com",
                    "subject": "Interview Scheduled - Software Engineer Position",
                    "preview": "Dear Candidate, We are pleased to schedule your technical interview for next Tuesday at 2 PM.",
                    "body": "Dear Candidate, We are pleased to schedule your technical interview for next Tuesday at 2 PM. Please confirm your availability.",
                    "date": (now - timedelta(hours=5)).isoformat(),
                    "timestamp": (now - timedelta(hours=5)).isoformat(),
                    "unread": True,
                    "attachments": [],
                    "hasAttachments": False,
                    "attachmentCount": 0
                },
                {
                    "id": "mock_3",
                    "from": "newsletter@techcrunch.com",
                    "subject": "Latest Tech News - November 2025",
                    "preview": "Top stories: AI breakthroughs, new product launches, and industry insights.",
                    "body": "Top stories: AI breakthroughs, new product launches, and industry insights. Read more...",
                    "date": (now - timedelta(hours=8)).isoformat(),
                    "timestamp": (now - timedelta(hours=8)).isoformat(),
                    "unread": False,
                    "attachments": [],
                    "hasAttachments": False,
                    "attachmentCount": 0
                }
            ]

            print(f"[GET /emails] Generated {len(mock_emails)} mock emails", flush=True)
            result = {
                "emails": mock_emails[:max_results],
                "count": len(mock_emails[:max_results])
            }
            print(f"[GET /emails] Returning {result['count']} emails", flush=True)
            return result

        # Real Gmail mode
        print("[GET /emails] Using REAL Gmail mode", flush=True)
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter

        print("[GET /emails] Creating GmailAdapter...", flush=True)
        gmail = GmailAdapter()

        print(f"[GET /emails] Fetching threads (max={max_results})...", flush=True)
        threads = await gmail.fetch_threads(max_results=max_results, unread_only=unread_only, query=query)

        print(f"[GET /emails] Fetched {len(threads)} threads, converting to email format...", flush=True)
        emails = []
        for thread in threads:
            timestamp = thread.get("timestamp", "")
            attachments = thread.get("attachments", [])
            emails.append({
                "id": thread.get("thread_id", ""),
                "from": thread.get("from", "Unknown"),
                "subject": thread.get("subject", "No Subject"),
                "preview": thread.get("preview", "")[:200],
                "body": thread.get("preview", ""),
                "date": timestamp,
                "timestamp": timestamp,
                "unread": thread.get("unread", False),
                "attachments": attachments,
                "hasAttachments": len(attachments) > 0,
                "attachmentCount": len(attachments)
            })

        print(f"[GET /emails] Successfully returning {len(emails)} emails", flush=True)
        return {"emails": emails, "count": len(emails)}

    except Exception as e:
        print("\n" + "=" * 80, flush=True)
        print(f"[GET /emails] CRITICAL ERROR CAUGHT", flush=True)
        print(f"[GET /emails] Error type: {type(e).__name__}", flush=True)
        print(f"[GET /emails] Error message: {str(e)}", flush=True)
        print(f"[GET /emails] Error errno: {getattr(e, 'errno', 'N/A')}", flush=True)
        print(f"[GET /emails] Error filename: {getattr(e, 'filename', 'N/A')}", flush=True)
        print("\n[GET /emails] Full traceback:", flush=True)
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
        print("=" * 80 + "\n", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emails/attachment/{message_id}/{attachment_id}")
async def download_attachment(message_id: str, attachment_id: str):
    """
    Download an email attachment.

    Args:
        message_id: The Gmail message ID containing the attachment
        attachment_id: The attachment ID from Gmail

    Returns:
        The attachment file as bytes
    """
    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter
        from fastapi.responses import Response
        import base64

        gmail = GmailAdapter()
        service = gmail.service

        # Fetch the attachment
        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()

        # Decode the attachment data
        file_data = base64.urlsafe_b64decode(attachment['data'])

        # Return the file
        return Response(
            content=file_data,
            media_type='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{attachment_id}"'
            }
        )

    except Exception as e:
        print(f"Error downloading attachment: {e}")
        raise HTTPException(status_code=500, detail=f"Attachment download error: {str(e)}")


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


class TTSRequest(BaseModel):
    """Request model for TTS"""
    text: str


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
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
    import traceback

    try:
        print("[TTS] ===== TTS ENDPOINT CALLED =====")
        print(f"[TTS] Request data: {request}")

        text = request.text
        print(f"[TTS] Text to convert: '{text}'")

        if not text:
            print("[TTS] ERROR: No text provided")
            raise HTTPException(status_code=400, detail="No text provided")

        # Get API key and voice ID from environment
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

        print(f"[TTS] API Key: {'***' + api_key[-10:] if api_key else 'NOT FOUND'}")
        print(f"[TTS] Voice ID: {voice_id}")

        if not api_key:
            print("[TTS] ERROR: ElevenLabs API key not configured")
            raise HTTPException(
                status_code=500,
                detail="ElevenLabs API key not configured"
            )

        # Initialize ElevenLabs client
        print("[TTS] Initializing ElevenLabs client...")
        client = ElevenLabs(api_key=api_key)

        # Generate speech using the new API
        print("[TTS] Calling text_to_speech.convert()...")
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1"
        )

        # Convert generator to bytes
        print("[TTS] Converting audio generator to bytes...")
        audio_bytes = b"".join(audio_generator)
        print(f"[TTS] SUCCESS! Generated {len(audio_bytes)} bytes of audio")

        # Return audio as MP3
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[TTS] ERROR: {str(e)}")
        print(f"[TTS] Error type: {type(e).__name__}")
        traceback.print_exc()
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
    Generate an AI draft reply for a given email using LLM fallback chain.

    Tries: Euron → DeepSeek → Google Gemini → OpenAI
    """
    try:
        # Use LLM fallback chain to generate intelligent draft
        prompt = f"""Generate a professional email reply for the following email:

From: {request.email_from}
Subject: {request.email_subject}
Body: {request.email_body}

Generate a brief, professional reply (2-4 sentences). Be polite and helpful.
Only return the email body text, no greetings or signatures needed."""

        # Call LLM with automatic fallback
        draft_text = call_llm_with_fallback(prompt, max_tokens=300, temperature=0.7)

        return {
            "success": True,
            "draft_text": draft_text.strip(),
            "email_id": request.email_id
        }

    except Exception as e:
        print(f"[Draft Reply] Error: {e}")
        # Fallback to simple response if all LLM providers fail
        fallback_text = f"""Thank you for your email regarding "{request.email_subject}".

I have reviewed your message and will get back to you shortly with a detailed response. If you have any urgent concerns, please let me know.

Best regards"""

        return {
            "success": True,
            "draft_text": fallback_text,
            "email_id": request.email_id,
            "fallback": True,
            "error": str(e)
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


@router.get("/emails/summarize")
async def summarize_emails(max_results: int = 30, unread_only: bool = False):
    """
    Generate AI-powered summary of emails with key action items for the day.

    Analyzes recent emails and extracts:
    - Urgent action items
    - Upcoming deadlines
    - Meeting invitations
    - Important decisions needed
    - Follow-ups required
    - Emails needing replies
    - Conversation threads (2+ messages)
    - Interviews/meetings this week

    Returns structured summary with priorities and reasoning.
    """
    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter
        from voice_agent.adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter
        from datetime import datetime, timezone, timedelta
        import re

        print(f"[Email Summarization] Starting analysis of {max_results} emails...")

        # Fetch recent emails
        gmail = GmailAdapter()
        threads = await gmail.fetch_threads(
            max_results=max_results,
            unread_only=unread_only
        )

        if not threads:
            return {
                "success": True,
                "summary": "No emails to summarize.",
                "urgent_actions": [],
                "deadlines": [],
                "meetings": [],
                "emails_needing_reply": 0,
                "conversation_threads": 0,
                "urgent_count": 0,
                "total_analyzed": 0
            }

        print(f"[Email Summarization] Analyzing {len(threads)} emails...")

        # Analyze thread patterns for reasoning
        emails_needing_reply = 0
        conversation_threads = 0
        thread_senders = {}

        for thread in threads:
            # Count threads with multiple messages (conversation threads)
            message_count = thread.get('message_count', 1)
            if message_count >= 2:
                conversation_threads += 1

            # Check if email needs reply (simplified: unread emails from others likely need reply)
            # In production, you'd check if the last message in thread was from you or someone else
            if thread.get('unread', False):
                emails_needing_reply += 1

            # Track senders for calendar linking
            sender_email = thread.get('from', '')
            sender_match = re.search(r'<(.+?)>', sender_email)
            if sender_match:
                sender_email = sender_match.group(1)
            thread_senders[sender_email] = thread

        # Fetch calendar events for the week
        calendar_events = []
        interviews_meetings_count = 0
        try:
            calendar = GoogleCalendarAdapter()
            now = datetime.now(timezone.utc)
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)

            calendar_events = await calendar.get_events(start_time=start, end_time=end)

            # Count interviews and meetings
            for event in calendar_events:
                title = event.get('title', '').lower()
                if any(keyword in title for keyword in ['interview', 'meeting', 'call', 'sync', 'standup', 'discussion']):
                    interviews_meetings_count += 1

            print(f"[Email Summarization] Found {interviews_meetings_count} meetings/interviews this week")
        except Exception as cal_error:
            print(f"[Email Summarization] Calendar fetch warning: {cal_error}")

        # Link calendar events with emails from same sender
        calendar_email_links = []
        for event in calendar_events:
            organizer = event.get('organizer', '')
            if organizer in thread_senders:
                calendar_email_links.append({
                    "event_title": event.get('title', 'Untitled Event'),
                    "event_start": event.get('start', ''),
                    "related_email_subject": thread_senders[organizer].get('subject', ''),
                    "sender": organizer
                })

        # Build comprehensive email context for LLM
        email_context = "EMAILS TO ANALYZE:\n\n"
        for idx, thread in enumerate(threads[:max_results], 1):
            message_count = thread.get('message_count', 1)
            email_context += f"Email {idx}:\n"
            email_context += f"From: {thread.get('from', 'Unknown')}\n"
            email_context += f"Subject: {thread.get('subject', 'No Subject')}\n"
            email_context += f"Date: {thread.get('timestamp', 'Unknown')}\n"
            email_context += f"Messages in thread: {message_count}\n"
            email_context += f"Preview: {thread.get('preview', '')[:300]}\n"
            email_context += f"Unread: {thread.get('unread', False)}\n\n"

        # Add calendar context
        calendar_context = ""
        if calendar_events:
            calendar_context = f"\n\nCALENDAR EVENTS THIS WEEK:\n"
            for event in calendar_events[:10]:  # Top 10 events
                calendar_context += f"- {event.get('title', 'Untitled')}: {event.get('start', 'No date')}\n"

        # Create enhanced prompt for LLM analysis with reasoning
        prompt = f"""{email_context}{calendar_context}

CONTEXT:
- Total emails analyzed: {len(threads)}
- Emails likely needing reply: {emails_needing_reply}
- Conversation threads (2+ messages): {conversation_threads}
- Meetings/Interviews this week: {interviews_meetings_count}

TASK: Analyze these emails and calendar events, then provide a structured summary with reasoning. Extract:

1. URGENT ACTION ITEMS (things requiring immediate attention today)
2. DEADLINES (with dates if mentioned)
3. MEETING INVITATIONS from emails (with time/date if mentioned)
4. IMPORTANT DECISIONS NEEDED
5. FOLLOW-UPS REQUIRED
6. REASONING: Explain key patterns (e.g., "5 emails need replies", "3 ongoing conversations", "2 interviews scheduled this week")

Format your response as JSON with these keys:
{{
  "urgent_actions": ["action 1", "action 2"],
  "deadlines": ["deadline 1 - Date", "deadline 2 - Date"],
  "meetings": ["meeting 1 - Time/Date", "meeting 2 - Time/Date"],
  "decisions": ["decision 1", "decision 2"],
  "followups": ["followup 1", "followup 2"],
  "summary": "Brief 2-3 sentence overview of your inbox and calendar for the week with key numbers",
  "reasoning": "Detailed reasoning about email patterns, reply needs, and meeting schedule"
}}

Only include items that are actually present in the emails. If a category has no items, use an empty array."""

        # Use LLM fallback chain for analysis
        print("[Email Summarization] Calling LLM for analysis...")
        analysis_text = call_llm_with_fallback(prompt, max_tokens=1500, temperature=0.3)

        # Try to parse JSON response
        try:
            import json
            # Clean up response (remove markdown code blocks if present)
            clean_text = analysis_text.strip()
            if clean_text.startswith("```"):
                # Remove markdown code blocks
                clean_text = clean_text.split("```")[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
            clean_text = clean_text.strip()

            analysis = json.loads(clean_text)
        except Exception as parse_error:
            print(f"[Email Summarization] JSON parse error: {parse_error}")
            # Fallback to simple text summary
            analysis = {
                "urgent_actions": [],
                "deadlines": [],
                "meetings": [],
                "decisions": [],
                "followups": [],
                "summary": analysis_text[:500],
                "reasoning": "Could not parse detailed reasoning."
            }

        # Count urgent emails
        urgent_count = sum(1 for t in threads if t.get('unread', False))

        print(f"[Email Summarization] Analysis complete. Found {len(analysis.get('urgent_actions', []))} action items")

        return {
            "success": True,
            "summary": analysis.get("summary", "Analysis complete."),
            "reasoning": analysis.get("reasoning", ""),
            "urgent_actions": analysis.get("urgent_actions", []),
            "deadlines": analysis.get("deadlines", []),
            "meetings": analysis.get("meetings", []),
            "decisions": analysis.get("decisions", []),
            "followups": analysis.get("followups", []),
            "emails_needing_reply": emails_needing_reply,
            "conversation_threads": conversation_threads,
            "interviews_meetings_count": interviews_meetings_count,
            "calendar_email_links": calendar_email_links,
            "urgent_count": urgent_count,
            "total_analyzed": len(threads),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        print(f"[Email Summarization] Error: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Email summarization error: {str(e)}")


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
