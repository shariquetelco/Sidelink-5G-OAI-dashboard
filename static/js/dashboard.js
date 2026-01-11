// OAI 5G Sidelink Tactical Dashboard - Research Grade
// Real-time charts and visualizations

const REFRESH_INTERVAL = 2000; // 2 seconds

// Chart instances
let throughputChart = null;
let signalChart = null;
let spectrumChart = null;

// Chart.js default configuration for tactical theme
Chart.defaults.color = '#00d4ff';
Chart.defaults.borderColor = 'rgba(0, 212, 255, 0.2)';
Chart.defaults.font.family = "'Courier New', 'Consolas', monospace";

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    init();
});

// Initialize all charts
function initCharts() {
    // Throughput Chart
    const throughputCtx = document.getElementById('throughputChart');
    if (throughputCtx) {
        throughputChart = new Chart(throughputCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Alpha TX',
                        data: [],
                        borderColor: '#ff3366',
                        backgroundColor: 'rgba(255, 51, 102, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Alpha RX',
                        data: [],
                        borderColor: '#ff6699',
                        backgroundColor: 'rgba(255, 102, 153, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        borderDash: [5, 5]
                    },
                    {
                        label: 'Bravo TX',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Bravo RX',
                        data: [],
                        borderColor: '#66e0ff',
                        backgroundColor: 'rgba(102, 224, 255, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { color: '#00d4ff', font: { size: 11 } }
                    },
                    title: {
                        display: true,
                        text: 'Real-Time Throughput (Mbps)',
                        color: '#00d4ff',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: { display: true, text: 'Time', color: '#00d4ff' },
                        ticks: { color: '#8892a6', maxTicksLimit: 10 },
                        grid: { color: 'rgba(0, 212, 255, 0.1)' }
                    },
                    y: {
                        display: true,
                        title: { display: true, text: 'Throughput (Mbps)', color: '#00d4ff' },
                        ticks: { color: '#8892a6' },
                        grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        beginAtZero: true
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    // Signal Quality Chart
    const signalCtx = document.getElementById('signalChart');
    if (signalCtx) {
        signalChart = new Chart(signalCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'RSRP (dBm)',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        yAxisID: 'y-rsrp'
                    },
                    {
                        label: 'SINR (dB)',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        yAxisID: 'y-sinr'
                    },
                    {
                        label: 'CQI',
                        data: [],
                        borderColor: '#ffcc00',
                        backgroundColor: 'rgba(255, 204, 0, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        yAxisID: 'y-cqi'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { color: '#00d4ff', font: { size: 11 } }
                    },
                    title: {
                        display: true,
                        text: 'Signal Quality Metrics (Unit Alpha)',
                        color: '#00d4ff',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: { display: true, text: 'Time', color: '#00d4ff' },
                        ticks: { color: '#8892a6', maxTicksLimit: 10 },
                        grid: { color: 'rgba(0, 212, 255, 0.1)' }
                    },
                    'y-rsrp': {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'RSRP (dBm)', color: '#00d4ff' },
                        ticks: { color: '#00d4ff' },
                        grid: { color: 'rgba(0, 212, 255, 0.1)' }
                    },
                    'y-sinr': {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'SINR (dB)', color: '#00ff88' },
                        ticks: { color: '#00ff88' },
                        grid: { display: false }
                    },
                    'y-cqi': {
                        type: 'linear',
                        display: false,
                        min: 0,
                        max: 15
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    // Spectrum Chart
    const spectrumCtx = document.getElementById('spectrumChart');
    if (spectrumCtx) {
        spectrumChart = new Chart(spectrumCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Channel Response',
                        data: [],
                        borderColor: '#ff3366',
                        backgroundColor: 'rgba(255, 51, 102, 0.2)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true,
                        pointRadius: 0
                    },
                    {
                        label: 'Noise Floor',
                        data: [],
                        borderColor: '#666',
                        backgroundColor: 'rgba(100, 100, 100, 0.1)',
                        borderWidth: 1,
                        tension: 0.3,
                        fill: true,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { color: '#00d4ff', font: { size: 11 } }
                    },
                    title: {
                        display: true,
                        text: 'Channel Frequency Response (2.6 GHz ± 53 MHz)',
                        color: '#00d4ff',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: { display: true, text: 'Frequency Offset (MHz)', color: '#00d4ff' },
                        ticks: { color: '#8892a6', maxTicksLimit: 15 },
                        grid: { color: 'rgba(0, 212, 255, 0.1)' }
                    },
                    y: {
                        display: true,
                        title: { display: true, text: 'Power (dBm)', color: '#00d4ff' },
                        ticks: { color: '#8892a6' },
                        grid: { color: 'rgba(0, 212, 255, 0.1)' }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }
}

// Update throughput chart
async function updateThroughputChart() {
    try {
        const response = await fetch('/api/throughput_history');
        const data = await response.json();
        
        if (!throughputChart) return;
        
        // Get last 60 data points
        const syncrefData = data.syncref.slice(-60);
        const nearbyData = data.nearby.slice(-60);
        
        // Extract timestamps
        const labels = syncrefData.map(d => {
            const time = new Date(d.timestamp);
            return time.toLocaleTimeString();
        });
        
        // Update chart data
        throughputChart.data.labels = labels;
        throughputChart.data.datasets[0].data = syncrefData.map(d => d.tx_mbps);
        throughputChart.data.datasets[1].data = syncrefData.map(d => d.rx_mbps);
        throughputChart.data.datasets[2].data = nearbyData.map(d => d.tx_mbps);
        throughputChart.data.datasets[3].data = nearbyData.map(d => d.rx_mbps);
        
        throughputChart.update('none'); // Faster update without animation
        
    } catch (error) {
        console.error('Error updating throughput chart:', error);
    }
}

// Update signal quality chart
async function updateSignalChart() {
    try {
        const response = await fetch('/api/signal_history');
        const data = await response.json();
        
        if (!signalChart) return;
        
        // Get last 60 data points for SyncRef
        const syncrefData = data.syncref.slice(-60);
        
        // Extract timestamps
        const labels = syncrefData.map(d => {
            const time = new Date(d.timestamp);
            return time.toLocaleTimeString();
        });
        
        // Update chart data
        signalChart.data.labels = labels;
        signalChart.data.datasets[0].data = syncrefData.map(d => d.rsrp);
        signalChart.data.datasets[1].data = syncrefData.map(d => d.sinr);
        signalChart.data.datasets[2].data = syncrefData.map(d => d.cqi);
        
        signalChart.update('none');
        
    } catch (error) {
        console.error('Error updating signal chart:', error);
    }
}

// Update spectrum visualization
async function updateSpectrumChart() {
    try {
        const response = await fetch('/api/spectrum_data');
        const data = await response.json();
        
        if (!spectrumChart) return;
        
        // Update chart data
        spectrumChart.data.labels = data.frequency;
        spectrumChart.data.datasets[0].data = data.channel_response;
        spectrumChart.data.datasets[1].data = data.noise_floor;
        
        spectrumChart.update('none');
        
    } catch (error) {
        console.error('Error updating spectrum chart:', error);
    }
}

// Update message flow sequence diagram
async function updateMessageFlow() {
    try {
        const response = await fetch('/api/message_flow');
        const data = await response.json();
        
        // Generate Mermaid sequence diagram
        let mermaidCode = 'sequenceDiagram\n';
        mermaidCode += '    participant Alpha as 🔴 Unit Alpha<br/>(SyncRef)\n';
        mermaidCode += '    participant Bravo as 🔵 Unit Bravo<br/>(Nearby)\n';
        mermaidCode += '    \n';
        
        data.flow.forEach(msg => {
            const arrow = msg.from === msg.to ? '->>' : '->>';
            mermaidCode += `    ${msg.from}-${arrow}${msg.to}: ${msg.message}<br/>${msg.description}\n`;
        });
        
        // Update diagram
        const diagramDiv = document.getElementById('messageFlowDiagram');
        if (diagramDiv) {
            diagramDiv.innerHTML = `<pre class="mermaid">${mermaidCode}</pre>`;
            mermaid.init(undefined, '.mermaid');
        }
        
    } catch (error) {
        console.error('Error updating message flow:', error);
    }
}

// Update SyncRef UE data (existing function - enhanced)
async function updateSyncRef() {
    try {
        const response = await fetch('/api/syncref');
        const data = await response.json();
        
        // Update status
        document.getElementById('syncref-status').textContent = data.status === 'running' ? '✅ OPERATIONAL' : '🔴 OFFLINE';
        document.getElementById('syncref-status').className = `status-badge ${data.status === 'running' ? 'operational' : 'offline'}`;
        
        // Update frame/slot
        document.getElementById('syncref-frame-slot').textContent = data.frame_slot;
        
        // Update radio parameters
        document.getElementById('syncref-carrier').textContent = data.carrier;
        document.getElementById('syncref-bandwidth').textContent = data.bandwidth;
        document.getElementById('syncref-mcs').textContent = data.mcs;
        document.getElementById('syncref-tx-power').textContent = data.tx_power;
        
        // Update PHY stats
        document.getElementById('syncref-psbch-tx').textContent = data.psbch.tx.toLocaleString();
        document.getElementById('syncref-pscch-tx').textContent = data.pscch.tx.toLocaleString();
        document.getElementById('syncref-pssch-tx').textContent = data.pssch.tx.toLocaleString();
        document.getElementById('syncref-psfch-tx').textContent = data.psfch.tx.toLocaleString();
        
        // Calculate success rate
        const successRate = calculateSuccessRate(data.pssch.tx, data.pssch.rx_ok, data.pssch.rx_not_ok);
        document.getElementById('syncref-success-rate').textContent = successRate.toFixed(1) + '%';
        document.getElementById('syncref-success-rate').className = `metric-value ${successRate >= 95 ? 'success' : 'error'}`;
        
        // Update link quality
        document.getElementById('syncref-rsrp').textContent = data.quality.rsrp + ' dBm';
        document.getElementById('syncref-sinr').textContent = data.quality.sinr + ' dB';
        document.getElementById('syncref-cqi').textContent = data.quality.cqi;
        document.getElementById('syncref-errors').textContent = data.pssch.rx_not_ok + '/' + data.pssch.tx;
        
        // Update terminal output
        const terminal = document.getElementById('syncref-terminal');
        terminal.innerHTML = data.terminal_output.map(line => 
            `<div class="terminal-line">${escapeHtml(line)}</div>`
        ).join('');
        terminal.scrollTop = terminal.scrollHeight;
        
    } catch (error) {
        console.error('Error updating SyncRef:', error);
    }
}

// Update Nearby UE data (existing function - no changes needed)
async function updateNearby() {
    try {
        const response = await fetch('/api/nearby');
        const data = await response.json();
        
        document.getElementById('nearby-status').textContent = data.status === 'running' ? '✅ OPERATIONAL' : '🔴 OFFLINE';
        document.getElementById('nearby-status').className = `status-badge ${data.status === 'running' ? 'operational' : 'offline'}`;
        
        document.getElementById('nearby-frame-slot').textContent = data.frame_slot;
        
        const syncStatus = data.synchronized ? '✅ Yes' : '❌ No';
        document.getElementById('nearby-synced').textContent = syncStatus;
        
        document.getElementById('nearby-carrier').textContent = data.carrier;
        document.getElementById('nearby-bandwidth').textContent = data.bandwidth;
        document.getElementById('nearby-mcs').textContent = data.mcs;
        document.getElementById('nearby-rx-gain').textContent = data.rx_gain;
        
        document.getElementById('nearby-psbch-rx').textContent = data.psbch.rx_ok.toLocaleString();
        document.getElementById('nearby-pscch-rx').textContent = data.pscch.rx_ok.toLocaleString();
        document.getElementById('nearby-pssch-rx').textContent = data.pssch.rx_ok.toLocaleString();
        document.getElementById('nearby-psfch-tx').textContent = data.psfch.tx.toLocaleString();
        
        const successRate = calculateSuccessRate(data.pssch.tx, data.pssch.rx_ok, data.pssch.rx_not_ok);
        document.getElementById('nearby-success-rate').textContent = successRate.toFixed(1) + '%';
        document.getElementById('nearby-success-rate').className = `metric-value ${successRate >= 95 ? 'success' : 'error'}`;
        
        document.getElementById('nearby-rsrp').textContent = data.quality.rsrp + ' dBm';
        document.getElementById('nearby-sinr').textContent = data.quality.sinr + ' dB';
        document.getElementById('nearby-cqi').textContent = data.quality.cqi;
        document.getElementById('nearby-errors').textContent = data.pssch.rx_not_ok + '/' + data.pssch.tx;
        
        const terminal = document.getElementById('nearby-terminal');
        terminal.innerHTML = data.terminal_output.map(line => 
            `<div class="terminal-line">${escapeHtml(line)}</div>`
        ).join('');
        terminal.scrollTop = terminal.scrollHeight;
        
    } catch (error) {
        console.error('Error updating Nearby UE:', error);
    }
}

// Update link status (existing function - no changes)
async function updateLinkStatus() {
    try {
        const response = await fetch('/api/link_status');
        const data = await response.json();
        
        const linkStatus = data.link_established ? '✅ TACTICAL LINK ESTABLISHED' : '❌ LINK DOWN';
        document.getElementById('topology-status').textContent = 'STATUS: ' + linkStatus;
        
        const qualityBar = document.getElementById('quality-bar-fill');
        qualityBar.style.width = data.overall_quality + '%';
        
        let qualityText = '';
        if (data.overall_quality >= 90) qualityText = '✅ EXCELLENT';
        else if (data.overall_quality >= 70) qualityText = '✅ GOOD';
        else if (data.overall_quality >= 50) qualityText = '⚠️ FAIR';
        else qualityText = '❌ POOR';
        
        qualityBar.textContent = Math.round(data.overall_quality) + '% ' + qualityText;
        
        document.getElementById('pssch-decode').textContent = 
            `${data.pssch_total_rx_ok.toLocaleString()}/${data.pssch_total_tx.toLocaleString()} (${((data.pssch_total_rx_ok/data.pssch_total_tx)*100).toFixed(1)}%)`;
        document.getElementById('psbch-decode').textContent = 
            `${data.psbch_sync_count.toLocaleString()}/${data.psbch_sync_count.toLocaleString()} (100.0%)`;
        
        const totalPackets = data.pssch_total_rx_ok + data.pssch_total_errors;
        const per = totalPackets > 0 ? ((data.pssch_total_errors/totalPackets)*100).toFixed(2) : '0.00';
        document.getElementById('packet-error-rate').textContent = per + '%';
        
    } catch (error) {
        console.error('Error updating link status:', error);
    }
}

// Update events (existing function - no changes)
async function updateEvents() {
    try {
        const response = await fetch('/api/events');
        const data = await response.json();
        
        const eventLog = document.getElementById('event-log');
        eventLog.innerHTML = data.events.map(event => 
            `<div class="event-item">
                <span class="event-time">${event.time}</span>
                ${escapeHtml(event.message)}
            </div>`
        ).join('');
        
    } catch (error) {
        console.error('Error updating events:', error);
    }
}

// Helper function to calculate success rate
function calculateSuccessRate(tx, rxOk, rxNotOk) {
    const total = rxOk + rxNotOk;
    if (total === 0) return tx > 0 ? 100.0 : 0.0;
    return (rxOk / total) * 100.0;
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize dashboard
function init() {
    console.log('OAI Sidelink Dashboard initialized - Research Grade');
    
    // Initialize Mermaid for sequence diagrams
    mermaid.initialize({ 
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
            primaryColor: '#00d4ff',
            primaryTextColor: '#fff',
            primaryBorderColor: '#00d4ff',
            lineColor: '#00d4ff',
            secondaryColor: '#ff3366',
            tertiaryColor: '#00ff88'
        }
    });
    
    // Initial update
    updateSyncRef();
    updateNearby();
    updateLinkStatus();
    updateEvents();
    updateThroughputChart();
    updateSignalChart();
    updateSpectrumChart();
    updateMessageFlow();
    
    // Set up periodic updates
    setInterval(updateSyncRef, REFRESH_INTERVAL);
    setInterval(updateNearby, REFRESH_INTERVAL);
    setInterval(updateLinkStatus, REFRESH_INTERVAL);
    setInterval(updateEvents, 5000);
    setInterval(updateThroughputChart, REFRESH_INTERVAL);
    setInterval(updateSignalChart, REFRESH_INTERVAL);
    setInterval(updateSpectrumChart, REFRESH_INTERVAL);
    setInterval(updateMessageFlow, 5000);
}
