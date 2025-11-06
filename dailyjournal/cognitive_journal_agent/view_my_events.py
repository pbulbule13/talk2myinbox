"""
Quick script to view all events in the calendar system.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from nodes.calendar_storage import CalendarStorageManager


def view_events():
    """Display all events in the calendar."""

    storage = CalendarStorageManager()

    print("\n" + "="*70)
    print("YOUR CALENDAR EVENTS")
    print("="*70 + "\n")

    # Get all calendar sources
    sources = storage.get_calendar_sources()
    print(f"Calendar Sources: {len(sources)}")
    for source in sources:
        status = "Active" if source.is_active else "Inactive"
        print(f"  - {source.display_name} ({source.source_type}) - {status}")

    print("\n" + "-"*70 + "\n")

    # Get all events
    events = storage.get_events()

    if not events:
        print("No events found in calendar.")
        print("\nTo add events:")
        print("  1. Run: python add_event_example.py")
        print("  2. Or connect a calendar via the web UI")
        print("  3. Or use the API endpoints")
    else:
        print(f"Total Events: {len(events)}\n")

        # Sort events by start time
        events.sort(key=lambda e: e.start_time)

        # Group events by month
        current_month = None

        for event in events:
            event_month = event.start_time.strftime("%B %Y")

            # Print month header if changed
            if event_month != current_month:
                current_month = event_month
                print(f"\n{event_month}")
                print("-" * 70)

            # Format dates
            start_str = event.start_time.strftime("%a, %b %d at %I:%M %p")
            end_str = event.end_time.strftime("%I:%M %p")

            # Print event details
            print(f"\n[EVENT] {event.title}")
            print(f"  When:     {start_str} - {end_str}")
            print(f"  Where:    {event.location or 'No location'}")
            print(f"  Source:   {event.source_id}")
            print(f"  Status:   {event.status}")

            if event.has_conflict:
                print(f"  WARNING:  Has scheduling conflict!")

            if event.description:
                # Show first 150 characters of description
                desc = event.description.replace('\n', ' ')
                if len(desc) > 150:
                    desc = desc[:150] + "..."
                print(f"  Details:  {desc}")

    print("\n" + "="*70)
    print("\nTo view in web UI:")
    print("  1. Run: python main.py api")
    print("  2. Open: web/calendar.html")
    print("  3. Navigate to 'Unified Events' tab")
    print("\nTo view via API:")
    print("  curl http://localhost:8000/calendar/events")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        view_events()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
