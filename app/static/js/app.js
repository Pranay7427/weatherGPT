// WeatherGPT Master Client Orchestrator
const weatherAppState = {
    lat: 28.6139,
    lon: 77.2090,
    cityName: "New Delhi",
    lang: "en",
    timezone: "Asia/Kolkata",
    utcOffsetSeconds: 19800,
    atmosphere: "sunny",
    currentWeather: null,
    alerts: []
};

window.weatherAppState = weatherAppState;

let deferredInstallPrompt = null;

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initClock();
    initAtmosphericCanvas();
    initEventListeners();
    initChatUI();
    initWebSocket();
    initPWA();
    loadWeatherData(weatherAppState.lat, weatherAppState.lon, weatherAppState.cityName);
});

function initPWA() {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(() => console.log("WeatherGPT PWA Service Worker Registered"))
            .catch(err => console.log("Service Worker Registration error:", err));
    }

    // Capture install prompt for mobile & desktop
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredInstallPrompt = e;
        const installBtn = document.getElementById("btn-install-app");
        if (installBtn) {
            installBtn.style.display = "flex";
            installBtn.onclick = () => {
                deferredInstallPrompt.prompt();
                deferredInstallPrompt.userChoice.then((choice) => {
                    if (choice.outcome === 'accepted') {
                        installBtn.style.display = "none";
                    }
                    deferredInstallPrompt = null;
                });
            };
        }
    });
}

