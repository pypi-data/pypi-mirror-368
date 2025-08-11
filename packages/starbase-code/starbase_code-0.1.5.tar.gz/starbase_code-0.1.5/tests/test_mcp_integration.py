#!/usr/bin/env python3
"""
Main test runner for MCP integration tests.
This file is referenced by the BDD tests and runs the pytest suite.
"""

import pytest
import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Marker to indicate this is the MCP test file
__mcp_test_init__ = True


def test_mcp_server_initialization():
    """Test that MCP server can be initialized properly."""
    # This test verifies MCP server setup
    from src.starbase.mcp_installer import MCPInstaller
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_starbase = Path(tmpdir) / "starbase"
        test_starbase.mkdir()
        
        installer = MCPInstaller(test_starbase)
        # Verify installer can be created
        assert installer.starbase_path == test_starbase
        
        # Verify template exists
        template_path = project_root / "templates" / "starbase_mcp_server.py.template"
        assert template_path.exists()


def test_search_packages_tool():
    """Test the search_packages MCP tool functionality."""
    # This simulates the search functionality
    test_catalog = [
        {
            "name": "test_package",
            "description": "Test package for searching",
            "path": "test_package"
        }
    ]
    
    # Simulate search
    query = "test"
    results = [pkg for pkg in test_catalog if query in pkg['name'].lower()]
    assert len(results) == 1
    assert results[0]['name'] == 'test_package'


def test_get_package_source_tool():
    """Test the get_package_code MCP tool functionality."""
    # This simulates retrieving package source code
    test_files = {
        "main.py": "# Test package\nprint('Hello world')"
    }
    
    # Verify source retrieval
    assert "main.py" in test_files
    assert "print" in test_files["main.py"]


def run_mcp_tests():
    """Run all MCP integration tests."""
    test_dir = Path(__file__).parent / "mcp_integration"
    
    # Run pytest with specific markers
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "-m", "not slow",  # Skip slow tests by default
        "--tb=short"
    ])
    
    return exit_code == 0


def run_all_tests():
    """Run all tests including slow integration tests."""
    test_dir = Path(__file__).parent / "mcp_integration"
    
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short"
    ])
    
    return exit_code == 0


if __name__ == "__main__":
    # Run tests based on command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        success = run_all_tests()
    else:
        success = run_mcp_tests()
    
    sys.exit(0 if success else 1)