# TimeSleuth

**Uncover digital footprints through timestamp forensics**

TimeSleuth is a lightweight Python library for digital forensics investigators, security researchers, and system administrators who need to analyze file timestamp patterns to detect suspicious activity, reconstruct incident timelines, and identify evidence tampering.

## Core Purpose

Detect timestamp anomalies that indicate:
- System compromise and malware activity
- Evidence tampering and anti-forensics attempts  
- Unauthorized file access patterns
- Data exfiltration events
- Timeline reconstruction for incident response

## Key Features

TimeSleuth provides comprehensive timestamp analysis through five main capabilities:

**Anomaly Detection** - Identify impossible timestamp combinations and suspicious patterns
**Timeline Reconstruction** - Build chronological activity maps from file metadata
**Backdating Detection** - Find files with artificially altered timestamps
**Batch Activity Analysis** - Detect automated/scripted file operations
**Comprehensive Reporting** - Generate forensics-ready reports in JSON/CSV formats

## Installation and Basic Usage

Install TimeSleuth using pip:

```bash
pip install timesleuth
```

## Complete Usage Guide

### 1. Directory Scanning for Anomalies

The primary function for detecting timestamp anomalies across files in a directory:

```python
import timesleuth as ts

# Basic directory scan
anomalies = ts.scan_directory("/evidence/")

# Advanced scanning options
anomalies = ts.scan_directory(
    directory_path="/evidence/",
    recursive=True,              # Include subdirectories
    include_hidden=True,         # Include hidden files
    file_extensions=['.log', '.txt', '.exe']  # Filter by extensions
)

# Process results
for anomaly in anomalies:
    print(f"File: {anomaly['path']}")
    print(f"Issue: {anomaly['reason']}")
    print(f"Severity: {anomaly['severity']}")
    print(f"Details: {anomaly['details']}")
    print("---")
```

### 2. Timeline Creation and Reconstruction  

Build chronological timelines from file timestamp data:

```python
# Create basic chronological timeline
timeline = ts.create_timeline("/evidence/", output_format='list', sort_by='modified')

# Alternative timeline formats
access_timeline = ts.create_timeline("/evidence/", sort_by='accessed')
grouped_timeline = ts.create_timeline("/evidence/", output_format='grouped')

# Comprehensive activity reconstruction
activity_data = ts.reconstruct_activity("/evidence/", analysis_type='comprehensive')

# Process timeline data
for activity in timeline:
    print(f"{activity['timestamp']}: {activity['file_path']}")
    print(f"  Type: {activity['type']}, Size: {activity['file_size']} bytes")

# Access activity groups for burst analysis
if 'activity_groups' in activity_data:
    for group in activity_data['activity_groups']['groups']:
        print(f"Activity burst: {group['activity_count']} files in {group['duration_seconds']} seconds")
```

### 3. Backdated File Detection

Identify files with potentially manipulated timestamps:

```python
# Find files backdated beyond threshold
backdated = ts.find_backdated_files(
    directory_path="/evidence/",
    threshold_days=30,           # Files older than 30 days are suspicious
    reference_time=None          # Use current time as reference
)

# Use specific reference time
backdated = ts.find_backdated_files(
    "/evidence/",
    reference_time="2024-01-15T10:00:00Z",
    threshold_days=7
)

# Process backdated files
for file_info in backdated:
    print(f"Backdated file: {file_info['path']}")
    print(f"Age: {file_info['age_days']} days")
    print(f"Suspicious reasons: {', '.join(file_info['reasons'])}")
    print(f"Timestamps: {file_info['timestamps']}")
```

### 4. Advanced Pattern Analysis

Detect sophisticated timestamp manipulation patterns:

```python
from pathlib import Path

# Get list of files for analysis
files = list(Path("/evidence/").rglob("*"))

# Analyze timestamp patterns
patterns = ts.analyze_timestamp_patterns(
    file_list=files,
    detect_batch_ops=True,       # Find batch operations
    detect_time_clustering=True  # Find artificial clustering
)

# Process batch operations
for batch in patterns['batch_operations']:
    print(f"Batch operation detected:")
    print(f"  Files: {batch['file_count']}")
    print(f"  Duration: {batch['duration_seconds']} seconds")
    print(f"  Time range: {batch['start_time']} to {batch['end_time']}")

# Process time clusters
for cluster in patterns['time_clusters']:
    print(f"Suspicious clustering in {cluster['timestamp_type']} timestamps")
    print(f"  Entropy: {cluster['entropy']:.2f} (lower = more suspicious)")
    print(f"  Severity: {cluster['severity']}")
```

