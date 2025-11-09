"""
Summary Routes: Calendar summaries, journal summaries, and combined views.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/api/summaries", tags=["summaries"])


class CalendarSummaryResponse(BaseModel):
    """Response model for calendar summary."""
    date: str
    total_events: int
    events: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    free_time: List[Dict[str, Any]]
    summary_text: Optional[str] = None


class JournalSummaryResponse(BaseModel):
    """Response model for journal summary."""
    date: str
    total_entries: int
    entries: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    tags: List[str]
    summary_text: Optional[str] = None


class OverallSummaryResponse(BaseModel):
    """Response model for overall daily summary (calendar + journal + actions)."""
    date: str
    calendar_summary: CalendarSummaryResponse
    journal_summary: JournalSummaryResponse
    combined_summary: str
    highlights: List[str]
    next_actions: List[str]


@router.get("/calendar/today", response_model=CalendarSummaryResponse)
async def get_today_calendar_summary():
    """Get calendar summary for today."""
    return await get_calendar_summary_for_date(datetime.now())


@router.get("/calendar/{date}", response_model=CalendarSummaryResponse)
async def get_calendar_summary(date: str):
    """
    Get calendar summary for a specific date.

    Args:
        date: Date in YYYY-MM-DD format
    """
    try:
        target_date = datetime.fromisoformat(date)
        return await get_calendar_summary_for_date(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


@router.get("/journal/today", response_model=JournalSummaryResponse)
async def get_today_journal_summary():
    """Get journal summary for today."""
    return await get_journal_summary_for_date(datetime.now())


@router.get("/journal/{date}", response_model=JournalSummaryResponse)
async def get_journal_summary(date: str):
    """
    Get journal summary for a specific date.

    Args:
        date: Date in YYYY-MM-DD format
    """
    try:
        target_date = datetime.fromisoformat(date)
        return await get_journal_summary_for_date(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


@router.get("/overall/today", response_model=OverallSummaryResponse)
async def get_today_overall_summary():
    """Get overall summary (calendar + journal + actions) for today."""
    return await get_overall_summary_for_date(datetime.now())


@router.get("/overall/{date}", response_model=OverallSummaryResponse)
async def get_overall_summary(date: str):
    """
    Get overall summary for a specific date.

    Args:
        date: Date in YYYY-MM-DD format
    """
    try:
        target_date = datetime.fromisoformat(date)
        return await get_overall_summary_for_date(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


@router.get("/week")
async def get_week_summary(
    start_date: Optional[str] = None
):
    """
    Get summary for the current or specified week.

    Args:
        start_date: Optional start date (YYYY-MM-DD). Defaults to current week start.
    """
    try:
        if start_date:
            week_start = datetime.fromisoformat(start_date)
        else:
            # Get start of current week (Monday)
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())

        week_end = week_start + timedelta(days=7)

        # Get all entries and events for the week
        from nodes.storage import StorageManager
        from nodes.calendar_storage import CalendarStorageManager

        storage = StorageManager()
        cal_storage = CalendarStorageManager()

        entries = storage.get_entries()
        events = cal_storage.get_events(week_start, week_end)

        # Filter entries for the week
        week_entries = [
            e for e in entries
            if week_start.date() <= e.timestamp.date() < week_end.date()
        ]

        # Group by day
        daily_summaries = []
        current_date = week_start

        while current_date < week_end:
            day_entries = [e for e in week_entries if e.timestamp.date() == current_date.date()]
            day_events = [e for e in events if e.start_time.date() == current_date.date()]

            daily_summaries.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": current_date.strftime("%A"),
                "entries_count": len(day_entries),
                "events_count": len(day_events),
                "has_activity": len(day_entries) > 0 or len(day_events) > 0
            })

            current_date += timedelta(days=1)

        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total_entries": len(week_entries),
            "total_events": len(events),
            "daily_summaries": daily_summaries
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

async def get_calendar_summary_for_date(date: datetime) -> CalendarSummaryResponse:
    """Generate calendar summary for a specific date."""
    try:
        from nodes.calendar_storage import CalendarStorageManager
        from services.calendar_ocr import ConflictDetector
        from services.gemini_calendar import CalendarAnalyzer

        cal_storage = CalendarStorageManager()
        conflict_detector = ConflictDetector()

        # Get events for the day
        day_start = date.replace(hour=0, minute=0, second=0)
        day_end = date.replace(hour=23, minute=59, second=59)

        events = cal_storage.get_events(day_start, day_end)

        # Detect conflicts
        conflicts = conflict_detector.detect_conflicts(events, day_start, day_end)

        # Get free time
        free_slots = conflict_detector.get_free_slots(day_start, day_end, min_duration_minutes=30)

        # Generate AI summary
        summary_text = None
        try:
            analyzer = CalendarAnalyzer()
            summary_text = analyzer.summarize_day(events, date)
        except:
            pass

        return CalendarSummaryResponse(
            date=date.strftime("%Y-%m-%d"),
            total_events=len(events),
            events=[e.model_dump() for e in events],
            conflicts=[
                {
                    "event1": e1.title,
                    "event2": e2.title,
                    "type": conflict_type,
                    "time": e1.start_time.strftime("%I:%M %p")
                }
                for e1, e2, conflict_type in conflicts
            ],
            free_time=[
                {
                    "start": slot['start'].strftime("%I:%M %p"),
                    "end": slot['end'].strftime("%I:%M %p"),
                    "duration_minutes": slot.get('duration_minutes', 0)
                }
                for slot in free_slots
            ],
            summary_text=summary_text
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate calendar summary: {str(e)}")


async def get_journal_summary_for_date(date: datetime) -> JournalSummaryResponse:
    """Generate journal summary for a specific date."""
    try:
        from nodes.storage import StorageManager

        storage = StorageManager()

        # Get all entries
        all_entries = storage.get_entries()

        # Filter for the specific date
        day_entries = [
            e for e in all_entries
            if e.timestamp.date() == date.date()
        ]

        # Get action items for the day
        all_actions = storage.get_pending_actions()
        day_actions = [
            a for a in all_actions
            if hasattr(a, 'timestamp') and a.timestamp.date() == date.date()
        ]

        # Collect all tags
        all_tags = set()
        for entry in day_entries:
            if hasattr(entry, 'contextual_tags') and entry.contextual_tags:
                all_tags.update(entry.contextual_tags)

        # Generate summary
        summary_text = f"You made {len(day_entries)} journal entries today"
        if len(day_actions) > 0:
            summary_text += f" with {len(day_actions)} action items"

        return JournalSummaryResponse(
            date=date.strftime("%Y-%m-%d"),
            total_entries=len(day_entries),
            entries=[
                {
                    "timestamp": e.timestamp.isoformat(),
                    "content": e.raw_content[:200] + "..." if len(e.raw_content) > 200 else e.raw_content,
                    "input_type": e.input_type,
                    "tags": getattr(e, 'contextual_tags', [])
                }
                for e in day_entries
            ],
            action_items=[
                {
                    "description": a.description if hasattr(a, 'description') else str(a),
                    "priority": getattr(a, 'priority_level', 'P2')
                }
                for a in day_actions
            ],
            tags=list(all_tags),
            summary_text=summary_text
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate journal summary: {str(e)}")


async def get_overall_summary_for_date(date: datetime) -> OverallSummaryResponse:
    """Generate overall summary combining calendar + journal + actions."""
    try:
        # Get individual summaries
        calendar_summary = await get_calendar_summary_for_date(date)
        journal_summary = await get_journal_summary_for_date(date)

        # Generate combined summary
        combined_summary = f"""**Daily Overview for {date.strftime('%A, %B %d, %Y')}**

