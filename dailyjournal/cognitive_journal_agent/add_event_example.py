"""
Example script to add the Data Science Salon event to the calendar system.
"""

import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_models.pydantic_schemas import CalendarSource, UnifiedEvent
from nodes.calendar_storage import CalendarStorageManager


def add_data_science_salon_event():
    """Add the Data Science Salon SF event to the calendar."""

    # Initialize storage
    storage = CalendarStorageManager()

    # Create a calendar source for manual events if it doesn't exist
    print("Creating calendar source...")
    source = CalendarSource(
        source_id="manual_events",
        source_type="manual",
        display_name="My Events",
        is_active=True,
        color="#FF6B6B",
        requires_oauth=False,
        sync_frequency_minutes=0,  # Manual events don't need syncing
        sync_window_days=365
    )

    storage.save_calendar_source(source)
    print(f"[OK] Calendar source created: {source.display_name}")

    # Create the event
    print("\nAdding event: Data Science Salon SF...")
    event = UnifiedEvent(
        event_id=f"manual_events_{uuid.uuid4().hex[:12]}",
        source_id="manual_events",
        title="Data Science Salon SF: GenAI and Intelligent Agents",
        description=(
            "Data Science Salon focused on GenAI and Intelligent Agents.\n\n"
            "Topics:\n"
            "- Generative AI applications\n"
            "- Intelligent agents architecture\n"
            "- Real-world implementations\n\n"
            "Status: [REGISTERED] (event at capacity)\n"
            "Email received: November 4, 2025"
        ),
        location="AWS Builder Loft, San Francisco, CA",
        start_time=datetime(2025, 11, 6, 9, 0, 0),  # November 6, 2025, 9:00 AM
        end_time=datetime(2025, 11, 6, 17, 0, 0),    # Estimated end time: 5:00 PM
        all_day=False,
        timezone="America/Los_Angeles",  # PST
        attendees=[],
        organizer="Data Science Salon",
        is_recurring=False,
        status="confirmed",
        response_status="accepted",
        original_event_id=f"dss_sf_{uuid.uuid4().hex[:8]}"
    )

    # Save the event
    storage.save_events([event])
    print(f"[OK] Event added: {event.title}")
    print(f"  Date: {event.start_time.strftime('%B %d, %Y at %I:%M %p %Z')}")
    print(f"  Location: {event.location}")
    print(f"  Event ID: {event.event_id}")

    # Verify by retrieving all events
    print("\n" + "="*60)
    print("Verifying - All events in calendar:")
    print("="*60)

    all_events = storage.get_events()

    if all_events:
        for evt in all_events:
            print(f"\n[EVENT] {evt.title}")
            print(f"   {evt.start_time.strftime('%B %d, %Y at %I:%M %p')} - {evt.end_time.strftime('%I:%M %p')}")
            print(f"   Location: {evt.location}")
            if evt.description:
                print(f"   Description: {evt.description[:100]}...")
    else:
        print("No events found.")

    print("\n" + "="*60)
    print("[OK] Event successfully added to calendar!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the server: python main.py api")
    print("2. Open the calendar UI: web/calendar.html")
    print("3. View your event in the 'Unified Events' tab")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Adding Data Science Salon SF Event to Calendar")
    print("="*60 + "\n")

    try:
        add_data_science_salon_event()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
