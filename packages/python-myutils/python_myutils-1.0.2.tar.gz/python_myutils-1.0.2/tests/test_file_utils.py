"""Tests for file_utils module."""

import pytest
import json
import csv
import tempfile
import os
from pathlib import Path
from myutils.file_utils import (
    read_json, write_json, read_csv_as_dicts, ensure_dir_exists,
    get_file_extension, file_exists, get_file_size
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "settings": {
            "theme": "dark",
            "notifications": True
        },
        "tags": ["admin", "user"]
    }


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return [
        {"name": "John", "age": "30", "city": "New York"},
        {"name": "Jane", "age": "25", "city": "San Francisco"},
        {"name": "Bob", "age": "35", "city": "Chicago"}
    ]


class TestJSONOperations:
    """Test JSON file operations."""
    
    def test_write_and_read_json(self, temp_dir, sample_json_data):
        """Test writing and reading JSON files."""
        json_path = os.path.join(temp_dir, "test.json")
        
        # Write JSON
        write_json(sample_json_data, json_path)
        
        # Verify file exists
        assert os.path.exists(json_path)
        
        # Read JSON
        read_data = read_json(json_path)
        
        # Verify data integrity
        assert read_data == sample_json_data
        assert read_data["name"] == "Test User"
        assert read_data["settings"]["theme"] == "dark"
        assert len(read_data["tags"]) == 2
    
    def test_write_json_with_indent(self, temp_dir, sample_json_data):
        """Test writing JSON with custom indentation."""
        json_path = os.path.join(temp_dir, "indented.json")
        
        write_json(sample_json_data, json_path, indent=4)
        
        # Read raw content to check formatting
        with open(json_path, 'r') as f:
            content = f.read()
        
        # Should have proper indentation
        assert "    " in content  # 4 spaces
        assert "{\n    " in content
    
    def test_read_nonexistent_json(self):
        """Test reading non-existent JSON file raises exception."""
        with pytest.raises(FileNotFoundError):
            read_json("nonexistent.json")
    
    def test_read_invalid_json(self, temp_dir):
        """Test reading invalid JSON raises exception."""
        invalid_json_path = os.path.join(temp_dir, "invalid.json")
        
        # Create invalid JSON file
        with open(invalid_json_path, 'w') as f:
            f.write("{ invalid json content }")
        
        with pytest.raises(json.JSONDecodeError):
            read_json(invalid_json_path)


class TestCSVOperations:
    """Test CSV file operations."""
    
    def test_read_csv_as_dicts(self, temp_dir, sample_csv_data):
        """Test reading CSV file as list of dictionaries."""
        csv_path = os.path.join(temp_dir, "test.csv")
        
        # Create CSV file
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['name', 'age', 'city']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_csv_data)
        
        # Read CSV
        result = read_csv_as_dicts(csv_path)
        
        # Verify data
        assert len(result) == 3
        assert result[0]['name'] == 'John'
        assert result[1]['age'] == '25'
        assert result[2]['city'] == 'Chicago'
    
    def test_read_empty_csv(self, temp_dir):
        """Test reading empty CSV file."""
        csv_path = os.path.join(temp_dir, "empty.csv")
        
        # Create empty CSV with just headers
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
        
        result = read_csv_as_dicts(csv_path)
        assert result == []
    
    def test_read_nonexistent_csv(self):
        """Test reading non-existent CSV file raises exception."""
        with pytest.raises(FileNotFoundError):
            read_csv_as_dicts("nonexistent.csv")


