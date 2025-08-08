"""
TimeSleuth utility functions for timestamp operations
"""

import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Union


def get_file_timestamps(file_path: Union[str, Path]) -> Dict[str, datetime]:
    """
    Get all available timestamps for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing timestamp information:
        - 'created': Creation time (Windows) or metadata change time (Unix)
        - 'modified': Last modification time
        - 'accessed': Last access time
        - 'metadata_changed': Metadata change time (Unix only)
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    stat_result = path.stat()
    timestamps = {}
    
    # Get modification time
    timestamps['modified'] = datetime.fromtimestamp(stat_result.st_mtime, timezone.utc)
    
    # Get access time
    timestamps['accessed'] = datetime.fromtimestamp(stat_result.st_atime, timezone.utc)
    
    # Get creation/metadata change time
    if hasattr(stat_result, 'st_birthtime'):
        # macOS has birth time
        timestamps['created'] = datetime.fromtimestamp(stat_result.st_birthtime, timezone.utc)
    elif os.name == 'nt':
        # Windows creation time
        timestamps['created'] = datetime.fromtimestamp(stat_result.st_ctime, timezone.utc)
    else:
        # Unix systems - st_ctime is metadata change time
        timestamps['metadata_changed'] = datetime.fromtimestamp(stat_result.st_ctime, timezone.utc)
        timestamps['created'] = None
    
    return timestamps


def format_timestamp(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string for datetime
        
    Returns:
        Formatted timestamp string or "N/A" if datetime is None
    """
    if dt is None:
        return "N/A"
    return dt.strftime(format_str)


def timestamp_to_epoch(dt: datetime) -> float:
    """
    Convert datetime to Unix epoch timestamp.
    
    Args:
        dt: Datetime object
        
    Returns:
        Unix epoch timestamp as float
    """
    return dt.timestamp()


def epoch_to_timestamp(epoch: float) -> datetime:
    """
    Convert Unix epoch timestamp to datetime.
    
    Args:
        epoch: Unix epoch timestamp
        
    Returns:
        Datetime object in UTC
    """
    return datetime.fromtimestamp(epoch, timezone.utc)


def is_valid_timestamp_range(timestamps: Dict[str, datetime]) -> bool:
    """
    Check if timestamp relationships are logically valid.
    
    Args:
        timestamps: Dictionary of timestamps from get_file_timestamps()
        
    Returns:
        True if timestamps are in valid relationship, False otherwise
    """
    modified = timestamps.get('modified')
    accessed = timestamps.get('accessed')
    created = timestamps.get('created')
    
    if not modified:
        return False
    
    # Creation time should not be after modification time
    if created and created > modified:
        return False
    
    # Access time anomalies are less strict due to mount options
    # but extreme differences might indicate tampering
    if accessed and modified:
        # Allow some flexibility for access time
        time_diff = abs((accessed - modified).total_seconds())
        if time_diff > 86400 * 365 * 10:  # 10 years difference is suspicious
            return False
    
    return True


def calculate_timestamp_entropy(timestamps_list: list) -> float:
    """
    Calculate entropy of timestamp distribution to detect batch operations.
    
    Args:
        timestamps_list: List of timestamp values
        
    Returns:
        Entropy value (higher = more random, lower = more clustered)
    """
    import math
    from collections import Counter
    
    if not timestamps_list:
        return 0.0
    
    # Group timestamps by second to detect clustering
    seconds = [int(ts.timestamp()) for ts in timestamps_list if ts]
    
    if not seconds:
        return 0.0
    
    # Calculate frequency distribution
    freq_dist = Counter(seconds)
    total = len(seconds)
    
    # Calculate Shannon entropy
    entropy = 0.0
    for count in freq_dist.values():
        if count > 0:
            prob = count / total
            entropy -= prob * math.log2(prob)
    
    return entropy


def detect_time_gaps(timestamps: list, threshold_hours: int = 24) -> list:
    """
    Detect unusual time gaps in a sequence of timestamps.
    
    Args:
        timestamps: List of datetime objects
        threshold_hours: Minimum gap size to flag (default 24 hours)
        
    Returns:
        List of gap information dictionaries
    """
    if len(timestamps) < 2:
        return []
    
    sorted_timestamps = sorted([ts for ts in timestamps if ts])
    gaps = []
    
    for i in range(1, len(sorted_timestamps)):
        gap = sorted_timestamps[i] - sorted_timestamps[i-1]
        gap_hours = gap.total_seconds() / 3600
        
        if gap_hours > threshold_hours:
            gaps.append({
                'start': sorted_timestamps[i-1],
                'end': sorted_timestamps[i],
                'duration_hours': gap_hours,
                'suspicious': gap_hours > threshold_hours * 7  # Week-long gaps are very suspicious
            })
    
    return gaps