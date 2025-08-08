"""
TimeSleuth anomaly detection algorithms
"""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional, Union
from collections import defaultdict, Counter
from .utils import is_valid_timestamp_range, calculate_timestamp_entropy


def detect_anomalies(file_path: Union[str, Path], timestamps: Dict[str, datetime]) -> List[Dict]:
    """
    Detect timestamp anomalies in a single file.
    
    Args:
        file_path: Path to the file being analyzed
        timestamps: Dictionary of file timestamps from get_file_timestamps()
        
    Returns:
        List of anomaly dictionaries with reason, severity, and details
    """
    anomalies = []
    path = Path(file_path)
    
    # Check basic timestamp validity
    if not is_valid_timestamp_range(timestamps):
        anomalies.append({
            'reason': 'Invalid timestamp relationships',
            'severity': 'high',
            'details': {'issue': 'Creation time after modification time or extreme time differences'}
        })
    
    # Check for impossible future dates
    now = datetime.now(timezone.utc)
    for ts_type, ts_value in timestamps.items():
        if ts_value and ts_value > now + timedelta(minutes=5):  # Allow 5 min clock skew
            anomalies.append({
                'reason': f'Future {ts_type} timestamp',
                'severity': 'high',
                'details': {
                    'timestamp_type': ts_type,
                    'timestamp_value': ts_value.isoformat(),
                    'future_by_seconds': (ts_value - now).total_seconds()
                }
            })
    
    # Check for suspiciously old timestamps (pre-1980 is often a sign of corruption)
    epoch_1980 = datetime(1980, 1, 1, tzinfo=timezone.utc)
    for ts_type, ts_value in timestamps.items():
        if ts_value and ts_value < epoch_1980:
            anomalies.append({
                'reason': f'Suspiciously old {ts_type} timestamp',
                'severity': 'medium',
                'details': {
                    'timestamp_type': ts_type,
                    'timestamp_value': ts_value.isoformat(),
                    'years_old': (now - ts_value).days / 365.25
                }
            })
    
    # Check for exact timestamp matches (suspicious for manual tampering)
    ts_values = [ts for ts in timestamps.values() if ts]
    if len(set(ts_values)) == 1 and len(ts_values) > 1:
        anomalies.append({
            'reason': 'All timestamps identical',
            'severity': 'medium',
            'details': {'timestamp_value': ts_values[0].isoformat()}
        })
    
    # Check for round timestamp values (ending in :00 seconds, suspicious for tampering)
    for ts_type, ts_value in timestamps.items():
        if ts_value and ts_value.second == 0 and ts_value.microsecond == 0:
            anomalies.append({
                'reason': f'Round timestamp value in {ts_type}',
                'severity': 'low',
                'details': {
                    'timestamp_type': ts_type,
                    'timestamp_value': ts_value.isoformat(),
                    'note': 'Timestamps ending in :00 seconds may indicate manual tampering'
                }
            })
    
    # Check for access time before modification time (usually impossible)
    if timestamps.get('accessed') and timestamps.get('modified'):
        if timestamps['accessed'] < timestamps['modified'] - timedelta(seconds=1):
            anomalies.append({
                'reason': 'Access time before modification time',
                'severity': 'medium',
                'details': {
                    'access_time': timestamps['accessed'].isoformat(),
                    'modified_time': timestamps['modified'].isoformat(),
                    'time_diff_seconds': (timestamps['modified'] - timestamps['accessed']).total_seconds()
                }
            })
    
    return anomalies


def analyze_timestamp_patterns(file_list: List[Path], 
                             detect_batch_ops: bool = True,
                             detect_time_clustering: bool = True) -> Dict:
    """
    Analyze patterns across multiple files to detect suspicious activity.
    
    Args:
        file_list: List of file paths to analyze
        detect_batch_ops: Whether to detect batch operations
        detect_time_clustering: Whether to detect time clustering
        
    Returns:
        Dictionary containing pattern analysis results
    """
    
    results = {
        'total_files': len(file_list),
        'batch_operations': [],
        'time_clusters': [],
        'suspicious_patterns': []
    }
    
    all_timestamps = defaultdict(list)
    file_timestamps = {}
    
    # Collect timestamps from all files
    for file_path in file_list:
        try:
            from .utils import get_file_timestamps
            timestamps = get_file_timestamps(file_path)
            file_timestamps[str(file_path)] = timestamps
            
            for ts_type, ts_value in timestamps.items():
                if ts_value:
                    all_timestamps[ts_type].append((ts_value, file_path))
                    
        except (OSError, PermissionError):
            continue
    
    if detect_batch_ops:
        results['batch_operations'] = _detect_batch_operations(all_timestamps)
    
    if detect_time_clustering:
        results['time_clusters'] = _detect_time_clustering(all_timestamps)
    
    # Detect other suspicious patterns
    results['suspicious_patterns'] = _detect_suspicious_patterns(file_timestamps)
    
    return results


