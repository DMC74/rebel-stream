import pytest
from typing import List, Dict, Any
import os
import json
from pathlib import Path

def create_test_file(directory: Path, filename: str, content: str) -> Path:
    """Create a test file with given content."""
    file_path = directory / filename
    file_path.write_text(content)
    return file_path

def read_json_file(file_path: Path) -> Dict[str, Any]:
    """Read and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def count_files_in_dir(directory: Path, pattern: str = "*") -> int:
    """Count files in directory matching pattern."""
    return len(list(directory.glob(pattern)))

def cleanup_test_files(directory: Path, pattern: str = "*") -> None:
    """Remove test files from directory."""
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            file_path.unlink()

class TestUtils:
    def test_create_test_file(self, test_dir):
        test_path = Path(test_dir)
        file_path = create_test_file(test_path, "test.txt", "test content")
        assert file_path.exists()
        assert file_path.read_text() == "test content"