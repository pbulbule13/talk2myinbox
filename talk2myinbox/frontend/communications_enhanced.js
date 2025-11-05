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
    threads: {},
    currentPage: 1,
    emailsPerPage: 10
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
    const from = (email.from || '').toLowerCase();
    const subject = (email.subject || '').toLowerCase();
    const preview = (email.preview || email.body || '').toLowerCase();

    // Strong automated email indicators in FROM address
    const strongAutomatedFromIndicators = [
        'noreply', 'no-reply', 'donotreply', 'do-not-reply',
        'automated', 'notification', 'alerts@', 'newsletter',
        'notifications@', 'info@', 'support@', 'team@',
        'hello@', 'welcome@', 'updates@', 'news@',
        'bounces', 'mailer-daemon', 'postmaster',
        'listserv', 'majordomo'
    ];

    // Check if from address has strong automated indicators
    if (strongAutomatedFromIndicators.some(indicator => from.includes(indicator))) {
        return false;
    }

    // Personal email domain indicators (strong signal for human)
    const personalDomains = [
        '@gmail.com', '@yahoo.com', '@outlook.com', '@hotmail.com',
        '@icloud.com', '@aol.com', '@protonmail.com', '@me.com'
    ];

    const isPersonalDomain = personalDomains.some(domain => from.includes(domain));

    // Automated subject patterns
    const automatedSubjectPatterns = [
        'unsubscribe', 'newsletter', 'digest', 'subscription',
        'confirm your', 'verify your', 'reset your password',
        'your order', 'order confirmation', 'receipt from',
        'action required', 'account notification', '[automated]',
        'weekly update', 'monthly update', 'daily update'
    ];

    const hasAutomatedSubject = automatedSubjectPatterns.some(pattern =>
        subject.includes(pattern)
    );

    // Check for reply/forward patterns (strong signal for human conversation)
    const isReplyOrForward = /^(re|fwd|fw):\s*/i.test(email.subject || '');

    // Human conversation indicators (questions, requests, greetings)
    const humanConversationIndicators = [
        'dear ', 'hi ', 'hello ', 'hey ', 'good morning', 'good afternoon',
        'thanks', 'thank you', 'regards', 'best regards', 'sincerely',
        'could you', 'can you', 'would you', 'will you', 'please',
        'let me know', 'get back to me', 'looking forward',
        'what do you think', 'what are your thoughts', 'any questions',
        'just wanted to', 'wanted to reach out', 'wanted to check',
        'hope you', 'hope all', 'hope this finds you',
        'attached is', 'please find attached', 'i\'ve attached',
        'let\'s', 'we should', 'we need to', 'can we',
        'quick question', 'i have a question', 'wondering if'
    ];

    const hasHumanConversation = humanConversationIndicators.some(indicator =>
        preview.includes(indicator) || subject.includes(indicator)
    );

    // Scoring system for better detection
    let humanScore = 0;
    let automatedScore = 0;

    if (isPersonalDomain) humanScore += 3;
    if (isReplyOrForward) humanScore += 2;
    if (hasHumanConversation) humanScore += 2;
    if (hasAutomatedSubject) automatedScore += 2;

    // Check for automated content patterns
    const automatedContentPatterns = [
        'unsubscribe', 'this is an automated message',
        'do not reply to this email', 'this email was sent automatically',
        'click here to confirm', 'verify your email',
        'your verification code', 'opt out', 'manage preferences'
    ];

    if (automatedContentPatterns.some(pattern => preview.includes(pattern))) {
        automatedScore += 2;
    }

    // Final decision based on scores
    if (automatedScore > humanScore) {
        return false;
    }

    if (humanScore > 0) {
        return true;
    }

    // Default: if it looks like a real person's email (has name-like patterns)
    // and doesn't have automated indicators, consider it human
    const hasNamePattern = /^[a-z\s]+<[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}>$/i.test(email.from || '');

    if (hasNamePattern && !hasAutomatedSubject) {
        return true;
    }

    // Default to human if uncertain (better user experience)
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
 * Detect if thread is job application related
 */
