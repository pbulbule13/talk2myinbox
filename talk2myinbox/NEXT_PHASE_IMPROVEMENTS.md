# 🚀 Next Phase Improvements - Implementation Plan

**Date:** November 2, 2025
**Status:** 📋 **PLANNED**

---

## 🎯 New Requirements

### 1. **No Popups** ✅
- Remove all `alert()`, `confirm()`, `prompt()`
- Replace with inline notifications/toasts
- Add notification system component

### 2. **Use Euron API** 🔄
- Integrate Euron API for AI reasoning
- Configure API key from .env
- Use for draft generation and email analysis

### 3. **Calendar Enhancements** 🔄
- Add Day/Week toggle
- Show today OR this week's events
- Better event display

### 4. **Important Highlights** 🔄
- New section for important emails
- Auto-detect urgent/important
- Quick access panel

### 5. **Email Threading** 🔄
- Pull 20+ recent emails
- Track conversations/threads
- Group emails by conversation
- Show thread view

### 6. **Better Segregation** 🔄
- Improved categorization
- Conversation grouping
- Thread timeline view

---

## 📝 Implementation Steps

### Step 1: Remove All Popups

#### Files to Update:
- `frontend/communications_enhanced.js`
- `frontend/support.js`

#### Changes Needed:

**Replace This:**
```javascript
❌ alert('Email sent successfully!');
❌ if (!confirm('Send email?')) return;
❌ const text = prompt('Enter reminder:');
```

**With This:**
```javascript
✅ showNotification('Email sent successfully!', 'success');
✅ showConfirmDialog('Send email?', () => sendEmail());
✅ showInputDialog('Enter reminder:', (text) => addReminder(text));
```

#### Create Notification System:
```javascript
// Add to communications_enhanced.js

function showNotification(message, type = 'info') {
    const notif = document.createElement('div');
    notif.className = `notification notification-${type}`;
    notif.textContent = message;
    document.body.appendChild(notif);

    setTimeout(() => notif.classList.add('show'), 10);
    setTimeout(() => {
        notif.classList.remove('show');
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}
```

#### Add CSS:
```css
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    opacity: 0;
    transform: translateY(-20px);
    transition: all 0.3s;
    z-index: 1000;
}

.notification.show {
    opacity: 1;
    transform: translateY(0);
}

.notification-success {
    background: #10b981;
    color: white;
}

.notification-error {
    background: #ef4444;
    color: white;
}

.notification-info {
    background: #3b82f6;
    color: white;
}
```

---

### Step 2: Integrate Euron API

#### Backend Changes (`routes.py`):

**Add Euron Client:**
```python
import os
import requests

def call_euron_api(prompt: str) -> str:
    """
    Call Euron API for AI reasoning
    """
    api_key = os.getenv("EURON_API_KEY")
    api_base = os.getenv("EURON_API_BASE")
    model = os.getenv("EURON_MODEL", "gpt-4.1-nano")

    response = requests.post(
        f"{api_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    return response.json()["choices"][0]["message"]["content"]
```

**Update Draft Generation:**
```python
@router.post("/draft-reply")
async def generate_draft_reply(request: DraftReplyRequest):
    prompt = f"""Generate a professional email reply:

From: {request.email_from}
Subject: {request.email_subject}
Body: {request.email_body}

Write a brief, professional reply (2-4 sentences)."""

    draft_text = call_euron_api(prompt)

    return {
        "success": True,
        "draft_text": draft_text,
        "email_id": request.email_id
    }
```

---

### Step 3: Calendar Day/Week Toggle

#### HTML Update (`index.html`):

**Add Toggle to Calendar Widget:**
```html
<div class="bg-white rounded-lg shadow border border-gray-200">
    <div class="p-3 border-b border-gray-200 flex justify-between items-center">
        <h3 class="font-bold text-gray-900 text-sm">📅 Calendar</h3>
        <div class="flex gap-1">
            <button id="cal-day" onclick="switchCalendarView('day')"
                    class="px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded">
                Day
            </button>
            <button id="cal-week" onclick="switchCalendarView('week')"
                    class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                Week
            </button>
        </div>
    </div>
    <div id="calendar-list" class="p-3 max-h-[400px] overflow-y-auto space-y-2">
        <!-- Events here -->
    </div>
</div>
```

