# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Document Search MCP (Model Context Protocol) server project that provides intelligent document search across multiple sources, starting with Google Drive integration. The server implements the MCP protocol to enable AI assistants like Claude Desktop to search and retrieve documents from connected sources.

**Implementation Language**: Python 3.11+
**MCP SDK**: Uses the official `mcp` Python package from https://github.com/modelcontextprotocol/python-sdk
**Package Management**: Uses `uv` for fast Python package management
**Entry Point**: `document-search-mcp` command (via `src.main:main`)

## Architecture

### Core Components
- **MCP Server** (`src/server/mcp_server.py`): Main server implementing MCP protocol with tools and resources
- **Document Connectors** (`src/connectors/`): Modular interfaces for different document sources
- **Search Orchestrator** (`src/server/search_orchestrator.py`): Coordinates searches across multiple sources  
- **Plugin System** (`src/plugins/`): Extensible framework for domain-specific enhancements
- **Data Models** (`src/models/`): Document and search models with extensible metadata

### Current MCP Tools
- `search_documents`: Search across connected document sources
- `get_document_content`: Retrieve full content from documents
- `list_sources`: Show configured document sources and status
- `setup_google_drive`: OAuth setup and configuration wizard

### Document Sources Status
- **Google Drive**: ✅ Implemented with OAuth 2.0 authentication
- **Confluence**: 🚧 Planned (connector interface ready)
- **Others**: Framework ready for extension

## Development Commands

### Environment Setup
```bash
# Install uv (recommended Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up development environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Running the Server
```bash
# Start MCP server (requires OAuth credentials in environment)
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
document-search-mcp --log-level DEBUG

# Alternative: Direct Python module execution
python -m src.main --log-level DEBUG
python -m src.main --config config/config.yaml.local
```

### Testing
```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html

# Test categories (markers defined in pyproject.toml)
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only  
pytest -m "not slow"        # Skip slow tests

# Run specific test file
pytest tests/test_basic.py -v
```

### Code Quality
```bash
# Type checking (strict mypy configuration)
mypy src/

# Linting and formatting (ruff configuration)
ruff check src/              # Lint check
ruff format src/             # Auto-format code

# Security scanning
bandit -r src/               # Security issues
safety check                 # Vulnerable dependencies
```

### Package Building
```bash
# Build package (using hatchling backend)
python -m build

# Validate package
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('pyproject.toml is valid')"

# Test installation
pip install -e .
python -c "from src.server.mcp_server import DocumentSearchServer; print('Import successful')"
```

## MCP Integration

### Claude Desktop Configuration
Add to Claude Desktop MCP settings (`~/.claude/mcp_servers.json`):
```json
{
  "mcpServers": {
    "document-search": {
      "command": "document-search-mcp"
    }
  }
}
```

### Testing with MCP Inspector
```bash
# Install and run MCP Inspector
npx @modelcontextprotocol/inspector
python -m src.main | npx @modelcontextprotocol/inspector
```

## Configuration

### OAuth Setup
The server uses environment-based OAuth credentials (no hardcoded secrets):
```bash
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

Configuration is automatically saved to `~/.config/document-search-mcp/config.yaml` after OAuth setup.

### Google Drive Setup Process
1. Set environment variables with Google OAuth credentials
2. Use `setup_google_drive` MCP tool with `step: "start"`
3. Visit provided OAuth URL to authorize access
4. Complete setup with `step: "complete"` and redirect URL
5. Configuration persists automatically for future use

## CI/CD Pipeline

### Current Pipeline Status
The project uses GitLab CI with a **PyPI publishing pipeline** (`.gitlab-ci.yml`):

**Stages:**
- `validate`: Code quality checks (ruff, mypy, bandit, safety)
- `build`: Python package building 
- `test`: Package integrity testing and unit tests
- `publish`: PyPI publishing (manual/tag-triggered)

**Key Commands for Pipeline:**
```bash
# Validate GitLab CI configuration
glab ci lint

# Common pipeline fixes
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"  # TOML validation
```

