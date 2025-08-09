# Document Search MCP Server - Technical Design Document

## 1. Executive Summary

This document outlines the technical design for a Document Search MCP (Model Context Protocol) server that enables AI clients like Claude Desktop to search and retrieve documents from Google Drive. The system provides a foundation for document search with an extensible architecture designed to support additional document sources and enhancements in the future.

**Current Implementation**: Google Drive integration with OAuth 2.0 authentication
**Future Plans**: Support for additional document sources, semantic search, and plugin system

## 2. System Overview

### 2.1 Objectives
- ✅ **Implemented**: Google Drive document search and retrieval
- ✅ **Implemented**: Secure OAuth 2.0 authentication with environment-based credentials
- ✅ **Implemented**: MCP protocol integration for AI assistants
- ✅ **Implemented**: Extensible connector architecture (ready for additional sources)
- 🚧 **Planned**: Support for additional document sources (Confluence, etc.)
- 🚧 **Planned**: Semantic search capabilities with embeddings
- 🚧 **Planned**: Plugin system for domain-specific enhancements

### 2.2 Current Scope

**✅ Currently Implemented:**
- Google Drive API integration (Docs, Sheets, Slides)
- OAuth 2.0 authentication flow with guided setup
- MCP server implementation with core tools
- Document search and content retrieval
- Environment-based credential management
- Extensible connector architecture

**🚧 Future Planned Features:**
- Confluence REST API integration
- Semantic search with vector embeddings
- Plugin system for metadata enhancement
- Additional document sources (SharePoint, etc.)
- Advanced filtering and categorization

**❌ Explicitly Out of Scope:**
- Document editing or modification capabilities
- Multi-tenancy support
- Real-time document synchronization
- Built-in business logic (delegated to future plugins)

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌─────────────────┐    ┌──────────────────────────────────────┐
│   AI Client     │    │            MCP Server                │
│ (Claude Desktop)│◄──►│         (This System)                │
└─────────────────┘    └──────────────────────────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Unified Search  │
                       │     Engine       │
                       └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ Google Drive │ │  Confluence  │ │   Future     │
        │  Connector   │ │  Connector   │ │ Connectors   │
        └──────────────┘ └──────────────┘ └──────────────┘
                │             │             │
                ▼             ▼             ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ Google Drive │ │ Confluence   │ │  Other Doc   │
        │     API      │ │ REST API     │ │   Sources    │
        └──────────────┘ └──────────────┘ └──────────────┘
```

### 3.2 Core Components

#### 3.2.1 MCP Server Layer
- **Transport Handler**: Manages stdio/HTTP communication with AI clients
- **Tool Router**: Routes tool calls to appropriate handlers
- **Multi-Auth Manager**: Handles authentication for multiple document sources

#### 3.2.2 Document Store Connectors
- **Connector Interface**: Abstract base class defining common operations
- **Google Drive Connector**: Handles Google Drive, Docs, Sheets, Slides
- **Confluence Connector**: Integrates with Confluence Wiki via REST API
- **Connector Registry**: Manages available connectors and their configurations

#### 3.2.3 Unified Search Engine
- **Search Orchestrator**: Coordinates searches across multiple sources and plugins
- **Source Aggregator**: Merges and ranks results from different connectors
- **Index Manager**: Maintains separate indices per document source
- **Query Processor**: Handles search requests with source filtering and plugin enhancement
- **Vector Store**: Manages embeddings for semantic search across all sources
- **Plugin Engine**: Executes domain-specific search enhancements and filtering

#### 3.2.4 Plugin/Layer System
- **Plugin Registry**: Manages loaded plugins and their capabilities
- **Metadata Enhancers**: Plugins that extract domain-specific metadata
- **Search Enhancers**: Plugins that modify or enhance search queries and results
- **Filter Providers**: Plugins that add custom filtering capabilities
- **Tool Extensions**: Plugins that add domain-specific MCP tools

#### 3.2.5 Data Layer
- **Multi-Source Cache**: Local storage partitioned by document source
- **Index Storage**: Separate indices for each connector with unified interface
- **Configuration Store**: Per-connector settings, plugin configs, and global configurations
- **Metadata Store**: Source attribution, cross-reference tracking, and plugin metadata
- **Schema Registry**: Manages metadata schemas and plugin-defined fields

## 4. Data Models

### 4.1 Document Model
```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

