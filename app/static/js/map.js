// Leaflet GIS Map & RainViewer Precipitation Radar Integration
let mapInstance = null;
let baseTileLayer = null;
let radarLayers = [];
let activeRadarIndex = 0;
let radarAnimationTimer = null;
let currentMarker = null;

function initWeatherMap(lat = 28.6139, lon = 77.2090, cityName = "New Delhi") {
    const mapContainer = document.getElementById("radar-map");
    if (!mapContainer || !window.L) return;

    if (!mapInstance) {
        mapInstance = L.map('radar-map', {
            center: [lat, lon],
            zoom: 7,
            zoomControl: true
        });

        const isLight = document.body.getAttribute("data-theme") === "light";
        const tileUrl = isLight 
            ? 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
            : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

        baseTileLayer = L.tileLayer(tileUrl, {
            attribution: '&copy; OpenStreetMap &copy; CARTO &copy; RainViewer',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(mapInstance);

        loadRainViewerRadar();
    } else {
        mapInstance.setView([lat, lon], 7);
    }

    // Update location marker
    if (currentMarker) {
        mapInstance.removeLayer(currentMarker);
    }

    const customIcon = L.divIcon({
        className: 'custom-map-pin',
        html: `<div style="background:#38bdf8;width:14px;height:14px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 12px #38bdf8;animation:pulse 1.5s infinite;"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    currentMarker = L.marker([lat, lon], { icon: customIcon }).addTo(mapInstance);
    currentMarker.bindPopup(`<b>${cityName}</b><br>Active Meteorological Monitoring`).openPopup();
}

async function loadRainViewerRadar() {
    try {
        const resp = await fetch("https://api.rainviewer.com/public/weather-maps.json");
        if (!resp.ok) return;
        const data = await resp.json();

        // Clear existing radar frames
        radarLayers.forEach(l => mapInstance.removeLayer(l));
        radarLayers = [];

        const pastFrames = data.radar ? data.radar.past : [];
        if (!pastFrames || pastFrames.length === 0) return;

        // Take last 6 radar timestamps
        const selectedFrames = pastFrames.slice(-6);
        selectedFrames.forEach((frame) => {
            const layer = L.tileLayer(`https://tilecache.rainviewer.com${frame.path}/256/{z}/{x}/{y}/2/1_1.png`, {
                tileSize: 256,
                opacity: 0.65,
                zIndex: 10
            });
            radarLayers.push({ layer, time: frame.time });
        });

        if (radarLayers.length > 0) {
            // Show the latest frame by default
            activeRadarIndex = radarLayers.length - 1;
            radarLayers[activeRadarIndex].layer.addTo(mapInstance);
            updateRadarTimeDisplay(radarLayers[activeRadarIndex].time);
        }
    } catch (e) {
        console.warn("RainViewer radar tiles unavailable:", e);
    }
}

function updateRadarTimeDisplay(timestamp) {
    const el = document.getElementById("radar-time-label");
    if (el && timestamp) {
        const d = new Date(timestamp * 1000);
        el.innerText = `Radar Frame: ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    }
}

function toggleRadarAnimation() {
    const playBtn = document.getElementById("btn-radar-play");
    if (radarAnimationTimer) {
        clearInterval(radarAnimationTimer);
        radarAnimationTimer = null;
        if (playBtn) playBtn.innerHTML = "▶ Play Animation";
    } else {
        if (radarLayers.length === 0) return;
        if (playBtn) playBtn.innerHTML = "⏸ Pause";
        radarAnimationTimer = setInterval(() => {
            if (radarLayers[activeRadarIndex]) {
                mapInstance.removeLayer(radarLayers[activeRadarIndex].layer);
            }
            activeRadarIndex = (activeRadarIndex + 1) % radarLayers.length;
            radarLayers[activeRadarIndex].layer.addTo(mapInstance);
            updateRadarTimeDisplay(radarLayers[activeRadarIndex].time);
        }, 1200);
    }
}

window.initWeatherMap = initWeatherMap;
window.toggleRadarAnimation = toggleRadarAnimation;
