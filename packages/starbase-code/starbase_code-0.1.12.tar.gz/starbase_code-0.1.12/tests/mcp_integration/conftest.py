"""
Pytest configuration for MCP integration tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_starbase(tmp_path):
    """Create a mock starbase directory for testing."""
    starbase_dir = tmp_path / "test_starbase"
    starbase_dir.mkdir()
    
    # Create catalog.json
    catalog_file = starbase_dir / "catalog.json"
    catalog_file.write_text("[]")
    
    return starbase_dir


@pytest.fixture
def example_packages():
    """Provide example package data for tests."""
    return [
        {
            "name": "calculator",
            "description": "Simple calculator with basic operations",
            "path": "calculator",
            "entry_points": ["calculator.py"]
        },
        {
            "name": "speech_to_text", 
            "description": "Text-to-speech for macOS",
            "path": "speech_to_text",
            "entry_points": ["speech_to_text.py"]
        }
    ]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "mcp: marks tests specific to MCP functionality"
    )