class DocumentType(Enum):
    GOOGLE_DOC = "google_doc"
    GOOGLE_SHEET = "google_sheet"
    GOOGLE_SLIDE = "google_slide"
    CONFLUENCE_PAGE = "confluence_page"
    CONFLUENCE_BLOG = "confluence_blog"

@dataclass
class DocumentSource:
    type: str  # 'google_drive' | 'confluence' | 'custom'
    name: str  # Human-readable source name
    connector: str  # Connector identifier
    config: Optional[Dict[str, Any]] = None  # Source-specific configuration

@dataclass
class BaseDocumentMetadata:
    """Core metadata fields common to all document sources"""
    author: Optional[str] = None  # Document author
    tags: Optional[List[str]] = None  # Manual or auto-generated tags
    language: Optional[str] = None  # Document language
    size: Optional[int] = None  # Document size in bytes
    category: Optional[str] = None  # Document category (e.g., "technical", "process", "incident")
    created_by: Optional[str] = None  # Creator of the document
    last_modified_by: Optional[str] = None  # Last person to modify the document

@dataclass
class GoogleDriveMetadata:
    """Google Drive specific metadata"""
    mime_type: Optional[str] = None  # Google Drive MIME type
    parents: Optional[List[str]] = None  # Parent folder IDs
    permissions: Optional[List[Dict[str, Any]]] = None
    drive_id: Optional[str] = None  # Shared drive ID if applicable
    folder_path: Optional[str] = None  # Full folder path
    sharing_settings: Optional[Dict[str, Any]] = None

@dataclass
class ConfluenceMetadata:
    """Confluence specific metadata"""
    space_key: Optional[str] = None  # Confluence space
    page_id: Optional[str] = None  # Confluence page ID
    version: Optional[int] = None  # Page version
    labels: Optional[List[str]] = None  # Confluence labels
    parent_page_id: Optional[str] = None  # Parent page ID
    ancestors: Optional[List[Dict[str, str]]] = None  # Page hierarchy
    restrictions: Optional[Dict[str, Any]] = None  # View/edit restrictions

@dataclass
class DocumentMetadata:
    """Unified document metadata with source-specific extensions"""
    # Core metadata (always present)
    base: BaseDocumentMetadata
    
    # Source-specific metadata (populated based on document source)
    google_drive: Optional[GoogleDriveMetadata] = None
    confluence: Optional[ConfluenceMetadata] = None
    
    # Plugin/domain-specific metadata
    custom_fields: Optional[Dict[str, Any]] = None  # Plugin-defined custom metadata
    schema_version: Optional[str] = None  # Metadata schema version for compatibility
    
    def get_source_metadata(self, source_type: str) -> Optional[Any]:
        """Get source-specific metadata by type"""
        return getattr(self, source_type, None)
    
    def add_custom_field(self, key: str, value: Any) -> None:
        """Add a custom field (typically used by plugins)"""
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields[key] = value
    
    def get_custom_field(self, key: str, default: Any = None) -> Any:
        """Get a custom field value"""
        if self.custom_fields is None:
            return default
        return self.custom_fields.get(key, default)

@dataclass
class Document:
    id: str  # Unique document ID (source-specific)
    source_id: str  # Document source identifier
    source: DocumentSource  # Source information
    title: str  # Document title
    content: str  # Extracted text content
    url: str  # Document URL
    last_modified: datetime  # Last modification timestamp
    created_date: datetime  # Creation timestamp
    metadata: DocumentMetadata  # Source-specific and extracted metadata
    embedding: Optional[List[float]] = None  # Vector representation
    type: Optional[DocumentType] = None  # Document type classification
```

### 4.2 Search Query Model
```python
@dataclass
class DateRange:
    start: datetime
    end: datetime

@dataclass
class BaseSearchFilters:
    """Core search filters applicable to all document sources"""
    authors: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    date_range: Optional[DateRange] = None
    created_by: Optional[List[str]] = None
    last_modified_by: Optional[List[str]] = None

@dataclass
class GoogleDriveFilters:
    """Google Drive specific search filters"""
    folder_ids: Optional[List[str]] = None
    mime_types: Optional[List[str]] = None
    drive_ids: Optional[List[str]] = None  # Shared drive filters
    folder_paths: Optional[List[str]] = None  # Path-based filtering
    sharing_permissions: Optional[List[str]] = None  # e.g., ["public", "restricted"]

