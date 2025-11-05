"""
Standalone Communications App Server
FastAPI server for the email and calendar communications application
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from voice_agent.api.routes import router as voice_agent_router

# Initialize FastAPI app
app = FastAPI(
    title="Communications App API",
    description="Email and Calendar Management System with Voice Agent Integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define direct email endpoint BEFORE including router (to avoid conflicts)
@app.get("/voice-agent/emails-direct")
async def get_emails_direct(max_results: int = 30, query: str = None, unread_only: bool = False):
    """Direct email endpoint - returns REAL Gmail data"""
    try:
        from voice_agent.adapters.email.gmail_adapter import GmailAdapter

        print(f"[emails-direct] Fetching {max_results} real emails from Gmail...")
        gmail = GmailAdapter()
        threads = await gmail.fetch_threads(max_results=max_results, unread_only=unread_only, query=query)

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

        print(f"[emails-direct] Successfully returning {len(emails)} real Gmail emails")
        return {"emails": emails, "count": len(emails)}

    except Exception as e:
        print(f"[emails-direct] ERROR: {e}")
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

# Include voice agent routes
app.include_router(voice_agent_router)

# Serve frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main communications app page"""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    return """
    <html>
        <head><title>Communications App</title></head>
        <body>
            <h1>Communications App</h1>
            <p>Frontend not found. Please ensure frontend files are in the 'frontend' directory.</p>
            <p>API documentation available at <a href="/docs">/docs</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "communications-app",
        "version": "1.0.0"
    }

@app.get("/voice-agent/emails-direct")
async def get_emails_direct(max_results: int = 10):
    """Direct email endpoint - bypasses complex routes"""
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)

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

    return {
        "emails": mock_emails[:max_results],
        "count": len(mock_emails[:max_results])
    }

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"""
    ========================================
    Communications App Server Starting
    ========================================
    Server: http://{host}:{port}
    API Docs: http://{host}:{port}/docs
    Health: http://{host}:{port}/health
    ========================================
    """)

    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