class TestDirectoryOperations:
    """Test directory operations."""
    
    def test_ensure_dir_exists_new_directory(self, temp_dir):
        """Test creating new directory."""
        new_dir = os.path.join(temp_dir, "new_directory")
        
        # Directory shouldn't exist initially
        assert not os.path.exists(new_dir)
        
        # Create directory
        ensure_dir_exists(new_dir)
        
        # Directory should now exist
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_ensure_dir_exists_nested_directories(self, temp_dir):
        """Test creating nested directories."""
        nested_dir = os.path.join(temp_dir, "level1", "level2", "level3")
        
        # Create nested directories
        ensure_dir_exists(nested_dir)
        
        # All levels should exist
        assert os.path.exists(nested_dir)
        assert os.path.isdir(nested_dir)
    
    def test_ensure_dir_exists_existing_directory(self, temp_dir):
        """Test calling ensure_dir_exists on existing directory."""
        # temp_dir already exists
        
        # Should not raise exception
        ensure_dir_exists(temp_dir)
        
        # Directory should still exist
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)


class TestFileUtilities:
    """Test file utility functions."""
    
    def test_get_file_extension(self):
        """Test getting file extensions."""
        assert get_file_extension("document.txt") == "txt"
        assert get_file_extension("archive.tar.gz") == "gz"
        assert get_file_extension("image.jpeg") == "jpeg"
        assert get_file_extension("no_extension") == ""
        assert get_file_extension(".hidden") == ""
        assert get_file_extension("path/to/file.pdf") == "pdf"
    
    def test_file_exists(self, temp_dir):
        """Test checking file existence."""
        # Create a test file
        test_file = os.path.join(temp_dir, "exists.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Test existing file
        assert file_exists(test_file) is True
        
        # Test non-existent file
        non_existent = os.path.join(temp_dir, "not_exists.txt")
        assert file_exists(non_existent) is False
    
    def test_get_file_size(self, temp_dir):
        """Test getting file size."""
        test_file = os.path.join(temp_dir, "size_test.txt")
        test_content = "Hello, World! This is a test file."
        
        # Create file with known content
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Get size
        size = get_file_size(test_file)
        
        # Verify size matches content length
        assert size == len(test_content.encode('utf-8'))
        assert size > 0
    
    def test_get_file_size_nonexistent(self):
        """Test getting size of non-existent file raises exception."""
        with pytest.raises(FileNotFoundError):
            get_file_size("nonexistent_file.txt")


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple operations."""
    
    def test_complete_workflow(self, temp_dir, sample_json_data):
        """Test complete file workflow."""
        # Setup paths
        data_dir = os.path.join(temp_dir, "data")
        json_file = os.path.join(data_dir, "config.json")
        
        # Create directory structure
        ensure_dir_exists(data_dir)
        
        # Write JSON data
        write_json(sample_json_data, json_file)
        
        # Verify file properties
        assert file_exists(json_file)
        assert get_file_extension(json_file) == "json"
        assert get_file_size(json_file) > 0
        
        # Read and verify data
        loaded_data = read_json(json_file)
        assert loaded_data == sample_json_data
    
    def test_data_processing_pipeline(self, temp_dir):
        """Test data processing pipeline."""
        # Create input data
        input_data = [
            {"id": 1, "name": "Alice", "score": 95},
            {"id": 2, "name": "Bob", "score": 87},
            {"id": 3, "name": "Charlie", "score": 92}
        ]
        
        # Setup directories
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        ensure_dir_exists(input_dir)
        ensure_dir_exists(output_dir)
        
        # Write input as JSON
        input_file = os.path.join(input_dir, "students.json")
        write_json(input_data, input_file)
        
        # Process: read JSON, filter high scores, write CSV
        data = read_json(input_file)
        high_scorers = [student for student in data if student["score"] >= 90]
        
        # Write processed data as CSV
        csv_file = os.path.join(output_dir, "high_scorers.csv")
        with open(csv_file, 'w', newline='') as f:
            if high_scorers:
                fieldnames = high_scorers[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(high_scorers)
        
        # Verify results
        result = read_csv_as_dicts(csv_file)
        assert len(result) == 2  # Alice and Charlie
        assert result[0]['name'] == 'Alice'
        assert result[1]['name'] == 'Charlie'