@dataclass
class ConfluenceFilters:
    """Confluence specific search filters"""
    space_keys: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    parent_page_ids: Optional[List[str]] = None
    content_types: Optional[List[str]] = None  # e.g., ["page", "blogpost"]
    restrictions: Optional[List[str]] = None  # Filter by restriction level

@dataclass
class SearchFilters:
    """Unified search filters with source-specific extensions"""
    # Core filters (always available)
    base: Optional[BaseSearchFilters] = None
    
    # Source-specific filters
    google_drive: Optional[GoogleDriveFilters] = None
    confluence: Optional[ConfluenceFilters] = None
    
    # Plugin/domain-specific filters
    custom_filters: Optional[Dict[str, Any]] = None  # Plugin-defined filters
    
    def get_source_filters(self, source_type: str) -> Optional[Any]:
        """Get source-specific filters by type"""
        return getattr(self, source_type, None)
    
    def add_custom_filter(self, key: str, value: Any) -> None:
        """Add a custom filter (typically used by plugins)"""
        if self.custom_filters is None:
            self.custom_filters = {}
        self.custom_filters[key] = value

@dataclass
class SearchQuery:
    query: str  # Search terms
    sources: Optional[List[str]] = None  # Filter by document sources
    document_types: Optional[List[DocumentType]] = None  # Filter by document types
    filters: Optional[SearchFilters] = None
    max_results: int = 10  # Default: 10
    semantic_search: bool = True  # Enable vector search
    source_weighting: Optional[Dict[str, float]] = None  # Weight results by source
```

### 4.3 Search Result Model
```python
@dataclass
class TextMatch:
    text: str  # Matched text snippet
    start_index: int  # Position in document
    end_index: int

@dataclass
class DocumentMatch:
    document: Document
    score: float  # Relevance score (0-1)
    matched_sections: List[TextMatch]  # Highlighted matching sections
    source_rank: int  # Rank within source

@dataclass
class SearchResult:
    documents: List[DocumentMatch]
    total_count: int
    search_time: float
    source_breakdown: Dict[str, int]  # Count by source
```

### 4.4 Document Connector Interface
```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class AuthConfig:
    def __init__(self, 
                 auth_type: str,  # 'oauth2' | 'api_key' | 'basic' | 'custom'
                 credentials: Dict[str, str],
                 scopes: Optional[List[str]] = None):
        self.type = auth_type
        self.credentials = credentials
        self.scopes = scopes

@dataclass
class ConnectorConfig:
    name: str
    enabled: bool
    settings: Dict[str, Any]
    auth_config: AuthConfig

class DocumentConnector(ABC):
    def __init__(self, connector_id: str, name: str, supported_types: List[DocumentType]):
        self.id = connector_id
        self.name = name
        self.supported_types = supported_types
    
    @abstractmethod
    async def initialize(self, config: ConnectorConfig) -> None:
        """Initialize the connector with configuration"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the document source"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up and disconnect from the source"""
        pass
    
    @abstractmethod
    async def get_documents(self, options: Optional[Dict[str, Any]] = None) -> AsyncIterator[Document]:
        """Get all documents from the source"""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Document:
        """Get a specific document by ID"""
        pass
    
    @abstractmethod
    async def search_documents(self, query: str, options: Optional[Dict[str, Any]] = None) -> List[DocumentMatch]:
        """Search documents in this source"""
        pass
    
    @abstractmethod
    async def get_last_sync_time(self) -> Optional[datetime]:
        """Get the last synchronization timestamp"""
        pass
    
    @abstractmethod
    async def set_last_sync_time(self, timestamp: datetime) -> None:
        """Set the last synchronization timestamp"""
        pass

# Example: Adding a new document source (SharePoint)
@dataclass
class SharePointMetadata:
    """SharePoint specific metadata"""
    site_id: Optional[str] = None
    list_id: Optional[str] = None
    library_name: Optional[str] = None
    content_type: Optional[str] = None
    check_out_user: Optional[str] = None
    approval_status: Optional[str] = None

@dataclass
class SharePointFilters:
    """SharePoint specific search filters"""
    site_ids: Optional[List[str]] = None
    library_names: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    approval_statuses: Optional[List[str]] = None

