/**
 * Pfula Chat Engine — Premium WhatsApp-style conversation
 * WebSocket streaming with buttery-smooth UX
 */

let conversationId = null;
let ws = null;
let currentLanguage = 'en';
let isStreaming = false;
let currentStreamBubble = null;
let messageCount = 0;

// --- Sound Effects (subtle, WhatsApp-like) ---
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        try { audioCtx = new AudioCtx(); } catch(e) {}
    }
}

function playSound(type) {
    if (!audioCtx) return;
    try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);

        if (type === 'send') {
            osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1);
            osc.start(audioCtx.currentTime);
            osc.stop(audioCtx.currentTime + 0.1);
        } else if (type === 'receive') {
            osc.frequency.setValueAtTime(800, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(1200, audioCtx.currentTime + 0.06);
            osc.frequency.exponentialRampToValueAtTime(1000, audioCtx.currentTime + 0.12);
            gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
            osc.start(audioCtx.currentTime);
            osc.stop(audioCtx.currentTime + 0.15);
        }
    } catch(e) {}
}

// --- Initialization ---

document.addEventListener('DOMContentLoaded', async () => {
    updateClock();
    setInterval(updateClock, 30000);

    // Initialize audio on first interaction
    document.addEventListener('click', initAudio, { once: true });
    document.addEventListener('keydown', initAudio, { once: true });

    await initConversation();
    connectWebSocket();

    // Focus with slight delay for smooth page load
    setTimeout(() => {
        document.getElementById('message-input').focus();
    }, 300);
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
    if (!conversationId) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${conversationId}`;

    try {
        ws = new WebSocket(wsUrl);
    } catch(e) {
        console.error('WebSocket creation failed:', e);
        return;
    }

    ws.onopen = () => {
        document.getElementById('wa-status').textContent = 'online';
        document.getElementById('wa-status').classList.remove('typing');
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
        // Reconnect with backoff
        setTimeout(connectWebSocket, 3000);
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

    initAudio();
    playSound('send');

    // Add user message with sent animation
    addMessageToChat('user', text, true);

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Hide quick actions with smooth fade
    const quickActions = document.getElementById('quick-actions');
    if (quickActions && quickActions.style.display !== 'none') {
        quickActions.style.transition = 'opacity 0.3s, transform 0.3s';
        quickActions.style.opacity = '0';
        quickActions.style.transform = 'translateY(-8px)';
        setTimeout(() => { quickActions.style.display = 'none'; }, 300);
    }

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
        playSound('receive');
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
        playSound('receive');

        // Create a new assistant message bubble for streaming
        const chatArea = document.getElementById('chat-area');
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message assistant';
        msgDiv.innerHTML = `
            <div class="message-bubble">
                <div class="message-text streaming-cursor" id="streaming-text"></div>
                <div class="message-time">
                    <span>${getCurrentTime()}</span>
                    <svg class="read-receipt" width="16" height="11" viewBox="0 0 16 11"><path d="M11.07 0L5.41 5.67 3.15 3.4 2 4.55l3.41 3.41 6.8-6.82L11.07 0zM8.6 8.22L7.45 9.37l-3.41-3.41L5.19 4.8l2.26 2.26 5.66-5.67L14.25 2.54 8.6 8.22z" fill="#d4a853"/></svg>
                </div>
            </div>
        `;
        chatArea.appendChild(msgDiv);
        currentStreamBubble = document.getElementById('streaming-text');
    }

    // Append text to the streaming bubble
    const rawText = (currentStreamBubble.getAttribute('data-raw') || '') + text;
    currentStreamBubble.setAttribute('data-raw', rawText);
    currentStreamBubble.innerHTML = formatMessage(rawText);

    // Keep cursor class during streaming
    currentStreamBubble.classList.add('streaming-cursor');

    scrollToBottom();
}

function handleStreamComplete(fullText) {
    if (currentStreamBubble) {
        currentStreamBubble.innerHTML = formatMessage(fullText);
        currentStreamBubble.classList.remove('streaming-cursor');
        currentStreamBubble.removeAttribute('id');
        currentStreamBubble.removeAttribute('data-raw');
    }
    currentStreamBubble = null;
    isStreaming = false;

    // Generate smart follow-up suggestions
    showFollowUpSuggestions(fullText);

    scrollToBottom();
}

// --- UI Helpers ---

function addMessageToChat(role, content, justSent) {
    const chatArea = document.getElementById('chat-area');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}${justSent ? ' just-sent' : ''}`;

    messageCount++;

    const timeStr = getCurrentTime();
    const formattedContent = role === 'assistant' ? formatMessage(content) : escapeHtml(content);

    const readReceipt = role === 'user'
        ? '<svg class="read-receipt" width="16" height="11" viewBox="0 0 16 11"><path d="M11.07 0L5.41 5.67 3.15 3.4 2 4.55l3.41 3.41 6.8-6.82L11.07 0zM8.6 8.22L7.45 9.37l-3.41-3.41L5.19 4.8l2.26 2.26 5.66-5.67L14.25 2.54 8.6 8.22z" fill="#d4a853"/></svg>'
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

    // Stagger animation for sequential messages
    msgDiv.style.animationDelay = '0.05s';

    chatArea.appendChild(msgDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.style.display = 'block';
    const status = document.getElementById('wa-status');
    status.textContent = 'typing...';
    status.classList.add('typing');
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.style.display = 'none';
    const status = document.getElementById('wa-status');
    status.textContent = 'online';
    status.classList.remove('typing');
}

function scrollToBottom() {
    const chatArea = document.getElementById('chat-area');
    // Use requestAnimationFrame for smooth scroll
    requestAnimationFrame(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    });
}

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    document.getElementById('current-time').textContent = timeStr;
    // Also update welcome time if it exists
    const welcomeTime = document.getElementById('welcome-time');
    if (welcomeTime) welcomeTime.textContent = timeStr;
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

    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Emoji bullet points: convert raw emoji at line start
    // Keep them as-is, they look great

    // Headers: ### text
    html = html.replace(/^### (.*?)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.*?)$/gm, '<h3>$1</h3>');

    // Bullet points: - text or * text (but not ** bold)
    html = html.replace(/^[\-] (.*?)$/gm, '<span style="padding-left:4px">&#8226; $1</span>');

    // Numbered lists: 1. text
    html = html.replace(/^(\d+)\. (.*?)$/gm, '<span style="padding-left:4px">$1. $2</span>');

    // Phone numbers: make clickable
    html = html.replace(/(\d{3,4}[\s-]?\d{3,4}[\s-]?\d{3,4})/g, '<a href="tel:$1">$1</a>');

    // URLs
    html = html.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');

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
    if (panel.style.display === 'none' || !panel.style.display) {
        panel.style.display = 'block';
    } else {
        panel.style.opacity = '0';
        panel.style.transform = 'translateY(20px)';
        setTimeout(() => {
            panel.style.display = 'none';
            panel.style.opacity = '';
            panel.style.transform = '';
        }, 200);
    }
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
        // Small delay for panel to close
        setTimeout(() => {
            sendQuickMessage(messages[0]);
        }, 250);
    }
}

