# 📖 Complete Step-by-Step User Guide

## How to Use the Cognitive Journal Agent

---

## 🎯 Quick Overview

The Cognitive Journal Agent is a smart journal that:
- Captures your thoughts and notes
- **Automatically** extracts tasks from your entries
- **Automatically** detects your emotions
- **Automatically** tags your entries
- Generates daily summaries with AI insights
- Reads summaries aloud with voice

---

## 🚀 STEP 1: Start the Application (30 seconds)

### A. Start the Server

1. Navigate to the folder:
   ```
   C:\Users\pbkap\Documents\euron\Projects\dailyjournal\cognitive_journal_agent
   ```

2. **Double-click** `start_server.bat`

3. You'll see a black terminal window with:
   ```
   Starting Cognitive Journal Agent API Server...

   The web UI will be available at:
   http://localhost:7000

   API documentation at:
   http://localhost:7000/docs

   ============================================================
   COGNITIVE JOURNAL AGENT - API Server
   ============================================================

   Starting server on 0.0.0.0:7000
   API docs available at: http://0.0.0.0:7000/docs

   INFO:     Uvicorn running on http://0.0.0.0:7000 ✓
   ```

4. **KEEP THIS WINDOW OPEN** - This is your server running!

---

### B. Open the Web Interface

1. In the same folder, **Double-click** `web_ui.html`

2. Your web browser will open showing:

```
╔══════════════════════════════════════════════════════════════╗
║  🧠 Cognitive Journal Agent                    • Connected   ║
║     Your AI-powered personal assistant                       ║
╚══════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────┐
│  📝 Create Journal Entry                                      │
│                                                               │
│  What's on your mind?                                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Type your thoughts, tasks, or notes...                 │  │
│  │                                                         │  │
│  │ Examples:                                               │  │
│  │ • "Had a great meeting with the team today"           │  │
│  │ • "Need to finish the project report by Friday"       │  │
│  │ • "Feeling productive and energized!"                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  [ ✍️ Add Entry ]  [ 📊 Get Summary ]                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎨 STEP 2: Understanding the Interface

Your screen has **4 main sections**:

### Left Side (Main Area):

#### 1. **Create Journal Entry Box** (Top Left)
- Large text area where you type
- Two buttons:
  - **"✍️ Add Entry"** - Saves your entry
  - **"📊 Get Summary"** - Shows daily summary

#### 2. **Recent Entries** (Bottom Left)
- Shows all your journal entries in timeline
- Each entry shows:
  - Date and time
  - Your text
  - Extracted tags (as colored bubbles)
  - Detected emotion

### Right Side (Sidebar):

#### 3. **Quick Stats** (Top Right)
- Shows counts:
  - Total Entries
  - Action Items
  - Today's Entries

#### 4. **Action Items** (Middle Right)
- Lists all extracted tasks
- Color-coded by priority:
  - 🔴 Red = High priority
  - 🟡 Yellow = Medium priority
  - 🟢 Green = Low priority

#### 5. **Quick Actions** (Bottom Right)
- Pre-filled templates:
  - Daily Standup
  - Mood Check-in
  - Capture Idea

---

## ✍️ STEP 3: Create Your First Entry (1 minute)

### Example 1: Work Update

1. **Click** in the text area (big white box)

2. **Type** something like:
   ```
   Had a productive morning meeting with the design team. We finalized
   the UI mockups for the mobile app. Everyone is excited about the
   new color scheme. Need to send the mockups to the client by Thursday
   and schedule a follow-up meeting next week.
   ```

3. **Click** the purple **"✍️ Add Entry"** button

4. **Watch the magic happen!** In 2-3 seconds you'll see:

   ✅ **Success message**: "Journal entry created successfully!"

   🏷️ **Tags extracted**: `design-team`, `meeting`, `ui-mockups`, `mobile-app`, `client`

   ✅ **Actions found**:
   - "Send mockups to client by Thursday"
   - "Schedule follow-up meeting next week"

   😊 **Emotion**: "Excited"

   ⭐ **Priority**: 7/10

5. **Scroll down** to "Recent Entries" - you'll see your entry appear!

---

### Example 2: Personal Reflection

1. **Click** in the text area again

2. **Type**:
   ```
   Feeling a bit stressed about the deadline this Friday. There's
   still a lot to do on the project. Need to focus and prioritize
   my tasks better. Going to block out 3 hours for deep work tomorrow.
   ```

3. **Click** **"✍️ Add Entry"**

4. **AI extracts**:

   🏷️ **Tags**: `stressed`, `deadline`, `project`, `prioritization`, `deep-work`

   ✅ **Actions**:
   - "Block out 3 hours for deep work tomorrow"
   - "Prioritize tasks for the project"

   😰 **Emotion**: "Stressed"

   ⭐ **Priority**: 8/10 (High!)

5. **Look at the right sidebar** - your action items now show up!

---

### Example 3: Quick Note

1. **Type**:
   ```
   Great idea during lunch: Create a dashboard widget that shows
   user activity in real-time. This could be a game-changer for
   our product!
   ```

2. **Click** **"✍️ Add Entry"**

3. **AI extracts**:

   🏷️ **Tags**: `idea`, `dashboard`, `widget`, `real-time`, `product`

   ✅ **Actions**: "Create a dashboard widget for real-time user activity"

   💡 **Emotion**: "Excited"

   ⭐ **Priority**: 6/10

---

## 📊 STEP 4: Generate Your Daily Summary (30 seconds)

After you've created **3-5 entries**, click the blue **"📊 Get Summary"** button.

### What You'll See:

```
╔═══════════════════════════════════════════════════════════╗
║             📈 Daily Summary                               ║
╚═══════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────┐
│  📅 2025-11-03                                            │
│  📝 Total Entries: 5                                      │
├───────────────────────────────────────────────────────────┤
│  🏷️ Key Themes:                                          │
│  ┌─────────────┬─────────────┬──────────────┐            │
│  │ design-team │ ui-mockups  │ mobile-app   │            │
│  │ deadline    │ project     │ prioritization│            │
│  │ idea        │ dashboard   │ real-time    │            │
│  └─────────────┴─────────────┴──────────────┘            │
├───────────────────────────────────────────────────────────┤
│  😊 Emotion Overview:                                     │
│  • Excited: 40% (2 entries)                              │
│  • Stressed: 20% (1 entry)                               │
│  • Focused: 40% (2 entries)                              │
├───────────────────────────────────────────────────────────┤
│  💡 AI Insights:                                          │
│  "Today showed strong creativity with multiple           │
│   innovative ideas. The stress around Friday's deadline   │
│   is notable. Recommend tackling high-priority tasks     │
│   first to reduce anxiety. The team collaboration on     │
│   UI design shows good momentum."                        │
├───────────────────────────────────────────────────────────┤
│  ✅ Pending Actions (5):                                  │
│  🔴 [HIGH] Send mockups to client by Thursday           │
│  🔴 [HIGH] Prioritize tasks for the project             │
│  🟡 [MED] Schedule follow-up meeting next week          │
│  🟡 [MED] Block out 3 hours for deep work tomorrow      │
│  🟢 [LOW] Create dashboard widget for real-time activity│
├───────────────────────────────────────────────────────────┤
│  🎯 Suggested First Task:                                │
│  "Send mockups to client by Thursday"                   │
│                                                          │
│  This is marked as high priority with an approaching    │
│  deadline. Completing this first will reduce stress     │
│  and maintain client trust.                             │
└───────────────────────────────────────────────────────────┘