### 5. Report Generation

Create comprehensive forensic reports in multiple formats:

```python
# Combine all analysis results
investigation_data = {
    'anomalies': ts.scan_directory("/evidence/", recursive=True),
    'timeline': ts.create_timeline("/evidence/"),
    'backdated_files': ts.find_backdated_files("/evidence/"),
    'file_count': len(list(Path("/evidence/").rglob("*")))
}

# Generate JSON report
ts.generate_forensics_report(
    scan_results=investigation_data,
    output_path="forensic_report.json",
    report_format='json',
    include_metadata=True
)

# Generate CSV report for spreadsheet analysis
ts.generate_forensics_report(
    investigation_data,
    "forensic_report.csv", 
    report_format='csv'
)

# Create specialized timeline report
timeline_data = ts.reconstruct_activity("/evidence/", analysis_type='comprehensive')
ts.create_timeline_report(timeline_data, "timeline_report.json", format_type='json')

# Export raw data in different formats
ts.export_to_json(investigation_data, "raw_data.json", pretty_print=True)
if investigation_data['anomalies']:
    ts.export_to_csv(investigation_data['anomalies'], "anomalies.csv")
```

### 6. Incident Investigation Workflow

Complete forensic investigation process:

```python
def investigate_incident(evidence_path, output_dir="investigation"):
    """Complete forensic timestamp investigation"""
    
    # Phase 1: Initial anomaly scan
    print("Phase 1: Scanning for anomalies...")
    anomalies = ts.scan_directory(evidence_path, recursive=True, include_hidden=True)
    
    # Phase 2: Timeline reconstruction
    print("Phase 2: Reconstructing timeline...")
    timeline = ts.reconstruct_activity(evidence_path, analysis_type='comprehensive')
    
    # Phase 3: Backdated file detection
    print("Phase 3: Finding backdated files...")
    backdated = ts.find_backdated_files(evidence_path, threshold_days=90)
    
    # Phase 4: Pattern analysis
    print("Phase 4: Analyzing patterns...")
    files = list(Path(evidence_path).rglob("*"))
    patterns = ts.analyze_timestamp_patterns(files)
    
    # Phase 5: Generate comprehensive report
    print("Phase 5: Generating reports...")
    complete_findings = {
        'anomalies': anomalies,
        'timeline': timeline,
        'backdated_files': backdated,
        'patterns': patterns,
        'file_count': len(files)
    }
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate reports
    ts.generate_forensics_report(complete_findings, f"{output_dir}/investigation_report.json")
    ts.create_timeline_report(timeline, f"{output_dir}/timeline.json")
    
    if anomalies:
        ts.export_to_csv(anomalies, f"{output_dir}/anomalies.csv")
    
    print(f"Investigation complete. Reports in {output_dir}/")
    return complete_findings

# Run investigation
results = investigate_incident("/path/to/evidence")
```

## Detection Capabilities

TimeSleuth detects various types of timestamp anomalies and suspicious patterns:

**Timestamp Anomalies**
- Future timestamps that exceed current system time
- Pre-1980 timestamps indicating file corruption or manipulation
- Identical timestamp sets across multiple files (mass tampering)
- Creation time occurring after modification time (impossible sequence)
- Round timestamp values ending in :00 seconds (manual tampering indicator)
- Access time occurring before modification time

**Activity Patterns**  
- Batch file operations indicating automated scripts or malware activity
- Time clustering showing artificial grouping of file operations
- Off-hours activity bursts suggesting unauthorized access
- High-intensity activity periods with unusual file operation rates
- Suspicious file type patterns in timestamp modifications

**Evidence Tampering Detection**
- Files with suspiciously old timestamps relative to content
- Timestamp relationship violations between different timestamp types
- Low entropy timestamp distributions indicating artificial patterns
- Files sharing identical timestamp signatures across multiple attributes

## API Reference

### Primary Functions

**scan_directory(directory_path, recursive=True, include_hidden=False, file_extensions=None)**

Scan directory for timestamp anomalies.

Parameters:
- `directory_path` (str): Path to directory to scan
- `recursive` (bool): Include subdirectories in scan
- `include_hidden` (bool): Include hidden files in analysis  
- `file_extensions` (list): Filter files by extensions (e.g., ['.log', '.exe'])

Returns: List of anomaly dictionaries with path, reason, severity, timestamps, and details

**create_timeline(directory_path, output_format='list', sort_by='modified')**

Generate chronological timeline from file timestamps.

