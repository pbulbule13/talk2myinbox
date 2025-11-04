# 🚀 Quick Start: Enable Google Calendar

## TL;DR - Fastest Method

Run this batch file, it will do everything for you:

```bash
setup_calendar_oauth.bat
```

That's it! The script will:
1. Install required package
2. Guide you through enabling Calendar API
3. Open your browser for OAuth authorization
4. Generate the new token for you

---

## Manual Steps (If You Prefer)

### Step 1: Enable Calendar API in Google Cloud Console

1. Go to: **https://console.cloud.google.com/apis/library**
2. Search for: **"Google Calendar API"**
3. Click: **ENABLE**

### Step 2: Generate New OAuth Token

```bash
cd backend
.venv\Scripts\pip.exe install google-auth-oauthlib
.venv\Scripts\python.exe get_calendar_token.py
```

### Step 3: Authorize in Browser

- Browser will open automatically
- Sign in with your Gmail account
- **Check BOTH permissions:**
  - ✅ Gmail access
  - ✅ Calendar access
- Click **"Allow"**

### Step 4: Update .env

Copy the refresh token from the script output and update your `.env` file:

```env
GMAIL_REFRESH_TOKEN=<NEW_TOKEN_HERE>
CALENDAR_REFRESH_TOKEN=<NEW_TOKEN_HERE>
```

**Note:** Use the same token for both - it has both scopes!

### Step 5: Restart Server

```bash
taskkill //F //IM python.exe //T
cd backend
.venv\Scripts\python.exe -u server.py
```

### Step 6: Verify Calendar Works

```bash
curl http://localhost:8000/voice-agent/calendar?timeframe=week
```

You should see your actual calendar events instead of mock data.

---

## What Changed?

**Before:**
```
[Calendar Service] ERROR: Failed to initialize: ('invalid_scope: Bad Request'
Calendar error: Can't instantiate abstract class GoogleCalendarAdapter
```

**After:**
```
SUCCESS: Google Calendar credentials refreshed successfully
[Calendar Service] SUCCESS: Google Calendar API service initialized
[Email Summarization] Found 3 meetings/interviews this week
```

---

## Testing Email Summarization with Calendar

Once Calendar is working, test the enhanced summarization:

```bash
curl http://localhost:8000/voice-agent/emails/summarize?max_results=20
```

You'll now see:
```json
{
  "interviews_meetings_count": 3,
  "calendar_email_links": [
    {
      "event_title": "Interview with Company X",
      "related_email_subject": "Interview Confirmation",
      "sender": "recruiter@company.com"
    }
  ]
}
```

---

## Why Is This Needed?

OAuth tokens are **scope-specific**. Your current token only has Gmail access:
- ✅ `https://www.googleapis.com/auth/gmail.modify`

To use Calendar, we need to add:
- ✅ `https://www.googleapis.com/auth/calendar`

By re-authorizing with **both scopes**, you get a new token that works for both APIs.

---

## Troubleshooting

**Error: "Access blocked: This app's request is invalid"**
- Solution: Enable Calendar API in Google Cloud Console (Step 1 above)

**Error: "Redirect URI mismatch"**
- Solution: Add `http://localhost:8080/` to authorized redirect URIs in Google Cloud Console

**Error: "Invalid scope"**
- Solution: Make sure both Gmail and Calendar scopes are in the authorization request

**Need More Help?**
- See detailed guide: `CALENDAR_OAUTH_SETUP.md`
- Server logs: Check backend console for error messages

---

**Last Updated:** 2025-11-04
**Status:** Ready to enable Calendar integration
