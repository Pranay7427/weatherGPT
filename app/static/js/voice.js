// Web Speech API Integration for WeatherGPT (STT & TTS)
class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.synth = window.speechSynthesis;
        this.initRecognition();
    }

    initRecognition() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRec) {
            this.recognition = new SpeechRec();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;

            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateUIListening(true);
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const input = document.getElementById("chat-query-input");
                if (input) {
                    input.value = transcript;
                    // Auto submit query
                    if (window.handleChatSubmit) {
                        window.handleChatSubmit();
                    }
                }
            };

            this.recognition.onerror = (e) => {
                console.warn("Speech recognition error:", e.error);
                this.stopListening();
            };

            this.recognition.onend = () => {
                this.stopListening();
            };
        } else {
            console.log("SpeechRecognition not supported in this browser environment.");
        }
    }

    startListening(langCode = "en-IN") {
        if (!this.recognition) {
            alert("Speech recognition is not supported in this browser. Please type your query.");
            return;
        }
        if (this.isListening) {
            this.stopListening();
            return;
        }
        try {
            this.recognition.lang = langCode;
            this.recognition.start();
        } catch (e) {
            console.error("Start speech recognition failed:", e);
        }
    }

    stopListening() {
        this.isListening = false;
        this.updateUIListening(false);
        if (this.recognition) {
            try { this.recognition.stop(); } catch(e){}
        }
    }

    updateUIListening(active) {
        const micBtn = document.getElementById("btn-voice-mic");
        const statusIndicator = document.getElementById("voice-status-indicator");
        if (micBtn) {
            if (active) {
                micBtn.classList.add("listening");
            } else {
                micBtn.classList.remove("listening");
            }
        }
        if (statusIndicator) {
            statusIndicator.style.display = active ? "flex" : "none";
        }
    }

    speak(text, lang = "en") {
        if (!this.synth) return;
        // Cancel ongoing speech
        this.synth.cancel();

        // Strip markdown asterisks and backticks for clean audio speech
        const cleanText = text
            .replace(/\*\*/g, "")
            .replace(/\*/g, "")
            .replace(/`/g, "")
            .replace(/#/g, "")
            .replace(/•/g, ", ");

        const utterance = new SpeechSynthesisUtterance(cleanText);

        // Map language to BCP47
        const langMap = {
            "en": "en-IN",
            "hi": "hi-IN",
            "bn": "bn-IN",
            "te": "te-IN",
            "ta": "ta-IN",
            "mr": "mr-IN",
            "gu": "gu-IN",
            "kn": "kn-IN"
        };
        utterance.lang = langMap[lang] || "en-IN";
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        this.synth.speak(utterance);
    }
}

window.voiceAssistant = new VoiceAssistant();
