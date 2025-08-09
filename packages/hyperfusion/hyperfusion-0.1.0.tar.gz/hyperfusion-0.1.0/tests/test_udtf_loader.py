"""Tests for UDTF loader functionality."""

import os
import tempfile
import pytest
from pathlib import Path
from dataclasses import dataclass
from hyperfusion.service.udtf_loader import (
    parse_udtf_paths, 
    validate_python_file, 
    load_udtf_files,
    UDTFLoaderError,
    UDTFFileValidationError
)
from hyperfusion.udtf.registry import registry


@dataclass
class TestResult:
    value: int


class TestUDTFLoader:
    
    def test_parse_udtf_paths_empty_input(self):
        """Test parsing empty or None input."""
        assert parse_udtf_paths(None) == []
        assert parse_udtf_paths("") == []
        assert parse_udtf_paths([]) == []
    
    def test_parse_udtf_paths_string_input(self):
        """Test parsing colon-separated string input."""
        # Create temporary test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file1 = temp_path / "test1.py"
            file2 = temp_path / "test2.py"
            file1.write_text("# test file 1")
            file2.write_text("# test file 2")
            
            # Test colon-separated paths
            input_str = f"{file1}:{file2}"
            result = parse_udtf_paths(input_str)
            
            assert len(result) == 2
            assert file1.resolve() in result
            assert file2.resolve() in result
    
    def test_parse_udtf_paths_list_input(self):
        """Test parsing list input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file1 = temp_path / "test1.py"
            file1.write_text("# test file")
            
            result = parse_udtf_paths([str(file1)])
            assert len(result) == 1
            assert file1.resolve() in result
    
    def test_parse_udtf_paths_directory_input(self):
        """Test parsing directory input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create Python files
            file1 = temp_path / "test1.py"
            file2 = temp_path / "subdir" / "test2.py"
            file2.parent.mkdir()
            file1.write_text("# test file 1")
            file2.write_text("# test file 2")
            
            # Create non-Python file (should be ignored)
            non_py = temp_path / "test.txt"
            non_py.write_text("not python")
            
            result = parse_udtf_paths([str(temp_path)])
            
            assert len(result) == 2
            assert file1.resolve() in result
            assert file2.resolve() in result
    
    def test_parse_udtf_paths_nonexistent_path(self):
        """Test error handling for nonexistent paths."""
        with pytest.raises(UDTFLoaderError, match="does not exist"):
            parse_udtf_paths(["/nonexistent/path.py"])
    
    def test_validate_python_file_valid(self):
        """Test validation of valid Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    return 42\n")
            temp_file = Path(f.name)
        
        try:
            validate_python_file(temp_file)  # Should not raise
        finally:
            temp_file.unlink()
    
    def test_validate_python_file_syntax_error(self):
        """Test validation of file with syntax error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def invalid_syntax(\n    return 42\n")  # Missing closing parenthesis
            temp_file = Path(f.name)
        
        try:
            with pytest.raises(UDTFFileValidationError, match="Syntax error"):
                validate_python_file(temp_file)
        finally:
            temp_file.unlink()
    
    def test_load_udtf_files_success(self):
        """Test successful loading of UDTF files."""
        # Clear registry first
        registry.clear()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            udtf_file = temp_path / "test_udtf.py"
            
            # Create a valid UDTF file
            udtf_content = '''
from hyperfusion.udtf import udtf
from dataclasses import dataclass

@dataclass
class TestResult:
    value: int

@udtf
async def test_function(x: int) -> TestResult:
    return TestResult(value=x * 2)
'''
            udtf_file.write_text(udtf_content)
            
            successful_modules, error_messages = load_udtf_files([str(udtf_file)])
            
            assert len(successful_modules) == 1
            assert len(error_messages) == 0
            assert "test_function" in registry.names()
    
    def test_load_udtf_files_with_errors(self):
        """Test loading UDTF files with some errors."""
        # Clear registry first
        registry.clear()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Valid UDTF file
            valid_file = temp_path / "valid.py"
            valid_content = '''
from hyperfusion.udtf import udtf
from dataclasses import dataclass

@dataclass
class ValidResult:
    result: int

@udtf
async def valid_function(x: int) -> ValidResult:
    return ValidResult(result=x + 1)
'''
            valid_file.write_text(valid_content)
            
            # Invalid syntax file
            invalid_file = temp_path / "invalid.py"
            invalid_file.write_text("def broken(\n    return 42")
            
            successful_modules, error_messages = load_udtf_files([str(valid_file), str(invalid_file)])
            
            assert len(successful_modules) == 1
            assert len(error_messages) == 1
            assert "valid_function" in registry.names()
            assert "Syntax error" in error_messages[0]
    
    def test_load_udtf_files_directory(self):
        """Test loading UDTF files from directory."""
        # Clear registry first
        registry.clear()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            subdir = temp_path / "subdir"
            subdir.mkdir()
            
            # Create UDTF files in different locations
            file1 = temp_path / "func1.py"
            file2 = subdir / "func2.py"
            
            content1 = '''
from hyperfusion.udtf import udtf
from dataclasses import dataclass

@dataclass
class NumericResult:
    result: int

@udtf
async def function_one(x: int) -> NumericResult:
    return NumericResult(result=x * 3)
'''
            
            content2 = '''
from hyperfusion.udtf import udtf
from dataclasses import dataclass

@dataclass
class StringResult:
    result: str

@udtf
async def function_two(x: str) -> StringResult:
    return StringResult(result=x.upper())
'''
            
            file1.write_text(content1)
            file2.write_text(content2)
            
            successful_modules, error_messages = load_udtf_files([str(temp_path)])
            
            assert len(successful_modules) == 2
            assert len(error_messages) == 0
            assert "function_one" in registry.names()
            assert "function_two" in registry.names()
    
    
    def teardown_method(self):
        """Clean up after each test."""
        registry.clear()