function initEventListeners() {
    // Tab switching
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.dataset.tab;
            switchTab(targetTab);
        });
    });

    // Theme toggle (Dark / Light)
    const themeBtn = document.getElementById("btn-theme-toggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const currentTheme = document.body.getAttribute("data-theme") === "light" ? "light" : "dark";
            const newTheme = currentTheme === "light" ? "dark" : "light";
            applyTheme(newTheme);
        });
    }

    // Language switcher
    const langSelect = document.getElementById("lang-select");
    if (langSelect) {
        langSelect.addEventListener("change", (e) => {
            setLanguage(e.target.value);
        });
    }

    // Search bar input debouncing
    const searchInput = document.getElementById("city-search-input");
    let debounceTimer = null;
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            clearTimeout(debounceTimer);
            const val = e.target.value.trim();
            if (val.length < 2) {
                hideLocationDropdown();
                return;
            }
            debounceTimer = setTimeout(() => {
                fetchLocationSuggestions(val);
            }, 300);
        });
    }

    // Geolocation button
    const locateBtn = document.getElementById("btn-locate-me");
    if (locateBtn) {
        locateBtn.addEventListener("click", handleGeolocation);
    }

    // Voice mic button
    const micBtn = document.getElementById("btn-voice-mic");
    if (micBtn) {
        micBtn.addEventListener("click", () => {
            const bcpMap = {
                "en": "en-IN", "hi": "hi-IN", "bn": "bn-IN", "te": "te-IN",
                "ta": "ta-IN", "mr": "mr-IN", "gu": "gu-IN", "kn": "kn-IN"
            };
            window.voiceAssistant.startListening(bcpMap[weatherAppState.lang] || "en-IN");
        });
    }

    // Phone QR Modal
    const phoneBtn = document.getElementById("btn-open-phone");
    const closePhoneBtn = document.getElementById("btn-close-phone");
    const phoneModal = document.getElementById("phone-modal");

    if (phoneBtn && phoneModal) {
        phoneBtn.addEventListener("click", () => {
            // Determine active host or use detected local IP
            let hostIp = window.location.hostname;
            if (hostIp === "localhost" || hostIp === "127.0.0.1") {
                hostIp = "10.72.55.222"; // User's local Wi-Fi IP
            }
            const phoneUrl = `http://${hostIp}:8000`;
            const displayEl = document.getElementById("phone-url-display");
            const qrImg = document.getElementById("phone-qr-img");

            if (displayEl) displayEl.innerText = phoneUrl;
            if (qrImg) {
                qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(phoneUrl)}`;
            }
            phoneModal.style.display = "flex";
        });
    }
    if (closePhoneBtn && phoneModal) {
        closePhoneBtn.addEventListener("click", () => {
            phoneModal.style.display = "none";
        });
    }

    // Settings Modal
    const settingsBtn = document.getElementById("btn-open-settings");
    const closeSettingsBtn = document.getElementById("btn-close-settings");
    const saveSettingsBtn = document.getElementById("btn-save-settings");
    const settingsModal = document.getElementById("settings-modal");

    if (settingsBtn && settingsModal) {
        settingsBtn.addEventListener("click", () => {
            const keyInput = document.getElementById("gemini-api-key-input");
            if (keyInput) {
                keyInput.value = localStorage.getItem("weathergpt_gemini_key") || "";
            }
            settingsModal.style.display = "flex";
        });
    }
    if (closeSettingsBtn && settingsModal) {
        closeSettingsBtn.addEventListener("click", () => {
            settingsModal.style.display = "none";
        });
    }
    if (saveSettingsBtn && settingsModal) {
        saveSettingsBtn.addEventListener("click", () => {
            const keyInput = document.getElementById("gemini-api-key-input");
            if (keyInput) {
                localStorage.setItem("weathergpt_gemini_key", keyInput.value.trim());
                alert("Settings saved successfully!");
                settingsModal.style.display = "none";
            }
        });
    }
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.tab === tabId);
    });
    document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.toggle("active", pane.id === `tab-${tabId}`);
    });

    // Lazy load specialized tab views
    if (tabId === "radar") {
        setTimeout(() => {
            window.initWeatherMap(weatherAppState.lat, weatherAppState.lon, weatherAppState.cityName);
        }, 100);
    } else if (tabId === "nwp") {
        loadNWPData();
    } else if (tabId === "advisory") {
        window.loadSectorAdvisory("agriculture");
    } else if (tabId === "climate") {
        loadClimateData();
    } else if (tabId === "alerts") {
        loadAlertsView();
    }
}

async function fetchLocationSuggestions(query) {
    try {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!resp.ok) return;
        const data = await resp.json();
        const results = data.results || [];
        showLocationDropdown(results);
    } catch (e) {
        console.error("Geocoding fetch error:", e);
    }
}

function showLocationDropdown(items) {
    const dropdown = document.getElementById("location-dropdown");
    if (!dropdown) return;
    if (items.length === 0) {
        dropdown.style.display = "none";
        return;
    }

    dropdown.innerHTML = items.map(item => `
        <div class="location-item" onclick="selectLocation(${item.latitude}, ${item.longitude}, '${item.name.replace("'", "\\'")}')">
            <div>
                <div class="location-item-name">${item.name}</div>
                <div class="location-item-sub">${item.display_name}</div>
            </div>
            <span style="font-size:12px;color:#38bdf8;">📍 Select</span>
        </div>
    `).join("");

    dropdown.style.display = "block";
}

function hideLocationDropdown() {
    const dropdown = document.getElementById("location-dropdown");
    if (dropdown) dropdown.style.display = "none";
}

function selectLocation(lat, lon, cityName) {
    weatherAppState.lat = lat;
    weatherAppState.lon = lon;
    weatherAppState.cityName = cityName;

    const input = document.getElementById("city-search-input");
    if (input) input.value = cityName;
    hideLocationDropdown();

    loadWeatherData(lat, lon, cityName);
}

function handleGeolocation() {
    if (!("geolocation" in navigator)) {
        alert("Geolocation is not supported on this device.");
        return;
    }

    const input = document.getElementById("city-search-input");
    const locateBtn = document.getElementById("btn-locate");
    if (locateBtn) locateBtn.classList.add("loading");
    if (input) input.value = "Detecting your location...";

    navigator.geolocation.getCurrentPosition(
        async (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            let detectedName = "";

            // 1. Try backend reverse geocoding API
            try {
                const geoResp = await fetch(`/api/reverse-geocode?lat=${lat}&lon=${lon}`);
                if (geoResp.ok) {
                    const geoData = await geoResp.json();
                    if (geoData.name && !geoData.name.startsWith("Location (")) {
                        detectedName = geoData.name;
                    }
                }
            } catch (e) {
                console.warn("Backend reverse-geocode error:", e);
            }

            // 2. Try fast client-side reverse geocoding fallback
            if (!detectedName) {
                try {
                    const clientResp = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
                    if (clientResp.ok) {
                        const data = await clientResp.json();
                        const city = data.city || data.locality || data.principalSubdivision;
                        const state = data.principalSubdivision;
                        if (city && state && city !== state) {
                            detectedName = `${city}, ${state}`;
                        } else if (city) {
                            detectedName = city;
                        }
                    }
                } catch (e) {
                    console.warn("Client reverse-geocode error:", e);
                }
            }

            // 3. Fallback to coordinates
            if (!detectedName) {
                detectedName = `GPS (${lat.toFixed(2)}°, ${lon.toFixed(2)}°)`;
            }

            if (locateBtn) locateBtn.classList.remove("loading");
            selectLocation(lat, lon, detectedName);
        },
        (err) => {
            console.warn("Geolocation denied or error:", err);
            if (locateBtn) locateBtn.classList.remove("loading");
            if (input) input.value = weatherAppState.cityName || "";
            alert("Could not access GPS location. Please check browser permissions or search your city.");
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
}

async function loadWeatherData(lat, lon, cityName) {
    try {
        const resp = await fetch(`/api/weather?lat=${lat}&lon=${lon}&name=${encodeURIComponent(cityName)}`);
        if (!resp.ok) throw new Error("Weather request failed");
        const data = await resp.json();
        weatherAppState.currentWeather = data;

        if (data.timezone) {
            weatherAppState.timezone = data.timezone;
        }
        if (data.utc_offset_seconds !== undefined) {
            weatherAppState.utcOffsetSeconds = data.utc_offset_seconds;
        }

        renderLiveDashboard(data);
        updateAlertTicker(data.alerts);

        // Update atmospheric background & particles as per the location's weather
        if (data.current) {
            setWeatherAtmosphere(data.current.weather_code, data.current.is_day);
        }

        // Update charts if hourly available
        if (data.hourly) {
            window.renderHourlyChart(data.hourly.slice(0, 24));
        }
    } catch (e) {
        console.error("Load weather failed:", e);
    }
}

function renderLiveDashboard(data) {
    const curr = data.current || {};
    const aqi = data.aqi || {};
    const daily = data.daily || [];

    // Header location label
    const locLabels = document.querySelectorAll(".display-current-city");
    locLabels.forEach(el => el.innerText = data.location_name || weatherAppState.cityName);

    // Hero metrics
    const tempEl = document.getElementById("hero-temperature");
    const condEl = document.getElementById("hero-condition-text");
    const feelsEl = document.getElementById("hero-feels-like");
    const iconEl = document.getElementById("hero-weather-icon");

    if (tempEl) tempEl.innerText = Math.round(curr.temperature || 28);
    if (condEl) condEl.innerText = curr.condition || "Clear";
    if (feelsEl) feelsEl.innerText = `Feels like ${curr.apparent_temperature || 29}°C`;
    if (iconEl) iconEl.innerText = getWeatherEmoji(curr.weather_code);

    // Metric boxes
    const humEl = document.getElementById("val-humidity");
    const windEl = document.getElementById("val-wind");
    const pressEl = document.getElementById("val-pressure");
    const aqiEl = document.getElementById("val-aqi");
    const aqiCatEl = document.getElementById("val-aqi-category");

    if (humEl) humEl.innerText = `${curr.humidity || 60}%`;
    if (windEl) windEl.innerText = `${curr.wind_speed || 12} km/h`;
    if (pressEl) pressEl.innerText = `${curr.pressure || 1012} hPa`;
    if (aqiEl) {
        aqiEl.innerText = aqi.us_aqi || 75;
        aqiEl.style.color = aqi.color || "#22c55e";
    }
    if (aqiCatEl) {
        aqiCatEl.innerText = aqi.category || "Moderate";
        aqiCatEl.style.color = aqi.color || "#eab308";
    }

    // 7-day forecast cards
    const dailyContainer = document.getElementById("daily-forecast-container");
    if (dailyContainer && daily.length > 0) {
        dailyContainer.innerHTML = daily.map(d => {
            const dateObj = new Date(d.date);
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
            return `
                <div class="daily-row">
                    <div style="font-weight:600;min-width:110px;">${dayName}</div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:20px;">${getWeatherEmoji(d.weather_code)}</span>
                        <span style="font-size:13.5px;color:#cbd5e1;">${d.condition}</span>
                    </div>
                    <div style="font-size:13px;color:#94a3b8;">
                        💧 ${d.precip_prob_max}%
                    </div>
                    <div style="font-weight:700;font-size:14px;">
                        <span style="color:#f8fafc;">${Math.round(d.temp_max)}°</span>
                        <span style="color:#64748b;margin-left:4px;">${Math.round(d.temp_min)}°</span>
                    </div>
                </div>
            `;
        }).join("");
    }
}

function updateAlertTicker(alerts) {
    const ticker = document.getElementById("alert-ticker-text");
    if (!ticker) return;

    if (!alerts || alerts.length === 0 || alerts[0].color_code === "GREEN") {
        ticker.innerText = "Normal synoptic conditions. No active extreme weather warnings.";
        ticker.style.color = "#93c5fd";
    } else {
        const topAlert = alerts[0];
        ticker.innerText = `⚠️ ${topAlert.event}: ${topAlert.headline} — ${topAlert.instruction}`;
        ticker.style.color = "#fed7aa";
    }
}

async function loadNWPData() {
    try {
        const resp = await fetch(`/api/nwp?lat=${weatherAppState.lat}&lon=${weatherAppState.lon}`);
        if (!resp.ok) return;
        const data = await resp.json();

        // Render NWP cards
        const gfsTemp = data.models.GFS.temps[0];
        const ecmwfTemp = data.models.ECMWF.temps[0];
        const iconTemp = data.models.ICON.temps[0];
        const wrfTemp = data.models.WRF.temps[0];

        const gfsEl = document.getElementById("nwp-gfs-temp");
        const ecmwfEl = document.getElementById("nwp-ecmwf-temp");
        const iconEl = document.getElementById("nwp-icon-temp");
        const wrfEl = document.getElementById("nwp-wrf-temp");

        if (gfsEl) gfsEl.innerText = `${gfsTemp}°C`;
        if (ecmwfEl) ecmwfEl.innerText = `${ecmwfTemp}°C`;
        if (iconEl) iconEl.innerText = `${iconTemp}°C`;
        if (wrfEl) wrfEl.innerText = `${wrfTemp}°C`;

        const confEl = document.getElementById("nwp-confidence-score");
        const confBadge = document.getElementById("nwp-confidence-badge");
        const synopticEl = document.getElementById("nwp-synoptic-text");

        if (confEl) confEl.innerText = `${data.consensus.confidence_score}%`;
        if (confBadge) {
            confBadge.innerText = data.consensus.confidence_level;
            confBadge.style.background = `${data.consensus.confidence_color}33`;
            confBadge.style.color = data.consensus.confidence_color;
        }
        if (synopticEl) synopticEl.innerText = data.synoptic_analysis;

        window.renderNWPChart(data);
    } catch (e) {
        console.error("NWP load error:", e);
    }
}

async function loadAlertsView() {
    try {
        const resp = await fetch(`/api/alerts?lat=${weatherAppState.lat}&lon=${weatherAppState.lon}&name=${encodeURIComponent(weatherAppState.cityName)}`);
        if (!resp.ok) return;
        const data = await resp.json();

        const localContainer = document.getElementById("local-alerts-container");
        if (localContainer) {
            localContainer.innerHTML = data.local_alerts.map(a => `
                <div class="alert-card ${a.color_code}">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <h4 style="font-size:16px;font-weight:700;color:${a.color};">${a.event}</h4>
                        <span style="background:${a.color}22;color:${a.color};padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;">
                            ${a.color_code} ALERT (${a.action})
                        </span>
                    </div>
                    <p style="font-size:14px;color:#f1f5f9;margin-bottom:8px;">${a.headline}</p>
                    <p style="font-size:13px;color:#94a3b8;line-height:1.5;">${a.description}</p>
                    <div style="margin-top:12px;padding:10px 14px;background:rgba(0,0,0,0.3);border-radius:8px;font-size:13px;color:#fed7aa;">
                        <b>🛡️ Action Instructions:</b> ${a.instruction}
                    </div>
                </div>
            `).join("");
        }

        const nationalContainer = document.getElementById("national-alerts-container");
        if (nationalContainer) {
            nationalContainer.innerHTML = data.national_feed.map(f => `
                <div class="alert-card ${f.color_code}">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span style="font-weight:700;font-size:14px;">${f.region}</span>
                        <span style="font-size:11px;color:#94a3b8;">${f.valid_until}</span>
                    </div>
                    <div style="font-size:13.5px;color:#f8fafc;font-weight:600;margin-bottom:4px;">${f.event}</div>
                    <p style="font-size:12.5px;color:#cbd5e1;line-height:1.5;">${f.guidance}</p>
                </div>
            `).join("");
        }
    } catch (e) {
        console.error("Alerts view error:", e);
    }
}

async function loadClimateData() {
    try {
        const resp = await fetch(`/api/climate?lat=${weatherAppState.lat}&lon=${weatherAppState.lon}&name=${encodeURIComponent(weatherAppState.cityName)}`);
        if (!resp.ok) return;
        const data = await resp.json();

        const rateEl = document.getElementById("climate-warming-rate");
        const netEl = document.getElementById("climate-net-warming");
        const insightsList = document.getElementById("climate-insights-list");

        if (rateEl) rateEl.innerText = `+${data.decadal_warming_rate_c}°C / decade`;
        if (netEl) netEl.innerText = `+${data.net_warming_since_1995_c}°C since 1995`;
        if (insightsList) {
            insightsList.innerHTML = data.research_insights.map(i => `<li style="margin-bottom:8px;">${i}</li>`).join("");
        }

        window.renderClimateChart(data);
    } catch (e) {
        console.error("Climate load error:", e);
    }
}

function setLanguage(langKey) {
    weatherAppState.lang = langKey;
    const dict = window.I18N && window.I18N[langKey] ? window.I18N[langKey] : window.I18N["en"];

    // Update UI elements with data-i18n attribute
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key]) {
            el.innerText = dict[key];
        }
    });

    const searchInput = document.getElementById("city-search-input");
    if (searchInput && dict.search_placeholder) {
        searchInput.placeholder = dict.search_placeholder;
    }

    const chatInput = document.getElementById("chat-query-input");
    if (chatInput && dict.chat_placeholder) {
        chatInput.placeholder = dict.chat_placeholder;
    }
}

function getWeatherEmoji(code) {
    const emojis = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌧️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "⛈️",
        71: "🌨️", 73: "❄️", 75: "❄️",
        80: "🌦️", 81: "🌧️", 82: "⛈️",
        95: "⚡", 96: "⛈️", 99: "⛈️"
    };
    return emojis[code] || "⛅";
}

function initWebSocket() {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${proto}//${window.location.host}/ws/alerts`;
    try {
        const ws = new WebSocket(wsUrl);
        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === "BROADCAST_ALERT") {
                    alert(`🚨 REAL-TIME DISASTER WARNING: ${msg.headline}`);
                }
            } catch(e){}
        };
        ws.onerror = (e) => {
            console.log("WebSocket optional alert channel not connected (offline mode).");
        };
    } catch (e) {
        console.warn("WebSocket init:", e);
    }
}

