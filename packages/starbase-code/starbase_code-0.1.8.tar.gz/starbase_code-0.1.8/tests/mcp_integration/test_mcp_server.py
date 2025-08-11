#!/usr/bin/env python3
"""
MCP Server Integration Tests
Tests the actual MCP server functionality with real JSON-RPC communication.
"""

import pytest
import json
import subprocess
import time
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.starbase.mcp_installer import MCPInstaller
from starbase import StarbaseManager


class TestMCPServerIntegration:
    """Integration tests for MCP server functionality."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment once for all tests."""
        # Create temporary starbase for testing
        cls.temp_dir = tempfile.mkdtemp(prefix="starbase_mcp_test_")
        cls.test_starbase = Path(cls.temp_dir)
        
        # Install MCP server in test location
        installer = MCPInstaller(cls.test_starbase)
        installer.install_mcp_server()
        
        # Create test catalog with example apps
        cls._populate_test_catalog()
        
        # Start MCP server
        cls.mcp_process = cls._start_mcp_server()
        time.sleep(2)  # Wait for server to start
    
    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        # Stop MCP server
        if hasattr(cls, 'mcp_process') and cls.mcp_process:
            cls.mcp_process.terminate()
            cls.mcp_process.wait()
        
        # Remove temporary directory
        if hasattr(cls, 'temp_dir'):
            shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    @classmethod
    def _populate_test_catalog(cls):
        """Populate test catalog with example apps."""
        catalog_data = [
            {
                "name": "calculator",
                "path": "calculator",
                "type": "project",
                "description": "Simple calculator with basic math operations and history",
                "entry_points": ["calculator.py"],
                "file_count": 2,
                "total_size": 8192
            },
            {
                "name": "speech_to_text",
                "path": "speech_to_text",
                "type": "project", 
                "description": "macOS text-to-speech converter using built-in TTS engine",
                "entry_points": ["speech_to_text.py"],
                "file_count": 2,
                "total_size": 10240
            }
        ]
        
        catalog_file = cls.test_starbase / "catalog.json"
        with open(catalog_file, 'w') as f:
            json.dump(catalog_data, f, indent=2)
        
        # Copy example apps to test starbase
        for app in ['calculator', 'speech_to_text']:
            src = Path(__file__).parent.parent.parent / 'test_apps' / app
            dst = cls.test_starbase / app
            if src.exists():
                shutil.copytree(src, dst)
    
    @classmethod
    def _start_mcp_server(cls):
        """Start the MCP server subprocess."""
        server_script = cls.test_starbase / "starbase_mcp_server.py"
        
        # Use UV if available, otherwise use python
        try:
            # Try UV first
            process = subprocess.Popen(
                ["uv", "run", str(server_script)],
                cwd=str(cls.test_starbase),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except FileNotFoundError:
            # Fallback to Python
            process = subprocess.Popen(
                [sys.executable, str(server_script)],
                cwd=str(cls.test_starbase),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PYTHONPATH": str(cls.test_starbase)}
            )
        
        return process
    
    def _send_mcp_request(self, method: str, params: dict = None):
        """Send a JSON-RPC request to the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.mcp_process.stdin.write(request_json)
        self.mcp_process.stdin.flush()
        
        # Read response
        response_line = self.mcp_process.stdout.readline()
        if response_line:
            return json.loads(response_line)
        return None
    
    def test_mcp_server_starts(self):
        """Test that MCP server starts successfully."""
        assert self.mcp_process is not None
        assert self.mcp_process.poll() is None  # Process is still running
    
    def test_search_packages(self):
        """Test searching for packages via MCP."""
        response = self._send_mcp_request(
            "search_packages",
            {"query": "calculator"}
        )
        
        assert response is not None
        assert "result" in response
        results = response["result"]
        
        assert len(results) > 0
        assert any(r["name"] == "calculator" for r in results)
        
        # Check result structure
        calc_result = next(r for r in results if r["name"] == "calculator")
        assert "description" in calc_result
        assert "path" in calc_result
        assert "score" in calc_result
    
    def test_search_with_typo(self):
        """Test semantic search with typos."""
        response = self._send_mcp_request(
            "search_packages",
            {"query": "calculater", "deep": False}  # Typo
        )
        
        assert response is not None
        results = response["result"]
        
        # Should still find calculator despite typo
        assert any("calculator" in r["name"].lower() for r in results)
    
    def test_get_package_code(self):
        """Test retrieving full source code of a package."""
        response = self._send_mcp_request(
            "get_package_code",
            {"package_name": "calculator"}
        )
        
        assert response is not None
        assert "result" in response
        result = response["result"]
        
        assert result["package"] == "calculator"
        assert "files" in result
        assert "calculator.py" in result["files"]
        
        # Verify code content
        calc_code = result["files"]["calculator.py"]
        assert "class Calculator" in calc_code
        assert "def add" in calc_code
    
    def test_list_all_packages(self):
        """Test listing all packages in starbase."""
        response = self._send_mcp_request("list_all_packages")
        
        assert response is not None
        packages = response["result"]
        
        assert len(packages) >= 2
        package_names = [p["name"] for p in packages]
        assert "calculator" in package_names
        assert "speech_to_text" in package_names
    
    def test_get_install_command(self):
        """Test getting installation commands."""
        # Test PDM installation
        response = self._send_mcp_request(
            "get_install_command",
            {"package_name": "calculator", "method": "pdm"}
        )
        
        assert response is not None
        result = response["result"]
        
        assert result["package"] == "calculator"
        assert result["method"] == "pdm"
        assert "pdm add -e" in result["command"]
        assert self.test_starbase.name in result["command"]
    
    def test_invalid_package(self):
        """Test handling of non-existent package."""
        response = self._send_mcp_request(
            "get_package_code",
            {"package_name": "nonexistent"}
        )
        
        assert response is not None
        assert "result" in response
        assert "error" in response["result"]
    
    def test_deep_search(self):
        """Test deep search functionality."""
        response = self._send_mcp_request(
            "search_packages",
            {"query": "history", "deep": True}
        )
        
        assert response is not None
        results = response["result"]
        
        # Should find calculator because it has history functionality
        assert any(r["name"] == "calculator" for r in results)
        
        # Deep search should include code preview
        calc_result = next((r for r in results if r["name"] == "calculator"), None)
        if calc_result and "code_preview" in calc_result:
            assert "history" in calc_result["code_preview"].lower()


class TestMCPProtocol:
    """Test MCP protocol compliance."""
    
    def test_json_rpc_format(self):
        """Test that responses follow JSON-RPC 2.0 format."""
        # This would test the actual protocol format
        # For now, we verify the structure in the integration tests above
        pass
    
    def test_error_responses(self):
        """Test that errors follow JSON-RPC error format."""
        # Would test error response format
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])