"""
Google OAuth Token Generator - Gmail + Calendar Scopes
Generates a refresh token with BOTH Gmail and Calendar API access.

This script will:
1. Open your browser for Google OAuth authorization
2. Request access to Gmail AND Calendar APIs
3. Generate a refresh token you can use in .env file
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import sys

# Your existing OAuth credentials from .env
CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# IMPORTANT: Both Gmail and Calendar scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',  # Gmail access
    'https://www.googleapis.com/auth/calendar'        # Calendar access
]

print("=" * 70)
print("Google OAuth Token Generator - Gmail + Calendar")
print("=" * 70)
print("\nThis script will:")
print("  1. Open your browser for Google OAuth authorization")
print("  2. Request access to Gmail AND Calendar APIs")
print("  3. Generate a refresh token for your .env file")
print("\n" + "=" * 70)
print("IMPORTANT: Make sure you have enabled Calendar API in Google Cloud Console!")
print("  → https://console.cloud.google.com/apis/library")
print("  → Search for 'Google Calendar API' and click ENABLE")
print("=" * 70)

input("\nPress ENTER to continue...")

try:
    # Create OAuth flow
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": ["http://localhost:8080/"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES
    )

    print("\n[INFO] Starting OAuth flow...")
    print("[INFO] Your browser will open automatically in 3 seconds...")
    print("[INFO] Please sign in and authorize BOTH Gmail and Calendar access.\n")

    # Run local server for OAuth (browser will open automatically)
    credentials = flow.run_local_server(port=8080)

    # Success!
    print("\n" + "=" * 70)
    print("✅ SUCCESS! OAuth token generated successfully!")
    print("=" * 70)
    print("\n📋 Copy these lines to your backend/.env file:")
    print("=" * 70)
    print(f"\nGMAIL_CLIENT_ID={CLIENT_ID}")
    print(f"GMAIL_CLIENT_SECRET={CLIENT_SECRET}")
    print(f"GMAIL_REFRESH_TOKEN={credentials.refresh_token}")
    print(f"\n# Use the same token for Calendar (it has both scopes)")
    print(f"CALENDAR_REFRESH_TOKEN={credentials.refresh_token}")
    print("\n" + "=" * 70)
    print("\n✅ This single token now has BOTH Gmail and Calendar access!")
    print("\n📝 Next steps:")
    print("  1. Copy the refresh token above to your .env file")
    print("  2. Restart your server: cd backend && .venv\\Scripts\\python.exe server.py")
    print("  3. Test: curl http://localhost:8000/voice-agent/calendar?timeframe=week")
    print("\n" + "=" * 70)

except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR: Failed to generate OAuth token")
    print("=" * 70)
    print(f"\nError: {e}")
    print("\n🔍 Common fixes:")
    print("  1. Make sure Calendar API is enabled in Google Cloud Console")
    print("  2. Check that http://localhost:8080/ is in authorized redirect URIs")
    print("  3. Verify your Client ID and Secret are correct")
    print("\n📚 See CALENDAR_OAUTH_SETUP.md for detailed troubleshooting")
    print("=" * 70)
    sys.exit(1)
