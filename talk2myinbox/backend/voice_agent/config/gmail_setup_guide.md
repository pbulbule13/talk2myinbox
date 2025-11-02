# Gmail API Setup Guide

This guide will help you set up Gmail API credentials for the Voice Agent system.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- About 10 minutes

## Step-by-Step Setup

### 1. Go to Google Cloud Console

Visit: https://console.cloud.google.com/

### 2. Create a New Project (or select existing)

1. Click on the project dropdown at the top
2. Click "NEW PROJECT"
3. Name it: "CEO Dashboard Voice Agent"
4. Click "CREATE"

### 3. Enable Gmail API

1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click **ENABLE**

### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: "Voice Agent"
   - User support email: Your email
   - Developer contact: Your email
   - Click **SAVE AND CONTINUE** through all steps
4. Back to Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Voice Agent Desktop"
   - Click **CREATE**

### 5. Download Credentials

1. You'll see a dialog with your Client ID and Client Secret
2. Click **DOWNLOAD JSON**
3. Save the file as `gmail_credentials.json`

### 6. Place Credentials in Config Directory

```bash
# Create config directory if it doesn't exist
mkdir -p config

# Move the downloaded file
mv ~/Downloads/client_secret_*.json config/gmail_credentials.json
```

### 7. First-Time Authorization

When you first run the voice agent, it will:

1. Open a browser window
2. Ask you to sign in with Google
3. Show permissions it needs:
   - Read emails
   - Send emails
   - Modify emails (mark as read, archive)
4. Click **Allow**

The system will save a token file (`gmail_token.pickle`) so you don't need to authorize again.

## File Structure

After setup, you should have:

```
config/
├── gmail_credentials.json    # OAuth 2.0 credentials (keep secret!)
└── gmail_token.pickle         # Auto-generated token (keep secret!)
```

## Security Notes

⚠️ **Important:**

- **Never commit** `gmail_credentials.json` or `gmail_token.pickle` to git
- These files contain sensitive authentication data
- Keep them secure and private
- Add them to `.gitignore`

## Scopes & Permissions

The Voice Agent requests these Gmail scopes:

- `gmail.readonly` - Read your emails
- `gmail.send` - Send emails on your behalf
- `gmail.modify` - Mark as read, archive, add labels
- `gmail.compose` - Create draft emails

## Troubleshooting

### "Credentials file not found"

Make sure `gmail_credentials.json` is in the `config/` directory.

### "Access blocked: This app isn't verified"

Click **Advanced** → **Go to Voice Agent (unsafe)**

This warning appears because the app is in development. You can safely proceed since it's your own app.

### "Invalid grant" error

Your token has expired. Delete `config/gmail_token.pickle` and re-authorize.

### Still having issues?

Check the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) for more help.

## Testing Your Setup

After setup, test the Gmail integration:

```bash
python -c "
from voice_agent.adapters.email.gmail_adapter import GmailAdapter
import asyncio

async def test():
    adapter = GmailAdapter()
    threads = await adapter.fetch_threads(max_results=5)
    print(f'✅ Found {len(threads)} email threads')

asyncio.run(test())
"
```

If you see "Found X email threads", you're all set! 🎉
