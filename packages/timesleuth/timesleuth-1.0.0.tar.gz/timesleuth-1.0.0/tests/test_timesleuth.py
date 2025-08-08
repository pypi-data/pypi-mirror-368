#!/usr/bin/env python3
"""
Basic tests for TimeSleuth functionality

These tests verify core functionality works correctly.
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Import TimeSleuth modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import timesleuth as ts
from timesleuth.utils import get_file_timestamps, is_valid_timestamp_range


class TestTimeSleuthCore(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary files."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Create some test files
        for i in range(3):
            test_file = Path(self.test_dir) / f"test_file_{i}.txt"
            test_file.write_text(f"Test content {i}")
            self.test_files.append(test_file)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_file_timestamps(self):
        """Test basic timestamp extraction."""
        test_file = self.test_files[0]
        
        timestamps = get_file_timestamps(test_file)
        
        # Should have at least modified and accessed timestamps
        self.assertIn('modified', timestamps)
        self.assertIn('accessed', timestamps)
        
        # Timestamps should be datetime objects
        self.assertIsInstance(timestamps['modified'], datetime)
        self.assertIsInstance(timestamps['accessed'], datetime)
        
        # Timestamps should be recent (within last hour)
        now = datetime.now(timezone.utc)
        time_diff = now - timestamps['modified']
        self.assertLess(time_diff.total_seconds(), 3600)  # Within 1 hour
    
    def test_scan_directory_basic(self):
        """Test basic directory scanning."""
        anomalies = ts.scan_directory(self.test_dir, recursive=False)
        
        # Should return a list
        self.assertIsInstance(anomalies, list)
        
        # Each anomaly should be a dictionary with required fields
        for anomaly in anomalies:
            self.assertIsInstance(anomaly, dict)
            self.assertIn('path', anomaly)
            self.assertIn('reason', anomaly)
            self.assertIn('severity', anomaly)
            self.assertIn('timestamps', anomaly)
    
    def test_create_timeline(self):
        """Test timeline creation."""
        timeline = ts.create_timeline(self.test_dir, output_format='list')
        
        # Should return a list
        self.assertIsInstance(timeline, list)
        
        # Should have entries for our test files
        self.assertGreater(len(timeline), 0)
        
        # Each timeline entry should have required fields
        for entry in timeline:
            self.assertIsInstance(entry, dict)
            self.assertIn('timestamp', entry)
            self.assertIn('file_path', entry)
            self.assertIn('type', entry)
    
    def test_find_backdated_files(self):
        """Test backdated file detection."""
        backdated = ts.find_backdated_files(self.test_dir, threshold_days=1)
        
        # Should return a list
        self.assertIsInstance(backdated, list)
        
        # For newly created files, shouldn't find any backdated files
        # (unless there's an anomaly)
        # Just verify the structure is correct
        for file_info in backdated:
            self.assertIsInstance(file_info, dict)
            if file_info:  # If any backdated files found
                self.assertIn('path', file_info)
                self.assertIn('reasons', file_info)
                self.assertIn('timestamps', file_info)
                self.assertIn('age_days', file_info)
    
    def test_timestamp_validation(self):
        """Test timestamp validation logic."""
        now = datetime.now(timezone.utc)
        
        # Valid timestamp set
        valid_timestamps = {
            'created': now - timedelta(hours=2),
            'modified': now - timedelta(hours=1),
            'accessed': now
        }
        self.assertTrue(is_valid_timestamp_range(valid_timestamps))
        
        # Invalid timestamp set (creation after modification)
        invalid_timestamps = {
            'created': now,
            'modified': now - timedelta(hours=1),
            'accessed': now
        }
        self.assertFalse(is_valid_timestamp_range(invalid_timestamps))


class TestTimeSleuthUtils(unittest.TestCase):
    
    def test_format_timestamp(self):
        """Test timestamp formatting utility."""
        from timesleuth.utils import format_timestamp
        
        test_dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        formatted = format_timestamp(test_dt)
        
        self.assertIsInstance(formatted, str)
        self.assertIn('2024-01-15', formatted)
        self.assertIn('10:30:45', formatted)
        
        # Test None handling
        none_formatted = format_timestamp(None)
        self.assertEqual(none_formatted, "N/A")
    
    def test_timestamp_entropy(self):
        """Test timestamp entropy calculation."""
        from timesleuth.utils import calculate_timestamp_entropy
        
        # Create timestamps with low entropy (clustered)
        base_time = datetime.now(timezone.utc)
        clustered_timestamps = [base_time] * 5  # All same timestamp
        
        entropy = calculate_timestamp_entropy(clustered_timestamps)
        self.assertEqual(entropy, 0.0)  # Perfect clustering
        
        # Create timestamps with high entropy (spread out)
        spread_timestamps = [
            base_time + timedelta(seconds=i * 3600) 
            for i in range(10)
        ]
        
        entropy = calculate_timestamp_entropy(spread_timestamps)
        self.assertGreater(entropy, 2.0)  # Should be higher entropy


class TestTimeSleuthReporting(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_json_export(self):
        """Test JSON export functionality."""
        test_data = {
            'test_field': 'test_value',
            'timestamp': datetime.now(timezone.utc),
            'number': 42
        }
        
        output_file = Path(self.test_dir) / "test_export.json"
        ts.export_to_json(test_data, output_file)
        
        # Verify file was created
        self.assertTrue(output_file.exists())
        
        # Verify content is valid JSON
        import json
        with open(output_file, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['test_field'], 'test_value')
        self.assertEqual(loaded_data['number'], 42)
        # Timestamp should be converted to ISO format
        self.assertIsInstance(loaded_data['timestamp'], str)
    
    def test_csv_export(self):
        """Test CSV export functionality."""
        test_data = [
            {'file': 'test1.txt', 'size': 100, 'timestamp': datetime.now(timezone.utc)},
            {'file': 'test2.txt', 'size': 200, 'timestamp': datetime.now(timezone.utc)}
        ]
        
        output_file = Path(self.test_dir) / "test_export.csv"
        ts.export_to_csv(test_data, output_file)
        
        # Verify file was created
        self.assertTrue(output_file.exists())
        
        # Verify CSV structure
        import csv
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertIn('file', rows[0])
        self.assertIn('size', rows[0])
        self.assertIn('timestamp', rows[0])


def run_basic_functionality_test():
    """
    Quick functional test to verify TimeSleuth works end-to-end.
    """
    print("Running basic functionality test...")
    
    try:
        # Test on current directory (should be safe)
        current_dir = "."
        
        # Test 1: Basic scan
        print("  Testing directory scan...")
        anomalies = ts.scan_directory(current_dir, recursive=False)
        print(f"    Found {len(anomalies)} potential anomalies")
        
        # Test 2: Timeline creation
        print("  Testing timeline creation...")
        timeline = ts.create_timeline(current_dir, output_format='list')
        print(f"    Created timeline with {len(timeline)} entries")
        
        # Test 3: Pattern analysis
        print("  Testing pattern analysis...")
        files = [f for f in Path(current_dir).glob("*") if f.is_file()][:5]  # Limit to 5 files
        if files:
            patterns = ts.analyze_timestamp_patterns(files)
            print(f"    Analyzed {patterns['total_files']} files")
        
        print("✅ Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


if __name__ == "__main__":
    # Run basic functionality test first
    if run_basic_functionality_test():
        print("\nRunning unit tests...")
        unittest.main(verbosity=2)
    else:
        print("Basic functionality test failed - skipping unit tests")
        sys.exit(1)