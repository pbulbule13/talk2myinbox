"""
Calendar API Routes.
Endpoints for multi-calendar integration including OAuth, sync, and unified view.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import tempfile
from pathlib import Path
import uuid

from data_models.pydantic_schemas import CalendarSource, UnifiedEvent, CalendarConnection
from nodes.calendar_storage import CalendarStorageManager
from services.calendar_sync import GoogleCalendarSync, MicrosoftCalendarSync, ICalSync
from services.calendar_ocr import CalendarOCRProcessor, ConflictDetector


# Create router
router = APIRouter(prefix="/calendar", tags=["calendar"])

# Storage manager
calendar_storage = CalendarStorageManager()


# ============================================================================
# Request/Response Models
# ============================================================================

class AddCalendarSourceRequest(BaseModel):
    """Request to add a new calendar source."""
    source_type: str  # google, outlook, ical, ocr, manual
    display_name: str
    color: Optional[str] = None
    sync_frequency_minutes: int = 60
    sync_window_days: int = 90


class CalendarSourceResponse(BaseModel):
    """Response with calendar source details."""
    success: bool
    message: str
    source: Optional[Dict[str, Any]] = None


class EventsResponse(BaseModel):
    """Response with list of events."""
    success: bool
    count: int
    events: List[Dict[str, Any]]
    conflicts: Optional[List[Dict[str, Any]]] = None


class OAuthUrlResponse(BaseModel):
    """Response with OAuth URL."""
    success: bool
    auth_url: str
    message: str


class SyncResponse(BaseModel):
    """Response from calendar sync operation."""
    success: bool
    message: str
    events_synced: int
    conflicts_detected: int


# ============================================================================
# Calendar Source Management
# ============================================================================

@router.post("/sources", response_model=CalendarSourceResponse)
async def add_calendar_source(request: AddCalendarSourceRequest):
    """
    Add a new calendar source.

    Args:
        request: Calendar source details

    Returns:
        Calendar source response
    """
    try:
        # Create calendar source
        source = CalendarSource(
            source_id=f"{request.source_type}_{uuid.uuid4().hex[:8]}",
            source_type=request.source_type,
            display_name=request.display_name,
            is_active=True,
            color=request.color or "#4285F4",
            requires_oauth=request.source_type in ["google", "outlook", "apple"],
            sync_frequency_minutes=request.sync_frequency_minutes,
            sync_window_days=request.sync_window_days
        )

        # Save to storage
        success = calendar_storage.save_calendar_source(source)

        if success:
            return CalendarSourceResponse(
                success=True,
                message=f"Calendar source '{request.display_name}' added successfully",
                source=source.dict()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save calendar source")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def get_calendar_sources(active_only: bool = Query(False)):
    """
    Get all calendar sources.

    Args:
        active_only: Filter for active sources only

    Returns:
        List of calendar sources
    """
    try:
        sources = calendar_storage.get_calendar_sources(active_only=active_only)

        return {
            "success": True,
            "count": len(sources),
            "sources": [source.dict() for source in sources]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sources/{source_id}")
async def delete_calendar_source(source_id: str):
    """
    Delete or deactivate a calendar source.

    Args:
        source_id: ID of the source to delete

    Returns:
        Success response
    """
    try:
        success = calendar_storage.delete_calendar_source(source_id)

        if success:
            return {
                "success": True,
                "message": f"Calendar source {source_id} deactivated"
            }
        else:
            raise HTTPException(status_code=404, detail="Calendar source not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OAuth Authentication
# ============================================================================

@router.post("/auth/google", response_model=CalendarSourceResponse)
async def authenticate_google_calendar(user_email: str = Form(...)):
    """
    Authenticate with Google Calendar via OAuth.

    Args:
        user_email: User's email address

    Returns:
        Authentication result
    """
    try:
        sync_service = GoogleCalendarSync()
        success, error = sync_service.authenticate(user_email)

        if success:
            return CalendarSourceResponse(
                success=True,
                message="Google Calendar authenticated successfully"
            )
        else:
            raise HTTPException(status_code=401, detail=error)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/microsoft/url", response_model=OAuthUrlResponse)
async def get_microsoft_auth_url():
    """
    Get Microsoft OAuth authorization URL.

    Returns:
        OAuth URL for user to visit
    """
    try:
        sync_service = MicrosoftCalendarSync()
        auth_url = sync_service.get_auth_url()

        return OAuthUrlResponse(
            success=True,
            auth_url=auth_url,
            message="Visit this URL to authorize Microsoft Calendar access"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/microsoft/callback")
async def microsoft_auth_callback(
    code: str = Form(...),
    user_email: str = Form(...)
):
    """
    Handle Microsoft OAuth callback.

    Args:
        code: Authorization code from OAuth redirect
        user_email: User's email address

    Returns:
        Authentication result
    """
    try:
        sync_service = MicrosoftCalendarSync()
        success, error = sync_service.authenticate(code, user_email)

        if success:
            return {
                "success": True,
                "message": "Microsoft Calendar authenticated successfully"
            }
        else:
            raise HTTPException(status_code=401, detail=error)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Calendar Synchronization
# ============================================================================

@router.post("/sync/{source_id}", response_model=SyncResponse)
async def sync_calendar_source(source_id: str):
    """
    Sync events from a calendar source.

    Args:
        source_id: ID of the calendar source to sync

    Returns:
        Sync result
    """
    try:
        # Get source
        sources = calendar_storage.get_calendar_sources()
        source = next((s for s in sources if s.source_id == source_id), None)

        if not source:
            raise HTTPException(status_code=404, detail="Calendar source not found")

        if not source.is_active:
            raise HTTPException(status_code=400, detail="Calendar source is inactive")

        # Sync based on source type
        events = []
        error = None

        if source.source_type == "google":
            sync_service = GoogleCalendarSync()
            events, error = sync_service.fetch_events(source)

        elif source.source_type == "outlook":
            sync_service = MicrosoftCalendarSync()
            # Need user email - get from connection
            connection = calendar_storage.get_connection("outlook", "")  # TODO: get user email
            if connection:
                events, error = sync_service.fetch_events(source, connection.user_email)
            else:
                error = "No OAuth connection found for Outlook"

        elif source.source_type == "ical":
            if not source.file_path:
                error = "No iCal file path specified"
            else:
                sync_service = ICalSync()
                events, error = sync_service.import_ical_file(source, source.file_path)

        else:
            error = f"Sync not supported for source type: {source.source_type}"

        if error:
            raise HTTPException(status_code=400, detail=error)

        # Detect conflicts
        conflict_detector = ConflictDetector()
        conflicts = conflict_detector.detect_conflicts(events)

        return SyncResponse(
            success=True,
            message=f"Successfully synced {len(events)} events",
            events_synced=len(events),
            conflicts_detected=len(conflicts)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/all", response_model=SyncResponse)
async def sync_all_calendars():
    """
    Sync all active calendar sources.

    Returns:
        Combined sync result
    """
    try:
        sources = calendar_storage.get_calendar_sources(active_only=True)

        total_events = 0
        total_conflicts = 0
        errors = []

        for source in sources:
            try:
                # Sync each source
                if source.source_type == "google":
                    sync_service = GoogleCalendarSync()
                    events, error = sync_service.fetch_events(source)

                elif source.source_type == "outlook":
                    sync_service = MicrosoftCalendarSync()
                    connection = calendar_storage.get_connection("outlook", "")
                    if connection:
                        events, error = sync_service.fetch_events(source, connection.user_email)
                    else:
                        error = "No OAuth connection found"

                elif source.source_type == "ical" and source.file_path:
                    sync_service = ICalSync()
                    events, error = sync_service.import_ical_file(source, source.file_path)

                else:
                    continue

                if error:
                    errors.append(f"{source.display_name}: {error}")
                else:
                    total_events += len(events)

            except Exception as e:
                errors.append(f"{source.display_name}: {str(e)}")

        # Detect conflicts across all events
        conflict_detector = ConflictDetector()
        conflicts = conflict_detector.detect_conflicts()
        total_conflicts = len(conflicts)

        message = f"Synced {total_events} events from {len(sources)} sources"
        if errors:
            message += f". Errors: {'; '.join(errors)}"

        return SyncResponse(
            success=True,
            message=message,
            events_synced=total_events,
            conflicts_detected=total_conflicts
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Event Retrieval and Management
# ============================================================================

@router.get("/events", response_model=EventsResponse)
async def get_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    source_ids: Optional[str] = Query(None),  # Comma-separated list
    detect_conflicts: bool = Query(True)
):
    """
    Get unified calendar events.

    Args:
        start_date: Filter start date (ISO format)
        end_date: Filter end date (ISO format)
        source_ids: Comma-separated source IDs to filter
        detect_conflicts: Whether to detect and include conflicts

    Returns:
        List of events with optional conflict information
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # Parse source IDs
        source_id_list = source_ids.split(',') if source_ids else None

        # Fetch events
        events = calendar_storage.get_events(
            start_date=start_dt,
            end_date=end_dt,
            source_ids=source_id_list
        )

        # Detect conflicts if requested
        conflicts_data = None
        if detect_conflicts:
            conflict_detector = ConflictDetector()
            conflicts = conflict_detector.detect_conflicts(events)

            conflicts_data = [
                {
                    "event1_id": c[0].event_id,
                    "event2_id": c[1].event_id,
                    "conflict_type": c[2],
                    "event1_title": c[0].title,
                    "event2_title": c[1].title,
                    "event1_time": f"{c[0].start_time.isoformat()} - {c[0].end_time.isoformat()}",
                    "event2_time": f"{c[1].start_time.isoformat()} - {c[1].end_time.isoformat()}"
                }
                for c in conflicts
            ]

        return EventsResponse(
            success=True,
            count=len(events),
            events=[event.dict() for event in events],
            conflicts=conflicts_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/free-slots")
async def get_free_slots(
    start_date: str = Query(...),
    end_date: str = Query(...),
    min_duration_minutes: int = Query(30),
    work_hours_only: bool = Query(True)
):
    """
    Find free time slots between events.

    Args:
        start_date: Search range start (ISO format)
        end_date: Search range end (ISO format)
        min_duration_minutes: Minimum slot duration
        work_hours_only: Only show work hours (9am-5pm M-F)

    Returns:
        List of free time slots
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        conflict_detector = ConflictDetector()
        free_slots = conflict_detector.get_free_slots(
            start_dt,
            end_dt,
            min_duration_minutes,
            work_hours_only
        )

        return {
            "success": True,
            "count": len(free_slots),
            "free_slots": [
                {
                    "start": slot['start'].isoformat(),
                    "end": slot['end'].isoformat(),
                    "duration_minutes": (slot['end'] - slot['start']).total_seconds() / 60
                }
                for slot in free_slots
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OCR Calendar Import
# ============================================================================

@router.post("/import/ocr")
async def import_calendar_ocr(
    file: UploadFile = File(...),
    source_id: str = Form(...),
    reference_date: Optional[str] = Form(None)
):
    """
    Import calendar events from an image using OCR.

    Args:
        file: Calendar image file
        source_id: ID of the calendar source
        reference_date: Reference date for parsing (ISO format)

    Returns:
        Import result with extracted events
    """
    try:
        # Get source
        sources = calendar_storage.get_calendar_sources()
        source = next((s for s in sources if s.source_id == source_id), None)

        if not source:
            raise HTTPException(status_code=404, detail="Calendar source not found")

        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix if file.filename else '.png'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process image
            ocr_processor = CalendarOCRProcessor()
            ref_date = datetime.fromisoformat(reference_date) if reference_date else None

            events, error = ocr_processor.process_calendar_image(source, tmp_path, ref_date)

            if error:
                raise HTTPException(status_code=400, detail=error)

            # Detect conflicts
            conflict_detector = ConflictDetector()
            conflicts = conflict_detector.detect_conflicts(events)

            return {
                "success": True,
                "message": f"Extracted {len(events)} events from calendar image",
                "events_count": len(events),
                "conflicts_detected": len(conflicts),
                "events": [event.dict() for event in events]
            }

        finally:
            # Clean up temp file
            try:
                Path(tmp_path).unlink()
            except:
                pass

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# iCal File Import
# ============================================================================

@router.post("/import/ical")
async def import_ical_file(
    file: UploadFile = File(...),
    source_id: str = Form(...)
):
    """
    Import calendar events from an iCal/ICS file.

    Args:
        file: iCal/ICS file
        source_id: ID of the calendar source

    Returns:
        Import result with extracted events
    """
    try:
        # Get source
        sources = calendar_storage.get_calendar_sources()
        source = next((s for s in sources if s.source_id == source_id), None)

        if not source:
            raise HTTPException(status_code=404, detail="Calendar source not found")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ics') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Import iCal file
            ical_sync = ICalSync()
            events, error = ical_sync.import_ical_file(source, tmp_path)

            if error:
                raise HTTPException(status_code=400, detail=error)

            # Detect conflicts
            conflict_detector = ConflictDetector()
            conflicts = conflict_detector.detect_conflicts(events)

            return {
                "success": True,
                "message": f"Imported {len(events)} events from iCal file",
                "events_count": len(events),
                "conflicts_detected": len(conflicts),
                "events": [event.dict() for event in events]
            }

        finally:
            # Clean up temp file
            try:
                Path(tmp_path).unlink()
            except:
                pass

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Calendar Analytics
# ============================================================================

@router.get("/analytics/daily")
async def get_daily_analytics(date: str = Query(...)):
    """
    Get calendar analytics for a specific day.

    Args:
        date: Date in ISO format (YYYY-MM-DD)

    Returns:
        Daily calendar insights
    """
    try:
        target_date = datetime.fromisoformat(date)
        start_of_day = target_date.replace(hour=0, minute=0, second=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59)

        # Fetch events for the day
        events = calendar_storage.get_events(
            start_date=start_of_day,
            end_date=end_of_day
        )

        # Calculate analytics
        total_duration = sum(
            (event.end_time - event.start_time).total_seconds() / 60
            for event in events
        )

        # Find busiest hours
        hour_counts = {}
        for event in events:
            hour = event.start_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        busiest_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:3]

        # Event breakdown by source
        source_breakdown = {}
        for event in events:
            source_breakdown[event.source_id] = source_breakdown.get(event.source_id, 0) + 1

        # Get free slots
        conflict_detector = ConflictDetector()
        free_slots = conflict_detector.get_free_slots(start_of_day, end_of_day, 30, True)

        # Detect conflicts
        conflicts = conflict_detector.detect_conflicts(events)

        return {
            "success": True,
            "date": date,
            "total_events": len(events),
            "total_duration_minutes": int(total_duration),
            "busiest_hours": busiest_hours,
            "event_breakdown": source_breakdown,
            "free_slots_count": len(free_slots),
            "free_time_minutes": sum((s['end'] - s['start']).total_seconds() / 60 for s in free_slots),
            "conflict_count": len(conflicts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
