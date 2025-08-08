#!/usr/bin/env python3
"""
TimeSleuth Forensics Investigation Example

This script demonstrates how to use TimeSleuth for a comprehensive
digital forensics investigation workflow.
"""

import timesleuth as ts
from pathlib import Path
from datetime import datetime, timedelta
import json


def investigate_directory(evidence_path, output_dir="investigation_output"):
    """
    Perform a comprehensive forensics investigation on a directory.
    
    Args:
        evidence_path: Path to directory under investigation
        output_dir: Directory to store investigation results
    """
    print(f"=== Starting Forensic Investigation of {evidence_path} ===")
    
    evidence_dir = Path(evidence_path)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    investigation_results = {
        'investigation_started': datetime.now().isoformat(),
        'evidence_directory': str(evidence_dir),
        'phases': {}
    }
    
    # Phase 1: Initial Directory Scan
    print("Phase 1: Initial anomaly detection...")
    anomalies = ts.scan_directory(evidence_path, recursive=True, include_hidden=True)
    investigation_results['phases']['anomaly_detection'] = {
        'anomalies_found': len(anomalies),
        'high_severity': len([a for a in anomalies if a.get('severity') == 'high']),
        'medium_severity': len([a for a in anomalies if a.get('severity') == 'medium']),
        'low_severity': len([a for a in anomalies if a.get('severity') == 'low'])
    }
    
    print(f"  Found {len(anomalies)} anomalies ({investigation_results['phases']['anomaly_detection']['high_severity']} high severity)")
    
    # Save anomalies report
    ts.export_to_json(anomalies, output_path / "anomalies_detailed.json")
    
    # Phase 2: Timeline Reconstruction
    print("Phase 2: Timeline reconstruction...")
    timeline_data = ts.reconstruct_activity(evidence_path, analysis_type='comprehensive')
    investigation_results['phases']['timeline_reconstruction'] = {
        'total_files': timeline_data['file_count'],
        'activities_recorded': len(timeline_data.get('chronological_timeline', [])),
        'activity_groups': len(timeline_data.get('activity_groups', {}).get('groups', []))
    }
    
    print(f"  Reconstructed timeline with {timeline_data['file_count']} files")
    
    # Save timeline reports
    ts.create_timeline_report(timeline_data, output_path / "timeline_analysis.json", "json")
    
    # Phase 3: Backdated File Detection
    print("Phase 3: Backdated file detection...")
    backdated_files = ts.find_backdated_files(evidence_path, threshold_days=90)
    investigation_results['phases']['backdating_analysis'] = {
        'backdated_files_found': len(backdated_files),
        'oldest_file_age_days': max([f['age_days'] for f in backdated_files], default=0)
    }
    
    print(f"  Found {len(backdated_files)} potentially backdated files")
    
    # Save backdated files report
    if backdated_files:
        ts.export_to_json(backdated_files, output_path / "backdated_files.json")
    
    # Phase 4: Pattern Analysis
    print("Phase 4: Advanced pattern analysis...")
    all_files = [f for f in evidence_dir.rglob("*") if f.is_file()]
    pattern_analysis = ts.analyze_timestamp_patterns(all_files)
    investigation_results['phases']['pattern_analysis'] = {
        'batch_operations_detected': len(pattern_analysis['batch_operations']),
        'time_clusters_detected': len(pattern_analysis['time_clusters']),
        'suspicious_patterns': len(pattern_analysis['suspicious_patterns'])
    }
    
    print(f"  Detected {len(pattern_analysis['batch_operations'])} batch operations")
    print(f"  Found {len(pattern_analysis['suspicious_patterns'])} suspicious patterns")
    
    # Save pattern analysis
    ts.export_to_json(pattern_analysis, output_path / "pattern_analysis.json")
    
    # Phase 5: Generate Summary Report
    print("Phase 5: Generating investigation summary...")
    
    # Compile all findings
    complete_findings = {
        'investigation_metadata': investigation_results,
        'anomalies': anomalies,
        'timeline_data': timeline_data,
        'backdated_files': backdated_files,
        'pattern_analysis': pattern_analysis
    }
    
    # Generate forensics report
    ts.generate_forensics_report(
        complete_findings,
        output_path / "forensic_investigation_report.json",
        report_format='json',
        include_metadata=True
    )
    
    # Generate CSV summary for easy review
    if anomalies:
        ts.generate_forensics_report(
            {'anomalies': anomalies, 'file_count': len(all_files)},
            output_path / "anomalies_summary.csv",
            report_format='csv'
        )
    
    investigation_results['investigation_completed'] = datetime.now().isoformat()
    
    # Print summary
    print("\n=== Investigation Summary ===")
    print(f"Evidence Directory: {evidence_path}")
    print(f"Files Analyzed: {len(all_files)}")
    print(f"Total Anomalies: {len(anomalies)}")
    print(f"High Severity Issues: {investigation_results['phases']['anomaly_detection']['high_severity']}")
    print(f"Backdated Files: {len(backdated_files)}")
    print(f"Batch Operations: {len(pattern_analysis['batch_operations'])}")
    print(f"Reports Generated in: {output_path}")
    
    return investigation_results