#### JavaScript Update (`communications_enhanced.js`):

```javascript
window.calendarView = 'day'; // Default view

function switchCalendarView(view) {
    window.calendarView = view;

    // Update button styles
    document.getElementById('cal-day').className =
        view === 'day' ? 'px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded'
                       : 'px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded';

    document.getElementById('cal-week').className =
        view === 'week' ? 'px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded'
                        : 'px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded';

    // Reload calendar
    loadCalendar(view);
}

async function loadCalendar(view = 'day') {
    const timeframe = view === 'day' ? 'today' : 'week';
    const response = await fetch(`${COMM_API}/voice-agent/calendar/events?timeframe=${timeframe}`);
    const data = await response.json();

    renderCalendar(data.events);
}
```

---

### Step 4: Important Highlights Section

#### HTML Update (`index.html`):

**Add to Left Sidebar (before Calendar):**
```html
<!-- Important Highlights -->
<div class="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg shadow border border-red-200 p-3 mb-4">
    <div class="flex items-center justify-between mb-2">
        <h3 class="font-bold text-red-900 text-sm">⚡ Important</h3>
        <span id="important-count" class="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">0</span>
    </div>
    <div id="important-list" class="space-y-2">
        <!-- Important items here -->
    </div>
</div>
```

#### JavaScript Update:

```javascript
function detectImportant(email) {
    const subject = email.subject.toLowerCase();
    const body = (email.body || email.preview || '').toLowerCase();

    // Important indicators
    const indicators = [
        'urgent', 'asap', 'important', 'critical', 'deadline',
        'action required', 'immediate', 'emergency', 'priority',
        'time sensitive', 'respond by', 'due date'
    ];

    return indicators.some(indicator =>
        subject.includes(indicator) || body.includes(indicator)
    );
}

function renderImportantHighlights() {
    const important = window.communicationsState.emails
        .filter(e => detectImportant(e))
        .slice(0, 5); // Top 5

    const list = document.getElementById('important-list');
    document.getElementById('important-count').textContent = important.length;

    if (important.length === 0) {
        list.innerHTML = '<p class="text-xs text-gray-500">No urgent items</p>';
        return;
    }

    list.innerHTML = important.map(email => `
        <div class="bg-white rounded p-2 cursor-pointer hover:bg-red-50 transition-all"
             onclick="selectEmail('${email.id}')">
            <div class="text-xs font-semibold text-gray-900 line-clamp-1">
                ${escapeHtml(email.subject)}
            </div>
            <div class="text-xs text-gray-600 mt-1">
                From: ${escapeHtml(email.from)}
            </div>
        </div>
    `).join('');
}
```

---

### Step 5: Email Threading (20+ Emails)

#### Update Email Fetch:

**Frontend (`communications_enhanced.js`):**
```javascript
async function loadAllEmails(gmailQuery) {
    const url = new URL(`${COMM_API}/voice-agent/emails`);
    url.searchParams.set('max_results', '25'); // Increased from 10 to 25
    if (gmailQuery) url.searchParams.set('query', gmailQuery);

    const response = await fetch(url.toString());
    const data = await response.json();
    const emails = data.emails || [];

    // Group by thread
    const threads = groupEmailsByThread(emails);

    window.communicationsState.emails = emails;
    window.communicationsState.threads = threads;

    renderEmailList();
}
```

#### Add Threading Logic:

