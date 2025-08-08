"""
TimeSleuth core functionality - main API functions
"""

import os
from pathlib import Path
from typing import List, Dict, Union, Optional
from .utils import get_file_timestamps
from .anomaly_detection import detect_anomalies
from .timeline import TimelineBuilder


def scan_directory(directory_path: Union[str, Path], 
                  recursive: bool = True,
                  include_hidden: bool = False,
                  file_extensions: Optional[List[str]] = None) -> List[Dict]:
    """
    Scan directory for timestamp anomalies and suspicious patterns.
    
    Args:
        directory_path: Path to directory to scan
        recursive: Whether to scan subdirectories
        include_hidden: Whether to include hidden files
        file_extensions: List of file extensions to include (e.g., ['.log', '.txt'])
        
    Returns:
        List of dictionaries containing anomaly information:
        - path: File path
        - reason: Description of anomaly
        - severity: 'high', 'medium', 'low'
        - timestamps: Dictionary of file timestamps
        - details: Additional details about the anomaly
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")
    
    anomalies = []
    
    # Get file iterator based on recursive setting
    if recursive:
        file_iterator = directory.rglob('*')
    else:
        file_iterator = directory.iterdir()
    
    for file_path in file_iterator:
        # Skip directories
        if not file_path.is_file():
            continue
            
        # Skip hidden files unless requested
        if not include_hidden and file_path.name.startswith('.'):
            continue
            
        # Filter by file extensions if specified
        if file_extensions and file_path.suffix.lower() not in [ext.lower() for ext in file_extensions]:
            continue
        
        try:
            # Get file timestamps
            timestamps = get_file_timestamps(file_path)
            
            # Run anomaly detection on this file
            file_anomalies = detect_anomalies(file_path, timestamps)
            
            # Add file-specific information to anomalies
            for anomaly in file_anomalies:
                anomaly['path'] = str(file_path)
                anomaly['timestamps'] = timestamps
                anomalies.append(anomaly)
                
        except (OSError, PermissionError) as e:
            # Log files we can't access but continue scanning
            anomalies.append({
                'path': str(file_path),
                'reason': f"Access denied: {e}",
                'severity': 'low',
                'timestamps': {},
                'details': {'error': str(e)}
            })
    
    return anomalies


def create_timeline(directory_path: Union[str, Path], 
                   output_format: str = 'list',
                   sort_by: str = 'modified') -> Union[List[Dict], Dict]:
    """
    Generate timeline data from directory contents.
    
    Args:
        directory_path: Path to directory to analyze
        output_format: 'list' for chronological list, 'grouped' for activity grouping
        sort_by: Timestamp type to sort by ('modified', 'accessed', 'created')
        
    Returns:
        Timeline data structure containing file activity information
    """
    builder = TimelineBuilder()
    
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Collect all files and their timestamps
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                timestamps = get_file_timestamps(file_path)
                builder.add_file(file_path, timestamps)
            except (OSError, PermissionError):
                continue
    
    # Generate timeline based on format
    if output_format == 'list':
        return builder.get_chronological_timeline(sort_by)
    elif output_format == 'grouped':
        return builder.get_activity_groups()
    else:
        raise ValueError(f"Invalid output format: {output_format}")


def find_backdated_files(directory_path: Union[str, Path],
                        reference_time: Optional[str] = None,
                        threshold_days: int = 30) -> List[Dict]:
    """
    Find files with potentially backdated timestamps.
    
    Args:
        directory_path: Path to directory to scan
        reference_time: Reference timestamp (ISO format) or None for current time
        threshold_days: Days before reference time to consider suspicious
        
    Returns:
        List of dictionaries containing backdated file information
    """
    from datetime import datetime, timezone, timedelta
    
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Set reference time
    if reference_time:
        ref_time = datetime.fromisoformat(reference_time)
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)
    else:
        ref_time = datetime.now(timezone.utc)
    
    threshold_time = ref_time - timedelta(days=threshold_days)
    backdated_files = []
    
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                timestamps = get_file_timestamps(file_path)
                
                # Check if any timestamp is suspiciously old
                suspicious_reasons = []
                
                if timestamps.get('modified') and timestamps['modified'] < threshold_time:
                    age_days = (ref_time - timestamps['modified']).days
                    if age_days > threshold_days * 2:  # Very old files are more suspicious
                        suspicious_reasons.append(f"Modified time is {age_days} days old")
                
                if timestamps.get('created') and timestamps['created'] < threshold_time:
                    age_days = (ref_time - timestamps['created']).days
                    if age_days > threshold_days * 2:
                        suspicious_reasons.append(f"Created time is {age_days} days old")
                
                # Also check for timestamp ordering issues
                if timestamps.get('created') and timestamps.get('modified'):
                    if timestamps['created'] > timestamps['modified']:
                        suspicious_reasons.append("Creation time is after modification time")
                
                if suspicious_reasons:
                    backdated_files.append({
                        'path': str(file_path),
                        'reasons': suspicious_reasons,
                        'timestamps': timestamps,
                        'age_days': (ref_time - timestamps.get('modified', ref_time)).days
                    })
                    
            except (OSError, PermissionError):
                continue
    
    # Sort by age (most suspicious first)
    return sorted(backdated_files, key=lambda x: x['age_days'], reverse=True)