// ==========================================================================
// Real-Time Live Clock Engine (Device & Selected Station Time)
// ==========================================================================
function initClock() {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
}

function updateLiveClock() {
    const now = new Date();

    // 1. Navigation bar live device clock (Time & Date)
    const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
    const dateOptions = { weekday: 'short', day: 'numeric', month: 'short' };

    const timeStr = now.toLocaleTimeString('en-US', timeOptions);
    const dateStr = now.toLocaleDateString('en-US', dateOptions);

    const navTimeEl = document.getElementById("nav-time-str");
    const navDateEl = document.getElementById("nav-date-str");

    if (navTimeEl) navTimeEl.innerText = timeStr;
    if (navDateEl) navDateEl.innerText = dateStr;

    // 2. Station Local Time (for the active selected city)
    const heroTimeEl = document.getElementById("hero-local-time");
    if (heroTimeEl) {
        let cityTimeStr = "";
        let tzLabel = "";
        try {
            if (weatherAppState.timezone) {
                const cityDate = new Date(now.toLocaleString("en-US", { timeZone: weatherAppState.timezone }));
                cityTimeStr = cityDate.toLocaleTimeString('en-US', timeOptions);
                tzLabel = weatherAppState.timezone.replace(/_/g, " ");
            } else {
                cityTimeStr = timeStr;
                tzLabel = "IST (UTC+5:30)";
            }
        } catch (e) {
            cityTimeStr = timeStr;
            tzLabel = "IST";
        }
        heroTimeEl.innerHTML = `🕒 Station Local Time: <b>${cityTimeStr}</b> <span style="font-size:11.5px;color:#94a3b8;font-weight:500;">(${tzLabel})</span>`;
    }
}