**Recent Pipeline Issues Fixed:**
- ✅ YAML emoji characters causing parsing errors  
- ✅ Invalid `python -m build --dry-run` command (flag doesn't exist)
- ✅ Script configuration validation errors

## Project Structure Understanding

### Package Configuration (`pyproject.toml`)
- **Build Backend**: Hatchling (modern Python packaging)
- **Dependencies**: 20+ packages including MCP SDK, Google APIs, ML libraries
- **Dev Dependencies**: pytest, mypy, ruff, security tools
- **Scripts**: `document-search-mcp = "src.main:main"`
- **Test Configuration**: pytest with asyncio, coverage requirements, test markers

### Code Organization
```
src/
├── main.py                 # CLI entry point with Click interface
├── models/                 # Data models with Pydantic
├── connectors/             # Document source connectors
│   ├── base_connector.py   # Abstract base class
│   └── google_drive_connector.py  # Google Drive implementation
├── server/                 # MCP server implementation
│   ├── mcp_server.py       # Main MCP protocol handling
│   └── search_orchestrator.py     # Multi-source search coordination
└── plugins/                # Plugin system framework
    └── base_plugin.py      # Plugin interfaces

tests/
└── test_basic.py          # Basic functionality tests

config/
├── config.yaml            # Default configuration
└── config.yaml.local      # Local development config
```

### Missing Infrastructure
**Note**: The current CLAUDE.md mentions Docker and AWS ECS infrastructure extensively, but these files don't exist in the repository:
- No `Dockerfile` or `docker-compose.yml` 
- No `infra/` directory with Terraform
- No `scripts/build-docker.sh` or deployment scripts
- No ECS or EC2 deployment configurations

The project currently focuses on local development and PyPI packaging rather than containerized deployment.

## Adding New Features

### Creating Document Connectors
Extend `DocumentConnector` base class from `src/connectors/base_connector.py`:
```python
from src.connectors.base_connector import DocumentConnector
from src.models.document import BaseDocument

class MySourceConnector(DocumentConnector):
    async def search(self, query: str, **kwargs) -> List[BaseDocument]:
        # Implement search logic
        pass
    
    async def get_content(self, document_id: str) -> str:
        # Implement content retrieval
        pass
        
    async def health_check(self) -> bool:
        # Implement health check
        pass
```

### Creating Plugins  
Implement plugin interfaces from `src/plugins/base_plugin.py`:
```python
from src.plugins.base_plugin import MetadataEnhancer

class CustomMetadataEnhancer(MetadataEnhancer):
    async def enhance_metadata(self, document: BaseDocument) -> dict:
        # Extract custom metadata
        return {"custom_field": "value"}
```

## Dependencies and Tools

### Core Runtime Dependencies
- `mcp>=1.0.0` - MCP protocol implementation
- `google-api-python-client>=2.100.0` - Google Drive integration
- `sentence-transformers>=2.2.0` - ML embeddings for semantic search
- `httpx>=0.25.0`, `aiohttp>=3.8.0` - HTTP clients
- `pydantic>=2.0.0` - Data validation and serialization
- `click>=8.1.0` - CLI interface

### Development Dependencies  
- `pytest>=7.0.0` with asyncio and coverage support
- `mypy>=1.5.0` - Type checking with strict configuration
- `ruff>=0.1.0` - Fast linting and formatting
- `bandit>=1.7.0`, `safety>=2.0.0` - Security scanning

### Package Management
This project uses `uv` for fast Python package management. Traditional `pip` also works but `uv` is recommended for development.

## Current Implementation Status

### ✅ Completed
- Complete MCP server implementation with Google Drive integration
- OAuth 2.0 authentication with environment-based credentials  
- Document search and content retrieval across Google Docs/Sheets/Slides
- Extensible plugin architecture and data models
- Comprehensive test framework with markers and coverage
- GitLab CI/CD pipeline for Python package publishing
- Type safety with strict mypy configuration

### 🚧 In Progress/Planned
- Additional document connectors (Confluence, SharePoint, etc.)
- Semantic search with vector embeddings
- Plugin implementations for specific domains
- Enhanced metadata extraction and filtering
- Web-based configuration interface

The project provides a solid foundation for document search across multiple sources with a clean, extensible architecture ready for additional features and connectors.