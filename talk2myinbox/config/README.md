# Configuration Directory

This directory stores credentials and tokens for Gmail and Google Calendar integration.

## Required Files (for real Gmail/Calendar access)

### 1. `gmail_credentials.json`
OAuth 2.0 credentials from Google Cloud Console.

**How to get:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create/select a project
3. Enable Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Select "Desktop app" as application type
6. Download JSON and save here as `gmail_credentials.json`

### 2. `gmail_token.json` (auto-generated)
OAuth access token - created automatically on first run after authentication.

**Don't create manually** - this file is generated when you:
1. Run the app with valid `gmail_credentials.json`
2. Complete OAuth flow in browser
3. App saves token here for future use

### 3. `calendar_credentials.json` (optional)
Similar to Gmail credentials but for Google Calendar API.

**How to get:**
1. Same project in Google Cloud Console
2. Enable Google Calendar API
3. Use same OAuth credentials or create new ones
4. Download and save here

### 4. `calendar_token.json` (auto-generated)
Calendar OAuth token - auto-generated on first use.

## Security Notes

⚠️ **IMPORTANT:**
- Never commit these files to version control
- These files contain sensitive authentication data
- Keep them secure and private
- Files are already in `.gitignore`

## File Permissions

Ensure proper permissions (Unix/Linux/Mac):
```bash
chmod 600 *.json
```

## Mock Mode (No Credentials Needed)

If you don't have Gmail/Calendar credentials, you can run in **mock mode**:

In `.env`:
```
EMAIL_MOCK_MODE=true
CALENDAR_MOCK_MODE=true
```

The app will generate sample data for testing.

## Troubleshooting

### Invalid Credentials Error
- Verify JSON file is valid
- Check API is enabled in Cloud Console
- Ensure OAuth scopes include Gmail/Calendar

### Token Expired
- Delete `gmail_token.json` or `calendar_token.json`
- App will re-authenticate on next run

### Permission Denied
- Check file permissions
- Ensure app can read/write to this directory

### OAuth Flow Not Working
- Verify redirect URI in Cloud Console: `http://localhost`
- Check credentials file path in `.env`
- Try incognito/private browser window

## Example Structure

```
config/
├── README.md                    (this file)
├── gmail_credentials.json       (your OAuth credentials)
├── gmail_token.json            (auto-generated)
├── calendar_credentials.json   (optional)
└── calendar_token.json        (auto-generated)
```

## OAuth Scopes Required

For Gmail:
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.modify`

For Calendar:
- `https://www.googleapis.com/auth/calendar.readonly`
- `https://www.googleapis.com/auth/calendar.events`

These scopes are configured in the application code.
