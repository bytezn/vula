/**
 * Pfula Chat Engine — WhatsApp-style conversation interface
 * Handles WebSocket streaming, message rendering, and demo scenarios
 */

let conversationId = null;
let ws = null;
let currentLanguage = 'en';
let isStreaming = false;
let currentStreamBubble = null;

// --- Initialization ---

document.addEventListener('DOMContentLoaded', async () => {
    updateClock();
    setInterval(updateClock, 30000);
    await initConversation();
    connectWebSocket();
    document.getElementById('message-input').focus();
});

async function initConversation() {
    try {
        const resp = await fetch('/api/conversation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'Citizen', language: currentLanguage }),
        });
        const data = await resp.json();
        conversationId = data.conversation_id;
    } catch (e) {
        console.error('Failed to init conversation:', e);
    }
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${conversationId}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        document.getElementById('wa-status').textContent = 'online';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'stream') {
            handleStreamChunk(data.content);
        } else if (data.type === 'complete') {
            handleStreamComplete(data.content);
        }
    };

    ws.onclose = () => {
        document.getElementById('wa-status').textContent = 'connecting...';
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = () => {
        console.error('WebSocket error');
    };
}

// --- Message Handling ---

function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    if (!text || isStreaming) return;

    // Add user message
    addMessageToChat('user', text);

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Hide quick actions on first message
    const quickActions = document.getElementById('quick-actions');
    if (quickActions) quickActions.style.display = 'none';

    // Show typing indicator
    showTypingIndicator();

    // Send via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ message: text }));
    } else {
        // Fallback to REST API
        sendViaRest(text);
    }
}

function sendQuickMessage(text) {
    document.getElementById('message-input').value = text;
    sendMessage();
}

async function sendViaRest(text) {
    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: conversationId,
                message: text,
            }),
        });
        const data = await resp.json();
        hideTypingIndicator();
        addMessageToChat('assistant', data.response);
    } catch (e) {
        hideTypingIndicator();
        addMessageToChat('assistant', 'I\'m having trouble connecting. Please try again.');
    }
}

// --- Stream Handling ---

function handleStreamChunk(text) {
    if (!currentStreamBubble) {
        hideTypingIndicator();
        isStreaming = true;

        // Create a new assistant message bubble for streaming
        const chatArea = document.getElementById('chat-area');
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message assistant';
        msgDiv.innerHTML = `
            <div class="message-bubble">
                <div class="message-text" id="streaming-text"></div>
                <div class="message-time">
                    <span>${getCurrentTime()}</span>
                    <svg class="read-receipt" width="16" height="11" viewBox="0 0 16 11"><path d="M11.07 0L5.41 5.67 3.15 3.4 2 4.55l3.41 3.41 6.8-6.82L11.07 0zM8.6 8.22L7.45 9.37l-3.41-3.41L5.19 4.8l2.26 2.26 5.66-5.67L14.25 2.54 8.6 8.22z" fill="#53bdeb"/></svg>
                </div>
            </div>
        `;
        chatArea.appendChild(msgDiv);
        currentStreamBubble = document.getElementById('streaming-text');
    }

    // Append text to the streaming bubble
    currentStreamBubble.innerHTML = formatMessage(
        currentStreamBubble.getAttribute('data-raw') ?
        currentStreamBubble.getAttribute('data-raw') + text : text
    );
    currentStreamBubble.setAttribute(
        'data-raw',
        (currentStreamBubble.getAttribute('data-raw') || '') + text
    );

    scrollToBottom();
}

function handleStreamComplete(fullText) {
    if (currentStreamBubble) {
        currentStreamBubble.innerHTML = formatMessage(fullText);
        currentStreamBubble.removeAttribute('id');
        currentStreamBubble.removeAttribute('data-raw');
    }
    currentStreamBubble = null;
    isStreaming = false;
    scrollToBottom();
}

// --- UI Helpers ---

