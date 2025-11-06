"""
Main entry point for Cognitive Journal Agent.
Supports CLI, API server, and programmatic usage modes.
"""

import sys
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config, get_config
from graph.agent_graph import run_agent, AgentWithMemory, create_agent_graph
from nodes.output import format_text_output


# ===========================
# CLI Interface
# ===========================

def cli_mode():
    """Interactive CLI mode for the journal agent."""
    print("\n" + "="*60)
    print("COGNITIVE JOURNAL AGENT - Interactive Mode")
    print("="*60)
    print("\nCommands:")
    print("  - Type journal entries, thoughts, or notes")
    print("  - Use action commands (e.g., 'send email', 'schedule meeting')")
    print("  - Type 'summarize' or 'report' for daily summary")
    print("  - Type 'quit' or 'exit' to exit")
    print("\n" + "="*60 + "\n")

    # Initialize agent with memory
    agent = AgentWithMemory()

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! Your journal entries have been saved.")
                break

            # Execute agent
            print("\nProcessing...\n")
            result = agent.execute(user_input)

            # Display result
            if result.get("tool_response"):
                print(f"Agent: {result['tool_response']}")

            elif result.get("final_report"):
                # Format and display report
                report = result["final_report"]
                print(format_text_output(report))

                # Mention audio if generated
                if result.get("audio_output_path"):
                    print(f"\nAudio report saved to: {result['audio_output_path']}")

            elif result.get("new_entry"):
                print("Agent: Journal entry recorded successfully!")

                entry = result["new_entry"]
                if entry.contextual_tags:
                    print(f"  Tags: {', '.join(entry.contextual_tags)}")
                if entry.extracted_action_items:
                    print(f"  Action items: {len(entry.extracted_action_items)}")

            else:
                print("Agent: Entry processed.")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Continuing...")


# ===========================
# API Server Mode
# ===========================

def api_mode():
    """Start FastAPI server for the journal agent."""
    try:
        from fastapi import FastAPI, HTTPException, File, UploadFile, Form
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        import uvicorn
        import tempfile
        import shutil
    except ImportError:
        print("Error: FastAPI and uvicorn are required for API mode.")
        print("Install with: pip install fastapi uvicorn")
        sys.exit(1)

    # Create FastAPI app
    app = FastAPI(
        title="Cognitive Journal Agent API",
        description="Multimodal, agentic personal journal assistant",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request/Response models
    class JournalRequest(BaseModel):
        user_input: str
        input_data: Optional[Dict[str, Any]] = None

    class JournalResponse(BaseModel):
        success: bool
        message: str
        data: Optional[Dict[str, Any]] = None

    # Endpoints
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Cognitive Journal Agent API",
            "version": "1.0.0",
            "status": "running"
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.post("/journal", response_model=JournalResponse)
    async def create_journal_entry(request: JournalRequest):
        """
        Create a new journal entry.

        Args:
            request: Journal request with user_input and optional input_data

        Returns:
            Journal response with processing result
        """
        try:
            # Run agent
            result = run_agent(request.user_input, request.input_data)

            # Format response
            if result.get("tool_response"):
                return JournalResponse(
                    success=True,
                    message=result["tool_response"],
                    data={"type": "tool_execution"}
                )

            elif result.get("final_report"):
                return JournalResponse(
                    success=True,
                    message="Report generated",
                    data={
                        "type": "report",
                        "report": result["final_report"].dict() if hasattr(result["final_report"], "dict") else str(result["final_report"]),
                        "audio_path": result.get("audio_output_path")
                    }
                )

            elif result.get("new_entry"):
                entry = result["new_entry"]
                return JournalResponse(
                    success=True,
                    message="Journal entry recorded",
                    data={
                        "type": "journal_entry",
                        "entry_id": entry.source_id if hasattr(entry, "source_id") else None,
                        "tags": entry.contextual_tags if hasattr(entry, "contextual_tags") else [],
                        "action_items": entry.extracted_action_items if hasattr(entry, "extracted_action_items") else []
                    }
                )

            else:
                return JournalResponse(
                    success=True,
                    message="Entry processed",
                    data={"type": "processed"}
                )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/entries")
    async def get_entries():
        """Retrieve all journal entries."""
        try:
            from nodes.storage import StorageManager
            storage = StorageManager()
            entries = storage.get_entries()

            return {
                "success": True,
                "count": len(entries),
                "entries": [entry.dict() for entry in entries]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/actions")
    async def get_actions():
        """Retrieve pending action items."""
        try:
            from nodes.storage import StorageManager
            storage = StorageManager()
            actions = storage.get_pending_actions()

            return {
                "success": True,
                "count": len(actions),
                "actions": [action.dict() for action in actions]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/summarize")
    async def generate_summary():
        """Generate daily summary."""
        try:
            result = run_agent("Generate my daily summary")

            if result.get("final_report"):
                report = result["final_report"]
                return {
                    "success": True,
                    "report": report.dict() if hasattr(report, "dict") else str(report),
                    "audio_path": result.get("audio_output_path")
                }
            else:
                return {
                    "success": False,
                    "message": "Could not generate summary"
                }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/upload", response_model=JournalResponse)
    async def upload_file(file: UploadFile = File(...), input_type: str = Form(...)):
        """
        Upload and process a file (voice memo, image, PDF).

        Args:
            file: The uploaded file
            input_type: Type of input ('voice', 'image', 'pdf')

        Returns:
            Journal response with processing result
        """
        try:
            # Create temporary file to save the upload
            suffix = Path(file.filename).suffix if file.filename else ''
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                # Copy uploaded file to temporary file
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name

            try:
                # Process based on input type
                from nodes.ingestion import MultimodalIngest
                ingestor = MultimodalIngest()

                if input_type == 'voice':
                    # Process voice memo
                    entry = ingestor.process_voice_memo(tmp_path)
                    message = "Voice memo processed"

                elif input_type == 'image':
                    # Process image with OCR
                    entry = ingestor.process_photo_ocr(tmp_path)
                    message = "Image processed with OCR"

                elif input_type == 'pdf':
                    # Process PDF
                    entry = ingestor.process_pdf(tmp_path)
                    message = "PDF document processed"

                else:
                    raise ValueError(f"Unknown input type: {input_type}")

                # Store the entry
                from nodes.storage import StorageManager
                storage = StorageManager()
                storage.store_entry(entry)

                return JournalResponse(
                    success=True,
                    message=message,
                    data={
                        "type": "journal_entry",
                        "entry_id": entry.source_id if hasattr(entry, "source_id") else None,
                        "tags": entry.contextual_tags if hasattr(entry, "contextual_tags") else [],
                        "action_items": entry.extracted_action_items if hasattr(entry, "extracted_action_items") else [],
                        "extracted_text": entry.raw_content[:200] if hasattr(entry, "raw_content") else ""
                    }
                )

            finally:
                # Clean up temporary file
                try:
                    Path(tmp_path).unlink()
                except:
                    pass

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))

    # Include calendar routes
    try:
        from api.calendar_routes import router as calendar_router
        app.include_router(calendar_router)
    except ImportError as e:
        print(f"Warning: Could not load calendar routes: {e}")
        print("Calendar features will not be available.")

    # Start server
    print("\n" + "="*60)
    print("COGNITIVE JOURNAL AGENT - API Server")
    print("="*60)
    print(f"\nStarting server on {config.api.host}:{config.api.port}")
    print(f"API docs available at: http://{config.api.host}:{config.api.port}/docs")
    print("\n" + "="*60 + "\n")

    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload
    )


