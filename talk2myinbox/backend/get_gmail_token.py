"""
Gmail OAuth Token Generator
Run this script to get your Gmail API credentials (Client ID, Client Secret, Refresh Token)
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import sys
import os

# Scopes for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_gmail_refresh_token():
    """Get Gmail refresh token via OAuth flow"""

    print("="*70)
    print(" Gmail API Token Generator for Talk2MyInbox")
    print("="*70)
    print()
    print("This script will help you get the credentials needed to access Gmail.")
    print()
    print("PREREQUISITES:")
    print("1. You've created a Google Cloud Project")
    print("2. You've enabled Gmail API and Calendar API")
    print("3. You've created OAuth 2.0 credentials (Desktop app)")
    print("4. You've downloaded the credentials JSON file")
    print()
    print("If you haven't done these steps, see GMAIL_SETUP_GUIDE.md")
    print("="*70)
    print()

    # Get credentials file path
    credentials_file = input("Enter the full path to your credentials JSON file: ").strip()
    credentials_file = credentials_file.replace('"', '').replace("'", "")  # Remove quotes if pasted with them

    if not os.path.exists(credentials_file):
        print(f"\n❌ ERROR: File not found: {credentials_file}")
        print("\nPlease check the path and try again.")
        sys.exit(1)

    print(f"\n✓ Found credentials file: {credentials_file}")
    print("\nStarting OAuth authorization flow...")
    print("A browser window will open. Please:")
    print("  1. Select your Google account")
    print("  2. Click 'Advanced' if you see a warning")
    print("  3. Click 'Go to Talk2MyInbox (unsafe)'")
    print("  4. Grant all requested permissions")
    print()

    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file,
            SCOPES
        )

        # This will open a browser for authorization
        print("Opening browser for authorization...")
        creds = flow.run_local_server(
            port=0,
            success_message='Authorization successful! You can close this window and return to the terminal.'
        )

        print("\n" + "="*70)
        print(" ✅ SUCCESS! Authorization Complete")
        print("="*70)
        print("\nYour Gmail API credentials:")
        print("-"*70)
        print(f"\nGMAIL_CLIENT_ID={creds.client_id}")
        print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
        print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
        print(f"\nCALENDAR_CLIENT_ID={creds.client_id}")
        print(f"CALENDAR_CLIENT_SECRET={creds.client_secret}")
        print(f"CALENDAR_REFRESH_TOKEN={creds.refresh_token}")
        print()
        print("-"*70)

        # Save to a file
        output_file = 'gmail_credentials_output.txt'
        with open(output_file, 'w') as f:
            f.write("# Gmail and Calendar API Credentials for Talk2MyInbox\n")
            f.write("# Copy these to your backend/.env file\n")
            f.write("#\n\n")
            f.write(f"GMAIL_CLIENT_ID={creds.client_id}\n")
            f.write(f"GMAIL_CLIENT_SECRET={creds.client_secret}\n")
            f.write(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}\n")
            f.write(f"\n")
            f.write(f"CALENDAR_CLIENT_ID={creds.client_id}\n")
            f.write(f"CALENDAR_CLIENT_SECRET={creds.client_secret}\n")
            f.write(f"CALENDAR_REFRESH_TOKEN={creds.refresh_token}\n")

        print(f"\n✓ Credentials saved to: {output_file}")
        print()
        print("="*70)
        print(" Next Steps:")
        print("="*70)
        print("1. Open backend/.env file")
        print("2. Replace the placeholder values with the credentials above")
        print("3. Save the .env file")
        print("4. Run start.bat to restart the application")
        print()
        print("The application will then load your REAL Gmail emails!")
        print("="*70)

    except Exception as e:
        print("\n" + "="*70)
        print(" ❌ ERROR during authorization")
        print("="*70)
        print(f"\nError: {e}")
        print()
        print("Common issues:")
        print("1. Wrong credentials file - Make sure you downloaded OAuth 2.0 credentials (Desktop app)")
        print("2. Scopes not configured - Add Gmail and Calendar scopes in OAuth consent screen")
        print("3. Test user not added - Add your email as a test user in OAuth consent screen")
        print()
        print("See GMAIL_SETUP_GUIDE.md for detailed instructions.")
        print("="*70)
        sys.exit(1)

if __name__ == "__main__":
    try:
        get_gmail_refresh_token()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
