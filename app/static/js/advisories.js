// Sector-Specific Decision Support UI Handlers
let currentSector = "agriculture";
let currentCrop = "Wheat";

async function loadSectorAdvisory(sector = "agriculture") {
    currentSector = sector;
    const state = window.weatherAppState || { lat: 28.6139, lon: 77.2090, cityName: "New Delhi" };
    
    // Update active tab buttons
    document.querySelectorAll(".sector-pill").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.sector === sector);
    });

    const container = document.getElementById("advisory-detail-container");
    if (!container) return;

    container.innerHTML = `<div style="text-align:center;padding:40px;color:#94a3b8;">Loading ${sector} advisory...</div>`;

    try {
        const resp = await fetch(`/api/advisory?sector=${sector}&lat=${state.lat}&lon=${state.lon}&name=${encodeURIComponent(state.cityName)}&crop=${encodeURIComponent(currentCrop)}`);
        if (!resp.ok) throw new Error("Advisory fetch failed");
        const json = await resp.json();
        renderAdvisoryContent(sector, json.data);
    } catch (e) {
        console.error("Advisory error:", e);
        container.innerHTML = `<div style="color:#ef4444;padding:20px;">Failed to load advisory. Please try again.</div>`;
    }
}

function renderAdvisoryContent(sector, data) {
    const container = document.getElementById("advisory-detail-container");
    if (!container) return;

    if (sector === "agriculture") {
        container.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
                <div>
                    <h3 style="font-size:18px;font-weight:700;">🌾 Precision Crop-Weather Advisory</h3>
                    <p style="font-size:13px;color:#94a3b8;">${data.summary}</p>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <label style="font-size:13px;color:#94a3b8;">Select Crop:</label>
                    <select id="crop-select" onchange="onCropChange(this.value)" style="background:#1e293b;color:#fff;border:1px solid rgba(255,255,255,0.1);padding:6px 12px;border-radius:8px;outline:none;">
                        <option value="Wheat" ${currentCrop === "Wheat" ? "selected" : ""}>Wheat (गेहूं)</option>
                        <option value="Rice / Paddy" ${currentCrop === "Rice / Paddy" ? "selected" : ""}>Rice / Paddy (धान)</option>
                        <option value="Cotton" ${currentCrop === "Cotton" ? "selected" : ""}>Cotton (कपास)</option>
                        <option value="Mustard" ${currentCrop === "Mustard" ? "selected" : ""}>Mustard (सरसों)</option>
                        <option value="Vegetables" ${currentCrop === "Vegetables" ? "selected" : ""}>Vegetables (सब्जियां)</option>
                    </select>
                </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:16px;">
                <div class="glass-card" style="border-left:4px solid ${data.irrigation.color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:600;font-size:15px;">💧 Irrigation Management</span>
                        <span style="background:${data.irrigation.color}22;color:${data.irrigation.color};padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700;">${data.irrigation.status}</span>
                    </div>
                    <p style="font-size:13.5px;color:#cbd5e1;line-height:1.5;">${data.irrigation.advice}</p>
                </div>

                <div class="glass-card" style="border-left:4px solid ${data.spraying.color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:600;font-size:15px;">🧪 Pesticide Spray Window</span>
                        <span style="background:${data.spraying.color}22;color:${data.spraying.color};padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700;">${data.spraying.status}</span>
                    </div>
                    <p style="font-size:13.5px;color:#cbd5e1;line-height:1.5;">${data.spraying.advice}</p>
                </div>

                <div class="glass-card" style="border-left:4px solid ${data.pest_disease.color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:600;font-size:15px;">🐛 Pest & Disease Risk</span>
                        <span style="background:${data.pest_disease.color}22;color:${data.pest_disease.color};padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700;">${data.pest_disease.risk_level}</span>
                    </div>
                    <p style="font-size:13.5px;color:#cbd5e1;line-height:1.5;">${data.pest_disease.advice}</p>
                </div>

                <div class="glass-card" style="border-left:4px solid #38bdf8;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:600;font-size:15px;">🐄 Livestock Thermal Comfort</span>
                        <span style="background:rgba(56,189,248,0.2);color:#38bdf8;padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700;">THI: ${data.livestock.thi_score} (${data.livestock.status})</span>
                    </div>
                    <p style="font-size:13.5px;color:#cbd5e1;line-height:1.5;">${data.livestock.advice}</p>
                </div>
            </div>
        `;
    } else if (sector === "aviation") {
        container.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
                <div>
                    <h3 style="font-size:18px;font-weight:700;">✈️ ICAO Aviation Meteorological Briefing</h3>
                    <p style="font-size:13px;color:#94a3b8;">Station: ${data.icao_station} | Ceiling: ${data.ceiling} | Visibility: ${data.visibility_meters} m</p>
                </div>
                <div style="background:${data.category_color}22;border:1px solid ${data.category_color};color:${data.category_color};padding:6px 14px;border-radius:8px;font-weight:700;font-size:13px;">
                    ${data.flight_category}
                </div>
            </div>

            <div style="display:flex;flex-direction:column;gap:16px;">
                <div class="glass-card">
                    <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:6px;">RAW METAR (Aviation Routine Weather Report)</div>
                    <code style="display:block;background:#090d16;padding:12px;border-radius:8px;color:#38bdf8;font-family:monospace;font-size:13.5px;">${data.metar}</code>
                </div>

                <div class="glass-card">
                    <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:6px;">TERMINAL AERODROME FORECAST (TAF)</div>
                    <code style="display:block;background:#090d16;padding:12px;border-radius:8px;color:#a855f7;font-family:monospace;font-size:13.5px;">${data.taf}</code>
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:16px;">
                    <div class="glass-card">
                        <div style="font-weight:600;margin-bottom:6px;">💨 Wind & Crosswind Analysis</div>
                        <p style="font-size:13.5px;color:#cbd5e1;">Surface Wind: <b>${data.wind}</b></p>
                        <p style="font-size:13.5px;color:#cbd5e1;margin-top:4px;">Crosswind Component: <b>${data.crosswind_kt} knots</b></p>
                        <p style="font-size:13.5px;color:#cbd5e1;margin-top:4px;">Active Recommendation: <span style="color:#38bdf8;">${data.runway_recommendation}</span></p>
                    </div>

                    <div class="glass-card">
                        <div style="font-weight:600;margin-bottom:6px;">⚠️ Flight Hazards Advisory</div>
                        <ul style="padding-left:18px;font-size:13px;color:#cbd5e1;line-height:1.6;">
                            ${data.hazards.filter(h => h).map(h => `<li>${h}</li>`).join("") || "<li>No significant terminal convective hazards. Normal operations.</li>"}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    } else if (sector === "marine") {
        container.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
                <div>
                    <h3 style="font-size:18px;font-weight:700;">🚢 Maritime & Coastal Safety Bulletin</h3>
                    <p style="font-size:13px;color:#94a3b8;">Region: ${data.location} | Sea State: ${data.sea_state}</p>
                </div>
                <div style="background:${data.safety_color}22;border:1px solid ${data.safety_color};color:${data.safety_color};padding:6px 14px;border-radius:8px;font-weight:700;font-size:13px;">
                    ${data.safety_level}
                </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:16px;margin-bottom:16px;">
                <div class="glass-card">
                    <div style="font-size:12px;color:#94a3b8;">Significant Wave Height</div>
                    <div style="font-size:28px;font-weight:800;color:#38bdf8;margin:6px 0;">${data.sig_wave_height_m} m</div>
                    <div style="font-size:12px;color:#64748b;">Douglas Sea Scale</div>
                </div>
                <div class="glass-card">
                    <div style="font-size:12px;color:#94a3b8;">Swell Wave Period</div>
                    <div style="font-size:28px;font-weight:800;color:#10b981;margin:6px 0;">${data.swell_period_sec} s</div>
                    <div style="font-size:12px;color:#64748b;">Peak oceanic energy cycle</div>
                </div>
                <div class="glass-card">
                    <div style="font-size:12px;color:#94a3b8;">Coastal Wind / Gusts</div>
                    <div style="font-size:28px;font-weight:800;color:#f59e0b;margin:6px 0;">${data.wind_knots} kt</div>
                    <div style="font-size:12px;color:#64748b;">Gusts up to ${data.wind_gusts_knots} kt</div>
                </div>
            </div>

            <div class="glass-card" style="border-left:4px solid ${data.safety_color};">
                <h4 style="font-size:15px;font-weight:600;margin-bottom:6px;">⚓ Fishermen & Port Operations Guidance</h4>
                <p style="font-size:14px;color:#cbd5e1;line-height:1.5;">${data.guidance}</p>
            </div>
        `;
    } else if (sector === "urban") {
        container.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
                <div>
                    <h3 style="font-size:18px;font-weight:700;">🏙️ Smart City Resilience & Inundation Risk</h3>
                    <p style="font-size:13px;color:#94a3b8;">City: ${data.location} | ${data.air_quality_summary}</p>
                </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:16px;">
                <div class="glass-card" style="border-left:4px solid ${data.uhi_color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:600;font-size:15px;">🔥 Urban Heat Island (UHI)</span>
                        <span style="background:${data.uhi_color}22;color:${data.uhi_color};padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700;">Index: ${data.uhi_index}/10</span>
                    </div>
                    <p style="font-size:13.5px;color:#cbd5e1;line-height:1.5;">${data.uhi_status}: Surface heat absorption intensified by concrete density and diurnal stagnation.</p>
                </div>

                <div class="glass-card" style="border-left:4px solid ${data.flood_color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:600;font-size:15px;">🌊 Urban Waterlogging Hazard</span>
                        <span style="background:${data.flood_color}22;color:${data.flood_color};padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700;">${data.flood_status} (${data.flood_risk_pct}%)</span>
                    </div>
                    <p style="font-size:13.5px;color:#cbd5e1;line-height:1.5;">Drainage storm load probability calculated from rainfall intensity against impermeable surface runoff coefficients.</p>
                </div>

                <div class="glass-card" style="border-left:4px solid ${data.labor_color};grid-column:1 / -1;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:600;font-size:15px;">🏗️ Outdoor Labor & Construction Safety</span>
                        <span style="background:${data.labor_color}22;color:${data.labor_color};padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700;">${data.labor_suitability}</span>
                    </div>
                    <p style="font-size:13.5px;color:#cbd5e1;line-height:1.5;">${data.labor_action}</p>
                </div>
            </div>
        `;
    }
}

function onCropChange(crop) {
    currentCrop = crop;
    loadSectorAdvisory("agriculture");
}

window.loadSectorAdvisory = loadSectorAdvisory;
window.onCropChange = onCropChange;