function isJobApplicationThread(emails, subject) {
    const jobKeywords = [
        'application', 'interview', 'position', 'job', 'hiring',
        'candidate', 'resume', 'cv', 'opportunity', 'recruiter',
        'recruitment', 'apply', 'vacancy', 'career'
    ];

    const subjectLower = subject.toLowerCase();
    const hasJobKeyword = jobKeywords.some(keyword => subjectLower.includes(keyword));

    // Check if any email content mentions job-related terms
    const hasJobContent = emails.some(email => {
        const content = `${email.subject} ${email.preview || email.body || ''}`.toLowerCase();
        return jobKeywords.some(keyword => content.includes(keyword));
    });

    return hasJobKeyword || hasJobContent;
}

/**
 * Group emails by conversation thread with enhanced detection
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
                unreadCount: 0,
                messageCount: 0,
                isJobApplication: false,
                needsFollowUp: false
            };
        }

        threads[threadKey].emails.push(email);
        threads[threadKey].messageCount++;
        if (email.unread) threads[threadKey].unreadCount++;

        // Update last timestamp
        const emailTime = new Date(email.timestamp || email.date).getTime();
        const threadTime = new Date(threads[threadKey].lastTimestamp).getTime();
        if (emailTime > threadTime) {
            threads[threadKey].lastTimestamp = email.timestamp || email.date;
        }
    });

    // Post-process threads to detect special categories
    Object.values(threads).forEach(thread => {
        // Detect job application threads
        thread.isJobApplication = isJobApplicationThread(thread.emails, thread.subject);

        // Mark threads with >2 messages as needing follow-up
        thread.needsFollowUp = thread.messageCount > 2;

        // Special handling for job applications with >2 emails
        if (thread.isJobApplication && thread.messageCount > 2) {
            thread.category = 'job_application_active';
        } else if (thread.needsFollowUp) {
            thread.category = 'ongoing_conversation';
        }
    });

    // Sort: prioritize threads needing follow-up and recent activity
    return Object.values(threads).sort((a, b) => {
        // First, prioritize job applications with >2 messages
        if (a.isJobApplication && a.messageCount > 2 && !(b.isJobApplication && b.messageCount > 2)) return -1;
        if (b.isJobApplication && b.messageCount > 2 && !(a.isJobApplication && a.messageCount > 2)) return 1;

        // Then, prioritize threads needing follow-up
        if (a.needsFollowUp && !b.needsFollowUp) return -1;
        if (b.needsFollowUp && !a.needsFollowUp) return 1;

        // Finally, sort by timestamp
        return new Date(b.lastTimestamp) - new Date(a.lastTimestamp);
    });
}

/**
 * Load all emails from Gmail
 */