🔊 Audio summary saved to: audio_output/summary_2025-11-03.mp3
```

---

## 🔊 STEP 5: Listen to Your Summary (Optional)

1. **Navigate** to the folder:
   ```
   C:\Users\pbkap\Documents\euron\Projects\dailyjournal\cognitive_journal_agent\audio_output
   ```

2. **Double-click** the MP3 file (e.g., `summary_2025-11-03.mp3`)

3. **Listen** to a professional voice reading your summary!

---

## ⚡ STEP 6: Using Quick Actions

On the **right sidebar**, you'll see **Quick Actions** with purple buttons:

### 1. Daily Standup
**Click** this button and it pre-fills:
```
Daily standup completed. Discussed project progress.
```
Then you just **add details** and click **"Add Entry"**

### 2. Mood Check-in
**Click** this button and it pre-fills:
```
Feeling productive and energized today!
```
**Edit it** to match your mood and click **"Add Entry"**

### 3. Capture Idea
**Click** this button and it pre-fills:
```
Great idea:
```
**Add your idea** after the colon and click **"Add Entry"**

---

## 📱 STEP 7: Managing Action Items

### View Your Tasks

1. **Look at the right sidebar** under "Action Items"

2. You'll see all extracted tasks with:
   - Priority level (colored badge)
   - Task description
   - Source entry link

### Tasks are Automatically Extracted!

When you type things like:
- "Need to..."
- "Must..."
- "Should..."
- "Have to..."
- "Going to..."

The AI **automatically** creates action items for you!

---

## 🎯 Real-World Usage Scenarios

### Scenario 1: Morning Planning (5 minutes)

**8:00 AM - Start your day:**

1. Open the app (`start_server.bat` + `web_ui.html`)

2. Type your morning thoughts:
   ```
   Starting the day fresh. Top priorities: finish the Q4 report,
   review John's PR, and prepare for the 2pm client call. Need to
   focus on the report first - it's due today!
   ```

3. Click "Add Entry"

4. **AI extracts**:
   - Tags: `morning`, `planning`, `q4-report`, `code-review`, `client-call`
   - Actions: 3 tasks extracted automatically
   - Priority: Tasks sorted by urgency

5. **Check Action Items sidebar** - your day is planned!

---

### Scenario 2: After a Meeting (2 minutes)

**11:00 AM - Just finished a meeting:**

1. Quick entry:
   ```
   Great product sync with Sarah and Mike. Decided to pivot the
   dashboard design based on user feedback. Action items: update
   Figma mockups by EOD, schedule design review for tomorrow, and
   send meeting notes to the team.
   ```

2. Click "Add Entry"

3. **Done!** All action items are now tracked.

---

### Scenario 3: End of Day Review (5 minutes)

**6:00 PM - Wrapping up:**

1. Click **"📊 Get Summary"**

2. **Review**:
   - What you accomplished
   - Pending tasks for tomorrow
   - Emotion trends
   - AI insights

3. **Listen** to audio summary while commuting

4. **Plan tomorrow** based on suggested first task

---

### Scenario 4: Weekly Review (10 minutes)

**Friday 5:00 PM:**

1. Scroll through **Recent Entries** to see your week

2. **Check tags** to see themes:
   - What topics dominated?
   - Who did you collaborate with?
   - What projects got attention?

3. **Review Action Items**:
   - What got done?
   - What's pending?
   - What needs prioritization?

4. **Emotion check**:
   - How did you feel this week?
   - Any stress patterns?
   - What energized you?

---

## 💡 Pro Tips

### Tip 1: Be Natural
Don't worry about formatting or structure. Just write naturally:

❌ **Don't do this**:
```
- Task 1: Update docs
- Task 2: Send email
```

✅ **Do this**:
```
Had a productive day! Got through most of the documentation
updates. Still need to send that follow-up email to the client
about the project timeline.
```

The AI understands natural language!

---

### Tip 2: Mention People and Projects

Include names and project names:

✅ **Good**:
```
Met with Sarah about the Phoenix project. We discussed the API
redesign and decided to use GraphQL instead of REST.
```

The AI extracts:
- 👤 People: Sarah
- 📁 Projects: Phoenix
- 🏷️ Topics: API, GraphQL

---

### Tip 3: Express Feelings

Don't hide your emotions - they're valuable data:

✅ **Examples**:
```
"Feeling stressed about the deadline..."
"Excited about the new feature launch!"
"Frustrated with the CI/CD pipeline issues..."
"Proud of the team's performance this week."
```

The AI tracks these and shows patterns in your summary!

---

### Tip 4: Use Time References

Mention deadlines and timeframes:

✅ **Examples**:
```
"Need to finish this by Friday..."
"Must review before tomorrow's meeting..."
"Should schedule this for next week..."
"Due by end of day..."
```

The AI understands urgency and adjusts priority!

---

### Tip 5: Daily Habit

**Best practice**: Create entries throughout the day:
- Morning: Set intentions
- After meetings: Capture notes
- Midday: Quick progress updates
- End of day: Reflect and review

More entries = Better AI insights!

---

## 🔄 Daily Workflow Example

### A Complete Day with the Journal:

**8:00 AM** - Morning Entry
```
Starting the day energized! Going to focus on finishing the Q4
report first - it's my biggest priority. Then code reviews and
prep for client call at 2pm.
```
→ AI extracts 3 tasks, sets priorities

---

**10:00 AM** - After Morning Work
```
Knocked out the Q4 report! Sent it to leadership for review.
Feeling productive. Now moving on to code reviews.
```
→ AI detects "Focused" emotion

---

**12:00 PM** - Quick Update
```
Reviewed 3 PRs this morning. One needs significant changes,
sent feedback to the team. Grabbing lunch then preparing for
the client call.
```
→ AI tags: code-review, feedback, team

---

**3:00 PM** - Post-Meeting
```
Client call went great! They're happy with the progress and
approved the next phase. Need to update the project timeline
and schedule kickoff for phase 2 next week.
```
→ AI extracts 2 action items, detects "Excited"

---

**5:30 PM** - End of Day
Click **"📊 Get Summary"**

See:
- 4 entries today
- Multiple accomplishments
- 5 pending actions for tomorrow
- Overall emotion: 75% Focused, 25% Excited
- AI insight: "Highly productive day with strong momentum"

---

## 🎨 What Each UI Element Means

### Color Coding

**Priority Badges:**
- 🔴 **Red (P1/High)** = Urgent, do today
- 🟡 **Yellow (P2/Medium)** = Important, do this week
- 🟢 **Green (P3/Low)** = Nice to have, when time allows

**Entry Type Badges:**
- 🟣 **Purple** = text_note (most common)
- 🔵 **Blue** = voice_memo
- 🟢 **Green** = photo_ocr
- 🟠 **Orange** = pdf_document

**Status Indicator:**
- 🟢 **Green dot** = "Connected" (API is running)
- 🔴 **Red dot** = "Offline" (API not running - restart server!)

---

## ❓ Troubleshooting

### Problem: Nothing shows in UI

**Solution:**
1. Make sure server is running (black terminal window should be open)
2. Look for green "Connected" status in top right
3. Click the 🔄 Refresh button next to "Recent Entries"
4. Create a new entry - it should appear immediately

---

### Problem: "Offline" status showing

**Solution:**
1. Check if `start_server.bat` terminal is still open
2. If closed, double-click `start_server.bat` again
3. Wait 3 seconds for server to start
4. Refresh your browser (F5)
5. Should show "Connected" again

---

### Problem: Tags are generic (just "Task" or "Work")

**Solution:**
This means LLM processing isn't working. Check:
1. Is `USE_LLM_PROCESSING=true` in `.env`?
2. Is `OPENAI_API_KEY` set in `.env`?
3. Restart the server after changing `.env`

---

### Problem: No action items extracted

**Solution:**
Use action keywords in your entries:
- "Need to..."
- "Must..."
- "Should..."
- "Have to..."
- "Going to..."

Example: "Need to send email to John" ✓

---

## 📊 Understanding Your Data

### Where is everything stored?

```
data/
├── journal_entries.json     ← All your journal entries
├── action_items.json        ← All extracted tasks
└── audio/                   ← (future: audio recordings)

