#!/usr/bin/env python3
"""
OAI 5G Sidelink Tactical Dashboard
Flask backend for real-time monitoring
Author: Ahmad Sharique (ahmad@iabg.de)
Company: IABG mbH Munich
"""

from flask import Flask, render_template, jsonify
from parsers.sidelink_parser import SidelinkParser
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
SYNCREF_LOG = os.getenv('SYNCREF_LOG', os.path.expanduser('~/syncref_sl.log'))
NEARBY_LOG = os.getenv('NEARBY_LOG', os.path.expanduser('~/nearby_ue_sl.log'))

# Initialize parsers
syncref_parser = SidelinkParser(SYNCREF_LOG, ue_type='syncref')
nearby_parser = SidelinkParser(NEARBY_LOG, ue_type='nearby')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('tactical_dashboard.html')

@app.route('/api/syncref')
def api_syncref():
    """Get SyncRef UE metrics"""
    metrics = syncref_parser.get_latest_metrics()
    quality = syncref_parser.get_link_quality_metrics(metrics)
    
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
        'terminal_output': metrics['terminal_output'][-5:],  # Last 5 lines
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/nearby')
def api_nearby():
    """Get Nearby UE metrics"""
    metrics = nearby_parser.get_latest_metrics()
    quality = nearby_parser.get_link_quality_metrics(metrics)
    
    # Check if synchronized
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
        'terminal_output': metrics['terminal_output'][-5:],  # Last 5 lines
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/link_status')
def api_link_status():
    """Get overall link status"""
    syncref_metrics = syncref_parser.get_latest_metrics()
    nearby_metrics = nearby_parser.get_latest_metrics()
    
    syncref_quality = syncref_parser.get_link_quality_metrics(syncref_metrics)
    nearby_quality = nearby_parser.get_link_quality_metrics(nearby_metrics)
    
    # Overall link quality is average of both UEs
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
        'gnb_status': 'offline',  # Sidelink doesn't need gNB
        'core_status': 'offline',  # Sidelink doesn't need core
        'timestamp': datetime.now().isoformat()
    })

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
