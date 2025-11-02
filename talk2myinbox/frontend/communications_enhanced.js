/**
 * Enhanced Communications with Better Categorization, Draft Management, and Calendar
 */

const COMM_API = (window.DASHBOARD_CONFIG?.api?.baseUrl) || 'http://localhost:8000';

// Global state
window.communicationsState = {
    emails: [],
    drafts: [],
    selectedEmail: null,
    selectedDraft: null,
    currentCategory: 'all',
    calendar: [],
    reminders: [],
    calendarView: 'day', // 'day' or 'week'
    threads: {}
};

/**
 * Show inline notification (replaces alert())
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notif = document.createElement('div');
    notif.className = `notification notification-${type}`;
    notif.textContent = message;
    document.body.appendChild(notif);

    setTimeout(() => notif.classList.add('show'), 10);
    setTimeout(() => {
        notif.classList.remove('show');
        setTimeout(() => notif.remove(), 300);
    }, duration);
}

/**
 * Show inline confirmation dialog (replaces confirm())
 */
function showConfirmDialog(message, onConfirm, onCancel = null) {
    const overlay = document.createElement('div');
    overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    overlay.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md mx-4 shadow-xl">
            <p class="text-gray-900 mb-4">${escapeHtml(message)}</p>
            <div class="flex gap-2 justify-end">
                <button id="confirm-cancel" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded font-semibold">
                    Cancel
                </button>
                <button id="confirm-yes" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold">
                    Confirm
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    document.getElementById('confirm-yes').onclick = () => {
        overlay.remove();
        if (onConfirm) onConfirm();
    };

    document.getElementById('confirm-cancel').onclick = () => {
        overlay.remove();
        if (onCancel) onCancel();
    };

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            overlay.remove();
            if (onCancel) onCancel();
        }
    };
}

/**
 * Show inline input dialog (replaces prompt())
 */
function showInputDialog(message, onSubmit, defaultValue = '') {
    const overlay = document.createElement('div');
    overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    overlay.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md mx-4 shadow-xl">
            <p class="text-gray-900 mb-3">${escapeHtml(message)}</p>
            <input type="text" id="input-field" value="${escapeHtml(defaultValue)}"
                   class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4">
            <div class="flex gap-2 justify-end">
                <button id="input-cancel" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded font-semibold">
                    Cancel
                </button>
                <button id="input-submit" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold">
                    OK
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    const inputField = document.getElementById('input-field');
    inputField.focus();

    const submit = () => {
        const value = inputField.value.trim();
        overlay.remove();
        if (value && onSubmit) onSubmit(value);
    };

    document.getElementById('input-submit').onclick = submit;
    inputField.onkeypress = (e) => {
        if (e.key === 'Enter') submit();
    };

    document.getElementById('input-cancel').onclick = () => {
        overlay.remove();
    };

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    };
}

// Enhanced Email categories with human/automated detection
const EMAIL_CATEGORIES = {
    human: {
        name: 'From Humans',
        icon: '👤',
        color: 'blue',
        detector: (email) => detectHumanEmail(email)
    },
    automated: {
        name: 'Automated',
        icon: '🤖',
        color: 'gray',
        detector: (email) => detectAutomatedEmail(email)
    },
    urgent: {
        name: 'Urgent',
        icon: '🚨',
        color: 'red',
        keywords: ['urgent', 'asap', 'emergency', 'critical', 'immediate', 'priority']
    },
    work: {
        name: 'Work',
        icon: '💼',
        color: 'purple',
        keywords: ['meeting', 'project', 'deadline', 'report', 'client', 'business', 'presentation']
    },
    personal: {
        name: 'Personal',
        icon: '💚',
        color: 'green',
        keywords: ['family', 'personal', 'home', 'appointment', 'friend']
    }
};

/**
 * Detect if email is from a human (vs automated system)
 */
