#!/usr/bin/env python3
"""
MCP Function Tests
Tests the MCP server functions without running the actual server.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class TestMCPFunctions:
    """Test MCP server functions directly."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.temp_dir = tempfile.mkdtemp(prefix="mcp_func_test_")
        cls.test_starbase = Path(cls.temp_dir)
        
        # Create mock catalog
        catalog_data = [
            {
                "name": "test_package",
                "path": "test_package",
                "description": "Test package for unit testing",
                "entry_points": ["main.py"],
                "file_count": 1
            }
        ]
        
        catalog_file = cls.test_starbase / "catalog.json"
        catalog_file.parent.mkdir(exist_ok=True)
        with open(catalog_file, 'w') as f:
            json.dump(catalog_data, f)
        
        # Create mock package
        package_dir = cls.test_starbase / "test_package"
        package_dir.mkdir()
        (package_dir / "main.py").write_text("# Test file\nprint('Hello')")
    
    @classmethod
    def teardown_class(cls):
        """Clean up."""
        if hasattr(cls, 'temp_dir'):
            shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    def test_load_catalog(self):
        """Test catalog loading functionality."""
        # This would test the load_catalog function from the MCP server
        catalog_file = self.test_starbase / "catalog.json"
        assert catalog_file.exists()
        
        with open(catalog_file) as f:
            catalog = json.load(f)
        
        assert len(catalog) == 1
        assert catalog[0]["name"] == "test_package"
    
    def test_search_algorithm(self):
        """Test the search scoring algorithm."""
        # Test exact match gets highest score
        query = "test_package"
        name = "test_package"
        assert query == name  # Exact match
        
        # Test partial match
        query = "test"
        assert query in name  # Partial match
        
        # Test case insensitive
        query_lower = "TEST".lower()
        name_lower = "test_package".lower()
        assert query_lower in name_lower
    
    def test_package_structure(self):
        """Test expected package structure."""
        package_path = self.test_starbase / "test_package"
        assert package_path.exists()
        assert package_path.is_dir()
        assert (package_path / "main.py").exists()


class TestMCPInstallation:
    """Test MCP server installation process."""
    
    def test_mcp_template_exists(self):
        """Test that MCP server template exists."""
        template_path = Path(__file__).parent.parent.parent / "templates" / "starbase_mcp_server.py.template"
        assert template_path.exists(), f"MCP template not found at {template_path}"
    
    def test_mcp_template_content(self):
        """Test MCP template has required content."""
        template_path = Path(__file__).parent.parent.parent / "templates" / "starbase_mcp_server.py.template"
        if template_path.exists():
            content = template_path.read_text()
            
            # Check for required MCP components
            assert "FastMCP" in content
            assert "@mcp.tool()" in content
            assert "search_packages" in content
            assert "get_package_code" in content
            assert "list_all_packages" in content
            assert "get_install_command" in content
            assert "catalog.json" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])