"""
TimeSleuth - Digital Forensics Timestamp Analysis Library
=========================================================

Uncover digital footprints through timestamp forensics.

A lightweight Python library for digital forensics investigators, security 
researchers, and system administrators to analyze file timestamp patterns 
and detect suspicious activity.

Basic Usage:
    import timesleuth as ts
    
    # Scan directory for timestamp anomalies
    anomalies = ts.scan_directory("/evidence/")
    
    # Generate timeline data
    timeline = ts.create_timeline("/var/log/")
    
    # Detect backdated files
    backdated = ts.find_backdated_files("/suspicious_folder/")
"""

__version__ = "1.0.0"
__author__ = "TimeSleuth Contributors"
__license__ = "MIT"

from .core import scan_directory, create_timeline, find_backdated_files
from .anomaly_detection import detect_anomalies, analyze_timestamp_patterns
from .timeline import TimelineBuilder, reconstruct_activity
from .utils import get_file_timestamps, format_timestamp
from .reporting import (export_to_json, export_to_csv, generate_forensics_report,
                       create_timeline_report, create_summary_report)

__all__ = [
    'scan_directory',
    'create_timeline', 
    'find_backdated_files',
    'detect_anomalies',
    'analyze_timestamp_patterns',
    'TimelineBuilder',
    'reconstruct_activity',
    'get_file_timestamps',
    'format_timestamp',
    'export_to_json',
    'export_to_csv',
    'generate_forensics_report',
    'create_timeline_report',
    'create_summary_report'
]