async function loadAllEmails(gmailQuery) {
    console.log('[Communications] Loading Gmail emails...');
    console.log('[Communications] API URL:', COMM_API);

    const emailList = document.getElementById('email-list');

    try {
        const url = new URL(`${COMM_API}/voice-agent/emails-direct`);
        url.searchParams.set('max_results', '30'); // Show 30 emails minimum
        if (gmailQuery) url.searchParams.set('query', gmailQuery);

        console.log('[Communications] Fetching from:', url.toString());

        const response = await fetch(url.toString());

        console.log('[Communications] Response status:', response.status);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('[Communications] Received data:', data);

        const emails = data.emails || [];

        // Check if we're using mock data (mock IDs start with "thread_mock_")
        const usingMockData = emails.length > 0 && emails[0].id && emails[0].id.startsWith('thread_mock_');
        if (usingMockData) {
            console.warn('[Communications] ⚠️ Using MOCK DATA - Gmail token may be expired');
            // Show the warning banner
            const banner = document.getElementById('mock-data-banner');
            if (banner) {
                banner.classList.remove('hidden');
            }
        } else {
            // Hide the banner if using real data
            const banner = document.getElementById('mock-data-banner');
            if (banner) {
                banner.classList.add('hidden');
            }
        }

        if (emails.length === 0) {
            console.warn('[Communications] No emails returned from API');
            emailList.innerHTML = `
                <div class="p-6 text-center text-yellow-600">
                    <p class="text-sm font-semibold">No emails found</p>
                    <p class="text-xs mt-2">Your inbox appears to be empty</p>
                    <button onclick="refreshCommunications()"
                            class="mt-3 text-xs bg-blue-600 text-white px-3 py-1.5 rounded">
                        Refresh
                    </button>
                </div>
            `;
            return;
        }

        // Categorize emails
        console.log('[Communications] Categorizing emails...');
        try {
            window.communicationsState.emails = emails.map(email => ({
                ...email,
                category: categorizeEmail(email),
                isHuman: detectHumanEmail(email),
                timestamp: email.timestamp || email.date
            }));
            console.log('[Communications] ✓ Categorization complete');
        } catch (catError) {
            console.error('[Communications] Error during categorization:', catError);
            // Fallback: use emails without categorization
            window.communicationsState.emails = emails.map(email => ({
                ...email,
                category: 'all',
                isHuman: true,
                timestamp: email.timestamp || email.date
            }));
        }

        // Group by thread
        console.log('[Communications] Grouping by thread...');
        try {
            window.communicationsState.threads = groupEmailsByThread(window.communicationsState.emails);
            console.log(`[Communications] ✓ Created ${window.communicationsState.threads.length} threads`);
        } catch (threadError) {
            console.error('[Communications] Error during thread grouping:', threadError);
            // Fallback: no threading
            window.communicationsState.threads = [];
        }

        console.log(`[Communications] ✓ Loaded ${emails.length} emails, ${window.communicationsState.threads.length} threads`);

        console.log('[Communications] Rendering email list...');
        try {
            renderEmailList();
            console.log('[Communications] ✓ Render complete');
        } catch (renderError) {
            console.error('[Communications] Error during rendering:', renderError);
            // Show error in UI
            emailList.innerHTML = `
                <div class="p-6 text-center text-red-600">
                    <p class="text-sm font-semibold">⚠️ Error Rendering Emails</p>
                    <p class="text-xs mt-2">${escapeHtml(renderError.message)}</p>
                    <p class="text-xs mt-2">Emails loaded but display failed. Check console for details.</p>
                    <button onclick="location.reload()"
                            class="mt-3 text-xs bg-blue-600 text-white px-3 py-1.5 rounded">
                        Reload Page
                    </button>
                </div>
            `;
            throw renderError; // Re-throw to see full stack trace
        }

        updateCategoryBadges();

        // Auto-detect calendar invites
        console.log('[Communications] Auto-detecting calendar invites...');
        try {
            autoDetectCalendarInvites();
        } catch (calError) {
            console.warn('[Communications] Calendar auto-detect failed:', calError);
        }

    } catch (error) {
        console.error('[Communications] ✗ Error loading emails:', error);
        console.error('[Communications] Error stack:', error.stack);

        emailList.innerHTML = `
            <div class="p-6 text-center text-red-600">
                <p class="text-sm font-semibold">⚠️ Error Loading Emails</p>
                <p class="text-xs mt-2 text-gray-700">${escapeHtml(error.message)}</p>
                <p class="text-xs mt-1 text-gray-500">Check console (F12) for details</p>
                <button onclick="refreshCommunications()"
                        class="mt-3 text-xs bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700">
                    🔄 Retry
                </button>
            </div>
        `;

        showNotification('Failed to load emails: ' + error.message, 'error', 5000);
    }
}

