"""Base connector interface for document sources."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..models.document import Document, DocumentType
from ..models.search import DocumentMatch


@dataclass
class AuthConfig:
    """Authentication configuration for connectors."""

    type: str  # 'oauth2' | 'api_key' | 'basic' | 'custom'
    credentials: dict[str, str]
    scopes: list[str] | None = None

    def get_credential(self, key: str, default: str | None = None) -> str | None:
        """Get a credential value by key."""
        return self.credentials.get(key, default)


@dataclass
class ConnectorConfig:
    """Configuration for a document connector."""

    name: str
    enabled: bool
    settings: dict[str, Any]
    auth_config: AuthConfig

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key."""
        return self.settings.get(key, default)


class DocumentConnector(ABC):
    """Abstract base class for document connectors."""

    def __init__(self, connector_id: str, name: str, supported_types: list[DocumentType]):
        """Initialize the connector.

        Args:
            connector_id: Unique identifier for this connector
            name: Human-readable name for this connector
            supported_types: List of document types this connector supports
        """
        self.id = connector_id
        self.name = name
        self.supported_types = supported_types
        self._config: ConnectorConfig | None = None
        self._authenticated = False

    @property
    def config(self) -> ConnectorConfig | None:
        """Get the current configuration."""
        return self._config

    @property
    def is_authenticated(self) -> bool:
        """Check if the connector is authenticated."""
        return self._authenticated

    @abstractmethod
    async def initialize(self, config: ConnectorConfig) -> None:
        """Initialize the connector with configuration.

        Args:
            config: Connector configuration including auth and settings

        Raises:
            ConnectionError: If initialization fails
            ValueError: If configuration is invalid
        """
        self._config = config

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the document source.

        Returns:
            True if authentication successful, False otherwise

        Raises:
            AuthenticationError: If authentication fails with error details
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up and disconnect from the source.

        Should close any open connections and clean up resources.
        """
        self._authenticated = False

    @abstractmethod
    def get_documents(self, options: dict[str, Any] | None = None) -> AsyncIterator[Document]:
        """Get all documents from the source.

        Args:
            options: Optional parameters for document retrieval

        Yields:
            Document objects from the source

        Raises:
            ConnectionError: If connection to source fails
            PermissionError: If access is denied to documents
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Document:
        """Get a specific document by ID.

        Args:
            document_id: Source-specific document identifier

        Returns:
            The requested document

        Raises:
            DocumentNotFoundError: If document doesn't exist
            PermissionError: If access is denied to document
        """
        pass

    @abstractmethod
    async def search_documents(
        self, query: str, options: dict[str, Any] | None = None
    ) -> list[DocumentMatch]:
        """Search documents in this source.

        Args:
            query: Search query string
            options: Optional search parameters and filters

        Returns:
            List of matching documents with relevance scores

        Raises:
            SearchError: If search operation fails
        """
        pass

    @abstractmethod
    async def get_last_sync_time(self) -> datetime | None:
        """Get the last synchronization timestamp.

        Returns:
            Timestamp of last sync, or None if never synced
        """
        pass

    @abstractmethod
    async def set_last_sync_time(self, timestamp: datetime) -> None:
        """Set the last synchronization timestamp.

        Args:
            timestamp: Timestamp to record as last sync time
        """
        pass

    async def health_check(self) -> dict[str, Any]:
        """Perform a health check on the connector.

        Returns:
            Health status information including connectivity and auth status
        """
        try:
            if not self.is_authenticated:
                await self.authenticate()

            # Basic connectivity test - try to get a small batch of documents
            count = 0
            async for _ in self.get_documents({"limit": 1}):
                count += 1
                break

            return {
                "status": "healthy",
                "authenticated": self.is_authenticated,
                "connector_id": self.id,
                "name": self.name,
                "supported_types": [dt.value for dt in self.supported_types],
                "last_check": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "authenticated": self.is_authenticated,
                "connector_id": self.id,
                "name": self.name,
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }


class ConnectorError(Exception):
    """Base exception for connector errors."""

    pass


class AuthenticationError(ConnectorError):
    """Authentication failed."""

    pass


class DocumentNotFoundError(ConnectorError):
    """Document not found."""

    pass


class SearchError(ConnectorError):
    """Search operation failed."""

    pass
