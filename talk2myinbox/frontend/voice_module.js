/**
 * Voice Interaction Module
 * Supports 3 modes: Text, Semi-Voice, Full-Voice
 */

const VOICE_API = (window.DASHBOARD_CONFIG?.api?.baseUrl) || 'http://localhost:8000';

// Voice state management
window.voiceState = {
    mode: 'text', // 'text', 'semi-voice', 'full-voice'
    isRecording: false,
    isPlaying: false,
    recognition: null,
    mediaRecorder: null,
    audioChunks: [],
    currentAudio: null
};

/**
 * Initialize voice module
 */
function initVoiceModule() {
    console.log('[Voice] Initializing voice module...');

    // Check browser support
    checkBrowserSupport();

    // Initialize Web Speech API if available
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
        initSpeechRecognition();
    }

    console.log('[Voice] Voice module initialized');
}

/**
 * Check browser support for voice features
 */
function checkBrowserSupport() {
    const support = {
        speechRecognition: !!(window.SpeechRecognition || window.webkitSpeechRecognition),
        mediaRecorder: !!navigator.mediaDevices?.getUserMedia,
        audioContext: !!(window.AudioContext || window.webkitAudioContext)
    };

    console.log('[Voice] Browser support:', support);

    // Update UI based on support
    if (!support.speechRecognition && !support.mediaRecorder) {
        console.warn('[Voice] Limited voice support - Full voice mode may not work');
        updateVoiceStatus('Limited browser support', 'warning');
    }

    return support;
}

/**
 * Switch interaction mode
 */
function switchVoiceMode(mode) {
    console.log(`[Voice] Switching to ${mode} mode`);

    // Stop any ongoing activity
    stopRecording();
    stopAudioPlayback();

    window.voiceState.mode = mode;

    // Update UI
    updateModeButtons(mode);
    updateVoicePanel(mode);

    // Show mode-specific instructions
    showModeInstructions(mode);
}

/**
 * Update mode selector buttons
 */
function updateModeButtons(activeMode) {
    const modes = ['text', 'semi-voice', 'full-voice'];

    modes.forEach(mode => {
        const btn = document.getElementById(`mode-${mode}`);
        if (btn) {
            if (mode === activeMode) {
                btn.classList.add('bg-indigo-600', 'text-white');
                btn.classList.remove('bg-gray-100', 'text-gray-700');
            } else {
                btn.classList.remove('bg-indigo-600', 'text-white');
                btn.classList.add('bg-gray-100', 'text-gray-700');
            }
        }
    });
}

/**
 * Update voice panel based on mode
 */
function updateVoicePanel(mode) {
    const textInput = document.getElementById('voice-text-input');
    const micButton = document.getElementById('voice-mic-button');
    const sendButton = document.getElementById('voice-send-button');

    if (!textInput || !micButton || !sendButton) return;

    switch (mode) {
        case 'text':
            textInput.classList.remove('hidden');
            micButton.classList.add('hidden');
            sendButton.classList.remove('hidden');
            textInput.placeholder = 'Type your query here...';
            break;

        case 'semi-voice':
            textInput.classList.remove('hidden');
            micButton.classList.add('hidden');
            sendButton.classList.remove('hidden');
            textInput.placeholder = 'Type your query (response will be spoken)...';
            break;

        case 'full-voice':
            textInput.classList.add('hidden');
            micButton.classList.remove('hidden');
            sendButton.classList.add('hidden');
            break;
    }
}

/**
 * Show mode-specific instructions
 */
function showModeInstructions(mode) {
    const instructions = {
        'text': 'Type your query and click Send',
        'semi-voice': 'Type your query and hear the AI response',
        'full-voice': 'Click the microphone to speak your query'
    };

    updateVoiceStatus(instructions[mode], 'info');
}

/**
 * Handle text query submission
 */
