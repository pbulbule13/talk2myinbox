"""
Standalone Communications App Server
FastAPI server for the email and calendar communications application
"""

import os
import sys
from pathlib import Path

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
