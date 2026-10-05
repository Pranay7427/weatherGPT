// Chart.js Visualization Orchestrator for WeatherGPT
let hourlyChartInstance = null;
let nwpChartInstance = null;
let climateChartInstance = null;

function renderHourlyChart(hourlyData) {
    const canvas = document.getElementById("hourlyChart");
    if (!canvas || !window.Chart) return;

    const ctx = canvas.getContext("2d");
    if (hourlyChartInstance) {
        hourlyChartInstance.destroy();
    }

    const labels = hourlyData.map(h => {
        const d = new Date(h.time);
        return `${d.getHours().toString().padStart(2, '0')}:00`;
    });
    const temps = hourlyData.map(h => h.temperature);
    const rainProbs = hourlyData.map(h => h.precipitation_prob);

    hourlyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temps,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    yAxisID: 'y'
                },
                {
                    label: 'Rain Probability (%)',
                    data: rainProbs,
                    borderColor: '#818cf8',
                    backgroundColor: 'rgba(129, 140, 248, 0.1)',
                    borderDash: [4, 4],
                    fill: false,
                    tension: 0.2,
                    borderWidth: 2,
                    pointRadius: 2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#fff',
                    bodyColor: '#cbd5e1'
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b' }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#38bdf8', callback: v => `${v}°C` }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#818cf8', callback: v => `${v}%` },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

function renderNWPChart(nwpData) {
    const canvas = document.getElementById("nwpChart");
    if (!canvas || !window.Chart) return;

    const ctx = canvas.getContext("2d");
    if (nwpChartInstance) {
        nwpChartInstance.destroy();
    }

    const times = nwpData.times.map(t => {
        const d = new Date(t);
        return `${d.getHours().toString().padStart(2, '0')}:00`;
    });

    const gfs = nwpData.models.GFS.temps;
    const ecmwf = nwpData.models.ECMWF.temps;
    const icon = nwpData.models.ICON.temps;
    const wrf = nwpData.models.WRF.temps;
    const consensus = nwpData.consensus.temperature_curve;

    nwpChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: times,
            datasets: [
                {
                    label: 'NOAA GFS (13km)',
                    data: gfs,
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'ECMWF IFS (9km)',
                    data: ecmwf,
                    borderColor: '#10b981',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'DWD ICON (13km)',
                    data: icon,
                    borderColor: '#f59e0b',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'Mesoscale WRF (3km)',
                    data: wrf,
                    borderColor: '#ec4899',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'Consensus Ensemble Mean',
                    data: consensus,
                    borderColor: '#ffffff',
                    borderWidth: 3.5,
                    borderDash: [6, 4],
                    tension: 0.3,
                    pointRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#cbd5e1', callback: v => `${v}°C` }
                }
            }
        }
    });
}

function renderClimateChart(climateData) {
    const canvas = document.getElementById("climateChart");
    if (!canvas || !window.Chart) return;

    const ctx = canvas.getContext("2d");
    if (climateChartInstance) {
        climateChartInstance.destroy();
    }

    const years = climateData.years;
    const anomalies = climateData.temperature_anomalies;

    climateChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [{
                label: 'Temperature Anomaly vs 1991-2020 Baseline (°C)',
                data: anomalies,
                backgroundColor: anomalies.map(v => v >= 0 ? 'rgba(239, 68, 68, 0.75)' : 'rgba(56, 189, 248, 0.75)'),
                borderColor: anomalies.map(v => v >= 0 ? '#ef4444' : '#38bdf8'),
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94a3b8' }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', callback: v => `${v > 0 ? '+' : ''}${v}°C` }
                }
            }
        }
    });
}

window.renderHourlyChart = renderHourlyChart;
window.renderNWPChart = renderNWPChart;
window.renderClimateChart = renderClimateChart;