def _detect_batch_operations(all_timestamps: Dict[str, List]) -> List[Dict]:
    """
    Detect evidence of batch file operations (automated scripts, malware, etc.)
    """
    batch_operations = []
    
    for ts_type, ts_list in all_timestamps.items():
        if len(ts_list) < 3:  # Need at least 3 files for pattern detection
            continue
            
        # Sort timestamps
        sorted_ts = sorted([(ts, path) for ts, path in ts_list])
        
        # Look for sequences of files with very similar timestamps
        clusters = []
        current_cluster = [sorted_ts[0]]
        
        for i in range(1, len(sorted_ts)):
            ts, path = sorted_ts[i]
            prev_ts, prev_path = sorted_ts[i-1]
            
            # If timestamps are within 1 second, consider them part of same operation
            if (ts - prev_ts).total_seconds() <= 1.0:
                current_cluster.append((ts, path))
            else:
                if len(current_cluster) >= 3:  # Significant batch operation
                    clusters.append(current_cluster)
                current_cluster = [(ts, path)]
        
        # Don't forget the last cluster
        if len(current_cluster) >= 3:
            clusters.append(current_cluster)
        
        # Report significant clusters
        for cluster in clusters:
            batch_operations.append({
                'timestamp_type': ts_type,
                'start_time': cluster[0][0].isoformat(),
                'end_time': cluster[-1][0].isoformat(),
                'file_count': len(cluster),
                'duration_seconds': (cluster[-1][0] - cluster[0][0]).total_seconds(),
                'files': [str(path) for _, path in cluster]
            })
    
    return batch_operations


def _detect_time_clustering(all_timestamps: Dict[str, List]) -> List[Dict]:
    """
    Detect unusual time clustering that might indicate tampering
    """
    clusters = []
    
    for ts_type, ts_list in all_timestamps.items():
        if len(ts_list) < 5:  # Need reasonable sample size
            continue
            
        timestamps = [ts for ts, path in ts_list]
        entropy = calculate_timestamp_entropy(timestamps)
        
        # Low entropy indicates clustering
        if entropy < 2.0:  # Threshold based on experimentation
            clusters.append({
                'timestamp_type': ts_type,
                'entropy': entropy,
                'file_count': len(ts_list),
                'severity': 'high' if entropy < 1.0 else 'medium',
                'description': f'Low timestamp entropy ({entropy:.2f}) suggests artificial clustering'
            })
    
    return clusters


def _detect_suspicious_patterns(file_timestamps: Dict[str, Dict]) -> List[Dict]:
    """
    Detect other suspicious patterns across files
    """
    patterns = []
    
    # Count files with identical timestamp sets
    timestamp_signatures = defaultdict(list)
    
    for file_path, timestamps in file_timestamps.items():
        # Create signature from timestamp values (rounded to seconds)
        sig_parts = []
        for ts_type in ['modified', 'accessed', 'created']:
            ts = timestamps.get(ts_type)
            if ts:
                sig_parts.append(int(ts.timestamp()))
            else:
                sig_parts.append(None)
        
        signature = tuple(sig_parts)
        timestamp_signatures[signature].append(file_path)
    
    # Report groups with identical timestamps
    for signature, file_paths in timestamp_signatures.items():
        if len(file_paths) > 1:
            patterns.append({
                'pattern': 'identical_timestamp_sets',
                'file_count': len(file_paths),
                'files': file_paths,
                'severity': 'high' if len(file_paths) > 5 else 'medium',
                'description': f'{len(file_paths)} files have identical timestamp signatures'
            })
    
    # Check for files with suspiciously round timestamps
    round_timestamp_files = []
    for file_path, timestamps in file_timestamps.items():
        round_count = 0
        for ts in timestamps.values():
            if ts and ts.second == 0 and ts.microsecond == 0:
                round_count += 1
        
        if round_count >= 2:  # Multiple round timestamps suspicious
            round_timestamp_files.append(file_path)
    
    if round_timestamp_files:
        patterns.append({
            'pattern': 'round_timestamps',
            'file_count': len(round_timestamp_files),
            'files': round_timestamp_files,
            'severity': 'medium',
            'description': f'{len(round_timestamp_files)} files have multiple round timestamps'
        })
    
    return patterns