# To add SharePoint support, extend DocumentMetadata and SearchFilters:
# DocumentMetadata would get: sharepoint: Optional[SharePointMetadata] = None
# SearchFilters would get: sharepoint: Optional[SharePointFilters] = None
```

### 4.5 Plugin System Interface
```python
from abc import ABC, abstractmethod
from typing import Protocol

class MetadataEnhancer(ABC):
    """Plugin interface for extracting domain-specific metadata"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def supported_document_types(self) -> List[DocumentType]:
        """Document types this enhancer supports"""
        pass
    
    @abstractmethod
    async def enhance_metadata(self, document: Document) -> Dict[str, Any]:
        """Extract additional metadata from document"""
        pass

class SearchEnhancer(ABC):
    """Plugin interface for enhancing search queries and results"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @abstractmethod
    async def enhance_query(self, query: SearchQuery) -> SearchQuery:
        """Modify or enhance the search query"""
        pass
    
    @abstractmethod
    async def enhance_results(self, results: SearchResult, original_query: SearchQuery) -> SearchResult:
        """Post-process search results"""
        pass

class FilterProvider(ABC):
    """Plugin interface for providing custom filters"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def filter_schema(self) -> Dict[str, Any]:
        """JSON schema for this filter's parameters"""
        pass
    
    @abstractmethod
    async def apply_filter(self, documents: List[Document], filter_params: Dict[str, Any]) -> List[Document]:
        """Apply custom filtering logic"""
        pass

@dataclass
class PluginConfig:
    name: str
    enabled: bool
    settings: Dict[str, Any]
    priority: int = 100  # Lower numbers = higher priority
