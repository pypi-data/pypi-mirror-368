"""Main MCP server implementation for document search."""

import json
import logging
import os
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

import yaml
from google_auth_oauthlib.flow import Flow
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)

from ..connectors.base_connector import AuthConfig, ConnectorConfig
from ..connectors.google_drive_connector import GoogleDriveConnector
from ..models.document import DocumentType
from ..models.search import (
    BaseSearchFilters,
    ConfluenceFilters,
    GoogleDriveFilters,
    SearchFilters,
    SearchQuery,
)
from .search_orchestrator import SearchOrchestrator

logger = logging.getLogger(__name__)


class DocumentSearchServer:
    """MCP server for document search."""

    def __init__(self, config_path: Path | None = None):
        """Initialize the document search server."""
        self.server = Server("document-search")
        self.search_orchestrator = SearchOrchestrator()
        self.config_path = config_path
        self.config: dict[str, Any] | None = None

        # Default paths for simplified setup
        self.token_file = Path.home() / ".config" / "document-search-mcp" / "token.json"
        self.config_file = Path.home() / ".config" / "document-search-mcp" / "config.yaml"

        # OAuth credentials (must be provided via environment variables)
        self.embedded_credentials = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }

        self._setup_handlers()

    def _is_configured(self) -> bool:
        """Check if the server is properly configured."""
        return self.token_file.exists() and self.config_file.exists()

    def _needs_setup(self) -> bool:
        """Check if setup is needed."""
        return not self._is_configured()

    def _extract_folder_id(self, url: str) -> str | None:
        """Extract folder ID from Google Drive folder URL."""
        patterns = [
            r"drive\.google\.com/drive/folders/([a-zA-Z0-9-_]+)",
            r"drive\.google\.com/drive/u/\d+/folders/([a-zA-Z0-9-_]+)",
            r"folders/([a-zA-Z0-9-_]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.server.list_tools()  # type: ignore[misc]
        async def list_tools() -> list[Tool]:
            """List available tools."""
            tools = []

            # If setup is needed, only show setup tools
            if self._needs_setup():
                tools.extend(
                    [
                        Tool(
                            name="setup_google_drive",
                            description="🔧 Set up Google Drive access (first-time setup required)",
                            inputSchema={
                                "type": "object",
                                "properties": {
                                    "step": {
                                        "type": "string",
                                        "enum": ["start", "complete"],
                                        "description": "Setup step: 'start' to get OAuth URL, 'complete' to finish with redirect URL",
                                    },
                                    "redirect_url": {
                                        "type": "string",
                                        "description": "Full redirect URL from browser (only for 'complete' step)",
                                    },
                                    "folder_urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Google Drive folder URLs to search (only for 'complete' step)",
                                        "default": [],
                                    },
                                },
                                "required": ["step"],
                            },
                        )
                    ]
                )
                return tools

            # Normal tools when configured
            tools.extend(
                [
                    Tool(
                        name="search_documents",
                        description="Search across all connected document sources",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query (keywords or natural language)",
                                },
                                "sources": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by specific document sources",
                                },
                                "document_types": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "google_doc",
                                            "google_sheet",
                                            "google_slide",
                                            "confluence_page",
                                            "confluence_blog",
                                        ],
                                    },
                                    "description": "Filter by document types",
                                },
                                "filters": {
                                    "type": "object",
                                    "properties": {
                                        "base": {
                                            "type": "object",
                                            "properties": {
                                                "authors": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "tags": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "categories": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "created_by": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "last_modified_by": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            },
                                        },
                                        "google_drive": {
                                            "type": "object",
                                            "properties": {
                                                "folder_ids": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "mime_types": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "drive_ids": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            },
                                        },
                                        "confluence": {
                                            "type": "object",
                                            "properties": {
                                                "space_keys": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "labels": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            },
                                        },
                                        "custom_filters": {
                                            "type": "object",
                                            "description": "Plugin-defined custom filters",
                                            "additionalProperties": True,
                                        },
                                    },
                                },
                                "max_results": {"type": "number", "default": 10, "maximum": 50},
                                "semantic_search": {"type": "boolean", "default": True},
                            },
                            "required": ["query"],
                        },
                    ),
                    Tool(
                        name="get_document_content",
                        description="Retrieve full content of a specific document from any source",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "document_id": {
                                    "type": "string",
                                    "description": "Document ID (source-specific)",
                                },
                                "source": {
                                    "type": "string",
                                    "description": "Document source identifier",
                                },
                                "include_metadata": {"type": "boolean", "default": True},
                                "format": {
                                    "type": "string",
                                    "enum": ["text", "markdown", "html"],
                                    "default": "text",
                                },
                            },
                            "required": ["document_id", "source"],
                        },
                    ),
                    Tool(
                        name="list_sources",
                        description="List all configured document sources and their status",
                        inputSchema={
                            "type": "object",
                            "properties": {"include_stats": {"type": "boolean", "default": True}},
                        },
                    ),
                    Tool(
                        name="sync_source",
                        description="Manually trigger synchronization for a specific document source",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "description": "Source identifier to synchronize",
                                },
                                "force": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Force full re-sync instead of incremental",
                                },
                            },
                            "required": ["source"],
                        },
                    ),
                ]
            )

            return tools

        @self.server.call_tool()  # type: ignore[misc]
        async def call_tool(name: str, arguments: dict[str, Any] | None) -> Sequence[TextContent]:
            """Handle tool calls."""
            try:
                if name == "setup_google_drive":
                    return await self._handle_setup_google_drive(arguments or {})
                elif name == "search_documents":
                    return await self._handle_search_documents(arguments or {})
                elif name == "get_document_content":
                    return await self._handle_get_document_content(arguments or {})
                elif name == "list_sources":
                    return await self._handle_list_sources(arguments or {})
                elif name == "sync_source":
                    return await self._handle_sync_source(arguments or {})
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

        @self.server.list_resources()  # type: ignore[misc]
        async def list_resources() -> list[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri=cast(Any, "sources://configured"),
                    name="Configured Document Sources",
                    description="List of all configured document sources and their configurations",
                    mimeType="application/json",
                ),
                Resource(
                    uri=cast(Any, "search://indices"),
                    name="Search Indices Status",
                    description="Status and statistics for all search indices across sources",
                    mimeType="application/json",
                ),
            ]

        @self.server.read_resource()  # type: ignore[misc]
        async def read_resource(uri: str) -> str:
            """Read a resource by URI."""
            try:
                if uri == "sources://configured":
                    sources = await self.search_orchestrator.get_configured_sources()
                    return json.dumps(sources, indent=2)
                elif uri == "search://indices":
                    indices = await self.search_orchestrator.get_index_status()
                    return json.dumps(indices, indent=2)
                else:
                    raise ValueError(f"Unknown resource: {uri}")
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": str(e)})

    async def _handle_setup_google_drive(self, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Handle setup_google_drive tool call."""
        step = arguments.get("step", "start")

        if step == "start":
            # Check if OAuth credentials are configured
            if (
                not self.embedded_credentials["client_id"]
                or not self.embedded_credentials["client_secret"]
            ):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "error": "OAuth credentials not configured",
                                "message": "This MCP server requires Google OAuth credentials to be set via environment variables.",
                                "setup_required": [
                                    "1. Create a Google Cloud Project at https://console.cloud.google.com",
                                    "2. Enable the Google Drive API",
                                    "3. Create OAuth 2.0 credentials (Desktop Application type)",
                                    "4. Set environment variables:",
                                    "   export GOOGLE_CLIENT_ID='your-client-id'",
                                    "   export GOOGLE_CLIENT_SECRET='your-client-secret'",
                                    "5. Restart the MCP server",
                                ],
                            },
                            indent=2,
                        ),
                    )
                ]

            # Generate OAuth URL
            flow_data = {"web": self.embedded_credentials}

            flow = Flow.from_client_config(
                flow_data, scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
            flow.redirect_uri = "http://localhost"

            auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

            result = {
                "step": "oauth_authorization",
                "message": "🔧 Google Drive Setup - Step 1 of 2",
                "instructions": [
                    "1. Click the OAuth URL below to authorize access to your Google Drive",
                    "2. Sign in with your Google account",
                    "3. Grant permission to access your Google Drive files",
                    "4. Copy the FULL redirect URL from your browser",
                    "5. Use the setup tool again with step='complete' and the redirect URL",
                ],
                "oauth_url": auth_url,
                "next_step": "Call setup_google_drive with step='complete' and your redirect_url",
            }

            # Store the flow state temporarily
            self._temp_flow = flow

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif step == "complete":
            redirect_url = arguments.get("redirect_url")
            folder_urls = arguments.get("folder_urls", [])

            if not redirect_url:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": "redirect_url is required for the 'complete' step"}, indent=2
                        ),
                    )
                ]

            try:
                # Parse authorization code from redirect URL
                parsed_url = urlparse(redirect_url)
                query_params = parse_qs(parsed_url.query)

                if "code" not in query_params:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {"error": "No authorization code found in redirect URL"}, indent=2
                            ),
                        )
                    ]

                auth_code = query_params["code"][0]

                # Complete OAuth flow
                if not hasattr(self, "_temp_flow"):
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "error": "OAuth flow not started. Please call setup with step='start' first."
                                },
                                indent=2,
                            ),
                        )
                    ]

                self._temp_flow.fetch_token(code=auth_code)
                credentials = self._temp_flow.credentials

                # Create config directory
                self.token_file.parent.mkdir(parents=True, exist_ok=True)
                self.config_file.parent.mkdir(parents=True, exist_ok=True)

                # Save token
                with open(self.token_file, "w") as f:
                    f.write(credentials.to_json())

                # Process folder URLs and create config
                folder_ids = []
                for url in folder_urls:
                    folder_id = self._extract_folder_id(url)
                    if folder_id:
                        folder_ids.append(folder_id)
                    else:
                        logger.warning(f"Could not extract folder ID from URL: {url}")

                config = {
                    "sources": {
                        "google_drive": {
                            "enabled": True,
                            "name": "Google Drive",
                            "auth": {"type": "oauth", "token_file": str(self.token_file)},
                            "settings": {"folder_ids": folder_ids if folder_ids else None},
                        }
                    }
                }

                # Save config
                with open(self.config_file, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)

                # Clean up temp flow
                delattr(self, "_temp_flow")

                result = {
                    "step": "completed",
                    "message": "🎉 Google Drive setup completed successfully!",
                    "summary": {
                        "token_saved": str(self.token_file),
                        "config_saved": str(self.config_file),
                        "folders_configured": len(folder_ids),
                        "folder_ids": folder_ids,
                    },
                    "next_steps": [
                        "Setup is complete! You can now use document search tools.",
                        "Try: search_documents with your query",
                        "The server will automatically restart to load the new configuration.",
                    ],
                }

                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                logger.error(f"Setup completion failed: {e}")
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": f"Setup failed: {str(e)}"}, indent=2)
                    )
                ]

        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"error": f"Unknown step: {step}. Use 'start' or 'complete'."}, indent=2
                    ),
                )
            ]

    async def _handle_search_documents(self, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Handle search_documents tool call."""
        query = arguments["query"]

        # Parse filters
        filters = None
        if "filters" in arguments:
            filter_data = arguments["filters"]
            filters = SearchFilters()

            if "base" in filter_data:
                base_data = filter_data["base"]
                filters.base = BaseSearchFilters(
                    authors=base_data.get("authors"),
                    tags=base_data.get("tags"),
                    categories=base_data.get("categories"),
                    created_by=base_data.get("created_by"),
                    last_modified_by=base_data.get("last_modified_by"),
                )

            if "google_drive" in filter_data:
                gd_data = filter_data["google_drive"]
                filters.google_drive = GoogleDriveFilters(
                    folder_ids=gd_data.get("folder_ids"),
                    mime_types=gd_data.get("mime_types"),
                    drive_ids=gd_data.get("drive_ids"),
                )

            if "confluence" in filter_data:
                conf_data = filter_data["confluence"]
                filters.confluence = ConfluenceFilters(
                    space_keys=conf_data.get("space_keys"),
                    labels=conf_data.get("labels"),
                )

            if "custom_filters" in filter_data:
                filters.custom_filters = filter_data["custom_filters"]

        # Parse document types
        document_types = None
        if "document_types" in arguments:
            document_types = [DocumentType(dt) for dt in arguments["document_types"]]

        # Create search query
        search_query = SearchQuery(
            query=query,
            sources=arguments.get("sources"),
            document_types=document_types,
            filters=filters,
            max_results=arguments.get("max_results", 10),
            semantic_search=arguments.get("semantic_search", True),
        )

        # Execute search
        result = await self.search_orchestrator.search(search_query)

        return [TextContent(type="text", text=json.dumps(result.to_dict(), indent=2))]

    async def _handle_get_document_content(
        self, arguments: dict[str, Any]
    ) -> Sequence[TextContent]:
        """Handle get_document_content tool call."""
        document_id = arguments["document_id"]
        source = arguments["source"]
        include_metadata = arguments.get("include_metadata", True)
        format_type = arguments.get("format", "text")

        document = await self.search_orchestrator.get_document(source, document_id)

        result = {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "url": document.url,
            "source": document.source.name,
            "format": format_type,
        }

        if include_metadata:
            result["metadata"] = document.to_dict()["metadata"]

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_list_sources(self, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Handle list_sources tool call."""
        include_stats = arguments.get("include_stats", True)
        sources = await self.search_orchestrator.list_sources(include_stats)
        return [TextContent(type="text", text=json.dumps({"sources": sources}, indent=2))]

    async def _handle_sync_source(self, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Handle sync_source tool call."""
        source = arguments["source"]
        force = arguments.get("force", False)

        result = await self.search_orchestrator.sync_source(source, force)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def load_config(self) -> None:
        """Load configuration and initialize connectors."""
        config_file = self.config_path or self.config_file

        if config_file and config_file.exists():
            try:
                with open(config_file) as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self.config = {}
        else:
            if self._needs_setup():
                logger.info("No configuration found - setup required")
                self.config = {}
                return
            else:
                logger.warning("No configuration file found, using defaults")
                self.config = {}

        # Initialize connectors from config
        await self._initialize_connectors()

    async def _initialize_connectors(self) -> None:
        """Initialize and register connectors from configuration."""
        sources = self.config.get("sources", {}) if self.config else {}

        # Initialize Google Drive connector if configured
        if "google_drive" in sources:
            gd_config = sources["google_drive"]
            if gd_config.get("enabled", False):
                try:
                    connector = GoogleDriveConnector()

                    # Create auth config
                    auth_data = gd_config.get("auth", {})

                    # Use the token file from auth config or default
                    token_file = auth_data.get("token_file", str(self.token_file))

                    # Prepare credentials - include environment variables if available
                    credentials = {"token_file": token_file}
                    if (
                        self.embedded_credentials["client_id"]
                        and self.embedded_credentials["client_secret"]
                    ):
                        credentials.update(
                            {
                                "client_id": self.embedded_credentials["client_id"],
                                "client_secret": self.embedded_credentials["client_secret"],
                            }
                        )

                    auth_config = AuthConfig(
                        type=auth_data.get("type", "oauth"),
                        credentials=credentials,
                        scopes=["https://www.googleapis.com/auth/drive.readonly"],
                    )

                    # Create connector config
                    connector_config = ConnectorConfig(
                        name=gd_config.get("name", "Google Drive"),
                        enabled=True,
                        settings=gd_config.get("settings", {}),
                        auth_config=auth_config,
                    )

                    # Initialize and register
                    await connector.initialize(connector_config)
                    self.search_orchestrator.register_connector(connector)

                    logger.info("Google Drive connector initialized and registered")

                except Exception as e:
                    logger.error(f"Failed to initialize Google Drive connector: {e}")

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting Document Search MCP Server")

        # Load configuration and initialize connectors
        await self.load_config()

        # Initialize search orchestrator
        await self.search_orchestrator.initialize()

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="document-search",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(), experimental_capabilities={}
                    ),
                ),
            )
