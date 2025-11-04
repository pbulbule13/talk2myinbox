# 📅 Google Calendar OAuth Setup Guide

## Problem

The current Gmail OAuth credentials don't include the **Calendar API scope**, causing this error:
```
[Calendar Service] ERROR: Failed to initialize: ('invalid_scope: Bad Request', {'error': 'invalid_scope', 'error_description': 'Bad Request'})
```

**Current OAuth Scopes:**
- ✅ Gmail API (working)
- ❌ Calendar API (missing)

**Solution:** Re-authorize OAuth with Calendar scope included.

---

## Option 1: Re-use Gmail Credentials (Recommended - Easiest)

The simplest solution is to generate a **new refresh token** using the same Google Cloud Project but with Calendar scope added.

### Steps:

1. **Go to Google Cloud Console OAuth Consent Screen:**
   - https://console.cloud.google.com/apis/credentials
   - Select your existing project (the one with client ID `YOUR_CLIENT_ID.apps.googleusercontent.com`)

2. **Enable Calendar API:**
   - Go to: https://console.cloud.google.com/apis/library
   - Search for "Google Calendar API"
   - Click **ENABLE**

3. **Generate New OAuth Refresh Token with Calendar Scope:**

   Run this Python script to get a new refresh token:

   ```python
   # save as: get_calendar_token.py
   from google_auth_oauthlib.flow import InstalledAppFlow
   import json

   # Your existing OAuth credentials
   CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
   CLIENT_SECRET = "YOUR_CLIENT_SECRET"

   # IMPORTANT: Add Calendar scope
   SCOPES = [
       'https://www.googleapis.com/auth/gmail.modify',
       'https://www.googleapis.com/auth/calendar'  # ← Calendar scope
   ]

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

   # Run local server for OAuth
   credentials = flow.run_local_server(port=8080)

   # Print the refresh token
   print("\n" + "="*60)
   print("SUCCESS! Copy this refresh token to your .env file:")
   print("="*60)
   print(f"\nGMAIL_REFRESH_TOKEN={credentials.refresh_token}")
   print(f"CALENDAR_REFRESH_TOKEN={credentials.refresh_token}")
   print("\n" + "="*60)
   print("\nThis single token now has BOTH Gmail and Calendar access!")
   print("="*60)
   ```

4. **Run the Script:**
   ```bash
   cd backend
   .venv\Scripts\python.exe get_calendar_token.py
   ```

5. **Authorize in Browser:**
   - Browser will open automatically
   - Sign in with your Gmail account
   - **IMPORTANT:** Check BOTH permissions:
     - ✅ "See, edit, create and delete all of your Google Drive files"
     - ✅ "See, edit, share, and permanently delete all the calendars you can access using Google Calendar"
   - Click "Allow"

6. **Copy New Refresh Token:**
   - Script will print a new refresh token
   - Copy it to your `.env` file:

   ```env
   GMAIL_REFRESH_TOKEN=<NEW_TOKEN_HERE>
   CALENDAR_REFRESH_TOKEN=<NEW_TOKEN_HERE>
   ```

   **Note:** You can use the same token for both Gmail and Calendar since it has both scopes.

7. **Restart Server:**
   ```bash
   cd backend
   .venv\Scripts\python.exe -u server.py
   ```

---

## Option 2: Use Separate Calendar Credentials

If you prefer separate credentials for Calendar:

### Steps:

1. **Create New OAuth Client (Optional):**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Application type: **Desktop app**
   - Name: "Talk2MyInbox Calendar"
   - Click **CREATE**
   - Download credentials JSON

2. **Generate Calendar-Only Refresh Token:**

   ```python
   # save as: get_calendar_only_token.py
   from google_auth_oauthlib.flow import InstalledAppFlow

   SCOPES = ['https://www.googleapis.com/auth/calendar']

   flow = InstalledAppFlow.from_client_secrets_file(
       'credentials.json',  # Download from Google Cloud Console
       scopes=SCOPES
   )

   credentials = flow.run_local_server(port=8080)

   print(f"\nCALENDAR_CLIENT_ID={flow.client_config['installed']['client_id']}")
   print(f"CALENDAR_CLIENT_SECRET={flow.client_config['installed']['client_secret']}")
   print(f"CALENDAR_REFRESH_TOKEN={credentials.refresh_token}")
   ```

3. **Update .env:**
   ```env
   # Separate Calendar credentials
   CALENDAR_CLIENT_ID=<your_calendar_client_id>
   CALENDAR_CLIENT_SECRET=<your_calendar_secret>
   CALENDAR_REFRESH_TOKEN=<your_calendar_refresh_token>
   ```

---

## Option 3: Quick Test with OAuth Playground

