"""Base plugin interfaces for extensible functionality."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..models.document import Document, DocumentType
from ..models.search import SearchQuery, SearchResult


@dataclass
class PluginConfig:
    """Configuration for a plugin."""

    name: str
    enabled: bool
    settings: dict[str, Any]
    priority: int = 100  # Lower numbers = higher priority

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key."""
        return self.settings.get(key, default)


class MetadataEnhancer(ABC):
    """Plugin interface for extracting domain-specific metadata."""

    def __init__(self, config: PluginConfig):
        """Initialize the metadata enhancer.

        Args:
            config: Plugin configuration
        """
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def supported_document_types(self) -> list[DocumentType]:
        """Document types this enhancer supports."""
        pass

    @abstractmethod
    async def enhance_metadata(self, document: Document) -> dict[str, Any]:
        """Extract additional metadata from document.

        Args:
            document: The document to enhance

        Returns:
            Dictionary of custom metadata fields to add

        Raises:
            PluginError: If metadata enhancement fails
        """
        pass

    async def can_enhance(self, document: Document) -> bool:
        """Check if this enhancer can process the given document.

        Args:
            document: The document to check

        Returns:
            True if this enhancer can process the document
        """
        return (
            document.type in self.supported_document_types
            or not self.supported_document_types  # Empty list means all types supported
        )


class SearchEnhancer(ABC):
    """Plugin interface for enhancing search queries and results."""

    def __init__(self, config: PluginConfig):
        """Initialize the search enhancer.

        Args:
            config: Plugin configuration
        """
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @abstractmethod
    async def enhance_query(self, query: SearchQuery) -> SearchQuery:
        """Modify or enhance the search query.

        Args:
            query: The original search query

        Returns:
            Enhanced search query

        Raises:
            PluginError: If query enhancement fails
        """
        pass

    @abstractmethod
    async def enhance_results(
        self, results: SearchResult, original_query: SearchQuery
    ) -> SearchResult:
        """Post-process search results.

        Args:
            results: The search results to enhance
            original_query: The original search query

        Returns:
            Enhanced search results

        Raises:
            PluginError: If result enhancement fails
        """
        pass


class FilterProvider(ABC):
    """Plugin interface for providing custom filters."""

    def __init__(self, config: PluginConfig):
        """Initialize the filter provider.

        Args:
            config: Plugin configuration
        """
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def filter_schema(self) -> dict[str, Any]:
        """JSON schema for this filter's parameters.

        Returns:
            JSON schema dictionary defining the filter parameters
        """
        pass

    @abstractmethod
    async def apply_filter(
        self, documents: list[Document], filter_params: dict[str, Any]
    ) -> list[Document]:
        """Apply custom filtering logic.

        Args:
            documents: List of documents to filter
            filter_params: Filter parameters from the query

        Returns:
            Filtered list of documents

        Raises:
            PluginError: If filtering fails
        """
        pass

    async def validate_params(self, filter_params: dict[str, Any]) -> bool:
        """Validate filter parameters against the schema.

        Args:
            filter_params: Filter parameters to validate

        Returns:
            True if parameters are valid
        """
        # Basic validation - subclasses can override for more sophisticated validation
        required_keys = self._get_required_keys()
        return all(key in filter_params for key in required_keys)

    def _get_required_keys(self) -> list[str]:
        """Get required parameter keys from schema.

        Returns:
            List of required parameter keys
        """
        schema = self.filter_schema
        if "required" in schema:
            return list(schema["required"])
        return []


class PluginError(Exception):
    """Base exception for plugin errors."""

    def __init__(self, plugin_name: str, message: str, cause: Exception | None = None):
        """Initialize plugin error.

        Args:
            plugin_name: Name of the plugin that caused the error
            message: Error message
            cause: Original exception that caused this error
        """
        self.plugin_name = plugin_name
        self.cause = cause
        super().__init__(f"Plugin '{plugin_name}': {message}")