# ===========================
# Demo Mode
# ===========================

def demo_mode():
    """
    Run a demo with sample journal entries.
    """
    print("\n" + "="*60)
    print("COGNITIVE JOURNAL AGENT - Demo Mode")
    print("="*60 + "\n")

    sample_entries = [
        "Had a productive morning meeting with the team about Q4 goals. Need to send follow-up email to Sarah.",
        "Feeling stressed about the upcoming project deadline next Friday. Should block out time for deep work.",
        "Great idea: Create a new feature for automatic task prioritization in the app.",
        "Lunch meeting with John went well. He suggested we collaborate on the ML project.",
        "Need to review the budget proposal before tomorrow's board meeting."
    ]

    print("Processing sample journal entries...\n")

    for idx, entry in enumerate(sample_entries, 1):
        print(f"Entry {idx}: {entry}")
        result = run_agent(entry)

        if result.get("new_entry"):
            journal_entry = result["new_entry"]
            print(f"  > Tags: {', '.join(journal_entry.contextual_tags)}")
            if journal_entry.extracted_action_items:
                print(f"  > Actions: {journal_entry.extracted_action_items[0]}")
        print()

    print("\nGenerating daily summary...\n")
    result = run_agent("Generate my daily summary")

    if result.get("final_report"):
        print(format_text_output(result["final_report"]))

        if result.get("audio_output_path"):
            print(f"\nAudio report saved to: {result['audio_output_path']}")

    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60 + "\n")


# ===========================
# Single Command Mode
# ===========================

def single_command_mode(command: str):
    """
    Execute a single command and exit.

    Args:
        command: Command to execute
    """
    print(f"\nExecuting: {command}\n")

    result = run_agent(command)

    # Display result
    if result.get("tool_response"):
        print(f"Result: {result['tool_response']}")

    elif result.get("final_report"):
        print(format_text_output(result["final_report"]))

        if result.get("audio_output_path"):
            print(f"\nAudio report: {result['audio_output_path']}")

    elif result.get("new_entry"):
        entry = result["new_entry"]
        print("Journal entry recorded!")
        print(f"Tags: {', '.join(entry.contextual_tags)}")
        if entry.extracted_action_items:
            print(f"Actions: {len(entry.extracted_action_items)}")

    else:
        print("Processed.")


# ===========================
# Main Entry Point
# ===========================

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Cognitive Journal Agent - Multimodal, Agentic Personal Assistant"
    )

    parser.add_argument(
        "mode",
        nargs="?",
        choices=["cli", "api", "demo"],
        default="cli",
        help="Execution mode (default: cli)"
    )

    parser.add_argument(
        "-c", "--command",
        type=str,
        help="Execute a single command and exit"
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Display current configuration"
    )

    parser.add_argument(
        "--create-env",
        action="store_true",
        help="Create .env.template file"
    )

    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate workflow visualization"
    )

    args = parser.parse_args()

    # Handle special flags
    if args.config:
        config.print_config()
        return

    if args.create_env:
        from config import create_env_template
        create_env_template()
        return

    if args.visualize:
        from graph.agent_graph import visualize_graph
        visualize_graph()
        return

    # Handle single command
    if args.command:
        single_command_mode(args.command)
        return

    # Handle execution modes
    if args.mode == "cli":
        cli_mode()
    elif args.mode == "api":
        api_mode()
    elif args.mode == "demo":
        demo_mode()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