/**
 * Render email list with enhanced UI and pagination
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

    // Pagination
    const totalPages = Math.ceil(filteredEmails.length / window.communicationsState.emailsPerPage);
    const currentPage = window.communicationsState.currentPage;
    const startIdx = (currentPage - 1) * window.communicationsState.emailsPerPage;
    const endIdx = startIdx + window.communicationsState.emailsPerPage;
    const paginatedEmails = filteredEmails.slice(startIdx, endIdx);

    const emailsHTML = paginatedEmails.map(email => {
        // Find thread info for this email
        const thread = window.communicationsState.threads?.find(t =>
            t.emails.some(e => e.id === email.id)
        );

        // Format attachments
        const attachments = email.attachments || [];
        const attachmentsHTML = attachments.length > 0 ? `
            <div class="mt-2 flex flex-wrap gap-1">
                ${attachments.map(att => `
                    <a href="${COMM_API}/voice-agent/emails/attachment/${att.messageId}/${att.attachmentId}"
                       download="${escapeHtml(att.filename)}"
                       onclick="event.stopPropagation();"
                       class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded flex items-center gap-1"
                       title="${escapeHtml(att.filename)} (${formatFileSize(att.size)})">
                        📎 ${escapeHtml(att.filename.substring(0, 20))}${att.filename.length > 20 ? '...' : ''}
                    </a>
                `).join('')}
            </div>
        ` : '';

        return `
        <div class="email-item border-b border-gray-200 p-4 hover:bg-gray-50 cursor-pointer transition-all"
             onclick="selectEmail('${email.id}')">
            <div class="flex justify-between items-start mb-1">
                <div class="flex-1">
                    <div class="flex items-center gap-2 flex-wrap">
                        <span class="font-semibold text-gray-900 text-sm">${escapeHtml(email.from)}</span>
                        ${email.isHuman ? '<span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">👤 Human</span>' : '<span class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">🤖 Auto</span>'}
                        ${email.unread ? '<span class="w-2 h-2 bg-blue-600 rounded-full"></span>' : ''}
                        ${thread && thread.messageCount > 2 ? `<span class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">💬 ${thread.messageCount} msgs</span>` : ''}
                        ${thread && thread.isJobApplication ? '<span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">💼 Job App</span>' : ''}
                        ${thread && thread.needsFollowUp ? '<span class="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">⚠️ Follow-up</span>' : ''}
                        ${attachments.length > 0 ? `<span class="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">📎 ${attachments.length}</span>` : ''}
                    </div>
                    <div class="text-sm font-medium text-gray-800 line-clamp-1">${escapeHtml(email.subject)}</div>
                    <div class="text-xs text-gray-600 line-clamp-2">${escapeHtml(email.preview || email.body || '')}</div>
                    ${attachmentsHTML}
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
                ${thread && thread.messageCount > 1 ? `
                <button onclick="event.stopPropagation(); viewThread('${thread.id}')"
                        class="text-xs bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded font-semibold">
                    👁️ View Thread
                </button>
                ` : ''}
            </div>
        </div>
    `;
    }).join('');

    // Pagination controls
    const paginationHTML = totalPages > 1 ? `
        <div class="flex justify-between items-center p-4 border-t border-gray-200 bg-gray-50">
            <div class="text-xs text-gray-600">
                Showing ${startIdx + 1}-${Math.min(endIdx, filteredEmails.length)} of ${filteredEmails.length} emails
            </div>
            <div class="flex gap-2">
                <button onclick="changePage(${currentPage - 1})"
                        ${currentPage === 1 ? 'disabled' : ''}
                        class="px-3 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded font-semibold disabled:opacity-50 disabled:cursor-not-allowed">
                    ← Prev
                </button>
                <div class="text-xs text-gray-600 px-3 py-1">
                    Page ${currentPage} of ${totalPages}
                </div>
                <button onclick="changePage(${currentPage + 1})"
                        ${currentPage === totalPages ? 'disabled' : ''}
                        class="px-3 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded font-semibold disabled:opacity-50 disabled:cursor-not-allowed">
                    Next →
                </button>
            </div>
        </div>
    ` : '';

    emailList.innerHTML = emailsHTML + paginationHTML;
}

/**
 * Change current page
 */