class PluginManager:
    """Manages loading and execution of plugins."""

    def __init__(self) -> None:
        """Initialize the plugin manager."""
        self.metadata_enhancers: list[MetadataEnhancer] = []
        self.search_enhancers: list[SearchEnhancer] = []
        self.filter_providers: list[FilterProvider] = []

    def register_metadata_enhancer(self, enhancer: MetadataEnhancer) -> None:
        """Register a metadata enhancer plugin.

        Args:
            enhancer: The metadata enhancer to register
        """
        self.metadata_enhancers.append(enhancer)
        # Sort by priority (lower numbers first)
        self.metadata_enhancers.sort(key=lambda e: e.config.priority)

    def register_search_enhancer(self, enhancer: SearchEnhancer) -> None:
        """Register a search enhancer plugin.

        Args:
            enhancer: The search enhancer to register
        """
        self.search_enhancers.append(enhancer)
        # Sort by priority (lower numbers first)
        self.search_enhancers.sort(key=lambda e: e.config.priority)

    def register_filter_provider(self, provider: FilterProvider) -> None:
        """Register a filter provider plugin.

        Args:
            provider: The filter provider to register
        """
        self.filter_providers.append(provider)
        # Sort by priority (lower numbers first)
        self.filter_providers.sort(key=lambda p: p.config.priority)

    async def enhance_document_metadata(self, document: Document) -> Document:
        """Run all applicable metadata enhancers on a document.

        Args:
            document: The document to enhance

        Returns:
            Document with enhanced metadata
        """
        enhanced_document = document

        for enhancer in self.metadata_enhancers:
            if not enhancer.config.enabled:
                continue

            try:
                if await enhancer.can_enhance(enhanced_document):
                    custom_metadata = await enhancer.enhance_metadata(enhanced_document)

                    # Add custom metadata to document
                    for key, value in custom_metadata.items():
                        enhanced_document.metadata.add_custom_field(key, value)

            except Exception as e:
                # Log error but continue with other enhancers
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Metadata enhancer {enhancer.name} failed: {e}")

        return enhanced_document

    async def enhance_search_query(self, query: SearchQuery) -> SearchQuery:
        """Run all search enhancers on a query.

        Args:
            query: The original search query

        Returns:
            Enhanced search query
        """
        enhanced_query = query

        for enhancer in self.search_enhancers:
            if not enhancer.config.enabled:
                continue

            try:
                enhanced_query = await enhancer.enhance_query(enhanced_query)
            except Exception as e:
                # Log error but continue with other enhancers
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Search enhancer {enhancer.name} failed: {e}")

        return enhanced_query

    async def enhance_search_results(
        self, results: SearchResult, original_query: SearchQuery
    ) -> SearchResult:
        """Run all search enhancers on results.

        Args:
            results: The search results to enhance
            original_query: The original search query

        Returns:
            Enhanced search results
        """
        enhanced_results = results

        for enhancer in self.search_enhancers:
            if not enhancer.config.enabled:
                continue

            try:
                enhanced_results = await enhancer.enhance_results(enhanced_results, original_query)
            except Exception as e:
                # Log error but continue with other enhancers
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Search enhancer {enhancer.name} failed: {e}")

        return enhanced_results

    async def apply_custom_filters(
        self, documents: list[Document], custom_filters: dict[str, Any]
    ) -> list[Document]:
        """Apply custom filters from filter providers.

        Args:
            documents: Documents to filter
            custom_filters: Custom filter parameters

        Returns:
            Filtered documents
        """
        filtered_documents = documents

        for provider in self.filter_providers:
            if not provider.config.enabled:
                continue

            # Check if this provider's filters are requested
            provider_filters = custom_filters.get(provider.name)
            if not provider_filters:
                continue

            try:
                if await provider.validate_params(provider_filters):
                    filtered_documents = await provider.apply_filter(
                        filtered_documents, provider_filters
                    )
            except Exception as e:
                # Log error but continue with other filters
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Filter provider {provider.name} failed: {e}")

        return filtered_documents

    def get_plugin_info(self) -> dict[str, Any]:
        """Get information about all registered plugins.

        Returns:
            Dictionary with plugin information
        """
        return {
            "metadata_enhancers": [
                {
                    "name": e.name,
                    "enabled": e.config.enabled,
                    "priority": e.config.priority,
                    "supported_types": [dt.value for dt in e.supported_document_types],
                }
                for e in self.metadata_enhancers
            ],
            "search_enhancers": [
                {
                    "name": e.name,
                    "enabled": e.config.enabled,
                    "priority": e.config.priority,
                }
                for e in self.search_enhancers
            ],
            "filter_providers": [
                {
                    "name": p.name,
                    "enabled": p.config.enabled,
                    "priority": p.config.priority,
                    "schema": p.filter_schema,
                }
                for p in self.filter_providers
            ],
        }
