# Gmail API Setup Guide - Get Your Real Emails

**Current Status:** Application is using MOCK data (test emails)
**Goal:** Configure real Gmail API to load your actual inbox emails

---

## 📋 Prerequisites

- A Google Account (Gmail)
- Access to Google Cloud Console
- Python installed (already done via UV)

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "**Select a project**" at the top
3. Click "**NEW PROJECT**"
4. Name your project: `Talk2MyInbox` (or any name you prefer)
5. Click "**CREATE**"
6. Wait for the project to be created (takes a few seconds)

### Step 2: Enable Gmail API

1. In Google Cloud Console, make sure your new project is selected
2. Go to "**APIs & Services**" → "**Library**"
   - Or direct link: https://console.cloud.google.com/apis/library
3. Search for "**Gmail API**"
4. Click on "**Gmail API**"
5. Click "**ENABLE**"
6. Wait for it to enable (takes a few seconds)

### Step 3: Enable Google Calendar API (Optional, for calendar features)

1. Still in APIs & Services → Library
2. Search for "**Google Calendar API**"
3. Click on "**Google Calendar API**"
4. Click "**ENABLE**"

### Step 4: Configure OAuth Consent Screen

1. Go to "**APIs & Services**" → "**OAuth consent screen**"
   - Or direct link: https://console.cloud.google.com/apis/credentials/consent
2. Select "**External**" user type
3. Click "**CREATE**"

**Fill in the required fields:**
- **App name:** Talk2MyInbox
- **User support email:** [Your email]
- **Developer contact email:** [Your email]
- Click "**SAVE AND CONTINUE**"

**Scopes (Step 2):**
- Click "**ADD OR REMOVE SCOPES**"
- Search for and add:
  - `https://www.googleapis.com/auth/gmail.readonly` (Read Gmail)
  - `https://www.googleapis.com/auth/gmail.send` (Send emails)
  - `https://www.googleapis.com/auth/calendar` (Calendar access)
- Click "**UPDATE**"
- Click "**SAVE AND CONTINUE**"

**Test users (Step 3):**
- Click "**+ ADD USERS**"
- Add your Gmail address
- Click "**ADD**"
- Click "**SAVE AND CONTINUE**"

**Summary (Step 4):**
- Review and click "**BACK TO DASHBOARD**"

### Step 5: Create OAuth 2.0 Credentials

1. Go to "**APIs & Services**" → "**Credentials**"
   - Or direct link: https://console.cloud.google.com/apis/credentials
2. Click "**+ CREATE CREDENTIALS**" at the top
3. Select "**OAuth client ID**"

**Configure:**
- **Application type:** Desktop app
- **Name:** Talk2MyInbox Desktop
- Click "**CREATE**"

**Download Credentials:**
- A popup appears with your Client ID and Client Secret
- Click "**DOWNLOAD JSON**"
- **Save this file** - you'll need it in the next step

### Step 6: Get Your Refresh Token

Now we need to run a script to get your refresh token.

**Create a file:** `backend/get_gmail_token.py`

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import json

# Scopes for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

def get_gmail_refresh_token():
    """Get Gmail refresh token via OAuth flow"""

    # Path to your downloaded credentials JSON file
    credentials_file = input("Enter path to your credentials JSON file (downloaded from Google Cloud): ")

    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file,
        SCOPES
    )

    # This will open a browser for you to authorize
    creds = flow.run_local_server(port=0)

    # Print the credentials
    print("\n" + "="*60)
    print("SUCCESS! Here are your credentials:")
    print("="*60)
    print(f"\nClient ID: {creds.client_id}")
    print(f"Client Secret: {creds.client_secret}")
    print(f"Refresh Token: {creds.refresh_token}")
    print("\n" + "="*60)
    print("Copy these values to your backend/.env file")
    print("="*60)

    # Save to a file for reference
    with open('gmail_credentials_output.txt', 'w') as f:
        f.write(f"GMAIL_CLIENT_ID={creds.client_id}\n")
        f.write(f"GMAIL_CLIENT_SECRET={creds.client_secret}\n")
        f.write(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}\n")
        f.write(f"\nCALENDAR_CLIENT_ID={creds.client_id}\n")
        f.write(f"CALENDAR_CLIENT_SECRET={creds.client_secret}\n")
        f.write(f"CALENDAR_REFRESH_TOKEN={creds.refresh_token}\n")

    print("\nCredentials also saved to: gmail_credentials_output.txt")

if __name__ == "__main__":
    get_gmail_refresh_token()