function changePage(page) {
    const category = window.communicationsState.currentCategory;
    let filteredEmails = window.communicationsState.emails;
    if (category !== 'all') {
        filteredEmails = filteredEmails.filter(email => email.category === category);
    }

    const totalPages = Math.ceil(filteredEmails.length / window.communicationsState.emailsPerPage);

    if (page < 1 || page > totalPages) return;

    window.communicationsState.currentPage = page;
    renderEmailList();
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
 * Format file size in human-readable format
 */
function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
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

/**
 * Detect calendar invite in email content
 */
function detectCalendarInvite(email) {
    const subject = (email.subject || '').toLowerCase();
    const body = (email.preview || email.body || '').toLowerCase();
    const content = `${subject} ${body}`;

    // Calendar invite keywords
    const inviteKeywords = [
        'meeting', 'interview', 'call', 'conference', 'appointment',
        'schedule', 'calendar', 'zoom', 'teams', 'google meet',
        'join us', 'invited to', 'booking', 'reservation'
    ];

    // Time patterns
    const timePatterns = [
        /\d{1,2}:\d{2}\s*(am|pm)/gi,
        /\d{1,2}\s*(am|pm)/gi,
        /(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/gi,
        /(tomorrow|today|next week|this week)/gi,
        /\d{1,2}\/\d{1,2}\/\d{2,4}/gi,
        /(january|february|march|april|may|june|july|august|september|october|november|december)/gi
    ];

    const hasInviteKeyword = inviteKeywords.some(keyword => content.includes(keyword));
    const hasTimePattern = timePatterns.some(pattern => pattern.test(content));

    if (hasInviteKeyword && hasTimePattern) {
        // Try to extract meeting details
        return extractMeetingDetails(email);
    }

    return null;
}

/**
 * Extract meeting details from email
 */
function extractMeetingDetails(email) {
    const subject = email.subject || 'Meeting';
    const body = email.preview || email.body || '';

    // Simple extraction (can be enhanced with NLP)
    const timeMatch = body.match(/(\d{1,2}:\d{2}\s*(am|pm)|(\d{1,2}\s*(am|pm)))/i);
    const dateMatch = body.match(/(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|\d{1,2}\/\d{1,2}\/\d{2,4})/i);

    return {
        title: subject.replace(/^(re|fwd|fw):\s*/i, '').trim(),
        suggestedTime: timeMatch ? timeMatch[0] : null,
        suggestedDate: dateMatch ? dateMatch[0] : null,
        duration: 60, // Default 1 hour
        emailId: email.id
    };
}

/**
 * Auto-detect and suggest calendar blocking for emails
 */
async function autoDetectCalendarInvites() {
    const emails = window.communicationsState.emails || [];
    const invites = [];

    emails.forEach(email => {
        const invite = detectCalendarInvite(email);
        if (invite) {
            invites.push(invite);
        }
    });

    if (invites.length > 0) {
        console.log(`[Calendar] Detected ${invites.length} calendar invites`);

        // Show notification to user
        showNotification(
            `Detected ${invites.length} calendar invite(s) in your emails. Click to review.`,
            'info',
            5000
        );

        // Optionally auto-create calendar events
        for (const invite of invites) {
            await proposeCalendarBlock(invite);
        }
    }
}

/**
 * Propose calendar blocking for detected invite
 */
async function proposeCalendarBlock(invite) {
    // Auto-create event without asking for authorization (as requested)
    try {
        const response = await fetch(`${COMM_API}/voice-agent/calendar/event`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: invite.title,
                start: invite.suggestedDate && invite.suggestedTime ?
                    `${invite.suggestedDate} ${invite.suggestedTime}` : new Date().toISOString(),
                duration: invite.duration,
                auto_created: true,
                source_email_id: invite.emailId
            })
        });

        if (response.ok) {
            console.log(`[Calendar] Auto-created event: ${invite.title}`);
        }
    } catch (error) {
        console.error('[Calendar] Error auto-creating event:', error);
    }
}

/**
 * View full conversation thread
 */
