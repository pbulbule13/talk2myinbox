/**
 * Support & Help Center JavaScript
 * Handles AI help, support tickets, and ticket tracking
 */

const SUPPORT_API = (window.DASHBOARD_CONFIG?.api?.baseUrl) || 'http://localhost:8000';

// Global support state
window.supportState = {
    tickets: [],
    currentTab: 'quick-help'
};

/**
 * Open support modal
 */
function openSupportModal() {
    document.getElementById('support-modal').classList.remove('hidden');
    loadMyTickets();
}

/**
 * Close support modal
 */
function closeSupportModal() {
    document.getElementById('support-modal').classList.add('hidden');
}

/**
 * Switch between support tabs
 */
function switchSupportTab(tabName) {
    window.supportState.currentTab = tabName;

    // Hide all tabs
    document.querySelectorAll('.support-tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });

    // Show selected tab
    document.getElementById(`support-tab-${tabName}`).classList.remove('hidden');

    // Update tab buttons
    document.querySelectorAll('[id^="tab-"]').forEach(btn => {
        btn.classList.remove('bg-white', 'text-indigo-600', 'border-b-2', 'border-indigo-600');
        btn.classList.add('text-gray-600');
    });

    const activeBtn = document.getElementById(`tab-${tabName}`);
    activeBtn.classList.add('bg-white', 'text-indigo-600', 'border-b-2', 'border-indigo-600');
    activeBtn.classList.remove('text-gray-600');

    // Load data for specific tabs
    if (tabName === 'my-tickets') {
        loadMyTickets();
    }
}

/**
 * Ask a quick question
 */
async function askQuickQuestion(question) {
    console.log('[Support] Quick question:', question);

    const responseArea = document.getElementById('ai-response-area');
    const responseText = document.getElementById('ai-response-text');

    // Show loading
    responseArea.classList.remove('hidden');
    responseText.innerHTML = '<div class="animate-pulse">Thinking...</div>';

    try {
        const response = await fetch(`${SUPPORT_API}/voice-agent/help`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error('Failed to get help');
        }

        const data = await response.json();
        responseText.innerHTML = data.answer || getDefaultAnswer(question);

    } catch (error) {
        console.error('[Support] Error:', error);
        responseText.innerHTML = getDefaultAnswer(question);
    }
}

/**
 * Ask custom question
 */
async function askCustomQuestion() {
    const input = document.getElementById('quick-help-input');
    const question = input.value.trim();

    if (!question) {
        alert('Please enter a question');
        return;
    }

    await askQuickQuestion(question);
    input.value = '';
}

/**
 * Get default answers for common questions
 */
function getDefaultAnswer(question) {
    const lowerQ = question.toLowerCase();

    if (lowerQ.includes('draft') && lowerQ.includes('reply')) {
        return `
            <p class="mb-3"><strong>To draft a reply to an email:</strong></p>
            <ol class="list-decimal ml-6 space-y-2">
                <li>Find the email in your inbox</li>
                <li>Click the <strong>"✍️ Draft Reply"</strong> button on the email</li>
                <li>Our AI will generate a professional reply for you</li>
                <li>The draft will appear in the <strong>"Pending Drafts"</strong> panel on the right</li>
                <li>You can edit the draft by clicking <strong>"✏️ Edit"</strong></li>
                <li>When ready, click <strong>"✓ Approve & Send"</strong> to send it</li>
            </ol>
            <p class="mt-3 text-sm text-gray-600">💡 Tip: All drafts are fully editable before sending!</p>
        `;
    }

    if (lowerQ.includes('send') && lowerQ.includes('email')) {
        return `
            <p class="mb-3"><strong>There are three ways to send emails:</strong></p>
            <ol class="list-decimal ml-6 space-y-2">
                <li><strong>Reply to an email:</strong> Click "✍️ Draft Reply" on any email, edit it, and click "✓ Approve & Send"</li>
                <li><strong>From drafts panel:</strong> Click "✓ Send" on any pending draft</li>
                <li><strong>Compose new:</strong> Click "✍️ Compose" button at the top of your inbox</li>
            </ol>
            <p class="mt-3 text-sm text-gray-600">💡 All emails are sent through your connected Gmail account.</p>
        `;
    }

    if (lowerQ.includes('categor')) {
        return `
            <p class="mb-3"><strong>Email categorization helps you organize your inbox:</strong></p>
            <ul class="list-disc ml-6 space-y-2">
                <li><strong>👤 From Humans:</strong> Emails from real people (filtered by detecting human language patterns)</li>
                <li><strong>🤖 Automated:</strong> Newsletters, notifications, and system emails</li>
                <li><strong>🚨 Urgent:</strong> Time-sensitive emails with urgent keywords</li>
                <li><strong>💼 Work:</strong> Business and professional emails</li>
                <li><strong>💚 Personal:</strong> Personal correspondence</li>
            </ul>
            <p class="mt-3 text-sm text-gray-600">💡 The AI automatically categorizes emails based on content and sender!</p>
        `;
    }

    if (lowerQ.includes('calendar')) {
        return `
            <p class="mb-3"><strong>Using the Calendar feature:</strong></p>
            <ul class="list-disc ml-6 space-y-2">
                <li>The calendar widget is in the <strong>left sidebar</strong></li>
                <li>It shows <strong>today's schedule</strong> from your Google Calendar</li>
                <li>Events are <strong>color-coded</strong> by type (meetings, calls, deadlines)</li>
                <li>Calendar <strong>auto-refreshes</strong> every 60 seconds</li>
                <li>Click the 🔄 button to manually refresh</li>
            </ul>
            <p class="mt-3 text-sm text-gray-600">💡 Make sure your Google Calendar is connected for real-time updates!</p>
        `;
    }

    // Default response
    return `
        <p class="mb-3">Thank you for your question! Here are some helpful resources:</p>
        <ul class="list-disc ml-6 space-y-2">
            <li>Check out the common questions above for quick guides</li>
            <li>Try asking more specific questions like "How do I draft a reply?"</li>
            <li>If you need personalized help, switch to the <strong>"👤 Contact Support"</strong> tab</li>
        </ul>
        <p class="mt-3 text-sm text-gray-600">💡 Our AI assistant is constantly learning to help you better!</p>
    `;
}

/**
 * Submit support ticket
 */
async function submitSupportTicket(event) {
    event.preventDefault();

    const subject = document.getElementById('support-subject').value;
    const category = document.getElementById('support-category').value;
    const priority = document.getElementById('support-priority').value;
    const description = document.getElementById('support-description').value;
    const email = document.getElementById('support-email').value;

    if (!subject || !category || !description) {
        alert('Please fill in all required fields');
        return;
    }

    console.log('[Support] Submitting ticket...');

    try {
        const response = await fetch(`${SUPPORT_API}/voice-agent/support/ticket`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject,
                category,
                priority,
                description,
                email,
                timestamp: new Date().toISOString()
            })
        });

        if (!response.ok) {
            throw new Error('Failed to submit ticket');
        }

        const data = await response.json();
        const ticketId = data.ticket_id || `TKT-${Date.now()}`;

        // Add to local tickets
        window.supportState.tickets.push({
            id: ticketId,
            subject,
            category,
            priority,
            status: 'open',
            timestamp: new Date().toISOString()
        });

        // Show success message
        document.getElementById('ticket-id-display').textContent = ticketId;
        document.getElementById('support-success-message').classList.remove('hidden');

        // Hide form
        document.getElementById('support-ticket-form').style.display = 'none';

        // Reset form after 3 seconds
        setTimeout(() => {
            resetSupportForm();
            document.getElementById('support-success-message').classList.add('hidden');
            document.getElementById('support-ticket-form').style.display = 'block';
        }, 5000);

        console.log('[Support] Ticket submitted:', ticketId);

    } catch (error) {
        console.error('[Support] Error submitting ticket:', error);
        alert('Failed to submit support ticket. Please try again.');
    }
}