function detectHumanEmail(email) {
    const from = email.from.toLowerCase();
    const subject = (email.subject || '').toLowerCase();
    const preview = (email.preview || email.body || '').toLowerCase();

    // Automated email indicators
    const automatedIndicators = [
        'noreply', 'no-reply', 'donotreply', 'automated', 'notification',
        'alerts', 'newsletter', 'subscriptions', 'update', 'digest',
        'unsubscribe', 'confirm your', 'verify your', 'reset your password'
    ];

    // Check if from address has automated indicators
    if (automatedIndicators.some(indicator => from.includes(indicator))) {
        return false;
    }

    // Check if subject/content has automated patterns
    if (automatedIndicators.some(indicator => subject.includes(indicator) || preview.includes(indicator))) {
        return false;
    }

    // Human indicators
    const humanIndicators = [
        'dear', 'hi ', 'hello', 'thanks', 'thank you', 'regards', 'sincerely',
        'could you', 'can you', 'would you', 'please', 'let me know'
    ];

    if (humanIndicators.some(indicator => preview.includes(indicator))) {
        return true;
    }

    // Default: consider as human if no clear automated indicators
    return true;
}

/**
 * Detect if email is automated
 */
function detectAutomatedEmail(email) {
    return !detectHumanEmail(email);
}

/**
 * Categorize email based on content and sender
 */
function categorizeEmail(email) {
    const text = `${email.subject} ${email.preview || email.body}`.toLowerCase();

    // First check human vs automated
    if (detectAutomatedEmail(email)) {
        return 'automated';
    }

    // Then check other categories
    for (const [key, category] of Object.entries(EMAIL_CATEGORIES)) {
        if (category.keywords && category.keywords.some(keyword => text.includes(keyword))) {
            return key;
        }
    }

    // Default to human category
    return 'human';
}

/**
 * Extract participants from email
 */
function extractParticipants(email) {
    const participants = new Set();

    if (email.from) {
        participants.add(email.from.toLowerCase().trim());
    }

    if (email.to) {
        const recipients = typeof email.to === 'string' ? email.to.split(',') : email.to;
        recipients.forEach(addr => participants.add(addr.toLowerCase().trim()));
    }

    return Array.from(participants).sort();
}

/**
 * Generate thread key for grouping emails
 */
function generateThreadKey(participants, subject) {
    // Remove Re:, Fwd:, Fw: prefixes from subject
    const cleanSubject = subject
        .replace(/^(re|fwd|fw):\s*/i, '')
        .trim()
        .toLowerCase();

    // Combine participants + subject for unique thread key
    return `${participants.join('|')}::${cleanSubject}`;
}

/**
 * Group emails by conversation thread
 */
function groupEmailsByThread(emails) {
    const threads = {};

    emails.forEach(email => {
        const participants = extractParticipants(email);
        const threadKey = generateThreadKey(participants, email.subject || 'No Subject');

        if (!threads[threadKey]) {
            threads[threadKey] = {
                id: threadKey,
                subject: email.subject || 'No Subject',
                participants: participants,
                emails: [],
                lastTimestamp: email.timestamp || email.date,
                unreadCount: 0
            };
        }

        threads[threadKey].emails.push(email);
        if (email.unread) threads[threadKey].unreadCount++;

        // Update last timestamp
        const emailTime = new Date(email.timestamp || email.date).getTime();
        const threadTime = new Date(threads[threadKey].lastTimestamp).getTime();
        if (emailTime > threadTime) {
            threads[threadKey].lastTimestamp = email.timestamp || email.date;
        }
    });

    return Object.values(threads).sort((a, b) => {
        return new Date(b.lastTimestamp) - new Date(a.lastTimestamp);
    });
}

/**
 * Load all emails from Gmail
 */
async function loadAllEmails(gmailQuery) {
    console.log('[Communications] Loading Gmail emails...');

    try {
        const url = new URL(`${COMM_API}/voice-agent/emails`);
        url.searchParams.set('max_results', '25'); // Increased to 25 for better coverage
        if (gmailQuery) url.searchParams.set('query', gmailQuery);

        const response = await fetch(url.toString());

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        const emails = data.emails || [];

        // Categorize emails
        window.communicationsState.emails = emails.map(email => ({
            ...email,
            category: categorizeEmail(email),
            isHuman: detectHumanEmail(email),
            timestamp: email.timestamp || email.date
        }));

        // Group by thread
        window.communicationsState.threads = groupEmailsByThread(window.communicationsState.emails);

        console.log(`[Communications] Loaded ${emails.length} emails, ${window.communicationsState.threads.length} threads`);
        renderEmailList();
        updateCategoryBadges();

    } catch (error) {
        console.error('[Communications] Error loading emails:', error);
        showError('email-list', error.message);
    }
}

/**
 * Render email list with enhanced UI
 */