// ==========================================================================
// Dynamic Weather Atmosphere System (Background & Canvas Particles)
// ==========================================================================
let currentAtmosphereType = "sunny"; // "sunny", "clear-night", "cloudy", "rain", "thunderstorm", "fog", "snow"

function setWeatherAtmosphere(weatherCode, isDay = true) {
    let mode = "sunny";
    if (weatherCode !== undefined && weatherCode !== null) {
        if ([95, 96, 99, 65, 82].includes(weatherCode)) {
            mode = "thunderstorm";
        } else if ([51, 53, 55, 61, 63, 80, 81].includes(weatherCode)) {
            mode = "rain";
        } else if ([71, 73, 75].includes(weatherCode)) {
            mode = "snow";
        } else if ([45, 48].includes(weatherCode)) {
            mode = "fog";
        } else if ([2, 3].includes(weatherCode)) {
            mode = "cloudy";
        } else if ([0, 1].includes(weatherCode)) {
            mode = isDay ? "sunny" : "clear-night";
        } else {
            mode = isDay ? "sunny" : "clear-night";
        }
    } else {
        mode = isDay ? "sunny" : "clear-night";
    }

    currentAtmosphereType = mode;
    weatherAppState.atmosphere = mode;

    // Update body classes for dynamic atmospheric gradient & lighting
    const weatherClasses = [
        "weather-sunny", "weather-clear-night", "weather-cloudy",
        "weather-rain", "weather-thunderstorm", "weather-fog", "weather-snow"
    ];
    document.body.classList.remove(...weatherClasses);
    document.body.classList.add(`weather-${mode}`);

    // Update Hero Atmosphere Badge
    const badgeText = document.getElementById("hero-atmosphere-text");
    const modeTitles = {
        "sunny": "Golden Sunlight Atmosphere",
        "clear-night": "Starlit Midnight Cosmos",
        "cloudy": "Overcast Cloud Mist",
        "rain": "Rain Shower Downpour",
        "thunderstorm": "Electric Thunderstorm Active",
        "fog": "Dense Fog & Haze",
        "snow": "Winter Snow Flurry"
    };
    if (badgeText) {
        badgeText.innerText = modeTitles[mode] || "Dynamic Atmosphere";
    }

    if (window.rebuildAtmosphericParticles) {
        window.rebuildAtmosphericParticles();
    }
}

