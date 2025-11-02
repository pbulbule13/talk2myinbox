# Email Provider Configuration Guide

The Voice Agent system supports multiple email providers through a pluggable adapter architecture.

## Supported Providers

### ✅ Gmail API (Fully Implemented)

**Best for:** Personal Gmail accounts, Google Workspace

**Setup:**

1. Follow the [Gmail Setup Guide](./gmail_setup_guide.md)
2. Configure in `.env`:
   ```env
   VOICE_AGENT_email_provider=gmail_api
   VOICE_AGENT_gmail_credentials_path=./config/gmail_credentials.json
   ```

**Features:**
- Full email reading and sending
- Thread management
- Labels and archiving
- Sender history tracking
- OAuth 2.0 authentication

### 🔜 IMAP/SMTP (Coming Soon)

**Best for:** Any email provider with IMAP/SMTP access (Gmail, Outlook, custom servers)

**Configuration:**
```env
VOICE_AGENT_email_provider=imap_smtp
VOICE_AGENT_imap_server=imap.gmail.com
VOICE_AGENT_smtp_server=smtp.gmail.com
VOICE_AGENT_email_username=your-email@gmail.com
VOICE_AGENT_email_password=your-app-password
```

**Features:**
- Universal email provider support
- Basic email reading and sending
- Works with any IMAP/SMTP server

### 🔜 Microsoft Outlook Graph API (Coming Soon)

**Best for:** Microsoft 365, Outlook.com, Exchange

**Configuration:**
```env
VOICE_AGENT_email_provider=outlook_graph
VOICE_AGENT_outlook_client_id=your_client_id
VOICE_AGENT_outlook_client_secret=your_client_secret
VOICE_AGENT_outlook_tenant_id=your_tenant_id
```

**Features:**
- Full Outlook integration
- Calendar and email in one
- Enterprise-grade security

## Quick Start with Gmail (Recommended)

### Step 1: Get Gmail Credentials

See [gmail_setup_guide.md](./gmail_setup_guide.md) for detailed instructions.

**Quick version:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project, enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json`
5. Save as `config/gmail_credentials.json`

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
VOICE_AGENT_email_provider=gmail_api
VOICE_AGENT_gmail_credentials_path=./config/gmail_credentials.json
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Test Connection

```bash
python -c "
from voice_agent.adapters.email.factory import EmailAdapterFactory
import asyncio

async def test():
    adapter = EmailAdapterFactory.create(provider='gmail_api')
    threads = await adapter.fetch_threads(max_results=5)
    print(f'✅ Connected! Found {len(threads)} email threads')
    for thread in threads:
        print(f'  - {thread[\"subject\"][:50]}...')

asyncio.run(test())
"
```

## Mock Mode for Testing

Don't want to set up Gmail right away? Use mock mode:

```python
from voice_agent.adapters.email.factory import EmailAdapterFactory

# Create adapter with mock data
adapter = EmailAdapterFactory.create(
    provider='gmail_api',
    use_mock=True  # Uses fake email data
)
```

The system automatically falls back to mock mode if Gmail credentials aren't found!

## Switching Providers

### From Gmail to IMAP (when available):

1. Update `.env`:
   ```env
   VOICE_AGENT_email_provider=imap_smtp
   VOICE_AGENT_imap_server=imap.your-provider.com
   VOICE_AGENT_smtp_server=smtp.your-provider.com
   VOICE_AGENT_email_username=you@example.com
   VOICE_AGENT_email_password=your-password
   ```

2. Restart the application - that's it!

No code changes needed. The factory pattern handles everything.

## Adding Custom Providers

Want to add a new email provider? Create an adapter:

1. **Create adapter class:**

```python
# voice_agent/adapters/email/my_provider_adapter.py
from .base import BaseEmailAdapter

class MyProviderAdapter(BaseEmailAdapter):
    async def fetch_threads(self, ...):
        # Your implementation
        pass

    async def send_email(self, ...):
        # Your implementation
        pass

    # Implement all abstract methods
```

2. **Register in factory:**

```python
# voice_agent/adapters/email/factory.py
from .my_provider_adapter import MyProviderAdapter

class EmailAdapterFactory:
    @staticmethod
    def create(provider, **kwargs):
        if provider == "my_provider":
            return MyProviderAdapter(**kwargs)
        # ...
```

3. **Use it:**

```env
VOICE_AGENT_email_provider=my_provider
```

## Provider Comparison

| Feature | Gmail API | IMAP/SMTP | Outlook Graph |
|---------|-----------|-----------|---------------|
| Status | ✅ Available | 🔜 Coming Soon | 🔜 Coming Soon |
| OAuth 2.0 | ✅ Yes | ❌ No | ✅ Yes |
| Thread Support | ✅ Full | ⚠️ Limited | ✅ Full |
| Sender History | ✅ Yes | ⚠️ Basic | ✅ Yes |
| Search | ✅ Advanced | ⚠️ Basic | ✅ Advanced |
| Rate Limits | High | Provider-specific | High |
| Setup Complexity | Medium | Low | Medium |

## Troubleshooting

### "Unknown email provider" error

Check that your provider is in the supported list. Currently only `gmail_api` is fully implemented.

### "Credentials file not found" (Gmail)

Make sure `config/gmail_credentials.json` exists. See [gmail_setup_guide.md](./gmail_setup_guide.md).

### System falls back to mock mode

This happens when:
- Gmail credentials aren't configured
- Authentication fails
- Network issues

The system continues working with fake data for testing.

### Want real email but credentials won't work?

1. Delete `config/gmail_token.pickle`
2. Run the app again
3. Re-authorize in the browser

## Next Steps

- **Production:** Set up Gmail API following [gmail_setup_guide.md](./gmail_setup_guide.md)
- **Testing:** Use mock mode (`use_mock=True`)
- **Enterprise:** Wait for Outlook Graph adapter or contribute one!
- **Universal:** Wait for IMAP/SMTP adapter (works with any provider)
