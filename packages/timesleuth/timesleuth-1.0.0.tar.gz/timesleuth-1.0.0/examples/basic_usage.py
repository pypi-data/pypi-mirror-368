#!/usr/bin/env python3
"""
TimeSleuth Basic Usage Examples

This script demonstrates the core functionality of the TimeSleuth library
for digital forensics timestamp analysis.
"""

import timesleuth as ts
from pathlib import Path
import json


def demo_directory_scan():
    """
    Demonstrate basic directory scanning for timestamp anomalies.
    """
    print("=== Directory Scan Demo ===")
    
    # Scan current directory for anomalies
    try:
        anomalies = ts.scan_directory(".", recursive=True)
        
        print(f"Found {len(anomalies)} potential anomalies:")
        
        for anomaly in anomalies[:5]:  # Show first 5 anomalies
            print(f"  • {anomaly['path']}")
            print(f"    Reason: {anomaly['reason']}")
            print(f"    Severity: {anomaly['severity']}")
            print()
            
    except Exception as e:
        print(f"Error during scan: {e}")


def demo_timeline_creation():
    """
    Demonstrate timeline reconstruction functionality.
    """
    print("=== Timeline Creation Demo ===")
    
    try:
        # Create chronological timeline
        timeline = ts.create_timeline(".", output_format='list', sort_by='modified')
        
        print(f"Timeline contains {len(timeline)} file activities")
        print("Recent activities:")
        
        # Show last 5 activities
        for activity in timeline[-5:]:
            print(f"  • {activity['timestamp']}: {activity['file_path']}")
            print(f"    Type: {activity['type']}, Size: {activity.get('file_size', 'Unknown')} bytes")
        
        # Create activity groups
        grouped = ts.create_timeline(".", output_format='grouped')
        print(f"\nActivity grouped into {len(grouped['groups'])} time windows")
        
        if grouped['groups']:
            peak_activity = max(grouped['groups'], key=lambda x: x['activity_count'])
            print(f"Peak activity: {peak_activity['activity_count']} files at {peak_activity['start_time']}")
        
    except Exception as e:
        print(f"Error creating timeline: {e}")


def demo_backdated_detection():
    """
    Demonstrate detection of backdated files.
    """
    print("=== Backdated Files Demo ===")
    
    try:
        # Find potentially backdated files
        backdated = ts.find_backdated_files(".", threshold_days=30)
        
        print(f"Found {len(backdated)} potentially backdated files:")
        
        for file_info in backdated[:3]:  # Show first 3
            print(f"  • {file_info['path']}")
            print(f"    Age: {file_info['age_days']} days")
            print(f"    Reasons: {', '.join(file_info['reasons'])}")
            print()
            
    except Exception as e:
        print(f"Error detecting backdated files: {e}")


def demo_advanced_analysis():
    """
    Demonstrate advanced pattern analysis.
    """
    print("=== Advanced Pattern Analysis Demo ===")
    
    try:
        # Get list of files in current directory
        files = [f for f in Path(".").glob("**/*") if f.is_file()][:20]  # Limit for demo
        
        # Analyze timestamp patterns
        patterns = ts.analyze_timestamp_patterns(files)
        
        print(f"Analyzed {patterns['total_files']} files")
        
        if patterns['batch_operations']:
            print(f"Found {len(patterns['batch_operations'])} potential batch operations")
            for batch in patterns['batch_operations'][:2]:
                print(f"  • {batch['file_count']} files modified in {batch['duration_seconds']:.1f} seconds")
        
        if patterns['time_clusters']:
            print(f"Found {len(patterns['time_clusters'])} suspicious time clusters")
            for cluster in patterns['time_clusters']:
                print(f"  • {cluster['timestamp_type']} timestamps with entropy {cluster['entropy']:.2f}")
        
    except Exception as e:
        print(f"Error in advanced analysis: {e}")


def demo_reporting():
    """
    Demonstrate report generation functionality.
    """
    print("=== Reporting Demo ===")
    
    try:
        # Perform a scan
        results = {
            'scan_directory': '.',
            'anomalies': ts.scan_directory(".", recursive=False),
            'file_count': len([f for f in Path(".").iterdir() if f.is_file()])
        }
        
        # Generate JSON report
        ts.generate_forensics_report(
            results, 
            'timesleuth_report.json', 
            report_format='json'
        )
        print("Generated JSON report: timesleuth_report.json")
        
        # Generate CSV report (if anomalies exist)
        if results['anomalies']:
            ts.generate_forensics_report(
                results, 
                'timesleuth_report.csv', 
                report_format='csv'
            )
            print("Generated CSV report: timesleuth_report.csv")
        
    except Exception as e:
        print(f"Error generating reports: {e}")


def main():
    """
    Run all demonstration functions.
    """
    print("TimeSleuth Digital Forensics Timestamp Analysis")
    print("=" * 50)
    
    demo_directory_scan()
    print()
    
    demo_timeline_creation()
    print()
    
    demo_backdated_detection()
    print()
    
    demo_advanced_analysis()
    print()
    
    demo_reporting()
    print()
    
    print("Demo completed! Check generated report files.")


if __name__ == "__main__":
    main()