// --- Voice Input (Web Speech API) ---

let recognition = null;
let isListening = false;

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = true;
    rec.maxAlternatives = 1;

    // Set language based on current toggle
    rec.lang = currentLanguage === 'zu' ? 'zu-ZA' : 'en-ZA';

    rec.onresult = (event) => {
        let transcript = '';
        let isFinal = false;
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
            if (event.results[i].isFinal) isFinal = true;
        }

        const input = document.getElementById('message-input');
        input.value = transcript;
        autoResize(input);

        // Auto-send on final result
        if (isFinal) {
            stopListening();
            setTimeout(() => sendMessage(), 200);
        }
    };

    rec.onend = () => {
        stopListening();
    };

    rec.onerror = (event) => {
        console.error('Speech error:', event.error);
        stopListening();
    };

    return rec;
}

function toggleVoiceInput() {
    initAudio();

    if (isListening) {
        stopListening();
        return;
    }

    // Update language before starting
    recognition = initSpeechRecognition();
    if (!recognition) {
        // Fallback: show a brief message
        const input = document.getElementById('message-input');
        input.placeholder = 'Voice not supported in this browser';
        setTimeout(() => {
            input.placeholder = currentLanguage === 'zu' ? 'Bhala umyalezo' : 'Type a message';
        }, 2000);
        return;
    }

    isListening = true;
    const micBtn = document.getElementById('mic-btn');
    micBtn.classList.add('listening');

    // Update status
    const status = document.getElementById('wa-status');
    status.textContent = 'listening...';
    status.classList.add('typing');

    // Update placeholder
    const input = document.getElementById('message-input');
    input.placeholder = currentLanguage === 'zu' ? 'Khuluma manje...' : 'Speak now...';
    input.value = '';

    playSound('send');

    try {
        recognition.start();
    } catch(e) {
        stopListening();
    }
}