```

## 5. MCP Tools and Resources

### 5.1 Tool Definitions

#### 5.1.0 setup_google_drive (✅ IMPLEMENTED)
```typescript
{
  name: "setup_google_drive",
  description: "🔧 Set up Google Drive access (first-time setup required)",
  inputSchema: {
    type: "object",
    properties: {
      step: {
        type: "string",
        enum: ["start", "complete"],
        description: "Setup step: 'start' to get OAuth URL, 'complete' to finish with redirect URL"
      },
      redirect_url: {
        type: "string",
        description: "Full redirect URL from browser (only for 'complete' step)"
      },
      folder_urls: {
        type: "array",
        items: { type: "string" },
        description: "Google Drive folder URLs to search (only for 'complete' step)",
        default: []
      }
    },
    required: ["step"]
  }
}
```

#### 5.1.1 search_documents
```typescript
{
  name: "search_documents",
  description: "Search across all connected document sources",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Search query (keywords or natural language)"
      },
      sources: {
        type: "array",
        items: { type: "string" },
        description: "Filter by specific document sources (e.g., 'google_drive', 'confluence')"
      },
      document_types: {
        type: "array",
        items: { 
          type: "string",
          enum: ["google_doc", "google_sheet", "google_slide", "confluence_page", "confluence_blog"]
        },
        description: "Filter by document types"
      },
      filters: {
        type: "object",
        properties: {
          google_drive: {
            type: "object",
            properties: {
              folder_ids: { type: "array", items: { type: "string" } },
              mime_types: { type: "array", items: { type: "string" } }
            }
          },
          confluence: {
            type: "object",
            properties: {
              space_keys: { type: "array", items: { type: "string" } },
              labels: { type: "array", items: { type: "string" } }
            }
          },
          authors: { type: "array", items: { type: "string" } },
          tags: { type: "array", items: { type: "string" } },
          categories: { type: "array", items: { type: "string" } },
          date_range: {
            type: "object",
            properties: {
              start: { type: "string", format: "date" },
              end: { type: "string", format: "date" }
            }
          },
          custom_filters: {
            type: "object",
            description: "Plugin-defined custom filters",
            additionalProperties: true
          }
        }
      },
      max_results: { type: "number", default: 10, maximum: 50 },
      semantic_search: { type: "boolean", default: true },
      source_weighting: {
        type: "object",
        description: "Weight results by source (source_name: weight)",
        additionalProperties: { type: "number" }
      }
    },
    required: ["query"]
  }
}
```

#### 5.1.2 get_document_content
```typescript
{
  name: "get_document_content",
  description: "Retrieve full content of a specific document from any source",
  inputSchema: {
    type: "object",
    properties: {
      document_id: {
        type: "string",
        description: "Document ID (source-specific)"
      },
      source: {
        type: "string",
        description: "Document source identifier (e.g., 'google_drive', 'confluence')"
      },
      include_metadata: { type: "boolean", default: true },
      format: {
        type: "string",
        enum: ["text", "markdown", "html"],
        default: "text",
        description: "Content format preference"
      }
    },
    required: ["document_id", "source"]
  }
}
```

#### 5.1.3 get_similar_documents
```typescript
{
  name: "get_similar_documents",
  description: "Find documents similar to a given description or reference document",
  inputSchema: {
    type: "object",
    properties: {
      description: {
        type: "string",
        description: "Description to find similar documents for"
      },
      reference_document_id: {
        type: "string",
        description: "ID of document to find similar documents for"
      },
      reference_source: {
        type: "string",
        description: "Source of reference document"
      },
      sources: {
        type: "array",
        items: { type: "string" },
        description: "Limit search to specific sources"
      },
      similarity_threshold: { type: "number", default: 0.7, minimum: 0, maximum: 1 },
      max_results: { type: "number", default: 5, maximum: 20 }
    }
  }
}
```

#### 5.1.4 list_sources
```typescript
{
  name: "list_sources",
  description: "List all configured document sources and their status",
  inputSchema: {
    type: "object",
    properties: {
      include_stats: { type: "boolean", default: true }
    }
  }
}
```

#### 5.1.5 sync_source
```typescript
{
  name: "sync_source",
  description: "Manually trigger synchronization for a specific document source",
  inputSchema: {
    type: "object",
    properties: {
      source: {
        type: "string",
        description: "Source identifier to synchronize"
      },
      force: {
        type: "boolean",
        default: false,
        description: "Force full re-sync instead of incremental"
      }
    },
    required: ["source"]
  }
}
```

#### 5.1.6 list_plugins
```typescript
{
  name: "list_plugins",
  description: "List all available and loaded plugins",
  inputSchema: {
    type: "object",
    properties: {
      include_disabled: { type: "boolean", default: false },
      plugin_type: {
        type: "string",
        enum: ["metadata_enhancer", "search_enhancer", "filter_provider", "all"],
        default: "all"
      }
    }
  }
}
```

#### 5.1.7 get_plugin_schema
```typescript
{
  name: "get_plugin_schema",
  description: "Get the configuration schema for a specific plugin",
  inputSchema: {
    type: "object",
    properties: {
      plugin_name: {
        type: "string",
        description: "Name of the plugin to get schema for"
      }
    },
    required: ["plugin_name"]
  }
}
```

#### 5.1.8 enhance_document_metadata
```typescript
{
  name: "enhance_document_metadata",
  description: "Run metadata enhancement plugins on a specific document",
  inputSchema: {
    type: "object",
    properties: {
      document_id: {
        type: "string",
        description: "Document ID to enhance"
      },
      source: {
        type: "string",
        description: "Document source identifier"
      },
      plugins: {
        type: "array",
        items: { type: "string" },
        description: "Specific plugins to run (optional - runs all if not specified)"
      }
    },
    required: ["document_id", "source"]
  }
}
```

### 5.2 Resource Definitions

#### 5.2.1 document_sources
```typescript
{
  uri: "sources://configured",
  name: "Configured Document Sources",
  description: "List of all configured document sources and their configurations",
  mimeType: "application/json"
}
```

#### 5.2.2 source_schemas
```typescript
{
  uri: "sources://schemas",
  name: "Source Configuration Schemas",
  description: "JSON schemas for configuring different document source types",
  mimeType: "application/json"
}
```

#### 5.2.3 search_indices
```typescript
{
  uri: "search://indices",
  name: "Search Indices Status",
  description: "Status and statistics for all search indices across sources",
  mimeType: "application/json"
}
```

#### 5.2.4 google_drive_folders
```typescript
{
  uri: "gdrive://folders",
  name: "Google Drive Folders",
  description: "Available Google Drive folders for document indexing",
  mimeType: "application/json"
}
```

#### 5.2.5 confluence_spaces
```typescript
{
  uri: "confluence://spaces",
  name: "Confluence Spaces",
  description: "Available Confluence spaces for document indexing",
  mimeType: "application/json"
}
```

#### 5.2.6 plugins
```typescript
{
  uri: "plugins://loaded",
  name: "Loaded Plugins",
  description: "Currently loaded plugins and their configurations",
  mimeType: "application/json"
}
```

#### 5.2.7 metadata_schemas
```typescript
{
  uri: "schemas://metadata",
  name: "Metadata Schemas",
  description: "Available metadata schemas and custom field definitions",
  mimeType: "application/json"
}
```

## 6. Authentication and Security

### 6.1 Multi-Source Authentication

#### 6.1.1 Google Drive Authentication (✅ IMPLEMENTED)
- **Simplified OAuth 2.0 Flow**: ✅ Built-in setup wizard with guided authentication
- **Environment-Based Credentials**: ✅ Secure credential management via environment variables
- **Automatic Setup Detection**: ✅ Server detects missing configuration and guides users
- **Scope Requirements**: ✅ Currently using `https://www.googleapis.com/auth/drive.readonly`
- **Token Management**: ✅ Automatic refresh with secure credential storage at `~/.config/document-search-mcp/`
- **Security**: ✅ No hardcoded credentials, environment variables required