// Multi-Mode Canvas Particle Engine
function initAtmosphericCanvas() {
    const canvas = document.getElementById("weather-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener("resize", () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        rebuildParticles();
    });

    let particles = [];
    let ripples = [];
    let shootingStar = null;
    let lightningFlash = 0;
    let nextLightningTime = Date.now() + Math.random() * 4000 + 3000;
    let nextShootingStarTime = Date.now() + Math.random() * 6000 + 4000;

    function rebuildParticles() {
        particles = [];
        ripples = [];

        if (currentAtmosphereType === "rain") {
            for (let i = 0; i < 55; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    length: Math.random() * 14 + 12,
                    speedY: Math.random() * 7 + 8,
                    speedX: -(Math.random() * 1.5 + 0.8),
                    opacity: Math.random() * 0.35 + 0.2
                });
            }
        } else if (currentAtmosphereType === "thunderstorm") {
            for (let i = 0; i < 85; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    length: Math.random() * 18 + 18,
                    speedY: Math.random() * 8 + 13,
                    speedX: -(Math.random() * 2.5 + 1.5),
                    opacity: Math.random() * 0.45 + 0.3
                });
            }
        } else if (currentAtmosphereType === "sunny") {
            for (let i = 0; i < 35; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    radius: Math.random() * 2.5 + 1.5,
                    speedY: -(Math.random() * 0.6 + 0.3),
                    sway: Math.random() * Math.PI * 2,
                    swaySpeed: Math.random() * 0.03 + 0.015,
                    opacity: Math.random() * 0.35 + 0.15
                });
            }
        } else if (currentAtmosphereType === "clear-night") {
            for (let i = 0; i < 75; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    radius: Math.random() * 1.6 + 0.7,
                    phase: Math.random() * Math.PI * 2,
                    pulseSpeed: Math.random() * 0.03 + 0.02,
                    baseAlpha: Math.random() * 0.5 + 0.3
                });
            }
        } else if (currentAtmosphereType === "cloudy") {
            for (let i = 0; i < 16; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * (height * 0.7),
                    radius: Math.random() * 60 + 70,
                    speedX: Math.random() * 0.25 + 0.1,
                    opacity: Math.random() * 0.06 + 0.03
                });
            }
        } else if (currentAtmosphereType === "fog") {
            for (let i = 0; i < 20; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    w: Math.random() * 180 + 160,
                    h: Math.random() * 35 + 35,
                    speedX: Math.random() * 0.2 + 0.1,
                    opacity: Math.random() * 0.05 + 0.03
                });
            }
        } else if (currentAtmosphereType === "snow") {
            for (let i = 0; i < 55; i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    radius: Math.random() * 2.2 + 1.2,
                    speedY: Math.random() * 1.2 + 0.9,
                    sway: Math.random() * Math.PI * 2,
                    swaySpeed: Math.random() * 0.03 + 0.02,
                    opacity: Math.random() * 0.4 + 0.3
                });
            }
        }
    }

    window.rebuildAtmosphericParticles = rebuildParticles;
    rebuildParticles();

    function animate() {
        ctx.clearRect(0, 0, width, height);

        const now = Date.now();

        // 1. RAIN & THUNDERSTORM MODE
        if (currentAtmosphereType === "rain" || currentAtmosphereType === "thunderstorm") {
            // Thunderstorm lightning flash handling
            if (currentAtmosphereType === "thunderstorm") {
                if (now > nextLightningTime) {
                    lightningFlash = 1.0;
                    nextLightningTime = now + Math.random() * 5000 + 4000;
                }
                if (lightningFlash > 0.02) {
                    ctx.fillStyle = `rgba(255, 255, 255, ${lightningFlash * 0.18})`;
                    ctx.fillRect(0, 0, width, height);
                    lightningFlash *= 0.85;
                }
            }

            ctx.lineWidth = currentAtmosphereType === "thunderstorm" ? 1.6 : 1.2;

            for (let p of particles) {
                ctx.strokeStyle = currentAtmosphereType === "thunderstorm" 
                    ? `rgba(186, 230, 253, ${p.opacity})` 
                    : `rgba(56, 189, 248, ${p.opacity})`;

                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x + p.speedX * 2, p.y + p.length);
                ctx.stroke();

                p.y += p.speedY;
                p.x += p.speedX;

                // When raindrop reaches bottom, trigger splash ripple
                if (p.y > height - 10) {
                    if (Math.random() < 0.35 && ripples.length < 25) {
                        ripples.push({
                            x: p.x,
                            y: height - Math.random() * 8,
                            radius: 1,
                            maxRadius: Math.random() * 8 + 6,
                            alpha: 0.4
                        });
                    }
                    p.y = -p.length;
                    p.x = Math.random() * (width + 100);
                }
            }

            // Draw splash ripples on ground
            for (let i = ripples.length - 1; i >= 0; i--) {
                const r = ripples[i];
                ctx.beginPath();
                ctx.ellipse(r.x, r.y, r.radius, r.radius * 0.4, 0, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(56, 189, 248, ${r.alpha})`;
                ctx.lineWidth = 1;
                ctx.stroke();

                r.radius += 0.5;
                r.alpha -= 0.025;

                if (r.alpha <= 0 || r.radius >= r.maxRadius) {
                    ripples.splice(i, 1);
                }
            }
        }

        // 2. SUNNY / CLEAR DAY MODE
        else if (currentAtmosphereType === "sunny") {
            // Ambient solar flare / glow at top right corner
            const sunGrad = ctx.createRadialGradient(width * 0.88, height * 0.1, 10, width * 0.88, height * 0.1, Math.min(width, height) * 0.55);
            sunGrad.addColorStop(0, "rgba(251, 191, 36, 0.14)");
            sunGrad.addColorStop(0.4, "rgba(56, 189, 248, 0.04)");
            sunGrad.addColorStop(1, "rgba(251, 191, 36, 0)");
            ctx.fillStyle = sunGrad;
            ctx.fillRect(0, 0, width, height);

            // Floating golden sun motes
            for (let p of particles) {
                p.sway += p.swaySpeed;
                p.y += p.speedY;
                const swayOffset = Math.sin(p.sway) * 0.8;

                ctx.beginPath();
                ctx.arc(p.x + swayOffset, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(251, 191, 36, ${p.opacity * (0.7 + 0.3 * Math.sin(p.sway))})`;
                ctx.fill();

                if (p.y < -10) {
                    p.y = height + 10;
                    p.x = Math.random() * width;
                }
            }
        }

        // 3. CLEAR NIGHT MODE
        else if (currentAtmosphereType === "clear-night") {
            // Twinkling celestial stars
            for (let p of particles) {
                p.phase += p.pulseSpeed;
                const alpha = p.baseAlpha + Math.sin(p.phase) * 0.25;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(224, 231, 255, ${Math.max(0.1, alpha)})`;
                ctx.fill();
            }

            // Sporadic Shooting Star
            if (!shootingStar && now > nextShootingStarTime) {
                shootingStar = {
                    x: Math.random() * width * 0.8 + width * 0.1,
                    y: Math.random() * height * 0.3,
                    dx: -(Math.random() * 9 + 8),
                    dy: Math.random() * 5 + 4,
                    length: Math.random() * 45 + 50,
                    alpha: 1.0
                };
                nextShootingStarTime = now + Math.random() * 8000 + 6000;
            }

            if (shootingStar) {
                ctx.beginPath();
                ctx.moveTo(shootingStar.x, shootingStar.y);
                ctx.lineTo(shootingStar.x + shootingStar.dx * 2, shootingStar.y + shootingStar.dy * 2);
                ctx.strokeStyle = `rgba(255, 255, 255, ${shootingStar.alpha})`;
                ctx.lineWidth = 1.6;
                ctx.stroke();

                shootingStar.x += shootingStar.dx;
                shootingStar.y += shootingStar.dy;
                shootingStar.alpha -= 0.04;

                if (shootingStar.alpha <= 0) {
                    shootingStar = null;
                }
            }
        }

        // 4. CLOUDY OVERCAST MODE
        else if (currentAtmosphereType === "cloudy") {
            for (let p of particles) {
                p.x += p.speedX;
                if (p.x - p.radius > width) {
                    p.x = -p.radius;
                    p.y = Math.random() * (height * 0.7);
                }

                const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius);
                grad.addColorStop(0, `rgba(148, 163, 184, ${p.opacity})`);
                grad.addColorStop(1, "rgba(148, 163, 184, 0)");

                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // 5. FOG / MIST MODE
        else if (currentAtmosphereType === "fog") {
            for (let p of particles) {
                p.x += p.speedX;
                if (p.x > width) {
                    p.x = -p.w;
                    p.y = Math.random() * height;
                }

                const grad = ctx.createLinearGradient(p.x, p.y, p.x + p.w, p.y);
                grad.addColorStop(0, "rgba(203, 213, 225, 0)");
                grad.addColorStop(0.5, `rgba(203, 213, 225, ${p.opacity})`);
                grad.addColorStop(1, "rgba(203, 213, 225, 0)");

                ctx.fillStyle = grad;
                ctx.fillRect(p.x, p.y, p.w, p.h);
            }
        }

        // 6. SNOW / WINTER MODE
        else if (currentAtmosphereType === "snow") {
            for (let p of particles) {
                p.sway += p.swaySpeed;
                p.y += p.speedY;
                const swayOffset = Math.sin(p.sway) * 1.4;

                ctx.beginPath();
                ctx.arc(p.x + swayOffset, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(241, 245, 249, ${p.opacity})`;
                ctx.fill();

                if (p.y > height + 10) {
                    p.y = -10;
                    p.x = Math.random() * width;
                }
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
}

function copyPhoneUrl() {
    const text = document.getElementById("phone-url-display").innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("Mobile URL copied to clipboard: " + text);
    });
}

function initTheme() {
    const savedTheme = localStorage.getItem("weathergpt_theme") || "dark";
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    const iconEl = document.getElementById("theme-icon");
    const textEl = document.getElementById("theme-text");

    if (theme === "light") {
        document.body.setAttribute("data-theme", "light");
        if (iconEl) iconEl.innerText = "🌙";
        if (textEl) textEl.innerText = "Dark";
    } else {
        document.body.removeAttribute("data-theme");
        if (iconEl) iconEl.innerText = "☀️";
        if (textEl) textEl.innerText = "Light";
    }
    localStorage.setItem("weathergpt_theme", theme);
}

window.copyPhoneUrl = copyPhoneUrl;
window.initTheme = initTheme;
window.applyTheme = applyTheme;
window.setWeatherAtmosphere = setWeatherAtmosphere;
window.initClock = initClock;
