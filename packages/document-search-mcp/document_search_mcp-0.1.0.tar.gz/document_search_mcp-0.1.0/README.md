# Document Search MCP

A Model Context Protocol (MCP) server that provides intelligent document search across multiple sources, starting with Google Drive integration.

## Overview

This MCP server enables AI assistants like Claude Desktop to search and retrieve documents from connected sources. It implements the official MCP protocol and provides a clean, extensible architecture for adding new document connectors.

## Features

- 🔍 **Multi-source document search** - Search across Google Drive documents, sheets, and presentations
- 🔐 **OAuth 2.0 authentication** - Secure authentication with environment-based credentials
- 📄 **Full content retrieval** - Get complete document content for analysis
- 🔌 **Extensible plugin system** - Ready framework for custom enhancements
- 🏗️ **Modular architecture** - Clean separation of connectors, models, and search orchestration

## Quick Start

### Prerequisites

- Python 3.11+
- Google OAuth 2.0 credentials (for Google Drive integration)

### Installation

```bash
# Install uv (recommended Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repository-url>
cd document-search-mcp
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Configuration

1. Set up Google OAuth credentials:
```bash
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

2. Configure Claude Desktop by adding to `~/.claude/mcp_servers.json`:
```json
{
  "mcpServers": {
    "document-search": {
      "command": "document-search-mcp"
    }
  }
}
```

### Usage

```bash
# Start the MCP server
document-search-mcp

# Or with debug logging
document-search-mcp --log-level DEBUG
```

## MCP Tools

The server provides these MCP tools:

- **`search_documents`** - Search across connected document sources
- **`get_document_content`** - Retrieve full content from documents  
- **`list_sources`** - Show configured document sources and status
- **`setup_google_drive`** - OAuth setup and configuration wizard

## Supported Document Sources

- ✅ **Google Drive** - Google Docs, Sheets, and Slides with OAuth 2.0
- 🚧 **Confluence** - Planned (connector interface ready)
- 🚧 **SharePoint** - Planned
- 🚧 **Other sources** - Framework ready for extension

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only  
pytest -m "not slow"        # Skip slow tests
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting and formatting
ruff check src/              # Lint check
ruff format src/             # Auto-format code

# Security scanning
bandit -r src/               # Security issues
safety check                 # Vulnerable dependencies
```

### Adding New Document Connectors

Create a new connector by extending the base class:

```python
from src.connectors.base_connector import DocumentConnector
from src.models.document import Document

class MySourceConnector(DocumentConnector):
    def get_documents(self, options: dict[str, Any] | None = None) -> AsyncIterator[Document]:
        # Implement async generator for document retrieval
        yield document
    
    async def get_document(self, document_id: str) -> Document:
        # Implement single document retrieval
        pass
        
    async def search_documents(self, query: str, options: dict[str, Any] | None = None) -> list[DocumentMatch]:
        # Implement search functionality
        pass
```

## Architecture

### Core Components

- **MCP Server** (`src/server/mcp_server.py`) - Main MCP protocol implementation
- **Document Connectors** (`src/connectors/`) - Modular interfaces for document sources
- **Search Orchestrator** (`src/server/search_orchestrator.py`) - Multi-source search coordination
- **Plugin System** (`src/plugins/`) - Extensible framework for enhancements
- **Data Models** (`src/models/`) - Document and search models with Pydantic validation

### Project Structure

```
src/
├── main.py                 # CLI entry point with Click interface
├── models/                 # Pydantic data models
├── connectors/             # Document source connectors
│   ├── base_connector.py   # Abstract base class
│   └── google_drive_connector.py  # Google Drive implementation
├── server/                 # MCP server implementation
│   ├── mcp_server.py       # Main MCP protocol handling
│   └── search_orchestrator.py     # Multi-source coordination
└── plugins/                # Plugin system framework
    └── base_plugin.py      # Plugin interfaces

tests/
└── test_basic.py          # Basic functionality tests

config/
├── config.yaml            # Default configuration
└── config.yaml.local      # Local development config
```

## Configuration

The server uses environment-based configuration with automatic persistence:

- **OAuth credentials**: Set via environment variables (never hardcoded)
- **Configuration file**: Automatically saved to `~/.config/document-search-mcp/config.yaml`
- **Setup wizard**: Use the `setup_google_drive` MCP tool for guided OAuth setup

### Google Drive Setup Process

1. Set environment variables with your Google OAuth credentials
2. Use `setup_google_drive` MCP tool with `step: "start"`
3. Visit provided OAuth URL to authorize access
4. Complete setup with `step: "complete"` and redirect URL
5. Configuration persists automatically for future use

## CI/CD Pipeline

The project uses GitLab CI with a PyPI publishing pipeline:

### Pipeline Stages
- **validate** - Code quality checks (ruff, mypy, bandit, safety)
- **build** - Python package building 
- **test** - Package integrity testing and unit tests
- **publish** - PyPI publishing (manual/tag-triggered)

### Running Validation Locally
```bash
# Complete validation suite (matches CI)
ruff check src/
ruff format --check src/
mypy src/
bandit -r src/
safety check
```

## Package Management

This project uses `uv` for fast Python package management:

```bash
# Development environment setup
uv venv
uv pip install -e ".[dev]"

# Package building
python -m build

# Validate package
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```

## Current Implementation Status

### ✅ Completed
- Complete MCP server implementation with Google Drive integration
- OAuth 2.0 authentication with environment-based credentials  
- Document search and content retrieval across Google Docs/Sheets/Slides
- Extensible plugin architecture and data models
- Comprehensive test framework with markers and coverage
- GitLab CI/CD pipeline for Python package publishing
- Type safety with strict mypy configuration (all type errors resolved)
- Code formatting and linting with ruff

### 🚧 In Progress/Planned
- Additional document connectors (Confluence, SharePoint, etc.)
- Semantic search with vector embeddings
- Plugin implementations for specific domains
- Enhanced metadata extraction and filtering
- Web-based configuration interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the full validation suite:
   ```bash
   ruff check src/ && ruff format --check src/ && mypy src/ && bandit -r src/
   ```
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and feature requests, please use the project's issue tracker.