#### 6.1.2 Confluence Authentication
- **Authentication Methods**:
  - Basic Authentication (username/password)
  - Personal Access Tokens (recommended)
  - OAuth 2.0 (for cloud instances)
- **Permissions Required**: Read access to spaces and pages
- **API Version**: REST API v2 or Cloud REST API

#### 6.1.3 Authentication Manager
- **Credential Isolation**: Separate credential storage per connector
- **Token Refresh**: Automatic token renewal with exponential backoff
- **Auth Validation**: Periodic authentication health checks
- **Fallback Handling**: Graceful degradation when sources are unavailable

### 6.2 Data Security
- **Local Storage Encryption**: Document cache encrypted at rest
- **Access Control**: Respect Google Drive sharing permissions
- **Audit Logging**: Track document access and search queries
- **Data Retention**: Configurable cache TTL and cleanup policies

### 6.3 Privacy Considerations
- **Content Sanitization**: Option to exclude sensitive patterns from indexing
- **Anonymization**: Support for removing PII from search results
- **Consent Management**: Clear disclosure of data usage and storage

## 7. Search Implementation

### 7.1 Indexing Strategy
- **Full-Text Index**: Elasticsearch or similar for keyword search
- **Vector Index**: FAISS or Pinecone for semantic search
- **Hybrid Search**: Combine keyword and semantic results with weighted scoring
- **Incremental Updates**: Monitor Google Drive changes via webhooks or polling

### 7.2 Content Processing Pipeline
1. **Document Discovery**: Scan configured Google Drive folders
2. **Content Extraction**: Use Google Docs API to retrieve text content
3. **Metadata Extraction**: Parse structured information using NLP or patterns
4. **Text Preprocessing**: Clean, normalize, and tokenize content
5. **Embedding Generation**: Create vector representations using sentence transformers
6. **Index Updates**: Store in both full-text and vector indices

### 7.3 Query Processing
1. **Query Analysis**: Determine intent and extract entities
2. **Multi-Modal Search**: Execute both keyword and semantic searches
3. **Result Fusion**: Combine and rank results from multiple indices
4. **Post-Processing**: Apply filters, snippets, and highlighting
5. **Response Formatting**: Structure results for MCP client consumption

## 8. Configuration Management

### 8.1 Configuration Management

#### 8.1.1 Simplified Setup Process (✅ IMPLEMENTED)
The server now features an automated setup wizard that eliminates manual configuration:

1. **Environment Variables**: OAuth credentials provided via environment
2. **Setup Wizard**: MCP tool `setup_google_drive` guides users through authentication
3. **Automatic Configuration**: Config files automatically generated at `~/.config/document-search-mcp/`
4. **Folder URL Parsing**: Users provide Drive folder URLs, IDs extracted automatically

