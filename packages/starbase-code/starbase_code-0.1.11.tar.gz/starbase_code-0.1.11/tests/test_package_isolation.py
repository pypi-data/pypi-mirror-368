"""Unit tests for package isolation functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
from unittest.mock import Mock, patch

# Import the functions we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from starbase import extract_to_isolated_package, trace_dependencies


class TestPackageIsolation:
    """Test suite for package isolation features."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        workspace = Path(tempfile.mkdtemp())
        yield workspace
        shutil.rmtree(workspace)
    
    @pytest.fixture
    def sample_python_file(self, temp_workspace):
        """Create a sample Python file for testing."""
        file_path = temp_workspace / "calculator.py"
        file_path.write_text('''#!/usr/bin/env python3
"""Simple calculator module."""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

if __name__ == "__main__":
    print(f"2 + 3 = {add(2, 3)}")
    print(f"5 - 2 = {subtract(5, 2)}")
''')
        return file_path
    
    @pytest.fixture
    def python_file_with_deps(self, temp_workspace):
        """Create Python files with dependencies."""
        # Create main file
        main_file = temp_workspace / "main.py"
        main_file.write_text('''#!/usr/bin/env python3
"""Main application file."""

from utils import helper_function
import config

def main():
    """Main entry point."""
    result = helper_function("test")
    print(f"Config: {config.APP_NAME}")
    return result

if __name__ == "__main__":
    main()
''')
        
        # Create dependency
        utils_file = temp_workspace / "utils.py"
        utils_file.write_text('''"""Utility functions."""

def helper_function(text):
    """A helper function."""
    return f"Processed: {text}"
''')
        
        # Create config file
        config_file = temp_workspace / "config.py"
        config_file.write_text('''"""Configuration module."""

APP_NAME = "Test Application"
VERSION = "1.0.0"
''')
        
        return main_file
    
    def test_extract_single_file_to_isolated_directory(self, sample_python_file, temp_workspace):
        """Test extracting a single file creates an isolated directory."""
        # Create target directory
        starbase_dir = temp_workspace / "starbase"
        package_dir = starbase_dir / "calculator"
        
        # Mock the manager to use our test directory
        with patch('starbase.manager') as mock_manager:
            mock_manager.get_active_path.return_value = str(starbase_dir)
            
            # Extract the file
            result = extract_to_isolated_package(sample_python_file, package_dir)
        
        # Verify results
        assert result['package_name'] == 'calculator'
        assert package_dir.exists()
        assert (package_dir / "calculator.py").exists()
        assert (package_dir / "package.json").exists()
        
        # Verify package.json content
        manifest = json.loads((package_dir / "package.json").read_text())
        assert manifest['name'] == 'calculator'
        assert manifest['entry_point'] == 'calculator.py'
        assert 'calculator.py' in manifest['files'][0]
    
    def test_extract_file_with_dependencies(self, python_file_with_deps, temp_workspace):
        """Test extracting a file with dependencies includes them."""
        # Create target directory
        starbase_dir = temp_workspace / "starbase"
        package_dir = starbase_dir / "main"
        
        # Mock the manager and trace_dependencies
        with patch('starbase.manager') as mock_manager:
            mock_manager.get_active_path.return_value = str(starbase_dir)
            
            # Mock trace_dependencies to return our test dependencies
            with patch('starbase.trace_dependencies') as mock_trace:
                utils_file = python_file_with_deps.parent / "utils.py"
                config_file = python_file_with_deps.parent / "config.py"
                mock_trace.return_value = [utils_file, config_file]
                
                # Extract the file
                result = extract_to_isolated_package(python_file_with_deps, package_dir)
        
        # Verify all files were extracted
        assert (package_dir / "main.py").exists()
        assert (package_dir / "utils.py").exists()
        assert (package_dir / "config.py").exists()
        assert len(result['extracted_files']) == 3
    
    def test_multiple_packages_remain_isolated(self, temp_workspace):
        """Test that multiple packages are kept in separate directories."""
        starbase_dir = temp_workspace / "starbase"
        
        # Create two different files
        calc_file = temp_workspace / "calculator.py"
        calc_file.write_text('def add(a, b): return a + b')
        
        menu_file = temp_workspace / "menu.py"
        menu_file.write_text('def show_menu(): print("Menu")')
        
        with patch('starbase.manager') as mock_manager:
            mock_manager.get_active_path.return_value = str(starbase_dir)
            
            # Extract both files
            calc_dir = starbase_dir / "calculator"
            menu_dir = starbase_dir / "menu"
            
            extract_to_isolated_package(calc_file, calc_dir)
            extract_to_isolated_package(menu_file, menu_dir)
        
        # Verify isolation
        assert calc_dir.exists()
        assert menu_dir.exists()
        assert (calc_dir / "calculator.py").exists()
        assert (menu_dir / "menu.py").exists()
        
        # Verify no cross-contamination
        assert not (calc_dir / "menu.py").exists()
        assert not (menu_dir / "calculator.py").exists()
    
    def test_package_manifest_creation(self, sample_python_file, temp_workspace):
        """Test that package manifest is created correctly."""
        starbase_dir = temp_workspace / "starbase"
        package_dir = starbase_dir / "calculator"
        
        with patch('starbase.manager') as mock_manager:
            mock_manager.get_active_path.return_value = str(starbase_dir)
            
            result = extract_to_isolated_package(sample_python_file, package_dir)
        
        manifest_path = package_dir / "package.json"
        assert manifest_path.exists()
        
        manifest = json.loads(manifest_path.read_text())
        assert manifest['name'] == 'calculator'
        assert manifest['version'] == '0.1.0'
        assert 'description' in manifest
        assert 'extracted_at' in manifest
        assert 'source_path' in manifest
        assert isinstance(manifest['files'], list)
        assert len(manifest['files']) > 0
    
    def test_catalog_update(self, sample_python_file, temp_workspace):
        """Test that the catalog is updated when extracting."""
        starbase_dir = temp_workspace / "starbase"
        package_dir = starbase_dir / "calculator"
        
        with patch('starbase.manager') as mock_manager:
            mock_manager.get_active_path.return_value = str(starbase_dir)
            
            # Mock the database
            with patch('starbase.tinydb.TinyDB') as mock_db_class:
                mock_db = Mock()
                mock_db_class.return_value = mock_db
                
                # Extract the file
                extract_to_isolated_package(sample_python_file, package_dir)
                
                # Verify catalog was updated
                mock_db.upsert.assert_called_once()
                call_args = mock_db.upsert.call_args[0][0]
                assert call_args['name'] == 'calculator'
                assert call_args['path'] == 'calculator'
                assert 'description' in call_args
                assert 'extracted_at' in call_args
    
    def test_no_file_mixing_between_packages(self, temp_workspace):
        """Test that files from one package never appear in another."""
        starbase_dir = temp_workspace / "starbase"
        
        # Create files with same names but different content
        file1 = temp_workspace / "utils.py"
        file1.write_text('# Utils for package 1\ndef helper1(): pass')
        
        file2 = temp_workspace / "helpers" / "utils.py"
        file2.parent.mkdir()
        file2.write_text('# Utils for package 2\ndef helper2(): pass')
        
        with patch('starbase.manager') as mock_manager:
            mock_manager.get_active_path.return_value = str(starbase_dir)
            
            # Extract to different packages
            pkg1_dir = starbase_dir / "package1"
            pkg2_dir = starbase_dir / "package2"
            
            extract_to_isolated_package(file1, pkg1_dir)
            extract_to_isolated_package(file2, pkg2_dir)
        
        # Verify each package has its own utils.py
        pkg1_utils = pkg1_dir / "utils.py"
        pkg2_utils = pkg2_dir / "utils.py"
        
        assert pkg1_utils.exists()
        assert pkg2_utils.exists()
        
        # Verify content is different
        assert "helper1" in pkg1_utils.read_text()
        assert "helper2" in pkg2_utils.read_text()
        assert "helper1" not in pkg2_utils.read_text()
        assert "helper2" not in pkg1_utils.read_text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])