def investigate_incident_timeframe(evidence_path, incident_start, incident_end, output_dir="incident_analysis"):
    """
    Investigate file activity within a specific incident timeframe.
    
    Args:
        evidence_path: Path to evidence directory
        incident_start: Start datetime of incident window (ISO format string)
        incident_end: End datetime of incident window (ISO format string)
        output_dir: Output directory for results
    """
    print(f"=== Incident Timeframe Analysis ===")
    print(f"Investigating activity between {incident_start} and {incident_end}")
    
    from datetime import datetime
    
    start_dt = datetime.fromisoformat(incident_start.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(incident_end.replace('Z', '+00:00'))
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get timeline data
    timeline_data = ts.create_timeline(evidence_path, output_format='list', sort_by='modified')
    
    # Filter activities within incident timeframe
    incident_activities = []
    for activity in timeline_data:
        activity_time = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
        if start_dt <= activity_time <= end_dt:
            incident_activities.append(activity)
    
    print(f"Found {len(incident_activities)} file activities during incident timeframe")
    
    # Analyze incident activities
    incident_analysis = {
        'incident_timeframe': {
            'start': incident_start,
            'end': incident_end,
            'duration_hours': (end_dt - start_dt).total_seconds() / 3600
        },
        'activities_in_timeframe': len(incident_activities),
        'files_affected': len(set(a['file_path'] for a in incident_activities)),
        'activity_timeline': incident_activities
    }
    
    # Generate incident report
    ts.export_to_json(incident_analysis, output_path / "incident_timeframe_analysis.json")
    
    if incident_activities:
        ts.export_to_csv(incident_activities, output_path / "incident_activities.csv")
    
    print(f"Incident analysis complete. Results in {output_path}")
    return incident_analysis


def compare_evidence_directories(dir1, dir2, output_dir="comparison_analysis"):
    """
    Compare timestamp patterns between two evidence directories.
    
    Args:
        dir1: First evidence directory
        dir2: Second evidence directory  
        output_dir: Output directory for comparison results
    """
    print(f"=== Evidence Directory Comparison ===")
    print(f"Comparing {dir1} vs {dir2}")
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Analyze both directories
    analysis1 = {
        'directory': str(dir1),
        'anomalies': ts.scan_directory(dir1, recursive=True),
        'backdated_files': ts.find_backdated_files(dir1)
    }
    
    analysis2 = {
        'directory': str(dir2),
        'anomalies': ts.scan_directory(dir2, recursive=True),
        'backdated_files': ts.find_backdated_files(dir2)
    }
    
    # Create comparison report
    comparison = {
        'comparison_metadata': {
            'directory_1': str(dir1),
            'directory_2': str(dir2),
            'analysis_date': datetime.now().isoformat()
        },
        'directory_1_analysis': analysis1,
        'directory_2_analysis': analysis2,
        'comparison_summary': {
            'anomalies_dir1': len(analysis1['anomalies']),
            'anomalies_dir2': len(analysis2['anomalies']),
            'backdated_files_dir1': len(analysis1['backdated_files']),
            'backdated_files_dir2': len(analysis2['backdated_files'])
        }
    }
    
    ts.export_to_json(comparison, output_path / "evidence_comparison.json")
    
    print(f"Directory 1 ({dir1}): {len(analysis1['anomalies'])} anomalies, {len(analysis1['backdated_files'])} backdated files")
    print(f"Directory 2 ({dir2}): {len(analysis2['anomalies'])} anomalies, {len(analysis2['backdated_files'])} backdated files")
    print(f"Comparison report saved to {output_path}")
    
    return comparison


def main():
    """
    Demonstrate forensic investigation workflows.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python forensics_investigation.py <evidence_directory>")
        print("Optional: Add 'incident' for incident timeframe analysis")
        print("Optional: Add 'compare <dir2>' for directory comparison")
        return
    
    evidence_path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == 'incident':
        # Example incident timeframe analysis
        # In real use, these would be provided based on incident details
        incident_start = "2024-01-15T09:00:00Z"
        incident_end = "2024-01-15T17:00:00Z"
        investigate_incident_timeframe(evidence_path, incident_start, incident_end)
    
    elif len(sys.argv) > 3 and sys.argv[2] == 'compare':
        compare_evidence_directories(evidence_path, sys.argv[3])
    
    else:
        # Standard comprehensive investigation
        investigate_directory(evidence_path)


if __name__ == "__main__":
    main()