#### 8.1.2 Generated Configuration Example
```yaml
# ~/.config/document-search-mcp/config.yaml (auto-generated)
sources:
  google_drive:
    enabled: true
    name: "Google Drive"
    auth:
      type: "oauth"
      token_file: "~/.config/document-search-mcp/token.json"
    settings:
      folder_ids:
        - "1ABC123def456ghi789jkl"  # Extracted from user-provided URL
        - "2DEF456ghi789jkl012mno"  # Extracted from user-provided URL
      include_shared: true
      file_types: ["docs", "sheets", "slides"]
  
  confluence:
    enabled: true
    name: "Company Confluence"
    auth:
      type: "personal_access_token"
      base_url: "https://company.atlassian.net"
      username: "service-account@company.com"
      token: "${CONFLUENCE_TOKEN}"
    settings:
      space_keys:
        - "ENGINEERING"
        - "DOCS"
        - "KB"  # Knowledge Base
      include_blogs: true
      include_archived: false

plugins:
  # Example: Incident Management Plugin
  incident_manager:
    enabled: false  # Disabled by default - enable for specific use cases
    type: "metadata_enhancer"
    module: "plugins.incident_manager"
    settings:
      severity_keywords:
        critical: ["critical", "urgent", "p0", "sev0"]
        high: ["high", "p1", "sev1"]
        medium: ["medium", "p2", "sev2"]
        low: ["low", "p3", "sev3"]
      incident_patterns:
        - "incident.*report"
        - "post.*mortem"
        - "escalation.*note"
  
  # Example: Technical Documentation Plugin
  tech_docs:
    enabled: true
    type: "search_enhancer"
    module: "plugins.tech_docs"
    settings:
      doc_categories:
        - "api_documentation"
        - "architecture"
        - "deployment_guide"
        - "troubleshooting"

metadata_schemas:
  # Base schema - always available
  base:
    version: "1.0"
    fields:
      category: { type: "string", enum: ["technical", "process", "incident", "general"] }
      priority: { type: "string", enum: ["low", "medium", "high", "critical"] }
      team: { type: "string" }
      project: { type: "string" }
  
  # Plugin-defined schemas
  incident_schema:  # Added by incident_manager plugin
    version: "1.0"
    fields:
      incident_type: { type: "string" }
      severity: { type: "string", enum: ["low", "medium", "high", "critical"] }
      services: { type: "array", items: { type: "string" } }
      resolution: { type: "string" }
      participants: { type: "array", items: { type: "string" } }

search:
  index_type: "hybrid"  # keyword, semantic, or hybrid
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  max_content_length: 50000
  update_interval: 3600  # seconds
  cross_source_similarity: true
  plugin_enhancement: true  # Enable plugin-based search enhancement
  
cache:
  storage_path: "./data/cache"
  ttl_days: 30
  max_size_mb: 1024
  partition_by_source: true
  
server:
  transport: "stdio"  # stdio or http
  port: 8080  # if http
  log_level: "info"
  plugin_directory: "./plugins"  # Directory to scan for plugins
```

### 8.2 Source Management
- **Dynamic Discovery**: Support for nested folder structures (Google Drive) and space hierarchies (Confluence)
- **Permission Handling**: Respect access controls and sharing settings across all sources
- **Inclusion/Exclusion Rules**: Pattern-based filtering for document types and content
- **Source Health Monitoring**: Track connectivity and sync status for each source

## 9. Implementation Status

### 9.1 ✅ Current Implementation (v0.1.0)

**Core MCP Server:**
- ✅ MCP protocol server implementation with stdio transport
- ✅ Document connector architecture with extensible base class
- ✅ Type-safe implementation with complete mypy validation
- ✅ CLI entry point with Click interface (`document-search-mcp`)

**Google Drive Integration:**
- ✅ Google Drive connector (Docs, Sheets, Slides support)
- ✅ OAuth 2.0 authentication with guided setup wizard
- ✅ Environment-based credential management (secure, no hardcoded secrets)
- ✅ Folder URL parsing with automatic ID extraction
- ✅ Document search and full content retrieval

**MCP Tools Provided:**
- ✅ `setup_google_drive` - OAuth setup and configuration wizard
- ✅ `search_documents` - Search across Google Drive documents
- ✅ `get_document_content` - Retrieve full document content
- ✅ `list_sources` - Show configured sources and status

**Development Infrastructure:**
- ✅ GitLab CI/CD pipeline with validation (ruff, mypy, bandit, safety)
- ✅ Comprehensive test framework setup with pytest
- ✅ Package building with hatchling (PyPI ready)
- ✅ Code quality tools: ruff formatting/linting, mypy type checking

### 9.2 🚧 Planned Future Enhancements

**Additional Document Sources:**
- 🚧 Confluence integration (connector interface ready)
- 🚧 SharePoint support
- 🚧 Local file system indexing