```

**Run the script:**

```bash
cd backend
.venv\Scripts\python.exe get_gmail_token.py
```

**What happens:**
1. Script asks for path to your downloaded JSON file
2. Opens a browser window for Google authorization
3. You'll see a warning "Google hasn't verified this app" - click "**Advanced**" → "**Go to Talk2MyInbox (unsafe)**"
4. Grant permissions for Gmail and Calendar access
5. Browser shows "The authentication flow has completed"
6. Terminal displays your credentials
7. Credentials are saved to `gmail_credentials_output.txt`

### Step 7: Update .env File

Open `backend/.env` and update these values with the ones from the script:

```env
# ========================================
# Gmail API Configuration
# ========================================
GMAIL_CLIENT_ID=your_actual_client_id_from_script
GMAIL_CLIENT_SECRET=your_actual_client_secret_from_script
GMAIL_REFRESH_TOKEN=your_actual_refresh_token_from_script

# ========================================
# Google Calendar API Configuration
# ========================================
CALENDAR_CLIENT_ID=your_actual_client_id_from_script
CALENDAR_CLIENT_SECRET=your_actual_client_secret_from_script
CALENDAR_REFRESH_TOKEN=your_actual_refresh_token_from_script
```

**💡 Note:** Calendar uses the same credentials as Gmail.

### Step 8: Restart the Application

```bash
start.bat
```

The application will now:
- ✅ Use your REAL Gmail credentials
- ✅ Load your ACTUAL inbox emails
- ✅ Access your Google Calendar events

---

## ✅ Verification

After restarting, check the server logs. You should see:

```
SUCCESS: Gmail credentials refreshed successfully
SUCCESS: Gmail API service initialized
```

Instead of:

```
ERROR: The OAuth client was not found
WARNING: Using mock data instead
```

---

## 🔍 Troubleshooting

### Error: "The OAuth client was not found"
**Cause:** Client ID or Client Secret is incorrect
**Solution:** Double-check you copied the correct values from the script output

### Error: "invalid_grant: Token has been expired or revoked"
**Cause:** Refresh token expired (happens if not used for 6 months)
**Solution:** Run `get_gmail_token.py` again to get a new refresh token

### Error: "Access blocked: This app's request is invalid"
**Cause:** Scopes mismatch or OAuth consent screen not configured
**Solution:**
1. Go back to OAuth consent screen
2. Make sure you added your Gmail address as a test user
3. Make sure Gmail and Calendar scopes are added

### Error: "Insufficient Permission"
**Cause:** Missing required scopes
**Solution:**
1. Delete the token
2. Run `get_gmail_token.py` again
3. Make sure to grant all permissions

### Browser doesn't open during get_gmail_token.py
**Solution:** The script will print a URL - copy and paste it into your browser manually

---

## 📊 What You'll See After Setup

Instead of the 3 mock emails (john.doe@partner.com, etc.), you'll see:

- ✉️ **Your actual Gmail inbox emails** (last 30 emails)
- 📅 **Your actual Google Calendar events**
- 🔄 **Real-time updates** every 60 seconds
- 📧 **Ability to draft and send replies**

---

## 🌐 Euron API Setup (Optional - For AI Features)

To enable AI-powered features (inbox summaries, smart replies, etc.):

**Update .env:**
```env
EURON_API_KEY=your_euron_api_key
EURON_API_BASE=https://api.euron.one/api/v1/euri
EURON_MODEL=gpt-4.1-nano
```

**Where to get Euron API Key:**
Contact Euron support or check your Euron dashboard.

---

## 📝 Summary

**Before Setup:** Mock data (3 test emails)
**After Setup:** Real Gmail emails from your inbox

**Steps:**
1. ✅ Create Google Cloud Project
2. ✅ Enable Gmail API
3. ✅ Configure OAuth consent screen
4. ✅ Create OAuth credentials
5. ✅ Run `get_gmail_token.py`
6. ✅ Update `.env` file
7. ✅ Restart application with `start.bat`

**Estimated Time:** 15-20 minutes

---

## 🚨 Security Notes

- **NEVER commit `.env` file to Git** - It contains sensitive credentials
- **Keep your credentials safe** - Don't share them
- **Refresh tokens don't expire** unless:
  - Not used for 6 months
  - User revokes access
  - Password changed

---

## 💡 Quick Start (If You Already Have Credentials)

If you already have Gmail OAuth credentials from another project:

1. Edit `backend/.env`
2. Add your Client ID, Client Secret, and Refresh Token
3. Run `start.bat`
4. Done!

---

**Need Help?** Check the console logs or send me the error messages!