audio_output/
└── summary_2025-11-03.mp3  ← Daily summary audio files
```

### Your data is:
- ✅ **Stored locally** on your computer
- ✅ **Not sent to cloud** (except API calls for AI processing)
- ✅ **Yours forever** - you own all files
- ✅ **Exportable** - just copy the JSON files
- ✅ **Readable** - JSON format is human-readable

---

## 🎓 Learning Path

### Week 1: Get Comfortable
- Create 2-3 entries per day
- Try different types (work, personal, ideas)
- Generate your first daily summary
- Listen to an audio summary

### Week 2: Build the Habit
- Create entries after each meeting
- Use Quick Actions for speed
- Check Action Items sidebar daily
- Review weekly patterns

### Week 3: Optimize
- Find your ideal entry frequency
- Develop your own templates
- Use insights for planning
- Track emotion patterns

### Week 4: Master It
- Daily summaries become routine
- Action items guide your day
- Insights improve decision-making
- Journaling feels natural

---

## 🎯 Success Checklist

After reading this guide, you should be able to:

- [ ] Start the server (`start_server.bat`)
- [ ] Open the web UI (`web_ui.html`)
- [ ] Create a journal entry
- [ ] See AI-extracted tags
- [ ] Find action items in sidebar
- [ ] View recent entries timeline
- [ ] Generate a daily summary
- [ ] Listen to an audio summary
- [ ] Use Quick Actions
- [ ] Understand the color coding
- [ ] Troubleshoot basic issues

---

## 🎉 You're Ready!

You now know everything you need to use the Cognitive Journal Agent effectively!

**Start using it today:**
1. `start_server.bat` ← Run this
2. `web_ui.html` ← Open this
3. Type your first entry
4. Watch the AI magic happen! ✨

---

**Questions? Check these files:**
- `GETTING_STARTED.md` - Quick start
- `WEB_UI_GUIDE.md` - Full UI reference
- `CONFIGURATION_STATUS.md` - Feature details
- `docs/` folder - Complete documentation

---

**Happy Journaling! 📝🧠✨**

**Version**: 1.0.0
**Last Updated**: 2025-11-03
