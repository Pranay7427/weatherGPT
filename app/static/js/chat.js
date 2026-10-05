// Conversational WeatherGPT AI Agent UI Logic
const defaultWelcomeMessage = {
    sender: "agent",
    text: "Namaste! I am **WeatherGPT**, your meteorological intelligence AI assistant. Ask me about live weather, 7-day forecasts, crop advisories for farmers, aviation METAR/TAF briefings, marine safety, or extreme disaster warnings.",
    source: "WeatherGPT Core",
    lang: "en"
};

let chatMessages = [defaultWelcomeMessage];

function initChatUI() {
    renderChatMessages();
    const input = document.getElementById("chat-query-input");
    if (input) {
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                handleChatSubmit();
            }
        });
    }
}

function renderChatMessages() {
    const container = document.getElementById("chat-messages-container");
    if (!container) return;

    container.innerHTML = chatMessages.map((msg, idx) => {
        const isUser = msg.sender === "user";
        const formattedText = formatMarkdown(msg.text);

        return `
            <div class="chat-bubble ${isUser ? 'user' : 'agent'}">
                ${!isUser && msg.source ? `<div class="chat-source-badge">⚡ ${msg.source}</div>` : ''}
                <div class="chat-text">${formattedText}</div>
                ${!isUser ? `
                    <div class="chat-actions">
                        <button class="btn-tts" onclick="speakMessage(${idx})" title="Listen to audio response">
                            🔊 Read Aloud
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }).join("");

    container.scrollTop = container.scrollHeight;
}

function formatMarkdown(text) {
    if (!text) return "";
    let html = text
        .replace(/\n\n/g, "<br><br>")
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
        .replace(/\*(.*?)\*/g, "<i>$1</i>")
        .replace(/`(.*?)`/g, "<code style='background:rgba(0,0,0,0.3);padding:2px 6px;border-radius:4px;'>$1</code>");
    return html;
}

async function handleChatSubmit() {
    const input = document.getElementById("chat-query-input");
    if (!input) return;
    const query = input.value.trim();
    if (!query) return;

    // Append user message
    chatMessages.push({ sender: "user", text: query });
    input.value = "";
    renderChatMessages();

    // Show typing placeholder
    const typingId = "typing-" + Date.now();
    const container = document.getElementById("chat-messages-container");
    if (container) {
        const typingEl = document.createElement("div");
        typingEl.id = typingId;
        typingEl.className = "chat-bubble agent";
        typingEl.innerHTML = `
            <div style="display:flex;align-items:center;gap:6px;color:#94a3b8;font-size:13px;">
                <span class="sound-wave"><span></span><span></span><span></span></span>
                Analyzing meteorological models & intent...
            </div>
        `;
        container.appendChild(typingEl);
        container.scrollTop = container.scrollHeight;
    }

    const state = window.weatherAppState || { lat: 28.6139, lon: 77.2090, cityName: "New Delhi", lang: "en" };
    const savedApiKey = localStorage.getItem("weathergpt_gemini_key") || "";

    try {
        const resp = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                latitude: state.lat,
                longitude: state.lon,
                location_name: state.cityName,
                language: state.lang,
                gemini_api_key: savedApiKey
            })
        });

        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        if (resp.ok) {
            const data = await resp.json();
            chatMessages.push({
                sender: "agent",
                text: data.text,
                source: data.source || "WeatherGPT Core",
                lang: data.language || state.lang
            });
            renderChatMessages();

            // Auto speak if user used mic
            if (window.voiceAssistant && window.voiceAssistant.isListening) {
                window.voiceAssistant.speak(data.text, data.language || state.lang);
            }
        } else {
            throw new Error("Chat response failed");
        }
    } catch (e) {
        console.error("Chat error:", e);
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        chatMessages.push({
            sender: "agent",
            text: "⚠️ An error occurred while retrieving meteorological insights. Please check connection and try again.",
            source: "System Error"
        });
        renderChatMessages();
    }
}

function sendQuickPrompt(promptText) {
    const input = document.getElementById("chat-query-input");
    if (input) {
        input.value = promptText;
        handleChatSubmit();
    }
}

function speakMessage(idx) {
    const msg = chatMessages[idx];
    if (msg && window.voiceAssistant) {
        window.voiceAssistant.speak(msg.text, msg.lang || "en");
    }
}

window.initChatUI = initChatUI;
window.handleChatSubmit = handleChatSubmit;
window.sendQuickPrompt = sendQuickPrompt;
window.speakMessage = speakMessage;