function viewThread(threadId) {
    const thread = window.communicationsState.threads?.find(t => t.id === threadId);
    if (!thread) return;

    // Create modal to show thread
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h2 class="text-xl font-bold text-gray-900">${escapeHtml(thread.subject)}</h2>
                    <p class="text-sm text-gray-600">${thread.messageCount} messages • ${thread.participants.length} participants</p>
                    <div class="flex gap-2 mt-2">
                        ${thread.isJobApplication ? '<span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">💼 Job Application</span>' : ''}
                        ${thread.needsFollowUp ? '<span class="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">⚠️ Needs Follow-up</span>' : ''}
                    </div>
                </div>
                <button onclick="this.closest('.fixed').remove()"
                        class="text-gray-500 hover:text-gray-700 text-2xl">
                    ×
                </button>
            </div>
            <div class="space-y-4">
                ${thread.emails.map(email => `
                    <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <div class="font-semibold text-gray-900">${escapeHtml(email.from)}</div>
                                <div class="text-xs text-gray-500">${formatTime(email.timestamp)}</div>
                            </div>
                            ${email.unread ? '<span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Unread</span>' : ''}
                        </div>
                        <div class="text-sm text-gray-800 whitespace-pre-wrap">${escapeHtml(email.body || email.preview || '')}</div>
                        <div class="flex gap-2 mt-3">
                            <button onclick="draftReplyForEmail('${email.id}'); this.closest('.fixed').remove();"
                                    class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded font-semibold">
                                ✍️ Reply
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

/**
 * Get inbox overview with AI reasoning
 */
async function getInboxOverview() {
    try {
        const response = await fetch(`${COMM_API}/voice-agent/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: "Give me a short overview of my inbox. How many interviews do I have this week? What emails need immediate attention?",
                user_id: "user_001",
                mode: "text"
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        const overview = data.response || data.text_response || '';

        // Show overview in notification or modal
        showInboxOverviewModal(overview);

        return overview;
    } catch (error) {
        console.error('[Overview] Error:', error);
        showNotification('Could not generate inbox overview', 'error');
    }
}

/**
 * Show inbox overview modal with voice capability
 */
function showInboxOverviewModal(overview) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-2xl mx-4 shadow-xl">
            <div class="flex justify-between items-start mb-4">
                <h2 class="text-xl font-bold text-gray-900">📬 Inbox Overview</h2>
                <button onclick="this.closest('.fixed').remove()"
                        class="text-gray-500 hover:text-gray-700 text-2xl">
                    ×
                </button>
            </div>
            <div class="text-gray-800 whitespace-pre-wrap mb-4" id="overview-text">${escapeHtml(overview)}</div>
            <div class="flex gap-2">
                <button onclick="speakOverviewText()"
                        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded font-semibold">
                    🔊 Speak
                </button>
                <button onclick="this.closest('.fixed').remove()"
                        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded font-semibold">
                    Close
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add speak function
    window.speakOverviewText = function() {
        const text = document.getElementById('overview-text').textContent;
        speakText(text);
    };
}

/**
 * Speak text using Text-to-Speech
 */
function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        window.speechSynthesis.speak(utterance);
    } else {
        showNotification('Text-to-speech not supported in this browser', 'error');
    }
}

/**
 * Block calendar time (e.g., 1 hour for kids school)
 */
async function blockCalendarTime(title, startTime, duration = 60) {
    try {
        const response = await fetch(`${COMM_API}/voice-agent/calendar/event`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                start: startTime,
                duration: duration,
                auto_created: false
            })
        });

        if (response.ok) {
            showNotification(`Calendar blocked: ${title}`, 'success');
            loadCalendar(); // Refresh calendar
        } else {
            throw new Error(`Failed to block calendar: ${response.status}`);
        }
    } catch (error) {
        console.error('[Calendar] Error blocking time:', error);
        showNotification('Failed to block calendar time', 'error');
    }
}

/**
 * Load Day Summarization with AI reasoning
 */
