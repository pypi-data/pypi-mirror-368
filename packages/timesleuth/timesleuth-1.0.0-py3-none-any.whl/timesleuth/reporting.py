"""
TimeSleuth reporting functionality for JSON and CSV output
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union, Any, Optional


def export_to_json(data: Union[List, Dict], 
                   output_path: Union[str, Path], 
                   pretty_print: bool = True) -> None:
    """
    Export data to JSON format.
    
    Args:
        data: Data to export (list or dictionary)
        output_path: Output file path
        pretty_print: Whether to format JSON with indentation
    """
    output_file = Path(output_path)
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Custom JSON encoder for datetime objects
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        if pretty_print:
            json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
        else:
            json.dump(data, f, ensure_ascii=False, default=json_serializer)


def export_to_csv(data: List[Dict], 
                  output_path: Union[str, Path],
                  fieldnames: Optional[List[str]] = None) -> None:
    """
    Export list of dictionaries to CSV format.
    
    Args:
        data: List of dictionaries to export
        output_path: Output file path
        fieldnames: Optional list of field names to include (auto-detected if None)
    """
    if not data:
        raise ValueError("Cannot export empty data to CSV")
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Auto-detect fieldnames if not provided
    if fieldnames is None:
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data:
            # Convert datetime objects to ISO format strings
            processed_item = {}
            for key, value in item.items():
                if isinstance(value, datetime):
                    processed_item[key] = value.isoformat()
                elif isinstance(value, Path):
                    processed_item[key] = str(value)
                elif isinstance(value, (list, dict)):
                    processed_item[key] = json.dumps(value)
                else:
                    processed_item[key] = value
            
            writer.writerow(processed_item)


def generate_forensics_report(scan_results: Dict, 
                            output_path: Union[str, Path],
                            report_format: str = 'json',
                            include_metadata: bool = True) -> Dict:
    """
    Generate a comprehensive forensics report from scan results.
    
    Args:
        scan_results: Results from TimeSleuth analysis
        output_path: Output file path
        report_format: 'json' or 'csv'
        include_metadata: Whether to include metadata in report
        
    Returns:
        Dictionary containing report metadata
    """
    report_data = {
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'timesleuth_version': '1.0.0',
            'report_type': 'forensics_timestamp_analysis'
        },
        'summary': _generate_summary(scan_results),
        'findings': scan_results
    }
    
    if not include_metadata:
        report_data = scan_results
    
    # Export based on format
    if report_format.lower() == 'json':
        export_to_json(report_data, output_path)
    elif report_format.lower() == 'csv':
        # For CSV, flatten the data structure
        flattened_data = _flatten_for_csv(scan_results)
        export_to_csv(flattened_data, output_path)
    else:
        raise ValueError(f"Unsupported report format: {report_format}")
    
    return report_data['report_metadata'] if include_metadata else {}


def _generate_summary(scan_results: Dict) -> Dict:
    """
    Generate executive summary from scan results.
    """
    summary = {
        'total_files_scanned': 0,
        'anomalies_found': 0,
        'high_severity_issues': 0,
        'medium_severity_issues': 0,
        'low_severity_issues': 0,
        'suspicious_patterns': 0,
        'backdated_files': 0
    }
    
    # Count anomalies if present
    if 'anomalies' in scan_results:
        summary['anomalies_found'] = len(scan_results['anomalies'])
        
        for anomaly in scan_results['anomalies']:
            severity = anomaly.get('severity', 'unknown')
            if severity == 'high':
                summary['high_severity_issues'] += 1
            elif severity == 'medium':
                summary['medium_severity_issues'] += 1
            elif severity == 'low':
                summary['low_severity_issues'] += 1
    
    # Count pattern analysis results
    if 'pattern_analysis' in scan_results:
        patterns = scan_results['pattern_analysis']
        if 'suspicious_patterns' in patterns:
            summary['suspicious_patterns'] = len(patterns['suspicious_patterns'])
    
    # Count backdated files
    if 'backdated_files' in scan_results:
        summary['backdated_files'] = len(scan_results['backdated_files'])
    
    # Count total files
    if 'file_count' in scan_results:
        summary['total_files_scanned'] = scan_results['file_count']
    
    return summary


def _flatten_for_csv(data: Dict, parent_key: str = '', sep: str = '_') -> List[Dict]:
    """
    Flatten nested dictionary structure for CSV export.
    """
    def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        items = []
        for key, value in d.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(_flatten_dict(value, new_key, sep).items())
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Handle list of dictionaries
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.extend(_flatten_dict(item, f"{new_key}_{i}", sep).items())
                    else:
                        items.append((f"{new_key}_{i}", item))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    # If data contains lists of items (like anomalies), create separate rows
    if isinstance(data, dict):
        if 'anomalies' in data and isinstance(data['anomalies'], list):
            # Create one row per anomaly
            flattened_rows = []
            for anomaly in data['anomalies']:
                row = _flatten_dict(anomaly)
                # Add summary information to each row
                if 'summary' in data:
                    for key, value in data['summary'].items():
                        row[f"summary_{key}"] = value
                flattened_rows.append(row)
            return flattened_rows
        else:
            return [_flatten_dict(data)]
    elif isinstance(data, list):
        return [_flatten_dict(item) if isinstance(item, dict) else {'value': item} for item in data]
    else:
        return [{'value': data}]


def create_timeline_report(timeline_data: Dict, 
                         output_path: Union[str, Path],
                         format_type: str = 'json') -> None:
    """
    Create a specialized timeline report.
    
    Args:
        timeline_data: Timeline data from TimelineBuilder
        output_path: Output file path
        format_type: 'json' or 'csv'
    """
    report = {
        'report_type': 'timeline_analysis',
        'generated_at': datetime.now().isoformat(),
        'timeline_data': timeline_data
    }
    
    if format_type.lower() == 'json':
        export_to_json(report, output_path)
    elif format_type.lower() == 'csv':
        # For timeline CSV, focus on chronological activities
        if 'chronological_timeline' in timeline_data:
            export_to_csv(timeline_data['chronological_timeline'], output_path)
        else:
            raise ValueError("No chronological timeline data found for CSV export")
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def create_summary_report(analysis_results: List[Dict], 
                        output_path: Union[str, Path]) -> None:
    """
    Create a high-level summary report from multiple analysis results.
    
    Args:
        analysis_results: List of analysis result dictionaries
        output_path: Output file path for summary report
    """
    summary_stats = {
        'total_analyses': len(analysis_results),
        'total_files_analyzed': 0,
        'total_anomalies': 0,
        'severity_breakdown': {'high': 0, 'medium': 0, 'low': 0},
        'common_patterns': [],
        'generated_at': datetime.now().isoformat()
    }
    
    # Aggregate statistics
    pattern_counts = {}
    
    for result in analysis_results:
        if 'file_count' in result:
            summary_stats['total_files_analyzed'] += result['file_count']
        
        if 'anomalies' in result:
            summary_stats['total_anomalies'] += len(result['anomalies'])
            
            for anomaly in result['anomalies']:
                severity = anomaly.get('severity', 'unknown')
                if severity in summary_stats['severity_breakdown']:
                    summary_stats['severity_breakdown'][severity] += 1
                
                # Track common patterns
                reason = anomaly.get('reason', 'unknown')
                pattern_counts[reason] = pattern_counts.get(reason, 0) + 1
    
    # Identify most common patterns
    summary_stats['common_patterns'] = sorted(
        pattern_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]  # Top 10 most common patterns
    
    export_to_json(summary_stats, output_path)