/**
 * Reset support form
 */
function resetSupportForm() {
    document.getElementById('support-subject').value = '';
    document.getElementById('support-category').value = '';
    document.getElementById('support-priority').value = 'medium';
    document.getElementById('support-description').value = '';
    document.getElementById('support-email').value = '';
}

/**
 * Load my tickets
 */
async function loadMyTickets() {
    console.log('[Support] Loading tickets...');

    const ticketsList = document.getElementById('tickets-list');
    const tickets = window.supportState.tickets;

    if (tickets.length === 0) {
        ticketsList.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <p class="text-sm">No tickets yet</p>
                <p class="text-xs mt-2">Your support tickets will appear here</p>
            </div>
        `;
        return;
    }

    ticketsList.innerHTML = tickets.map(ticket => {
        const statusColors = {
            open: 'bg-blue-100 text-blue-800',
            in_progress: 'bg-yellow-100 text-yellow-800',
            resolved: 'bg-green-100 text-green-800',
            closed: 'bg-gray-100 text-gray-800'
        };

        const priorityColors = {
            low: 'text-gray-600',
            medium: 'text-blue-600',
            high: 'text-orange-600',
            critical: 'text-red-600'
        };

        return `
            <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all">
                <div class="flex justify-between items-start mb-2">
                    <div class="flex-1">
                        <div class="font-semibold text-gray-900">${escapeHtml(ticket.subject)}</div>
                        <div class="text-xs text-gray-500 mt-1">
                            Ticket ID: <span class="font-mono">${ticket.id}</span>
                        </div>
                    </div>
                    <span class="text-xs px-2 py-1 rounded-full ${statusColors[ticket.status] || statusColors.open}">
                        ${ticket.status.replace('_', ' ').toUpperCase()}
                    </span>
                </div>
                <div class="flex items-center gap-4 text-xs text-gray-600 mt-3">
                    <span class="${priorityColors[ticket.priority]}">
                        ⚡ ${ticket.priority.toUpperCase()} Priority
                    </span>
                    <span>📂 ${ticket.category.replace('-', ' ')}</span>
                    <span>🕐 ${formatTicketTime(ticket.timestamp)}</span>
                </div>
                <div class="mt-3 flex gap-2">
                    <button onclick="viewTicketDetails('${ticket.id}')"
                            class="text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded">
                        View Details
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * View ticket details
 */
function viewTicketDetails(ticketId) {
    const ticket = window.supportState.tickets.find(t => t.id === ticketId);
    if (!ticket) return;

    alert(`Ticket Details:\n\nID: ${ticket.id}\nSubject: ${ticket.subject}\nCategory: ${ticket.category}\nPriority: ${ticket.priority}\nStatus: ${ticket.status}`);
}

/**
 * Format ticket timestamp
 */
function formatTicketTime(timestamp) {
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

// Initialize when page loads
console.log('[Support] Support system loaded');
