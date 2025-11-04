# Cognitive Journal Agent - Quick Start Guide

## 🚀 Getting Started

The Cognitive Journal Agent now has a **fully interactive web UI** with multimodal input support!

### Step 1: Start the Server

Run the provided batch file:
```batch
start_server.bat
```

Or manually:
```bash
python main.py api
```

The server will start on: **http://localhost:7000**

### Step 2: Open the Web UI

Open `web_ui.html` in your web browser:
- Double-click the file, or
- Navigate to: `file:///C:/Users/pbkap/Documents/euron/Projects/dailyjournal/cognitive_journal_agent/web_ui.html`

---

## ✨ Features Overview

The landing page provides **5 different ways** to capture your journal entries:

### 1. 📝 Text Entry
- Type your thoughts, notes, or tasks
- AI automatically:
  - Tags your entry (Work, Personal, Task, Idea, etc.)
  - Extracts action items
  - Infers your emotional state
  - Prioritizes tasks

**Example:**
```
"Had a productive meeting with the team today. Need to send follow-up email to Sarah by Friday."
```

**Result:**
- Tags: Work, Meeting, Task
- Action: "Send follow-up email to Sarah by Friday"
- Priority: P2 (Medium)

---

### 2. 🎤 Voice Memo Upload
- Upload audio files (MP3, WAV, M4A, OGG)
- AI transcribes your voice and processes it
- Perfect for:
  - Quick voice notes while driving
  - Meeting recordings
  - Voice journaling

**How to use:**
1. Click the "Voice" tab
2. Click to upload or drag & drop audio file
3. Click "Upload Voice Memo"
4. AI will transcribe and analyze the content

---

### 3. 📷 Image Upload (OCR)
- Upload images with text (photos of whiteboards, notes, documents)
- AI extracts text using OCR (Optical Character Recognition)
- Processes the extracted text like any other entry
- Supports: JPG, PNG, GIF, BMP

**Perfect for:**
- Whiteboard photos from meetings
- Handwritten notes
- Screenshots of important information
- Photos of documents

**How to use:**
1. Click the "Image" tab
2. Upload an image
3. Preview appears automatically
4. Click "Upload & Process Image"

---

### 4. 📄 PDF Document Upload
- Upload PDF documents
- AI extracts text from all pages
- Analyzes and stores the content
- Great for:
  - Meeting notes
  - Reports
  - Articles you want to reference

**How to use:**
1. Click the "PDF" tab
2. Upload a PDF file
3. Click "Upload & Process PDF"
4. AI extracts and analyzes the text

---

### 5. 💻 Code Snippet
- Save code snippets with context
- Select programming language (Python, JavaScript, Java, etc.)
- AI analyzes and tags your code
- Perfect for:
  - Tracking code solutions
  - Documenting bug fixes
  - Saving useful snippets

**How to use:**
1. Click the "Code" tab
2. Select programming language
3. Paste your code
4. Click "Add Code Snippet"

---

## 📊 Dashboard Features

### Recent Entries
- See all your journal entries in chronological order
- Each entry shows:
  - Timestamp
  - Content preview
  - Tags
  - Inferred emotion
  - Input type (text, voice, image, pdf, code)

### Quick Stats
- **Total Entries**: Count of all journal entries
- **Action Items**: Number of pending tasks
- **Today's Entries**: How many entries you've made today

### Action Items
- All extracted tasks in one place
- Color-coded by priority (P1=Red, P2=Yellow, P3=Green)
- Automatically extracted from your entries

### Daily Summary
- Click "Generate Daily Summary" to get:
  - Overview of your day
  - Key themes
  - Emotion analysis
  - Pending actions
  - Suggested first task

---

## 🎯 Usage Examples

### Example 1: Quick Task
1. Open web UI
2. Stay on Text tab
3. Type: "Finish project report by Friday and send to manager"
4. Click "Add Entry"

**Result:** Task extracted with deadline, tagged as Work/Task

---

### Example 2: Voice Journal
1. Record a voice memo on your phone
2. Transfer to computer or use a recording app
3. Go to Voice tab
4. Upload the audio file
5. AI transcribes and processes it

---

### Example 3: Meeting Notes
1. Take photo of whiteboard after meeting
2. Go to Image tab
3. Upload the photo
4. AI extracts text from whiteboard
5. Automatically tags and extracts action items

---

### Example 4: Code Solution
1. Solved a tricky bug? Save it!
2. Go to Code tab
3. Select language
4. Paste your solution
5. Add it to your journal for future reference

---

## 🔄 Quick Actions

The right sidebar has pre-made templates:
- **Daily Standup**: Quick logging of standup notes
- **Mood Check-in**: Record how you're feeling
- **Capture Idea**: Save quick thoughts

Just click any template to auto-fill the text area!

---

## 💡 Pro Tips

1. **Use Natural Language**: Just write naturally - the AI understands context
   - "Need to call John about the project tomorrow"
   - AI extracts: Task, priority, deadline

2. **Mix Input Types**: Use different input methods throughout the day
   - Voice memos during commute
   - Text entries at desk
   - Photos of meeting notes

3. **Daily Summaries**: Generate summaries at end of day to:
   - Review what you accomplished
   - See your emotional patterns
   - Get task recommendations

4. **Action Items**: Check the Action Items panel regularly
   - All tasks in one place
   - Sorted by priority
   - Nothing gets forgotten

---

## 🔧 Troubleshooting

### "API server is not running"
- Make sure you ran `start_server.bat` or `python main.py api`
- Check that port 7000 is not in use by another application

### "Error connecting to API"
- Verify server is running (check terminal)
- Ensure web UI is accessing `http://localhost:7000`
- Try refreshing the page

### File Upload Issues
- Check file format (must be supported type)
- Ensure file size is reasonable (< 10MB recommended)
- Make sure dependencies are installed:
  ```bash
  pip install openai-whisper pytesseract PyPDF2
  ```

### OCR Not Working
- Install Tesseract OCR:
  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Mac: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

---

## 📱 Mobile Usage

While the web UI is desktop-optimized, you can:
1. Create entries on mobile
2. Upload files later from computer
3. Or use the CLI mode: `python main.py cli`

---

## 🎨 UI Features

- **Responsive Design**: Works on all screen sizes
- **Real-time Updates**: Entries appear immediately
- **Beautiful Animations**: Smooth transitions and effects
- **Color-coded Tags**: Easy visual identification
- **Emoji Support**: Makes everything more engaging

---

## 🚀 Next Steps

1. ✅ Create your first entry (any type!)
2. ✅ Generate a daily summary
3. ✅ Try uploading a voice memo
4. ✅ Upload an image with text
5. ✅ Save a code snippet

---

## 📖 Need More Help?

See the full documentation:
- `USER_GUIDE_STEP_BY_STEP.md` - Comprehensive guide
- `ARCHITECTURE.md` - Technical details
- `docs/` folder - All documentation

---

**Enjoy your AI-powered journaling experience!** 🎉
