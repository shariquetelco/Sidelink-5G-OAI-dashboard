#!/usr/bin/env python3
"""
OAI 5G Sidelink Tactical Dashboard - Research Grade
Flask backend with historical data tracking
Author: Ahmad Sharique (ahmad@iabg.de)
"""

from flask import Flask, render_template, jsonify, send_file
from parsers.sidelink_parser import SidelinkParser
import os
import json
from datetime import datetime
from collections import deque
import csv
import io

app = Flask(__name__)

# Configuration
SYNCREF_LOG = os.getenv('SYNCREF_LOG', os.path.expanduser('~/syncref_sl.log'))
NEARBY_LOG = os.getenv('NEARBY_LOG', os.path.expanduser('~/nearby_ue_sl.log'))

# Initialize parsers
syncref_parser = SidelinkParser(SYNCREF_LOG, ue_type='syncref')
nearby_parser = SidelinkParser(NEARBY_LOG, ue_type='nearby')

# Historical data storage (in-memory circular buffers)
# Store last 120 data points (2 seconds refresh = 4 minutes of history)
MAX_HISTORY = 120

throughput_history = {
    'syncref': deque(maxlen=MAX_HISTORY),
    'nearby': deque(maxlen=MAX_HISTORY)
}

signal_history = {
    'syncref': deque(maxlen=MAX_HISTORY),
    'nearby': deque(maxlen=MAX_HISTORY)
}

packet_history = {
    'syncref': deque(maxlen=MAX_HISTORY),
    'nearby': deque(maxlen=MAX_HISTORY)
}

# Message flow tracking
message_flow = []
MAX_MESSAGES = 50

# Previous packet counts for throughput calculation
previous_counts = {
    'syncref': {'tx': 0, 'rx': 0, 'timestamp': datetime.now()},
    'nearby': {'tx': 0, 'rx': 0, 'timestamp': datetime.now()}
}

def calculate_throughput(ue_type, current_tx, current_rx):
    """Calculate throughput in Mbps"""
    global previous_counts
    
    now = datetime.now()
    prev = previous_counts[ue_type]
    time_delta = (now - prev['timestamp']).total_seconds()
    
    if time_delta == 0:
        return 0, 0
    
    # Calculate packets per second
    tx_pps = (current_tx - prev['tx']) / time_delta
    rx_pps = (current_rx - prev['rx']) / time_delta
    
    # Assume average packet size ~1500 bytes (MTU)
    # Throughput (Mbps) = packets/sec * bytes/packet * 8 bits/byte / 1,000,000
    packet_size = 1500
    tx_mbps = (tx_pps * packet_size * 8) / 1_000_000
    rx_mbps = (rx_pps * packet_size * 8) / 1_000_000
    
    # Update previous counts
    previous_counts[ue_type] = {
        'tx': current_tx,
        'rx': current_rx,
        'timestamp': now
    }
    
    return max(0, tx_mbps), max(0, rx_mbps)

def store_metrics(ue_type, metrics, quality):
    """Store metrics in historical buffers"""
    timestamp = datetime.now().isoformat()
    
    # Calculate throughput
    tx_mbps, rx_mbps = calculate_throughput(
        ue_type,
        metrics['pssch']['tx'],
        metrics['pssch']['rx_ok']
    )
    
    # Store throughput
    throughput_history[ue_type].append({
        'timestamp': timestamp,
        'tx_mbps': round(tx_mbps, 3),
        'rx_mbps': round(rx_mbps, 3)
    })
    
    # Store signal quality
    signal_history[ue_type].append({
        'timestamp': timestamp,
        'rsrp': quality['rsrp'],
        'sinr': quality['sinr'],
        'cqi': quality['cqi']
    })
    
    # Store packet counts
    packet_history[ue_type].append({
        'timestamp': timestamp,
        'psbch_tx': metrics['psbch']['tx'],
        'psbch_rx': metrics['psbch']['rx_ok'],
        'pssch_tx': metrics['pssch']['tx'],
        'pssch_rx': metrics['pssch']['rx_ok'],
        'errors': metrics['pssch']['rx_not_ok']
    })

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('tactical_dashboard.html')