async function submitTextQuery() {
    const input = document.getElementById('voice-text-input');
    const query = input?.value?.trim();

    if (!query) {
        updateVoiceStatus('Please enter a query', 'error');
        return;
    }

    console.log(`[Voice] Submitting query in ${window.voiceState.mode} mode:`, query);

    // Clear input
    input.value = '';

    // Show loading
    updateVoiceStatus('Processing query...', 'loading');
    showQueryInChat(query, 'user');

    try {
        // Send to backend
        const response = await fetch(`${VOICE_API}/voice-agent/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                mode: window.voiceState.mode === 'text' ? 'text' : 'voice'
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const result = await response.json();
        const responseText = result.text || 'No response';

        console.log('[Voice] Response:', result);

        // Show response in chat
        showQueryInChat(responseText, 'assistant');
        updateVoiceStatus('Response received', 'success');

        // If semi-voice or full-voice mode, speak the response
        if (window.voiceState.mode === 'semi-voice' || window.voiceState.mode === 'full-voice') {
            await speakText(responseText);
        }

        // Handle any actions in the response
        handleResponseActions(result);

    } catch (error) {
        console.error('[Voice] Error:', error);
        updateVoiceStatus(`Error: ${error.message}`, 'error');
        showQueryInChat(`Error: ${error.message}`, 'error');
    }
}

/**
 * Initialize Web Speech Recognition API
 */
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('[Voice] Speech Recognition not supported');
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        console.log('[Voice] Speech recognition started');
        window.voiceState.isRecording = true;
        updateVoiceStatus('Listening... Speak now', 'recording');
        updateMicButton(true);
    };

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');

        console.log('[Voice] Transcript:', transcript);

        // Show interim results
        if (event.results[0].isFinal) {
            handleVoiceInput(transcript);
        } else {
            updateVoiceStatus(`Listening: "${transcript}"`, 'recording');
        }
    };

    recognition.onerror = (event) => {
        console.error('[Voice] Speech recognition error:', event.error);
        window.voiceState.isRecording = false;
        updateMicButton(false);

        const errorMessages = {
            'no-speech': 'No speech detected. Please try again.',
            'audio-capture': 'Microphone not accessible. Check permissions.',
            'not-allowed': 'Microphone permission denied.',
            'network': 'Network error. Check your connection.'
        };

        updateVoiceStatus(errorMessages[event.error] || `Error: ${event.error}`, 'error');
    };

    recognition.onend = () => {
        console.log('[Voice] Speech recognition ended');
        window.voiceState.isRecording = false;
        updateMicButton(false);
    };

    window.voiceState.recognition = recognition;
}

/**
 * Start voice recording
 */
function startVoiceRecording() {
    if (window.voiceState.isRecording) {
        stopRecording();
        return;
    }

    console.log('[Voice] Starting voice recording...');

    // Use Web Speech API if available
    if (window.voiceState.recognition) {
        try {
            window.voiceState.recognition.start();
        } catch (error) {
            console.error('[Voice] Failed to start recognition:', error);
            updateVoiceStatus('Failed to start recording', 'error');
        }
    } else {
        // Fallback: record audio and send to backend
        startAudioRecording();
    }
}

/**
 * Start audio recording (fallback method)
 */
async function startAudioRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);

        window.voiceState.audioChunks = [];
        window.voiceState.mediaRecorder = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                window.voiceState.audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(window.voiceState.audioChunks, { type: 'audio/webm' });
            await sendAudioToBackend(audioBlob);

            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        window.voiceState.isRecording = true;
        updateVoiceStatus('Recording... Click again to stop', 'recording');
        updateMicButton(true);

        console.log('[Voice] Audio recording started');

    } catch (error) {
        console.error('[Voice] Failed to access microphone:', error);
        updateVoiceStatus('Microphone access denied', 'error');
    }
}

/**
 * Stop recording
 */
function stopRecording() {
    if (window.voiceState.recognition) {
        try {
            window.voiceState.recognition.stop();
        } catch (error) {
            // Already stopped
        }
    }

    if (window.voiceState.mediaRecorder && window.voiceState.mediaRecorder.state === 'recording') {
        window.voiceState.mediaRecorder.stop();
    }

    window.voiceState.isRecording = false;
    updateMicButton(false);
}

/**
 * Send audio blob to backend for transcription
 */
async function sendAudioToBackend(audioBlob) {
    console.log('[Voice] Sending audio to backend for transcription...');
    updateVoiceStatus('Transcribing audio...', 'loading');

    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        const response = await fetch(`${VOICE_API}/voice-agent/stt`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Transcription failed: ${response.status}`);
        }

        const result = await response.json();
        const transcript = result.transcript || result.text;

        if (transcript) {
            handleVoiceInput(transcript);
        } else {
            throw new Error('No transcript received');
        }

    } catch (error) {
        console.error('[Voice] Transcription error:', error);
        updateVoiceStatus(`Transcription error: ${error.message}`, 'error');
    }
}

/**
 * Handle voice input (transcribed text)
 */