Parameters:
- `directory_path` (str): Directory to analyze
- `output_format` (str): Output format ('list' for chronological, 'grouped' for time windows)
- `sort_by` (str): Timestamp type for sorting ('modified', 'accessed', 'created', 'all')

Returns: Timeline data structure with chronologically ordered file activities

**find_backdated_files(directory_path, reference_time=None, threshold_days=30)**

Identify files with potentially backdated timestamps.

Parameters:
- `directory_path` (str): Directory to scan for backdated files
- `reference_time` (str): ISO format reference timestamp (default: current time)
- `threshold_days` (int): Age threshold in days for flagging files as suspicious

Returns: List of backdated file information with paths, ages, and suspicious reasons

### Advanced Functions

**analyze_timestamp_patterns(file_list, detect_batch_ops=True, detect_time_clustering=True)**

Analyze timestamp patterns across multiple files for sophisticated detection.

Parameters:
- `file_list` (list): List of file paths to analyze
- `detect_batch_ops` (bool): Enable batch operation detection
- `detect_time_clustering` (bool): Enable time clustering analysis

Returns: Dictionary with batch operations, time clusters, and suspicious patterns

**reconstruct_activity(directory_path, analysis_type='comprehensive')**

Reconstruct complete file system activity from timestamps.

Parameters:
- `directory_path` (str): Path to directory for activity reconstruction
- `analysis_type` (str): Analysis depth ('basic', 'comprehensive', 'suspicious_only')

Returns: Comprehensive activity analysis with timelines, patterns, and statistics

### Reporting Functions

**generate_forensics_report(scan_results, output_path, report_format='json', include_metadata=True)**

Generate comprehensive forensic investigation report.

**export_to_json(data, output_path, pretty_print=True)**

Export analysis data to JSON format with timestamp serialization.

**export_to_csv(data, output_path, fieldnames=None)**

Export analysis results to CSV format for spreadsheet analysis.

**create_timeline_report(timeline_data, output_path, format_type='json')**

Generate specialized timeline reports for temporal analysis.

### Utility Functions

**get_file_timestamps(file_path)**

Extract all available timestamps from a file (creation, modification, access times).

**format_timestamp(dt, format_str='%Y-%m-%d %H:%M:%S UTC')**

Format datetime objects for consistent display across reports.

## Technical Architecture

**Pure Python Implementation**
- No external dependencies beyond Python standard library
- Cross-platform compatibility (Linux, Windows, macOS)
- Optimized for large directory structures with incremental processing
- Memory efficient file handling for forensic investigations

**Performance Characteristics**
- Processes thousands of files efficiently using generator patterns
- Minimal memory footprint through streaming analysis
- Concurrent timestamp extraction where possible
- Structured data outputs for integration with forensic tools

**Standards Compliance**
- ISO 8601 timestamp formatting throughout
- Structured JSON output compatible with forensic analysis tools
- CSV exports compatible with spreadsheet applications
- UTF-8 encoding for international file path support

## Project Structure

The TimeSleuth library is organized into focused modules:

```
timesleuth/
├── __init__.py              # Main API exports and version info
├── core.py                  # Primary scanning and detection functions
├── anomaly_detection.py     # Anomaly detection algorithms and pattern analysis
├── timeline.py              # Timeline reconstruction and activity analysis
├── utils.py                 # Timestamp utilities and validation functions
├── reporting.py             # Report generation and data export functions
└── examples/
    ├── basic_usage.py           # Core functionality demonstration
    └── forensics_investigation.py # Complete investigation workflow
```

## Educational Applications

TimeSleuth serves as an excellent educational tool for:

**Digital Forensics Training**
- Understanding file system timestamp behavior
- Learning evidence tampering detection techniques
- Practicing timeline reconstruction methods
- Developing forensic analysis workflows

**Cybersecurity Education**
- Incident response skill development
- Malware analysis timestamp patterns
- Anti-forensics technique recognition
- Automated threat detection principles

**System Administration**
- File integrity monitoring concepts
- System activity analysis methods
- Security audit trail examination
- Compliance monitoring implementations

## Contributing

Contributions are welcome through GitHub pull requests. Areas for improvement include:
- Additional timestamp anomaly detection algorithms
- Performance optimizations for very large datasets
- New output format support (XML, database integration)
- Enhanced pattern recognition capabilities
- Expanded cross-platform timestamp handling

## License

MIT License - See LICENSE file for complete terms.

TimeSleuth provides professional-grade timestamp forensics capabilities in a simple, accessible Python library designed for forensic investigators, security researchers, and system administrators.