**Search Enhancements:**
- 🚧 Semantic search with vector embeddings
- 🚧 Cross-document similarity search
- 🚧 Advanced filtering and ranking

**Plugin System:**
- 🚧 MetadataEnhancer plugins for domain-specific metadata extraction
- 🚧 SearchEnhancer plugins for query modification and result post-processing
- 🚧 FilterProvider plugins for custom filtering capabilities

**Production Features:**
- 🚧 Document caching and indexing
- 🚧 Real-time synchronization
- 🚧 Performance monitoring and analytics

## 10. Technical Considerations

### 10.1 Performance Requirements
- **Search Latency**: < 500ms for typical queries
- **Index Update Time**: < 5 minutes for new documents
- **Memory Usage**: < 2GB for 10,000 documents
- **Storage Efficiency**: Compressed indices and content

### 10.2 Scalability Considerations
- **Document Volume**: Support for 10,000+ documents initially
- **Concurrent Users**: Handle 10+ simultaneous AI client connections
- **Growth Planning**: Architecture supports horizontal scaling

### 10.3 Reliability and Monitoring
- **Health Checks**: Monitor Google API connectivity and index status
- **Error Recovery**: Graceful handling of API rate limits and failures
- **Logging Strategy**: Structured logging for debugging and analytics
- **Metrics Collection**: Track search performance and usage patterns

## 11. Dependencies and Technology Stack

### 11.1 Current Dependencies (v0.1.0)
- **MCP SDK**: `mcp>=1.0.0` - MCP protocol implementation
- **Google APIs**: 
  - `google-api-python-client>=2.100.0` - Google Drive API client
  - `google-auth>=2.20.0` - Google authentication
  - `google-auth-oauthlib>=1.0.0` - OAuth 2.0 flow
  - `google-auth-httplib2>=0.2.0` - HTTP transport
- **HTTP Client**: `httpx>=0.25.0` - Modern async HTTP client
- **Configuration**: 
  - `pyyaml>=6.0` - YAML configuration files
  - `pydantic>=2.0.0` - Data validation and serialization
  - `python-dotenv>=1.0.0` - Environment variable loading
- **CLI**: `click>=8.1.0` - Command-line interface
- **Output**: `rich>=13.0.0` - Rich terminal output

### 11.2 Development Tools
- **Language**: Python 3.11+
- **Package Management**: `uv` (recommended) or `pip`
- **Build System**: `hatchling` - Modern Python packaging
- **Testing**: `pytest` with async support and coverage
- **Type Checking**: `mypy>=1.5.0` - Strict type checking
- **Code Quality**: `ruff>=0.1.0` - Fast linting and formatting
- **Security**: `bandit` + `safety` - Security and vulnerability scanning
- **CI/CD**: GitLab CI with automated validation pipeline

### 11.3 Future Dependencies (Planned)
- **Additional Sources**: Confluence API client, SharePoint client
- **Search Enhancement**: Vector databases, embedding models
- **Caching**: Redis or local caching solutions

## 12. Risk Assessment and Mitigation

### 12.1 Technical Risks
- **Google API Rate Limits**: Implement exponential backoff and caching
- **Document Access Changes**: Handle permission errors gracefully
- **Search Quality**: Continuous improvement of ranking algorithms
- **Index Corruption**: Regular backups and recovery procedures

### 12.2 Operational Risks
- **Credential Management**: Secure storage and rotation of API keys
- **Data Privacy**: Ensure compliance with organizational policies
- **Service Dependencies**: Plan for Google API outages
- **Resource Usage**: Monitor and limit computational costs

## 13. Success Metrics

### 13.1 Functional Metrics
- **Search Accuracy**: Relevance of top-10 results for test queries
- **Coverage**: Percentage of documents successfully indexed
- **Availability**: Uptime and response rate of MCP server

### 13.2 Performance Metrics
- **Query Response Time**: P95 latency under 500ms
- **Index Freshness**: Documents updated within 1 hour of changes
- **Resource Utilization**: CPU and memory usage within targets

### 13.3 User Experience Metrics
- **Search Success Rate**: Queries returning relevant results
- **User Adoption**: Number of active AI client sessions
- **Query Patterns**: Analysis of common search patterns for optimization

---

*This technical design document serves as the foundation for implementing the Google Drive Escalation Search MCP Server. It should be reviewed and updated as requirements evolve during development.*