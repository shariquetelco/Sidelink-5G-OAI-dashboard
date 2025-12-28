#!/usr/bin/env python3
"""
OAI 5G Sidelink Log Parser
Extracts real-time metrics from SyncRef and Nearby UE logs
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

class SidelinkParser:
    """Parser for OAI sidelink UE logs"""
    
    def __init__(self, log_file: str, ue_type: str = "syncref"):
        """
        Initialize parser
        
        Args:
            log_file: Path to UE log file
            ue_type: "syncref" or "nearby"
        """
        self.log_file = log_file
        self.ue_type = ue_type
        self.last_position = 0
        
    def parse_stats_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single stats line from UE logs
        
        Example input:
        [NR_PHY] I [UE0] 128:19 PSBCH Stats: TX 1561, RX ok 0, RX not ok 0
        """
        # Extract frame:slot
        frame_slot_match = re.search(r'\[UE0\]\s+(\d+):(\d+)', line)
        if not frame_slot_match:
            return None
            
        frame = int(frame_slot_match.group(1))
        slot = int(frame_slot_match.group(2))
        
        # Extract channel type and stats
        stats = {}
        
        # PSBCH stats
        psbch_match = re.search(r'PSBCH Stats: TX (\d+), RX ok (\d+), RX not ok (\d+)', line)
        if psbch_match:
            stats['channel'] = 'PSBCH'
            stats['tx'] = int(psbch_match.group(1))
            stats['rx_ok'] = int(psbch_match.group(2))
            stats['rx_not_ok'] = int(psbch_match.group(3))
            
        # PSCCH stats
        pscch_match = re.search(r'PSCCH Stats: TX (\d+), RX ok (\d+)', line)
        if pscch_match:
            stats['channel'] = 'PSCCH'
            stats['tx'] = int(pscch_match.group(1))
            stats['rx_ok'] = int(pscch_match.group(2))
            stats['rx_not_ok'] = 0
            
        # PSSCH stats
        pssch_match = re.search(r'PSSCH Stats: TX (\d+), RX ok (\d+), RX not ok \((\d+)/(\d+)/(\d+)/(\d+)\)', line)
        if pssch_match:
            stats['channel'] = 'PSSCH'
            stats['tx'] = int(pssch_match.group(1))
            stats['rx_ok'] = int(pssch_match.group(2))
            stats['rx_not_ok'] = sum([
                int(pssch_match.group(3)),
                int(pssch_match.group(4)),
                int(pssch_match.group(5)),
                int(pssch_match.group(6))
            ])
            
        # PSFCH stats
        psfch_match = re.search(r'PSFCH Stats: TX (\d+)', line)
        if psfch_match:
            stats['channel'] = 'PSFCH'
            stats['tx'] = int(psfch_match.group(1))
            stats['rx_ok'] = 0
            stats['rx_not_ok'] = 0
            
        if stats:
            stats['frame'] = frame
            stats['slot'] = slot
            stats['timestamp'] = datetime.now().isoformat()
            return stats
            
        return None
        
    def get_latest_metrics(self) -> Dict:
        """
        Read log file and extract latest metrics
        
        Returns:
            Dict with current UE status and stats
        """
        metrics = {
            'status': 'unknown',
            'role': 'SyncRef' if self.ue_type == 'syncref' else 'Nearby UE',
            'frame': 0,
            'slot': 0,
            'uptime': 0,
            'psbch': {'tx': 0, 'rx_ok': 0, 'rx_not_ok': 0},
            'pscch': {'tx': 0, 'rx_ok': 0, 'rx_not_ok': 0},
            'pssch': {'tx': 0, 'rx_ok': 0, 'rx_not_ok': 0},
            'psfch': {'tx': 0, 'rx_ok': 0, 'rx_not_ok': 0},
            'terminal_output': [],
            'events': []
        }
        
        try:
            with open(self.log_file, 'r') as f:
                # Seek to last position
                f.seek(self.last_position)
                lines = f.readlines()
                self.last_position = f.tell()
                
                if not lines:
                    return metrics
                    
                metrics['status'] = 'running'
                
                # Process last 100 lines for stats
                for line in lines[-100:]:
                    parsed = self.parse_stats_line(line)
                    if parsed:
                        channel = parsed['channel']
                        metrics['frame'] = parsed['frame']
                        metrics['slot'] = parsed['slot']
                        
                        if channel in ['PSBCH', 'PSCCH', 'PSSCH', 'PSFCH']:
                            ch_key = channel.lower()
                            metrics[ch_key]['tx'] = parsed['tx']
                            metrics[ch_key]['rx_ok'] = parsed['rx_ok']
                            metrics[ch_key]['rx_not_ok'] = parsed['rx_not_ok']
                
                # Get last 10 lines for terminal output
                metrics['terminal_output'] = [
                    line.strip() for line in lines[-10:] 
                    if line.strip() and not line.startswith('[NR_PHY] I ============')
                ]
                
        except FileNotFoundError:
            metrics['status'] = 'stopped'
        except Exception as e:
            metrics['status'] = 'error'
            metrics['error'] = str(e)
            
        return metrics
        
    def calculate_success_rate(self, tx: int, rx_ok: int, rx_not_ok: int) -> float:
        """Calculate success rate percentage"""
        total = rx_ok + rx_not_ok
        if total == 0:
            return 100.0 if tx > 0 else 0.0
        return (rx_ok / total) * 100.0
        
    def get_link_quality_metrics(self, metrics: Dict) -> Dict:
        """
        Calculate link quality metrics
        
        Returns:
            Dict with quality indicators
        """
        pssch_success = self.calculate_success_rate(
            metrics['pssch']['tx'],
            metrics['pssch']['rx_ok'],
            metrics['pssch']['rx_not_ok']
        )
        
        psbch_success = self.calculate_success_rate(
            metrics['psbch']['tx'],
            metrics['psbch']['rx_ok'],
            metrics['psbch']['rx_not_ok']
        )
        
        # Overall quality based on PSSCH (data channel)
        if pssch_success >= 99:
            quality = 'EXCELLENT'
            quality_level = 100
        elif pssch_success >= 95:
            quality = 'GOOD'
            quality_level = 80
        elif pssch_success >= 90:
            quality = 'FAIR'
            quality_level = 60
        else:
            quality = 'POOR'
            quality_level = 40
            
        return {
            'quality': quality,
            'quality_level': quality_level,
            'pssch_success_rate': pssch_success,
            'psbch_success_rate': psbch_success,
            'rsrp': -45,  # Mock value (would need to parse from different log line)
            'sinr': 25,   # Mock value
            'cqi': 15     # Mock value
        }