async function handleVoiceInput(transcript) {
    console.log('[Voice] Handling voice input:', transcript);

    showQueryInChat(transcript, 'user');
    updateVoiceStatus('Processing query...', 'loading');

    try {
        const response = await fetch(`${VOICE_API}/voice-agent/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: transcript,
                mode: 'voice'
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const result = await response.json();
        const responseText = result.text || 'No response';

        showQueryInChat(responseText, 'assistant');

        // Speak the response in full-voice mode
        if (window.voiceState.mode === 'full-voice') {
            await speakText(responseText);
        }

        updateVoiceStatus('Ready for next query', 'success');
        handleResponseActions(result);

    } catch (error) {
        console.error('[Voice] Error processing voice input:', error);
        updateVoiceStatus(`Error: ${error.message}`, 'error');
        showQueryInChat(`Error: ${error.message}`, 'error');
    }
}

/**
 * Convert text to speech using ElevenLabs
 */
async function speakText(text) {
    if (!text) return;

    console.log('[Voice] Speaking text:', text.substring(0, 50) + '...');

    // Stop any current playback
    stopAudioPlayback();

    updateVoiceStatus('Generating speech...', 'loading');

    try {
        const response = await fetch(`${VOICE_API}/voice-agent/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error(`TTS Error: ${response.status}`);
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        const audio = new Audio(audioUrl);
        window.voiceState.currentAudio = audio;
        window.voiceState.isPlaying = true;

        audio.onplay = () => {
            updateVoiceStatus('Playing response...', 'playing');
            updateAudioButton(true);
        };

        audio.onended = () => {
            console.log('[Voice] Audio playback finished');
            window.voiceState.isPlaying = false;
            updateVoiceStatus('Ready for next query', 'success');
            updateAudioButton(false);
            URL.revokeObjectURL(audioUrl);
        };

        audio.onerror = (error) => {
            console.error('[Voice] Audio playback error:', error);
            updateVoiceStatus('Audio playback failed', 'error');
            window.voiceState.isPlaying = false;
            updateAudioButton(false);
        };

        await audio.play();

    } catch (error) {
        console.error('[Voice] TTS error:', error);
        updateVoiceStatus(`Speech generation failed: ${error.message}`, 'error');
        window.voiceState.isPlaying = false;
    }
}

/**
 * Stop audio playback
 */
function stopAudioPlayback() {
    if (window.voiceState.currentAudio) {
        window.voiceState.currentAudio.pause();
        window.voiceState.currentAudio.currentTime = 0;
        window.voiceState.currentAudio = null;
    }
    window.voiceState.isPlaying = false;
    updateAudioButton(false);
}

/**
 * Handle response actions (refresh, drafts, etc.)
 */
function handleResponseActions(result) {
    // If response includes drafts, refresh drafts list
    if (result.drafts && result.drafts.length > 0) {
        console.log('[Voice] Response includes drafts, refreshing...');
        if (typeof loadEmailDrafts === 'function') {
            loadEmailDrafts();
        }
    }

    // If response includes executed actions, refresh relevant sections
    if (result.executed && result.executed.length > 0) {
        console.log('[Voice] Actions executed, refreshing...');
        if (typeof refreshCommunications === 'function') {
            setTimeout(refreshCommunications, 1000);
        }
    }
}

/**
 * Update voice status indicator
 */
function updateVoiceStatus(message, type = 'info') {
    const statusEl = document.getElementById('voice-status');
    if (!statusEl) return;

    const icons = {
        info: 'ℹ️',
        success: '✓',
        error: '⚠️',
        loading: '⟳',
        recording: '🎤',
        playing: '🔊'
    };

    const colors = {
        info: 'text-blue-600',
        success: 'text-green-600',
        error: 'text-red-600',
        loading: 'text-gray-600',
        recording: 'text-red-600',
        playing: 'text-purple-600'
    };

    statusEl.innerHTML = `
        <span class="${colors[type]} font-semibold">${icons[type]} ${message}</span>
    `;
}

/**
 * Update microphone button state
 */
function updateMicButton(isRecording) {
    const micButton = document.getElementById('voice-mic-button');
    if (!micButton) return;

    if (isRecording) {
        micButton.classList.add('bg-red-600', 'animate-pulse');
        micButton.classList.remove('bg-indigo-600');
        micButton.innerHTML = '⏹️ Stop';
    } else {
        micButton.classList.remove('bg-red-600', 'animate-pulse');
        micButton.classList.add('bg-indigo-600');
        micButton.innerHTML = '🎤 Speak';
    }
}

/**
 * Update audio playback button
 */
function updateAudioButton(isPlaying) {
    const audioIndicator = document.getElementById('voice-audio-indicator');
    if (!audioIndicator) return;

    if (isPlaying) {
        audioIndicator.classList.remove('hidden');
    } else {
        audioIndicator.classList.add('hidden');
    }
}

/**
 * Show query/response in chat area
 */
function showQueryInChat(text, sender) {
    const chatArea = document.getElementById('voice-chat-area');
    if (!chatArea) return;

    const messageEl = document.createElement('div');
    messageEl.className = `mb-3 ${sender === 'user' ? 'text-right' : 'text-left'}`;

    const bubbleClass = sender === 'user'
        ? 'bg-indigo-600 text-white'
        : sender === 'error'
        ? 'bg-red-100 text-red-800'
        : 'bg-gray-100 text-gray-800';

    messageEl.innerHTML = `
        <div class="inline-block ${bubbleClass} px-4 py-2 rounded-lg max-w-[80%] text-sm">
            ${escapeHtml(text)}
        </div>
    `;

    chatArea.appendChild(messageEl);
    chatArea.scrollTop = chatArea.scrollHeight;
}

/**
 * Clear chat history
 */
function clearVoiceChat() {
    const chatArea = document.getElementById('voice-chat-area');
    if (chatArea) {
        chatArea.innerHTML = '';
    }
    updateVoiceStatus('Chat cleared', 'info');
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceModule);
} else {
    initVoiceModule();
}

console.log('[Voice] Voice module loaded');