@app.route('/api/syncref')
def api_syncref():
    """Get SyncRef UE metrics"""
    metrics = syncref_parser.get_latest_metrics()
    quality = syncref_parser.get_link_quality_metrics(metrics)
    
    # Store in history
    store_metrics('syncref', metrics, quality)
    
    return jsonify({
        'ue_type': 'syncref',
        'role': 'Primary Sync Source',
        'status': metrics['status'],
        'frame': metrics['frame'],
        'slot': metrics['slot'],
        'frame_slot': f"{metrics['frame']}:{metrics['slot']}",
        'carrier': '2.6 GHz',
        'bandwidth': '106 RBs',
        'mcs': 9,
        'tx_power': '23 dBm',
        'psbch': metrics['psbch'],
        'pscch': metrics['pscch'],
        'pssch': metrics['pssch'],
        'psfch': metrics['psfch'],
        'quality': quality,
        'terminal_output': metrics['terminal_output'][-5:],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/nearby')
def api_nearby():
    """Get Nearby UE metrics"""
    metrics = nearby_parser.get_latest_metrics()
    quality = nearby_parser.get_link_quality_metrics(metrics)
    
    # Store in history
    store_metrics('nearby', metrics, quality)
    
    is_synced = metrics['psbch']['rx_ok'] > 0
    
    return jsonify({
        'ue_type': 'nearby',
        'role': 'Synchronized Receiver',
        'status': metrics['status'],
        'frame': metrics['frame'],
        'slot': metrics['slot'],
        'frame_slot': f"{metrics['frame']}:{metrics['slot']}",
        'carrier': '2.6 GHz',
        'bandwidth': '106 RBs',
        'mcs': 9,
        'rx_gain': 'Auto',
        'synchronized': is_synced,
        'psbch': metrics['psbch'],
        'pscch': metrics['pscch'],
        'pssch': metrics['pssch'],
        'psfch': metrics['psfch'],
        'quality': quality,
        'terminal_output': metrics['terminal_output'][-5:],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/link_status')
def api_link_status():
    """Get overall link status"""
    syncref_metrics = syncref_parser.get_latest_metrics()
    nearby_metrics = nearby_parser.get_latest_metrics()
    
    syncref_quality = syncref_parser.get_link_quality_metrics(syncref_metrics)
    nearby_quality = nearby_parser.get_link_quality_metrics(nearby_metrics)
    
    overall_quality = (syncref_quality['quality_level'] + nearby_quality['quality_level']) / 2
    
    link_established = (
        syncref_metrics['status'] == 'running' and 
        nearby_metrics['status'] == 'running' and
        nearby_metrics['psbch']['rx_ok'] > 0
    )
    
    return jsonify({
        'link_established': link_established,
        'overall_quality': overall_quality,
        'syncref_running': syncref_metrics['status'] == 'running',
        'nearby_running': nearby_metrics['status'] == 'running',
        'pssch_total_tx': syncref_metrics['pssch']['tx'] + nearby_metrics['pssch']['tx'],
        'pssch_total_rx_ok': syncref_metrics['pssch']['rx_ok'] + nearby_metrics['pssch']['rx_ok'],
        'pssch_total_errors': syncref_metrics['pssch']['rx_not_ok'] + nearby_metrics['pssch']['rx_not_ok'],
        'psbch_sync_count': nearby_metrics['psbch']['rx_ok'],
        'gnb_status': 'offline',
        'core_status': 'offline',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/throughput_history')
def api_throughput_history():
    """Get throughput history for charts"""
    return jsonify({
        'syncref': list(throughput_history['syncref']),
        'nearby': list(throughput_history['nearby'])
    })

@app.route('/api/signal_history')
def api_signal_history():
    """Get signal quality history for charts"""
    return jsonify({
        'syncref': list(signal_history['syncref']),
        'nearby': list(signal_history['nearby'])
    })

@app.route('/api/message_flow')
def api_message_flow():
    """Get protocol message flow for sequence diagram"""
    syncref_metrics = syncref_parser.get_latest_metrics()
    nearby_metrics = nearby_parser.get_latest_metrics()
    
    # Generate message flow based on packet counts
    flow = []
    
    if syncref_metrics['psbch']['tx'] > 0:
        flow.append({
            'from': 'Alpha',
            'to': 'Bravo',
            'message': 'PSBCH',
            'count': syncref_metrics['psbch']['tx'],
            'description': 'Sync Signal'
        })
    
    if nearby_metrics['psbch']['rx_ok'] > 0:
        flow.append({
            'from': 'Bravo',
            'to': 'Bravo',
            'message': 'S-PSS/S-SSS',
            'count': nearby_metrics['psbch']['rx_ok'],
            'description': 'Detection'
        })
    
    if syncref_metrics['pssch']['tx'] > 0:
        flow.append({
            'from': 'Alpha',
            'to': 'Bravo',
            'message': 'PSSCH',
            'count': syncref_metrics['pssch']['tx'],
            'description': f"Data: {syncref_metrics['pssch']['tx']:,} pkts"
        })
    
    if nearby_metrics['pssch']['tx'] > 0:
        flow.append({
            'from': 'Bravo',
            'to': 'Alpha',
            'message': 'PSSCH',
            'count': nearby_metrics['pssch']['tx'],
            'description': f"Data: {nearby_metrics['pssch']['tx']:,} pkts"
        })
    
    if nearby_metrics['psfch']['tx'] > 0:
        flow.append({
            'from': 'Bravo',
            'to': 'Alpha',
            'message': 'PSFCH',
            'count': nearby_metrics['psfch']['tx'],
            'description': 'Feedback'
        })
    
    return jsonify({'flow': flow})

@app.route('/api/spectrum_data')
def api_spectrum_data():
    """Get spectrum/FFT data for visualization"""
    # Generate mock frequency response data
    # In production, this would parse from PCAP or SDR
    import numpy as np
    
    # Frequency bins (MHz offset from carrier)
    freq_bins = np.linspace(-53, 53, 106)  # 106 RBs
    
    # Simulated channel response (based on current RSRP/SINR)
    syncref_metrics = syncref_parser.get_latest_metrics()
    nearby_metrics = nearby_parser.get_latest_metrics()
    
    syncref_quality = syncref_parser.get_link_quality_metrics(syncref_metrics)
    nearby_quality = nearby_parser.get_link_quality_metrics(nearby_metrics)
    
    # Generate spectrum based on signal quality
    base_power = syncref_quality['rsrp']
    noise_floor = base_power - syncref_quality['sinr']
    
    # Channel response with some variation
    channel_response = base_power + np.random.normal(0, 2, 106)
    noise = noise_floor + np.random.normal(0, 1, 106)
    
    return jsonify({
        'frequency': freq_bins.tolist(),
        'channel_response': channel_response.tolist(),
        'noise_floor': noise.tolist(),
        'rsrp': syncref_quality['rsrp'],
        'sinr': syncref_quality['sinr']
    })

@app.route('/api/export/csv')
def export_csv():
    """Export all historical data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Timestamp', 'UE', 'TX_Mbps', 'RX_Mbps', 
        'RSRP', 'SINR', 'CQI', 
        'PSBCH_TX', 'PSSCH_TX', 'PSSCH_RX', 'Errors'
    ])
    
    # Write data
    for ue_type in ['syncref', 'nearby']:
        for i in range(len(throughput_history[ue_type])):
            tp = throughput_history[ue_type][i]
            sig = signal_history[ue_type][i]
            pkt = packet_history[ue_type][i]
            
            writer.writerow([
                tp['timestamp'],
                ue_type,
                tp['tx_mbps'],
                tp['rx_mbps'],
                sig['rsrp'],
                sig['sinr'],
                sig['cqi'],
                pkt['psbch_tx'],
                pkt['pssch_tx'],
                pkt['pssch_rx'],
                pkt['errors']
            ])
    
    # Prepare file for download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'sidelink_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/events')
def api_events():
    """Get recent events log"""
    events = [
        {
            'time': datetime.now().strftime('%H:%M:%S'),
            'type': 'success',
            'message': '✅ Tactical comms link: OPERATIONAL'
        },
        {
            'time': datetime.now().strftime('%H:%M:%S'),
            'type': 'info',
            'message': '⚠️ Operating in autonomous mode (no infrastructure)'
        },
        {
            'time': datetime.now().strftime('%H:%M:%S'),
            'type': 'success',
            'message': '🔐 Channel quality: Excellent'
        }
    ]
    
    return jsonify({'events': events})

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'OAI Sidelink Dashboard'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