function stopListening() {
    isListening = false;
    const micBtn = document.getElementById('mic-btn');
    if (micBtn) micBtn.classList.remove('listening');

    const status = document.getElementById('wa-status');
    if (status) {
        status.textContent = 'online';
        status.classList.remove('typing');
    }

    const input = document.getElementById('message-input');
    if (input) {
        input.placeholder = currentLanguage === 'zu' ? 'Bhala umyalezo' : 'Type a message';
    }

    if (recognition) {
        try { recognition.stop(); } catch(e) {}
    }
}

// --- Smart Follow-Up Suggestions ---

const FOLLOW_UP_MAP = [
    {
        keywords: ['sassa', 'srd', 'grant', 'social relief', 'declined', 'rejected'],
        suggestions: [
            'How do I appeal this decision?',
            'What documents do I need to reapply?',
            'Help me write a PAJA written reasons request',
        ]
    },
    {
        keywords: ['home affairs', 'smart id', 'id card', 'passport', 'birth certificate'],
        suggestions: [
            'What are my rights under PAJA if they delay?',
            'Can I collect at a bank branch instead?',
            'Help me write a formal escalation letter',
        ]
    },
    {
        keywords: ['tax', 'sars', 'efiling', 'tax return', 'tax bracket'],
        suggestions: [
            'What deductions can I claim?',
            'How do medical tax credits work?',
            'What happens if I file late?',
        ]
    },
    {
        keywords: ['uif', 'unemployment', 'ui-19', 'retrenched', 'maternity'],
        suggestions: [
            'My employer didn\'t register me — what now?',
            'How long will it take to get paid?',
            'Can I claim if I resigned?',
        ]
    },
    {
        keywords: ['municipal', 'rates', 'electricity', 'water', 'ethekwini', 'bill'],
        suggestions: [
            'How do I qualify for indigent support?',
            'Can they disconnect without notice?',
            'Help me dispute this bill formally',
        ]
    },
    {
        keywords: ['company', 'cipc', 'registration', 'annual return', 'deregistered'],
        suggestions: [
            'What are the annual return deadlines?',
            'How do I reinstate a deregistered company?',
            'What BEE level is my company?',
        ]
    },
    {
        keywords: ['property', 'transfer', 'deeds', 'title deed', 'conveyancing'],
        suggestions: [
            'What is the transfer duty on my property?',
            'How long does transfer take?',
            'What if my title deed is lost?',
        ]
    },
    {
        keywords: ['letter', 'formal', 'complaint', 'escalat', 'paja', 'public protector'],
        suggestions: [
            'Can you also draft a Public Protector complaint?',
            'What is the deadline for their response?',
            'What are my next steps if they ignore this?',
        ]
    },
    {
        keywords: ['isibonelelo', 'umama', 'sawubona', 'ngicela', 'imali'],
        suggestions: [
            'Ngicela ungisize ngokubhala incwadi yokukhalaza',
            'Yimaphi amaphepha engiwadingayo?',
            'Ngingathola kanjani usizo ngokushesha?',
        ]
    },
];

function showFollowUpSuggestions(responseText) {
    // Remove any existing follow-ups
    const existing = document.querySelector('.follow-up-suggestions');
    if (existing) existing.remove();

    if (!responseText) return;

    const lower = responseText.toLowerCase();
    let suggestions = null;

    // Find matching suggestions based on response content
    for (const mapping of FOLLOW_UP_MAP) {
        const matchCount = mapping.keywords.filter(k => lower.includes(k)).length;
        if (matchCount >= 1) {
            suggestions = mapping.suggestions;
            break;
        }
    }

    // Fallback generic suggestions
    if (!suggestions) {
        suggestions = [
            'Tell me more about my rights',
            'What documents do I need?',
            'Help me write a formal letter',
        ];
    }

    const chatArea = document.getElementById('chat-area');
    const container = document.createElement('div');
    container.className = 'follow-up-suggestions';

    suggestions.forEach(text => {
        const btn = document.createElement('button');
        btn.className = 'follow-up-btn';
        btn.textContent = text;
        btn.onclick = () => {
            container.style.opacity = '0';
            container.style.transform = 'translateY(-4px)';
            setTimeout(() => container.remove(), 200);
            sendQuickMessage(text);
        };
        container.appendChild(btn);
    });

    chatArea.appendChild(container);
    scrollToBottom();
}