async function loadDaySummary() {
    console.log('[DaySummary] Loading email summary...');
    const summaryContent = document.getElementById('day-summary-content');

    // Show loading state
    summaryContent.innerHTML = `
        <div class="text-center text-gray-500 py-3">
            <div class="text-sm">Loading summary...</div>
            <div class="text-xs mt-1">Analyzing your inbox</div>
        </div>
    `;

    try {
        const url = new URL(`${COMM_API}/voice-agent/emails/summarize`);
        url.searchParams.set('max_results', '50'); // Analyze 50 emails

        console.log('[DaySummary] Fetching from:', url.toString());

        const response = await fetch(url.toString());

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('[DaySummary] Received data:', data);

        // Build summary HTML
        let summaryHTML = '';

        // Main summary text
        if (data.summary) {
            summaryHTML += `
                <div class="bg-white rounded p-2 mb-2 text-xs text-gray-800 border border-indigo-100">
                    <div class="font-semibold text-indigo-900 mb-1">📝 Overview</div>
                    <div class="whitespace-pre-wrap">${escapeHtml(data.summary)}</div>
                </div>
            `;
        }

        // Store summary data globally for filtering
        window.dailySummaryData = data;

        // Key stats with click handlers to filter inbox
        summaryHTML += `
            <div class="grid grid-cols-2 gap-2 mb-2">
                <div onclick="filterInboxByCategory('all')" class="bg-blue-50 rounded p-2 text-center border border-blue-200 cursor-pointer hover:bg-blue-100 transition-all">
                    <div class="text-lg font-bold text-blue-700">${data.total_analyzed || 0}</div>
                    <div class="text-xs text-blue-600">Emails Analyzed</div>
                </div>
                <div onclick="filterInboxByCategory('urgent')" class="bg-red-50 rounded p-2 text-center border border-red-200 cursor-pointer hover:bg-red-100 transition-all">
                    <div class="text-lg font-bold text-red-700">${data.urgent_count || 0}</div>
                    <div class="text-xs text-red-600">Urgent Items</div>
                </div>
                <div onclick="filterInboxByCategory('need-reply')" class="bg-purple-50 rounded p-2 text-center border border-purple-200 cursor-pointer hover:bg-purple-100 transition-all">
                    <div class="text-lg font-bold text-purple-700">${data.emails_needing_reply || 0}</div>
                    <div class="text-xs text-purple-600">Need Reply</div>
                </div>
                <div onclick="filterInboxByCategory('conversations')" class="bg-green-50 rounded p-2 text-center border border-green-200 cursor-pointer hover:bg-green-100 transition-all">
                    <div class="text-lg font-bold text-green-700">${data.conversation_threads || 0}</div>
                    <div class="text-xs text-green-600">Conversations</div>
                </div>
            </div>
        `;

        // Urgent actions
        if (data.urgent_actions && data.urgent_actions.length > 0) {
            summaryHTML += `
                <div class="bg-red-50 rounded p-2 mb-2 border border-red-200">
                    <div class="font-semibold text-red-900 text-xs mb-1">🚨 Urgent Actions</div>
                    <div class="space-y-1">
                        ${data.urgent_actions.slice(0, 3).map(action => `
                            <div class="text-xs text-red-800">• ${escapeHtml(action)}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Meetings/Interviews
        if (data.meetings && data.meetings.length > 0) {
            summaryHTML += `
                <div class="bg-indigo-50 rounded p-2 mb-2 border border-indigo-200">
                    <div class="font-semibold text-indigo-900 text-xs mb-1">📅 Meetings</div>
                    <div class="space-y-1">
                        ${data.meetings.slice(0, 3).map(meeting => `
                            <div class="text-xs text-indigo-800">• ${escapeHtml(meeting)}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Deadlines
        if (data.deadlines && data.deadlines.length > 0) {
            summaryHTML += `
                <div class="bg-orange-50 rounded p-2 mb-2 border border-orange-200">
                    <div class="font-semibold text-orange-900 text-xs mb-1">⏰ Deadlines</div>
                    <div class="space-y-1">
                        ${data.deadlines.slice(0, 3).map(deadline => `
                            <div class="text-xs text-orange-800">• ${escapeHtml(deadline)}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Decisions needed
        if (data.decisions && data.decisions.length > 0) {
            summaryHTML += `
                <div class="bg-yellow-50 rounded p-2 mb-2 border border-yellow-200">
                    <div class="font-semibold text-yellow-900 text-xs mb-1">🤔 Decisions Needed</div>
                    <div class="space-y-1">
                        ${data.decisions.slice(0, 3).map(decision => `
                            <div class="text-xs text-yellow-800">• ${escapeHtml(decision)}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Follow-ups
        if (data.followups && data.followups.length > 0) {
            summaryHTML += `
                <div class="bg-teal-50 rounded p-2 border border-teal-200">
                    <div class="font-semibold text-teal-900 text-xs mb-1">🔄 Follow-ups</div>
                    <div class="space-y-1">
                        ${data.followups.slice(0, 3).map(followup => `
                            <div class="text-xs text-teal-800">• ${escapeHtml(followup)}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // If no data at all
        if (!summaryHTML) {
            summaryHTML = `
                <div class="text-center text-gray-500 py-3">
                    <div class="text-sm">No summary available</div>
                    <div class="text-xs mt-1">Try refreshing</div>
                </div>
            `;
        }

        summaryContent.innerHTML = summaryHTML;
        console.log('[DaySummary] ✓ Summary loaded successfully');

    } catch (error) {
        console.error('[DaySummary] ✗ Error loading summary:', error);
        summaryContent.innerHTML = `
            <div class="text-center text-red-600 py-3">
                <div class="text-sm font-semibold">⚠️ Error Loading Summary</div>
                <div class="text-xs mt-1">${escapeHtml(error.message)}</div>
                <button onclick="loadDaySummary()"
                        class="mt-2 text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded font-semibold">
                    🔄 Retry
                </button>
            </div>
        `;
        showNotification('Failed to load day summary: ' + error.message, 'error');
    }
}

/**
 * Filter inbox by daily summary category
 * @param {string} category - Category to filter by: 'all', 'urgent', 'need-reply', 'conversations'
 */
function filterInboxByCategory(category) {
    console.log(`[Filter] Filtering inbox by category: ${category}`);

    const emailList = document.getElementById('email-list');
    const allEmails = window.communicationsState.emails;

    if (!allEmails || allEmails.length === 0) {
        showNotification('No emails to filter', 'info');
        return;
    }

    let filteredEmails = [];
    let categoryLabel = '';

    switch(category) {
        case 'all':
            filteredEmails = allEmails;
            categoryLabel = 'All Emails';
            break;

        case 'urgent':
            // Filter emails with urgent keywords (matching backend logic)
            filteredEmails = allEmails.filter(email => {
                const subject = (email.subject || '').toLowerCase();
                const preview = (email.preview || '').toLowerCase();
                const urgentKeywords = ['urgent', 'asap', 'priority', 'immediate', 'critical'];
                return urgentKeywords.some(keyword =>
                    subject.includes(keyword) || preview.includes(keyword)
                );
            });
            categoryLabel = 'Urgent Items';
            break;

        case 'need-reply':
            // Filter unread emails (emails likely needing reply)
            filteredEmails = allEmails.filter(email => email.unread === true);
            categoryLabel = 'Emails Needing Reply';
            break;

        case 'conversations':
            // Filter conversation threads (2+ messages)
            filteredEmails = allEmails.filter(email => {
                // Find thread for this email
                const thread = window.communicationsState.threads?.find(t =>
                    t.emails?.some(e => e.id === email.id)
                );
                return thread && thread.messageCount >= 2;
            });
            categoryLabel = 'Conversation Threads';
            break;

        default:
            filteredEmails = allEmails;
            categoryLabel = 'All Emails';
    }

    console.log(`[Filter] Found ${filteredEmails.length} emails in category: ${category}`);

    // Update state and re-render
    const originalEmails = window.communicationsState.emails;
    window.communicationsState.emails = filteredEmails;
    window.communicationsState.currentPage = 1; // Reset to first page

    // Add filter indicator to inbox
    const inboxContainer = emailList.parentElement;
    let filterIndicator = document.getElementById('filter-indicator');

    if (!filterIndicator) {
        filterIndicator = document.createElement('div');
        filterIndicator.id = 'filter-indicator';
        inboxContainer.insertBefore(filterIndicator, emailList);
    }

    if (category === 'all') {
        // Remove filter indicator
        filterIndicator.innerHTML = '';
        filterIndicator.className = '';
    } else {
        // Show filter indicator
        filterIndicator.className = 'bg-blue-50 border border-blue-200 rounded p-2 mb-2 flex justify-between items-center';
        filterIndicator.innerHTML = `
            <div class="text-sm text-blue-800">
                <span class="font-semibold">🔍 Filtered:</span> ${categoryLabel} (${filteredEmails.length} emails)
            </div>
            <button onclick="filterInboxByCategory('all')"
                    class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded font-semibold">
                Clear Filter
            </button>
        `;
    }

    // Render filtered list
    renderEmailList();

    // Store original emails for restoring later
    if (category !== 'all') {
        window.communicationsState._originalEmails = originalEmails;
    } else if (window.communicationsState._originalEmails) {
        window.communicationsState.emails = window.communicationsState._originalEmails;
        delete window.communicationsState._originalEmails;
    }

    showNotification(`Showing ${filteredEmails.length} ${categoryLabel.toLowerCase()}`, 'success');
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    console.log('[Communications] Initializing...');
    refreshCommunications();

    // Auto-load Daily Summary
    loadDaySummary();

    // Auto-refresh every 60 seconds
    setInterval(() => {
        console.log('[Communications] Auto-refreshing...');
        loadAllEmails();
        loadCalendar();
    }, 60000);
});
