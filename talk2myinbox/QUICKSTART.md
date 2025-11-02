# Quick Start Guide

Get the Communications App running in 5 minutes!

## Step 1: Setup Environment

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` and add **at least one** LLM API key:
- `OPENAI_API_KEY=sk-...` OR
- `ANTHROPIC_API_KEY=sk-ant-...` OR
- `GOOGLE_API_KEY=...`

For testing without Gmail, set:
```
EMAIL_MOCK_MODE=true
CALENDAR_MOCK_MODE=true
```

## Step 2: Run the App

### Windows:
```bash
start.bat
```

### Mac/Linux:
```bash
chmod +x start.sh
./start.sh
```

### Manual:
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
cd backend
python server.py
```

## Step 3: Open Browser

Navigate to: **http://localhost:8000**

## That's It!

The app will run in **demo mode** with sample data if Gmail is not configured.

## Optional: Real Gmail Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Gmail API
3. Create OAuth credentials (Desktop app)
4. Download as `config/gmail_credentials.json`
5. Set in `.env`:
   ```
   EMAIL_MOCK_MODE=false
   GMAIL_CREDENTIALS_PATH=./config/gmail_credentials.json
   ```
6. Restart app and authorize when prompted

## Troubleshooting

**Port already in use?**
```bash
# In .env, change:
PORT=8001
```

**Import errors?**
```bash
pip install --upgrade -r requirements.txt
```

**Gmail not working?**
- Use mock mode: `EMAIL_MOCK_MODE=true`
- Check credentials file path
- Verify OAuth scopes

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check API docs at http://localhost:8000/docs
- Explore the voice agent features
- Customize the UI in `frontend/index.html`

## Need Help?

1. Check server logs in terminal
2. Visit http://localhost:8000/health
3. Review API docs at http://localhost:8000/docs
4. Check `.env` configuration