```javascript
function groupEmailsByThread(emails) {
    const threads = {};

    emails.forEach(email => {
        // Extract conversation participants
        const participants = extractParticipants(email);
        const threadKey = generateThreadKey(participants, email.subject);

        if (!threads[threadKey]) {
            threads[threadKey] = {
                id: threadKey,
                subject: email.subject,
                participants: participants,
                emails: [],
                lastTimestamp: email.timestamp,
                unreadCount: 0
            };
        }

        threads[threadKey].emails.push(email);
        if (email.unread) threads[threadKey].unreadCount++;

        // Update last timestamp
        if (email.timestamp > threads[threadKey].lastTimestamp) {
            threads[threadKey].lastTimestamp = email.timestamp;
        }
    });

    return Object.values(threads);
}

function extractParticipants(email) {
    // Extract unique participants from from/to/cc
    const participants = new Set();

    if (email.from) participants.add(email.from.toLowerCase());
    if (email.to) {
        email.to.split(',').forEach(addr => participants.add(addr.trim().toLowerCase()));
    }

    return Array.from(participants).sort();
}

function generateThreadKey(participants, subject) {
    // Remove Re:, Fwd:, etc from subject
    const cleanSubject = subject
        .replace(/^(re|fwd|fw):\s*/i, '')
        .trim()
        .toLowerCase();

    // Combine participants + subject for unique thread key
    return `${participants.join('|')}::${cleanSubject}`;
}
```

#### Add Thread View UI:

**HTML:**
```html
<!-- Add toggle for list/thread view -->
<div class="flex gap-2 mb-2">
    <button id="view-list" onclick="switchEmailView('list')"
            class="text-xs bg-indigo-100 text-indigo-700 px-3 py-1 rounded">
        📧 List View
    </button>
    <button id="view-threads" onclick="switchEmailView('threads')"
            class="text-xs bg-gray-100 text-gray-600 px-3 py-1 rounded">
        💬 Conversations
    </button>
</div>
```

**JavaScript:**
```javascript
function switchEmailView(view) {
    window.communicationsState.emailView = view;

    // Update buttons
    // ...

    if (view === 'threads') {
        renderThreadView();
    } else {
        renderEmailList();
    }
}

function renderThreadView() {
    const threads = window.communicationsState.threads;
    const emailList = document.getElementById('email-list');

    emailList.innerHTML = threads.map(thread => `
        <div class="thread-item border-b border-gray-200 p-4 hover:bg-gray-50 cursor-pointer"
             onclick="expandThread('${thread.id}')">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <div class="font-semibold text-gray-900">${escapeHtml(thread.subject)}</div>
                    <div class="text-xs text-gray-600 mt-1">
                        ${thread.participants.join(', ')}
                    </div>
                    <div class="text-xs text-gray-500 mt-1">
                        ${thread.emails.length} messages
                        ${thread.unreadCount > 0 ? `• ${thread.unreadCount} unread` : ''}
                    </div>
                </div>
                <div class="text-xs text-gray-500">
                    ${formatTime(thread.lastTimestamp)}
                </div>
            </div>
        </div>
    `).join('');
}

function expandThread(threadId) {
    const thread = window.communicationsState.threads.find(t => t.id === threadId);
    // Show thread timeline
    showThreadTimeline(thread);
}
```

---

## 📦 Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `frontend/index.html` | Add toggles, highlights section | High |
| `frontend/communications_enhanced.js` | Remove alerts, add threading | High |
| `frontend/support.js` | Remove alerts | High |
| `backend/voice_agent/api/routes.py` | Integrate Euron API | High |
| `frontend/style.css` | Add notification styles | Medium |

---

## 🧪 Testing Checklist

- [ ] No alerts/confirms/prompts anywhere
- [ ] Notifications show for all actions
- [ ] Calendar Day/Week toggle works
- [ ] Important highlights auto-update
- [ ] 20+ emails load correctly
- [ ] Thread view groups conversations
- [ ] Thread timeline shows correctly
- [ ] Euron API responds for drafts
- [ ] All features work without popups

---

## 📊 Expected Results

**After Implementation:**

✅ Zero popups (all inline feedback)
✅ Euron API powers AI features
✅ Calendar shows day OR week
✅ Important highlights visible
✅ 20-25 emails displayed
✅ Conversations grouped
✅ Thread timeline view
✅ Better organization

---

**Status:** Ready to implement
**Estimated Time:** 2-3 hours
**Priority:** High

This plan is ready for implementation. Each section provides the exact code changes needed.