function renderEmailList() {
    const emailList = document.getElementById('email-list');
    const category = window.communicationsState.currentCategory;

    let filteredEmails = window.communicationsState.emails;
    if (category !== 'all') {
        filteredEmails = filteredEmails.filter(email => email.category === category);
    }

    if (filteredEmails.length === 0) {
        emailList.innerHTML = `
            <div class="p-6 text-center text-gray-500">
                <p class="text-sm">No emails in this category</p>
            </div>
        `;
        return;
    }

    emailList.innerHTML = filteredEmails.map(email => `
        <div class="email-item border-b border-gray-200 p-4 hover:bg-gray-50 cursor-pointer transition-all"
             onclick="selectEmail('${email.id}')">
            <div class="flex justify-between items-start mb-1">
                <div class="flex-1">
                    <div class="flex items-center gap-2">
                        <span class="font-semibold text-gray-900 text-sm">${escapeHtml(email.from)}</span>
                        ${email.isHuman ? '<span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">👤 Human</span>' : '<span class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">🤖 Auto</span>'}
                        ${email.unread ? '<span class="w-2 h-2 bg-blue-600 rounded-full"></span>' : ''}
                    </div>
                    <div class="text-sm font-medium text-gray-800 line-clamp-1">${escapeHtml(email.subject)}</div>
                    <div class="text-xs text-gray-600 line-clamp-2">${escapeHtml(email.preview || email.body || '')}</div>
                </div>
                <div class="text-xs text-gray-500 ml-2">${formatTime(email.timestamp)}</div>
            </div>
            <div class="flex gap-2 mt-2">
                <button onclick="event.stopPropagation(); draftReplyForEmail('${email.id}')"
                        class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded font-semibold">
                    ✍️ Draft Reply
                </button>
                <button onclick="event.stopPropagation(); markAsRead('${email.id}')"
                        class="text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-1 rounded font-semibold">
                    ✓ Read
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Select an email to view details
 */
function selectEmail(emailId) {
    const email = window.communicationsState.emails.find(e => e.id === emailId);
    if (!email) return;

    window.communicationsState.selectedEmail = email;

    const detailPanel = document.getElementById('email-detail');
    const detailContent = document.getElementById('email-detail-content');

    detailContent.innerHTML = `
        <div class="space-y-3">
            <div>
                <div class="text-xs text-gray-500 mb-1">From:</div>
                <div class="font-semibold text-sm">${escapeHtml(email.from)}</div>
            </div>
            <div>
                <div class="text-xs text-gray-500 mb-1">Subject:</div>
                <div class="font-semibold text-sm">${escapeHtml(email.subject)}</div>
            </div>
            <div>
                <div class="text-xs text-gray-500 mb-1">Date:</div>
                <div class="text-sm">${formatTime(email.timestamp)}</div>
            </div>
            <div>
                <div class="text-xs text-gray-500 mb-1">Message:</div>
                <div class="text-sm text-gray-800 whitespace-pre-wrap">${escapeHtml(email.body || email.preview || '')}</div>
            </div>
            <div class="flex gap-2">
                ${email.isHuman ? '<span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">👤 From Human</span>' : '<span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">🤖 Automated</span>'}
                ${email.unread ? '<span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Unread</span>' : ''}
            </div>
        </div>
    `;

    detailPanel.classList.remove('hidden');

    // Mark all email items as unselected, then select this one
    document.querySelectorAll('.email-item').forEach(item => item.classList.remove('selected'));
    event.target.closest('.email-item')?.classList.add('selected');
}

/**
 * Draft a reply for selected email
 */
function draftReply() {
    const email = window.communicationsState.selectedEmail;
    if (!email) return;

    draftReplyForEmail(email.id);
}

/**
 * Draft a reply for specific email
 */
async function draftReplyForEmail(emailId) {
    const email = window.communicationsState.emails.find(e => e.id === emailId);
    if (!email) return;

    console.log('[Draft] Generating draft reply for:', emailId);

    try {
        // Call AI to generate draft
        const response = await fetch(`${COMM_API}/voice-agent/draft-reply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_id: emailId,
                email_subject: email.subject,
                email_body: email.body || email.preview,
                email_from: email.from
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to generate draft: ${response.status}`);
        }

        const data = await response.json();
        const draft = {
            id: `draft_${Date.now()}`,
            email_id: emailId,
            to: email.from,
            subject: `Re: ${email.subject}`,
            body: data.draft_text || data.text || '',
            timestamp: new Date().toISOString()
        };

        // Add to drafts
        window.communicationsState.drafts.push(draft);
        renderDraftsList();

        // Open draft editor
        openDraftEditor(draft);

    } catch (error) {
        console.error('[Draft] Error generating draft:', error);
        showNotification('Failed to generate draft. Please try again.', 'error');
    }
}

/**
 * Render drafts list
 */
function renderDraftsList() {
    const draftsList = document.getElementById('drafts-list');
    const draftsCount = document.getElementById('drafts-count');
    const drafts = window.communicationsState.drafts;

    draftsCount.textContent = drafts.length;

    if (drafts.length === 0) {
        draftsList.innerHTML = `
            <div class="p-4 text-center text-xs text-gray-500">No drafts pending</div>
        `;
        return;
    }

    draftsList.innerHTML = drafts.map(draft => `
        <div class="border-b border-gray-200 p-3 hover:bg-gray-50 cursor-pointer"
             onclick="openDraftEditor('${draft.id}')">
            <div class="text-sm font-semibold text-gray-900 line-clamp-1">${escapeHtml(draft.subject)}</div>
            <div class="text-xs text-gray-600 line-clamp-2">${escapeHtml(draft.body)}</div>
            <div class="text-xs text-gray-500 mt-1">To: ${escapeHtml(draft.to)}</div>
            <div class="flex gap-2 mt-2">
                <button onclick="event.stopPropagation(); openDraftEditor('${draft.id}')"
                        class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded">
                    ✏️ Edit
                </button>
                <button onclick="event.stopPropagation(); quickApproveDraft('${draft.id}')"
                        class="text-xs bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded">
                    ✓ Send
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Open draft editor
 */
function openDraftEditor(draftIdOrObject) {
    let draft;
    if (typeof draftIdOrObject === 'string') {
        draft = window.communicationsState.drafts.find(d => d.id === draftIdOrObject);
    } else {
        draft = draftIdOrObject;
    }

    if (!draft) return;

    window.communicationsState.selectedDraft = draft;

    document.getElementById('draft-to').value = draft.to;
    document.getElementById('draft-subject').value = draft.subject;
    document.getElementById('draft-body').value = draft.body;

    document.getElementById('draft-editor-modal').classList.remove('hidden');
}

/**
 * Close draft editor
 */
function closeDraftEditor() {
    document.getElementById('draft-editor-modal').classList.add('hidden');
    window.communicationsState.selectedDraft = null;
}

/**
 * Save draft changes
 */
function saveDraft() {
    const draft = window.communicationsState.selectedDraft;
    if (!draft) return;

    draft.subject = document.getElementById('draft-subject').value;
    draft.body = document.getElementById('draft-body').value;

    renderDraftsList();
    closeDraftEditor();

    showNotification('Draft saved successfully!', 'success');
}

/**
 * Approve and send draft
 */
async function approveSendDraft() {
    const draft = window.communicationsState.selectedDraft;
    if (!draft) return;

    // Update draft with latest edits
    draft.subject = document.getElementById('draft-subject').value;
    draft.body = document.getElementById('draft-body').value;

    showConfirmDialog(`Send email to ${draft.to}?`, async () => {
        try {
            console.log('[Send] Sending email:', draft);

            const response = await fetch(`${COMM_API}/voice-agent/send-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    to: draft.to,
                    subject: draft.subject,
                    body: draft.body
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to send email: ${response.status}`);
            }

            // Remove from drafts
            window.communicationsState.drafts = window.communicationsState.drafts.filter(d => d.id !== draft.id);
            renderDraftsList();
            closeDraftEditor();

            showNotification('Email sent successfully!', 'success');

        } catch (error) {
            console.error('[Send] Error sending email:', error);
            showNotification('Failed to send email. Please try again.', 'error');
        }
    });
}

/**
 * Quick approve and send draft (without opening editor)
 */
async function quickApproveDraft(draftId) {
    const draft = window.communicationsState.drafts.find(d => d.id === draftId);
    if (!draft) return;

    window.communicationsState.selectedDraft = draft;
    await approveSendDraft();
}

/**
 * Discard draft
 */
function discardDraft() {
    const draft = window.communicationsState.selectedDraft;
    if (!draft) return;

    showConfirmDialog('Discard this draft?', () => {
        window.communicationsState.drafts = window.communicationsState.drafts.filter(d => d.id !== draft.id);
        renderDraftsList();
        closeDraftEditor();
        showNotification('Draft discarded', 'info');
    });
}

/**
 * Mark email as read
 */
async function markAsRead(emailId) {
    try {
        const response = await fetch(`${COMM_API}/voice-agent/mark-read/${emailId}`, {
            method: 'POST'
        });

        if (response.ok) {
            const email = window.communicationsState.emails.find(e => e.id === emailId);
            if (email) {
                email.unread = false;
                renderEmailList();
            }
        }
    } catch (error) {
        console.error('[Email] Error marking as read:', error);
    }
}

/**
 * Switch category filter
 */
function switchCategory(category) {
    window.communicationsState.currentCategory = category;

    // Update button styles
    document.querySelectorAll('.category-tab').forEach(btn => {
        btn.classList.remove('bg-blue-100', 'text-blue-800');
        btn.classList.add('bg-gray-100', 'text-gray-700');
    });

    const activeBtn = document.getElementById(`cat-${category}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-gray-100', 'text-gray-700');
        activeBtn.classList.add('bg-blue-100', 'text-blue-800');
    }

    renderEmailList();
}

/**
 * Update category badges with counts
 */
function updateCategoryBadges() {
    const emails = window.communicationsState.emails;

    // Count all
    document.getElementById('badge-all').textContent = emails.length;

    // Count by category
    const counts = {
        human: emails.filter(e => e.isHuman).length,
        automated: emails.filter(e => !e.isHuman).length,
        urgent: emails.filter(e => e.category === 'urgent').length,
        work: emails.filter(e => e.category === 'work').length,
        personal: emails.filter(e => e.category === 'personal').length
    };

    Object.entries(counts).forEach(([cat, count]) => {
        const badge = document.getElementById(`badge-${cat}`);
        if (badge) badge.textContent = count;
    });

    // Update important highlights
    renderImportantHighlights();
}

/**
 * Detect if email is important/urgent
 */
function detectImportant(email) {
    const subject = (email.subject || '').toLowerCase();
    const body = (email.body || email.preview || '').toLowerCase();

    // Important indicators
    const indicators = [
        'urgent', 'asap', 'important', 'critical', 'deadline',
        'action required', 'immediate', 'emergency', 'priority',
        'time sensitive', 'respond by', 'due date', 'follow up required',
        'needs attention', 'high priority'
    ];

    return indicators.some(indicator =>
        subject.includes(indicator) || body.includes(indicator)
    );
}

/**
 * Render important highlights section
 */
function renderImportantHighlights() {
    const important = window.communicationsState.emails
        .filter(e => detectImportant(e))
        .slice(0, 5); // Top 5 important

    const list = document.getElementById('important-list');
    const countBadge = document.getElementById('important-count');

    if (!list || !countBadge) return;

    countBadge.textContent = important.length;

    if (important.length === 0) {
        list.innerHTML = '<p class="text-xs text-gray-500 text-center">No urgent items</p>';
        return;
    }

    list.innerHTML = important.map(email => `
        <div class="bg-white rounded p-2 cursor-pointer hover:bg-red-50 transition-all border border-red-100"
             onclick="selectEmail('${email.id}')">
            <div class="text-xs font-semibold text-gray-900 line-clamp-1">
                ${escapeHtml(email.subject)}
            </div>
            <div class="text-xs text-gray-600 mt-1">
                From: ${escapeHtml(email.from)}
            </div>
            <div class="text-xs text-red-600 mt-1">
                ${formatTime(email.timestamp)}
            </div>
        </div>
    `).join('');
}

/**
 * Switch calendar view (day/week)
 */
function switchCalendarView(view) {
    window.communicationsState.calendarView = view;

    // Update button styles
    document.getElementById('cal-day').className =
        view === 'day' ? 'flex-1 px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded font-semibold'
                       : 'flex-1 px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded';

    document.getElementById('cal-week').className =
        view === 'week' ? 'flex-1 px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded font-semibold'
                        : 'flex-1 px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded';

    // Reload calendar with new view
    loadCalendar(view);
}

/**
 * Load calendar events
 */
async function loadCalendar(view = null) {
    const calendarView = view || window.communicationsState.calendarView;
    console.log('[Calendar] Loading events for:', calendarView);

    try {
        const url = new URL(`${COMM_API}/voice-agent/calendar`);
        url.searchParams.set('timeframe', calendarView);

        const response = await fetch(url.toString());

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        window.communicationsState.calendar = data.events || [];

        renderCalendar();

    } catch (error) {
        console.error('[Calendar] Error loading events:', error);
        document.getElementById('calendar-list').innerHTML = `
            <div class="text-center text-xs text-red-500 py-4">Failed to load calendar</div>
        `;
    }
}

/**
 * Render calendar events
 */
function renderCalendar() {
    const calendarList = document.getElementById('calendar-list');
    const events = window.communicationsState.calendar;

    if (events.length === 0) {
        calendarList.innerHTML = `
            <div class="text-center text-xs text-gray-500 py-4">No events today</div>
        `;
        return;
    }

    calendarList.innerHTML = events.map(event => {
        const color = getEventColor(event);
        return `
            <div class="calendar-event bg-white rounded-lg p-2 shadow-sm" style="border-left-color: ${color};">
                <div class="text-sm font-semibold text-gray-900">${escapeHtml(event.title)}</div>
                <div class="text-xs text-gray-600">${formatEventTime(event.start, event.end)}</div>
                ${event.location ? `<div class="text-xs text-gray-500">📍 ${escapeHtml(event.location)}</div>` : ''}
            </div>
        `;
    }).join('');
}

/**
 * Get color for calendar event
 */
function getEventColor(event) {
    const title = event.title.toLowerCase();
    if (title.includes('meeting')) return '#3b82f6'; // blue
    if (title.includes('call')) return '#8b5cf6'; // purple
    if (title.includes('deadline')) return '#ef4444'; // red
    return '#10b981'; // green
}

/**
 * Format event time
 */
function formatEventTime(start, end) {
    const startTime = new Date(start).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    const endTime = new Date(end).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    return `${startTime} - ${endTime}`;
}

/**
 * Refresh calendar
 */
function refreshCalendar() {
    loadCalendar();
}

/**
 * Load quick reminders
 */
function loadReminders() {
    const remindersList = document.getElementById('reminders-list');
    const reminders = window.communicationsState.reminders;

    if (reminders.length === 0) {
        remindersList.innerHTML = `
            <div class="text-xs text-gray-500 text-center py-2">No reminders</div>
        `;
        return;
    }

    remindersList.innerHTML = reminders.map((reminder, index) => `
        <div class="flex items-center justify-between bg-white rounded p-2 text-xs">
            <span class="flex-1">${escapeHtml(reminder.text)}</span>
            <button onclick="removeReminder(${index})" class="text-red-600 hover:text-red-700 ml-2">✕</button>
        </div>
    `).join('');
}

/**
 * Add quick reminder
 */
function addQuickReminder() {
    showInputDialog('Enter reminder:', (text) => {
        window.communicationsState.reminders.push({
            text,
            timestamp: new Date().toISOString()
        });

        loadReminders();
        showNotification('Reminder added', 'success');
    });
}

/**
 * Remove reminder
 */
function removeReminder(index) {
    window.communicationsState.reminders.splice(index, 1);
    loadReminders();
}

/**
 * Compose new email
 */
function composeNewEmail() {
    const draft = {
        id: `draft_${Date.now()}`,
        to: '',
        subject: '',
        body: '',
        timestamp: new Date().toISOString()
    };

    window.communicationsState.drafts.push(draft);
    renderDraftsList();
    openDraftEditor(draft);
}

/**
 * Refresh all communications
 */
function refreshCommunications() {
    loadAllEmails();
    loadCalendar();
    loadReminders();
}

/**
 * Format timestamp
 */
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

    return date.toLocaleDateString();
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show error
 */
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="p-6 text-center text-red-600">
                <p class="text-sm font-semibold">Error: ${message}</p>
                <button onclick="refreshCommunications()"
                        class="mt-2 text-xs bg-blue-600 text-white px-3 py-1 rounded">
                    Retry
                </button>
            </div>
        `;
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    console.log('[Communications] Initializing...');
    refreshCommunications();

    // Auto-refresh every 60 seconds
    setInterval(() => {
        console.log('[Communications] Auto-refreshing...');
        loadAllEmails();
        loadCalendar();
    }, 60000);
});
