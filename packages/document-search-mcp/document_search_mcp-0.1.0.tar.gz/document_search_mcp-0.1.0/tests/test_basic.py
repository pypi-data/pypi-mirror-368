"""Basic tests for the Document Search MCP Server."""

import pytest
from pathlib import Path


def test_project_structure():
    """Test that the basic project structure exists."""
    project_root = Path(__file__).parent.parent
    
    # Check main directories exist
    assert (project_root / "src").exists()
    assert (project_root / "src" / "server").exists()
    assert (project_root / "src" / "connectors").exists()
    assert (project_root / "src" / "models").exists()
    
    # Check main files exist
    assert (project_root / "src" / "server" / "mcp_server.py").exists()
    assert (project_root / "src" / "connectors" / "google_drive_connector.py").exists()
    assert (project_root / "pyproject.toml").exists()


def test_imports():
    """Test that main modules can be imported."""
    try:
        from src.server.mcp_server import DocumentSearchServer
        from src.connectors.google_drive_connector import GoogleDriveConnector
        assert True  # Imports successful
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


def test_server_initialization():
    """Test that the MCP server can be initialized."""
    from src.server.mcp_server import DocumentSearchServer
    
    server = DocumentSearchServer()
    assert server is not None
    assert server.server is not None
    assert server.search_orchestrator is not None


def test_folder_id_extraction():
    """Test folder ID extraction from Google Drive URLs."""
    from src.server.mcp_server import DocumentSearchServer
    
    server = DocumentSearchServer()
    
    # Test various URL formats
    test_cases = [
        ("https://drive.google.com/drive/folders/1ABC123def456", "1ABC123def456"),
        ("https://drive.google.com/drive/u/0/folders/1XYZ789ghi012", "1XYZ789ghi012"),
        ("folders/1DEF456jkl789", "1DEF456jkl789"),
        ("invalid-url", None),
        ("", None),
    ]
    
    for url, expected in test_cases:
        result = server._extract_folder_id(url)
        assert result == expected, f"Failed for URL: {url}"


def test_setup_detection():
    """Test setup detection logic."""
    from src.server.mcp_server import DocumentSearchServer
    
    server = DocumentSearchServer()
    
    # Should need setup since token/config files don't exist
    assert server._needs_setup() is True
    assert server._is_configured() is False