function addMessageToChat(role, content) {
    const chatArea = document.getElementById('chat-area');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    const timeStr = getCurrentTime();
    const formattedContent = role === 'assistant' ? formatMessage(content) : escapeHtml(content);

    const readReceipt = role === 'user'
        ? '<svg class="read-receipt" width="16" height="11" viewBox="0 0 16 11"><path d="M11.07 0L5.41 5.67 3.15 3.4 2 4.55l3.41 3.41 6.8-6.82L11.07 0zM8.6 8.22L7.45 9.37l-3.41-3.41L5.19 4.8l2.26 2.26 5.66-5.67L14.25 2.54 8.6 8.22z" fill="#53bdeb"/></svg>'
        : '';

    msgDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-text">${formattedContent}</div>
            <div class="message-time">
                <span>${timeStr}</span>
                ${readReceipt}
            </div>
        </div>
    `;

    chatArea.appendChild(msgDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.style.display = 'block';
    document.getElementById('wa-status').textContent = 'typing...';
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.style.display = 'none';
    document.getElementById('wa-status').textContent = 'online';
}

function scrollToBottom() {
    const chatArea = document.getElementById('chat-area');
    chatArea.scrollTop = chatArea.scrollHeight;
}

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    document.getElementById('current-time').textContent = timeStr;
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
}

// --- Text Formatting ---

function formatMessage(text) {
    if (!text) return '';

    // Escape HTML first
    let html = escapeHtml(text);

    // Bold: **text** or __text__
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

    // Italic: *text* or _text_
    html = html.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');

    // Headers: ### text
    html = html.replace(/^### (.*?)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.*?)$/gm, '<h3>$1</h3>');

    // Bullet points: - text or * text
    html = html.replace(/^[\-\*] (.*?)$/gm, '• $1');

    // Numbered lists: 1. text
    html = html.replace(/^(\d+)\. (.*?)$/gm, '$1. $2');

    // Phone numbers: make clickable
    html = html.replace(/(\d{3,4}[\s-]?\d{3,4}[\s-]?\d{3,4})/g, '<a href="tel:$1">$1</a>');

    // URLs
    html = html.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank">$1</a>');

    // Line breaks
    html = html.replace(/\n/g, '<br>');

    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

// --- Input Handling ---

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// --- Language Toggle ---

function toggleLanguage() {
    currentLanguage = currentLanguage === 'en' ? 'zu' : 'en';
    const label = document.getElementById('lang-label');
    const welcomeText = document.getElementById('welcome-text');

    if (currentLanguage === 'zu') {
        label.textContent = 'ZU';
        document.getElementById('message-input').placeholder = 'Bhala umyalezo';
    } else {
        label.textContent = 'EN';
        document.getElementById('message-input').placeholder = 'Type a message';
    }
}

// --- Demo Panel ---

function toggleDemoPanel() {
    const panel = document.getElementById('demo-panel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

// --- Demo Scenarios ---

const DEMO_SCENARIOS = {
    sassa_rejection: [
        "My SASSA SRD grant was rejected this month. The status just says 'declined' but doesn't tell me why. I haven't been working and I really need this money. What can I do?",
    ],
    home_affairs_delay: [
        "I applied for my Smart ID card at the Durban Home Affairs office 8 months ago. They took my fingerprints and gave me a receipt. I've been back three times and each time they say 'it's still processing'. I need my ID for a job application. What should I do?",
    ],
    municipal_bill: [
        "My eThekwini rates bill this month is R4,200. Last month it was R1,400. Nothing changed in my house. I'm worried they'll cut my electricity if I don't pay. Can you help me understand what happened?",
    ],
    first_tax: [
        "I just got my first job after graduating. My employer says I need to register with SARS and file a tax return. I have no idea where to start. Can you walk me through it step by step?",
    ],
    zulu_sassa: [
        "Sawubona, umama wami oneminyaka engu-65 akayitholi isibonelelo sakhe sempesheni kule nyanga. Sivame ukuyithola ngomhla woku-3 kodwa manje sekuwumhla weshumi nanhlanu futhi ayikafiki. Akazi ukuthi kwenzenjani. Ngicela ungisize.",
    ],
    escalation: [
        "I've been waiting 10 months for my Smart ID from Home Affairs Durban. I've visited three times, called the hotline, and nothing happens. I need a formal complaint letter to escalate this. Can you write one for me? My name is Thandi Nkosi, my ID number is 8501015009081, and my reference number is DUR-2025-44891.",
    ],
};

function runScenario(scenario) {
    toggleDemoPanel();
    const messages = DEMO_SCENARIOS[scenario];
    if (messages && messages.length > 0) {
        sendQuickMessage(messages[0]);
    }
}