For quick testing, use Google's OAuth Playground:

1. **Go to OAuth Playground:**
   - https://developers.google.com/oauthplayground/

2. **Configure:**
   - Click ⚙️ (gear icon) in top right
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Secret
   - Click "Close"

3. **Select Scopes:**
   - In left panel, expand "Google Calendar API v3"
   - Check: `https://www.googleapis.com/auth/calendar`
   - Click "Authorize APIs"

4. **Get Refresh Token:**
   - Click "Exchange authorization code for tokens"
   - Copy the **Refresh token** value
   - Add to `.env` file

---

## Verification

After updating `.env` with the new refresh token:

1. **Restart Server:**
   ```bash
   taskkill //F //IM python.exe //T
   cd backend
   .venv\Scripts\python.exe -u server.py
   ```

2. **Test Calendar API:**
   ```bash
   curl http://localhost:8000/voice-agent/calendar?timeframe=week
   ```

3. **Check Server Logs:**
   Look for:
   ```
   ✅ SUCCESS: Google Calendar credentials refreshed successfully
   [Calendar Service] SUCCESS: Google Calendar API service initialized
   ```

   Instead of:
   ```
   ❌ [Calendar Service] ERROR: Failed to initialize: ('invalid_scope: Bad Request'
   ```

4. **Test Email Summarization with Calendar:**
   ```bash
   curl http://localhost:8000/voice-agent/emails/summarize?max_results=20
   ```

   Should show:
   ```json
   {
     "interviews_meetings_count": <number>,
     "calendar_email_links": [...]
   }
   ```

---

## Current .env Configuration

Your current `.env` has:
```env
GMAIL_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=YOUR_CLIENT_SECRET
GMAIL_REFRESH_TOKEN=YOUR_REFRESH_TOKEN
```

**Missing:** Calendar-scoped refresh token.

**After re-authorization with Calendar scope, it should be:**
```env
GMAIL_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=YOUR_CLIENT_SECRET
GMAIL_REFRESH_TOKEN=<NEW_TOKEN_WITH_BOTH_GMAIL_AND_CALENDAR_SCOPES>
CALENDAR_REFRESH_TOKEN=<SAME_AS_GMAIL_REFRESH_TOKEN>

# Or use the same token since it has both scopes:
# GMAIL_REFRESH_TOKEN=1//06ABC...XYZ
# CALENDAR_REFRESH_TOKEN=1//06ABC...XYZ (same token)
```

---

## Common Issues

### Issue: "Access blocked: This app's request is invalid"
**Solution:** Make sure Calendar API is enabled in Google Cloud Console.

### Issue: "Invalid scope"
**Solution:** Ensure both scopes are in the authorization request:
- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/calendar`

### Issue: "Redirect URI mismatch"
**Solution:** Add `http://localhost:8080/` to authorized redirect URIs in Google Cloud Console.

---

## Why This Happened

OAuth refresh tokens are **scope-specific**. Your original Gmail refresh token was authorized only for Gmail API scope:
- `https://www.googleapis.com/auth/gmail.modify` ✅

When we try to use it for Calendar API:
- `https://www.googleapis.com/auth/calendar` ❌

Google rejects it with "invalid_scope" error.

**Solution:** Generate a new refresh token that includes **both scopes** in a single authorization.

---

## Quick Start (TL;DR)

**Fastest method:**

1. Install required package:
   ```bash
   cd backend
   .venv\Scripts\pip.exe install google-auth-oauthlib
   ```

2. Create `get_token.py`:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow

   CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
   CLIENT_SECRET = "YOUR_CLIENT_SECRET"
   SCOPES = [
       'https://www.googleapis.com/auth/gmail.modify',
       'https://www.googleapis.com/auth/calendar'
   ]

   flow = InstalledAppFlow.from_client_config(
       {"installed": {
           "client_id": CLIENT_ID,
           "client_secret": CLIENT_SECRET,
           "redirect_uris": ["http://localhost:8080/"],
           "auth_uri": "https://accounts.google.com/o/oauth2/auth",
           "token_uri": "https://oauth2.googleapis.com/token"
       }},
       scopes=SCOPES
   )

   creds = flow.run_local_server(port=8080)
   print(f"\nGMAIL_REFRESH_TOKEN={creds.refresh_token}")
   print(f"CALENDAR_REFRESH_TOKEN={creds.refresh_token}")
   ```

3. Run and authorize:
   ```bash
   .venv\Scripts\python.exe get_token.py
   ```

4. Update `.env` with new token

5. Restart server

✅ **Done!** Calendar will now work.

---

**Last Updated:** 2025-11-04
**Status:** Awaiting OAuth re-authorization with Calendar scope