📅 **Calendar:** {calendar_summary.total_events} events scheduled
📝 **Journal:** {journal_summary.total_entries} entries recorded
✅ **Actions:** {len(journal_summary.action_items)} pending items

"""

        # Add calendar highlights
        if calendar_summary.total_events > 0:
            combined_summary += "\n**Today's Schedule:**\n"
            for event in calendar_summary.events[:3]:
                time_str = datetime.fromisoformat(event['start_time']).strftime('%I:%M %p')
                combined_summary += f"- {time_str}: {event['title']}\n"

        # Add conflict warnings
        if calendar_summary.conflicts:
            combined_summary += f"\n⚠️ **{len(calendar_summary.conflicts)} scheduling conflicts detected**\n"

        # Extract highlights
        highlights = []

        if calendar_summary.total_events > 0:
            highlights.append(f"{calendar_summary.total_events} calendar events")

        if journal_summary.total_entries > 0:
            highlights.append(f"{journal_summary.total_entries} journal entries")

        if journal_summary.tags:
            highlights.append(f"Tags: {', '.join(list(journal_summary.tags)[:5])}")

        # Extract next actions
        next_actions = [
            item['description']
            for item in journal_summary.action_items[:5]
        ]

        return OverallSummaryResponse(
            date=date.strftime("%Y-%m-%d"),
            calendar_summary=calendar_summary,
            journal_summary=journal_summary,
            combined_summary=combined_summary,
            highlights=highlights,
            next_actions=next_actions
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate overall summary: {str(e)}")
