"""
TimeSleuth timeline reconstruction and activity analysis
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Union, Optional
from collections import defaultdict, OrderedDict


class TimelineBuilder:
    """
    Build and analyze file activity timelines for forensic investigation.
    """
    
    def __init__(self):
        self.files = {}
        self.activities = []
    
    def add_file(self, file_path: Union[str, Path], timestamps: Dict[str, datetime]) -> None:
        """
        Add a file and its timestamps to the timeline.
        
        Args:
            file_path: Path to the file
            timestamps: Dictionary of timestamps from get_file_timestamps()
        """
        path_str = str(file_path)
        self.files[path_str] = {
            'path': file_path,
            'timestamps': timestamps,
            'size': None,
            'extension': Path(file_path).suffix.lower() if Path(file_path).suffix else None
        }
        
        # Add file size if possible
        try:
            self.files[path_str]['size'] = Path(file_path).stat().st_size
        except (OSError, PermissionError):
            pass
        
        # Create activity entries for each timestamp
        for ts_type, ts_value in timestamps.items():
            if ts_value:
                self.activities.append({
                    'timestamp': ts_value,
                    'type': ts_type,
                    'file_path': path_str,
                    'file_size': self.files[path_str]['size'],
                    'file_extension': self.files[path_str]['extension']
                })
    
    def get_chronological_timeline(self, sort_by: str = 'modified') -> List[Dict]:
        """
        Get chronologically sorted timeline of file activities.
        
        Args:
            sort_by: Timestamp type to sort by ('modified', 'accessed', 'created', 'all')
            
        Returns:
            List of activity dictionaries sorted by timestamp
        """
        if sort_by == 'all':
            timeline = sorted(self.activities, key=lambda x: x['timestamp'])
        else:
            # Filter activities by timestamp type
            filtered_activities = [
                activity for activity in self.activities 
                if activity['type'] == sort_by
            ]
            timeline = sorted(filtered_activities, key=lambda x: x['timestamp'])
        
        # Add sequence numbers and time gaps
        for i, activity in enumerate(timeline):
            activity['sequence'] = i + 1
            
            if i > 0:
                time_gap = activity['timestamp'] - timeline[i-1]['timestamp']
                activity['time_since_previous'] = time_gap.total_seconds()
            else:
                activity['time_since_previous'] = 0
        
        return timeline
    
    def get_activity_groups(self, time_window_minutes: int = 60) -> Dict:
        """
        Group activities by time windows to identify activity bursts.
        
        Args:
            time_window_minutes: Size of time window for grouping activities
            
        Returns:
            Dictionary containing grouped activities and analysis
        """
        if not self.activities:
            return {'groups': [], 'summary': {}}
        
        sorted_activities = sorted(self.activities, key=lambda x: x['timestamp'])
        groups = []
        current_group = []
        current_group_start = None
        
        time_window = timedelta(minutes=time_window_minutes)
        
        for activity in sorted_activities:
            if not current_group:
                # Start new group
                current_group = [activity]
                current_group_start = activity['timestamp']
            elif activity['timestamp'] - current_group_start <= time_window:
                # Add to current group
                current_group.append(activity)
            else:
                # Finish current group and start new one
                groups.append(self._finalize_activity_group(current_group))
                current_group = [activity]
                current_group_start = activity['timestamp']
        
        # Don't forget the last group
        if current_group:
            groups.append(self._finalize_activity_group(current_group))
        
        # Generate summary statistics
        summary = self._generate_activity_summary(groups)
        
        return {
            'groups': groups,
            'summary': summary,
            'time_window_minutes': time_window_minutes
        }
    
    def _finalize_activity_group(self, activities: List[Dict]) -> Dict:
        """
        Process and analyze a group of activities.
        """
        if not activities:
            return {}
        
        start_time = min(activity['timestamp'] for activity in activities)
        end_time = max(activity['timestamp'] for activity in activities)
        duration = (end_time - start_time).total_seconds()
        
        # Count activities by type
        activity_counts = defaultdict(int)
        file_types = defaultdict(int)
        total_size = 0
        unique_files = set()
        
        for activity in activities:
            activity_counts[activity['type']] += 1
            if activity['file_extension']:
                file_types[activity['file_extension']] += 1
            if activity['file_size']:
                total_size += activity['file_size']
            unique_files.add(activity['file_path'])
        
        return {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'activity_count': len(activities),
            'unique_files': len(unique_files),
            'activity_types': dict(activity_counts),
            'file_types': dict(file_types),
            'total_file_size': total_size,
            'activities': activities,
            'intensity': len(activities) / max(duration, 1)  # Activities per second
        }
    
    def _generate_activity_summary(self, groups: List[Dict]) -> Dict:
        """
        Generate summary statistics for activity groups.
        """
        if not groups:
            return {}
        
        total_activities = sum(group['activity_count'] for group in groups)
        total_files = sum(group['unique_files'] for group in groups)
        total_size = sum(group['total_file_size'] for group in groups)
        
        # Find peak activity periods
        peak_intensity = max(group['intensity'] for group in groups)
        peak_groups = [group for group in groups if group['intensity'] == peak_intensity]
        
        # Activity distribution over time
        activity_timeline = []
        for group in groups:
            activity_timeline.append({
                'time': group['start_time'],
                'activity_count': group['activity_count']
            })
        
        return {
            'total_activity_groups': len(groups),
            'total_activities': total_activities,
            'total_unique_files': total_files,
            'total_file_size': total_size,
            'peak_intensity': peak_intensity,
            'peak_activity_periods': len(peak_groups),
            'average_group_size': total_activities / len(groups),
            'activity_timeline': activity_timeline
        }


def reconstruct_activity(directory_path: Union[str, Path], 
                        analysis_type: str = 'comprehensive') -> Dict:
    """
    Reconstruct file system activity from directory timestamps.
    
    Args:
        directory_path: Path to directory to analyze
        analysis_type: Type of analysis ('basic', 'comprehensive', 'suspicious_only')
        
    Returns:
        Dictionary containing reconstructed activity analysis
    """
    from .utils import get_file_timestamps, detect_time_gaps
    
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    builder = TimelineBuilder()
    
    # Collect all files and timestamps
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                timestamps = get_file_timestamps(file_path)
                builder.add_file(file_path, timestamps)
            except (OSError, PermissionError):
                continue
    
    results = {
        'directory': str(directory),
        'analysis_type': analysis_type,
        'file_count': len(builder.files)
    }
    
    if analysis_type in ['basic', 'comprehensive']:
        # Basic timeline reconstruction
        results['chronological_timeline'] = builder.get_chronological_timeline('all')
        results['activity_groups'] = builder.get_activity_groups()
    
    if analysis_type == 'comprehensive':
        # Additional comprehensive analysis
        results['modification_timeline'] = builder.get_chronological_timeline('modified')
        results['access_timeline'] = builder.get_chronological_timeline('accessed')
        
        # Detect time gaps and unusual patterns
        all_timestamps = []
        for file_info in builder.files.values():
            all_timestamps.extend([ts for ts in file_info['timestamps'].values() if ts])
        
        results['time_gaps'] = detect_time_gaps(all_timestamps)
        results['activity_patterns'] = _analyze_activity_patterns(builder)
    
    if analysis_type == 'suspicious_only':
        # Focus on suspicious activity only
        results['suspicious_patterns'] = _find_suspicious_activity(builder)
    
    return results


def _analyze_activity_patterns(builder: TimelineBuilder) -> Dict:
    """
    Analyze activity patterns for forensic insights.
    """
    patterns = {
        'working_hours_activity': 0,
        'off_hours_activity': 0,
        'weekend_activity': 0,
        'bulk_operations': [],
        'file_type_patterns': defaultdict(list)
    }
    
    for activity in builder.activities:
        timestamp = activity['timestamp']
        hour = timestamp.hour
        weekday = timestamp.weekday()
        
        # Categorize by time of day
        if 9 <= hour <= 17:  # Business hours
            patterns['working_hours_activity'] += 1
        else:
            patterns['off_hours_activity'] += 1
        
        # Weekend activity (Saturday=5, Sunday=6)
        if weekday >= 5:
            patterns['weekend_activity'] += 1
        
        # Track file type patterns
        if activity['file_extension']:
            patterns['file_type_patterns'][activity['file_extension']].append(timestamp)
    
    # Convert defaultdict to regular dict
    patterns['file_type_patterns'] = dict(patterns['file_type_patterns'])
    
    return patterns


def _find_suspicious_activity(builder: TimelineBuilder) -> List[Dict]:
    """
    Identify suspicious activity patterns in timeline.
    """
    suspicious = []
    
    # Look for high-intensity activity bursts
    activity_groups = builder.get_activity_groups(time_window_minutes=5)
    
    for group in activity_groups['groups']:
        if group['intensity'] > 10:  # More than 10 activities per second
            suspicious.append({
                'pattern': 'high_intensity_burst',
                'start_time': group['start_time'],
                'end_time': group['end_time'],
                'intensity': group['intensity'],
                'activity_count': group['activity_count'],
                'severity': 'high'
            })
    
    # Look for off-hours activity
    off_hours_count = 0
    for activity in builder.activities:
        hour = activity['timestamp'].hour
        if hour < 6 or hour > 22:  # Very early or very late
            off_hours_count += 1
    
    if off_hours_count > len(builder.activities) * 0.3:  # More than 30% off-hours
        suspicious.append({
            'pattern': 'excessive_off_hours_activity',
            'off_hours_count': off_hours_count,
            'total_activities': len(builder.activities),
            'percentage': (off_hours_count / len(builder.activities)) * 100,
            'severity': 'medium'
        })
    
    return suspicious