# Talk2MyInbox - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Run the Application

Simply **double-click** `start.bat` in the project root directory.

**Or** from command line:
```bash
start.bat
```

That's it! The script will:
1. ✅ Check UV installation
2. ✅ Create virtual environment (.venv)
3. ✅ Install all dependencies
4. ✅ Configure the application
5. ✅ Kill any existing server on port 8000
6. ✅ Start the Talk2MyInbox server

### Step 2: Open Your Browser

Navigate to:
```
http://localhost:8000
```

### Step 3: Use the Application

The application will automatically load and display:
- 📧 **30 emails** from your Gmail (or mock data)
- 📅 **Calendar events** for today
- 🎯 **Smart categorization** (Human vs Automated)
- 💬 **Thread grouping** for conversations
- 💼 **Job application** detection

## 🎯 What You'll See

### Email List
- **Pagination**: 10 emails per page (30 total)
- **Badges**:
  - 👤 **Human** - Real person email
  - 🤖 **Auto** - Automated/system email
  - 💬 **X msgs** - Thread message count
  - 💼 **Job App** - Job application related
  - ⚠️ **Follow-up** - Needs attention

### Quick Actions
- **Draft Reply** - AI-powered draft generation
- **View Thread** - See full conversation
- **Mark Read** - Mark as read

### Calendar
- View today's or this week's events
- Auto-detected meeting invites from emails

## 🔧 What start.bat Does

```
[1/6] Checking UV installation...
✓ UV is installed

[2/6] Setting up virtual environment...
✓ Virtual environment created/exists

[3/6] Installing dependencies...
✓ Dependencies installed

[4/6] Checking configuration...
✓ Configuration ready (MOCK mode)

[5/6] Checking for existing server...
✓ Port 8000 is available

[6/6] Starting Talk2MyInbox server...
Server: http://localhost:8000
```

## 📊 Application Modes

### MOCK Mode (Default)
- ✅ Works out of the box
- ✅ No setup required
- ✅ Shows your real Gmail emails
- ✅ Shows sample calendar events

### Real Gmail/Calendar Mode
To use real Gmail and Calendar APIs:

1. Get Google API credentials
2. Create `backend/.env` file
3. Add credentials:
```env
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
```

See `backend/.env.example` for full configuration options.

## 🎨 Features You Can Try

### 1. View Emails
- Scroll through your emails
- Use pagination to see more
- Click on emails to view details

### 2. Draft Replies
- Click "✍️ Draft Reply" on any email
- AI will generate a contextual response

### 3. View Threads
- Click "👁️ View Thread" on conversations
- See all messages in the thread
- Reply from the thread viewer

### 4. AI Inbox Overview
Open browser console (F12) and run:
```javascript
getInboxOverview()
```

This shows:
- Important emails to review
- Interview count for the week
- Short, crisp summary
- Voice-enabled with 🔊 Speak button

### 5. Block Calendar Time
Open browser console (F12) and run:
```javascript
// Block 1 hour for kids' school
blockCalendarTime('Kids School', '2025-01-27T15:00:00', 60)
```

## 🛑 Stopping the Server

Press `Ctrl+C` in the command window, or simply close the window.

## 🔄 Restarting

Just run `start.bat` again. It will:
- Kill any existing server
- Restart with latest code
- Reload dependencies if needed

## 🐛 Troubleshooting

### Issue: "UV is not installed"
**Solution:**
```bash
pip install uv
```

### Issue: Port 8000 already in use
**Solution:** start.bat automatically kills processes on port 8000. If it doesn't work:
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Dependencies fail to install
**Solution:**
```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Emails not loading
**Solutions:**
1. Check server logs in command window
2. Open http://localhost:8000/docs
3. Test `/voice-agent/emails` endpoint
4. Check browser console (F12) for errors

### Issue: Application doesn't open in browser
**Solutions:**
1. Manually open: http://localhost:8000
2. Check if server started successfully
3. Look for errors in command window

## 📖 Next Steps

- **Full Documentation**: See `README.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **API Reference**: Visit http://localhost:8000/docs when server is running

## 💡 Tips

1. **Keep terminal open**: You'll see all logs and errors
2. **Use F12**: Browser console shows frontend errors
3. **Check /docs**: Interactive API documentation
4. **Mock mode first**: Test without API credentials
5. **Real API later**: Add credentials when ready

## ✨ You're All Set!

Your Talk2MyInbox application is now running with:
- ✅ Email management (30 emails with pagination)
- ✅ Thread grouping and job detection
- ✅ Calendar integration
- ✅ AI-powered features
- ✅ Voice capabilities

**Enjoy your enhanced email and calendar management!** 🎉

---

**Need help?** Check `README.md` or open an issue on GitHub.
