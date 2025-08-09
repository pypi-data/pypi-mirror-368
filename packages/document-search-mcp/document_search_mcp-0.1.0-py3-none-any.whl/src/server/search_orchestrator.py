"""Search orchestrator that coordinates searches across multiple sources."""

import logging
from typing import Any

from ..connectors.base_connector import DocumentConnector
from ..models.document import Document
from ..models.search import DocumentMatch, SearchQuery, SearchResult

logger = logging.getLogger(__name__)


class SearchOrchestrator:
    """Orchestrates searches across multiple document sources."""

    def __init__(self) -> None:
        """Initialize the search orchestrator."""
        self.connectors: dict[str, DocumentConnector] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the search orchestrator and load connectors."""
        if self._initialized:
            return

        # TODO: Load connectors from configuration
        # For now, we'll have empty connectors dict
        logger.info("Search orchestrator initialized (no connectors configured)")
        self._initialized = True

    def register_connector(self, connector: DocumentConnector) -> None:
        """Register a document connector.

        Args:
            connector: The connector to register
        """
        self.connectors[connector.id] = connector
        logger.info(f"Registered connector: {connector.id} ({connector.name})")

    def unregister_connector(self, connector_id: str) -> None:
        """Unregister a document connector.

        Args:
            connector_id: ID of the connector to unregister
        """
        if connector_id in self.connectors:
            del self.connectors[connector_id]
            logger.info(f"Unregistered connector: {connector_id}")

    async def search(self, query: SearchQuery) -> SearchResult:
        """Execute a search across all or specified sources.

        Args:
            query: The search query with filters and options

        Returns:
            Aggregated search results from all sources
        """
        if not self._initialized:
            await self.initialize()

        # Determine which connectors to search
        target_connectors = self._get_target_connectors(query.sources)

        if not target_connectors:
            logger.warning("No connectors available for search")
            return SearchResult(documents=[], total_count=0, search_time=0.0, source_breakdown={})

        # Execute searches across connectors
        all_matches: list[DocumentMatch] = []
        source_breakdown: dict[str, int] = {}

        import time

        start_time = time.time()

        for connector in target_connectors:
            try:
                if not connector.is_authenticated:
                    await connector.authenticate()

                # Convert search query to connector-specific options
                options = self._build_search_options(query, connector.id)

                # Execute search on this connector
                matches = await connector.search_documents(query.query, options)

                # Add to results
                all_matches.extend(matches)
                source_breakdown[connector.id] = len(matches)

                logger.debug(f"Connector {connector.id} returned {len(matches)} matches")

            except Exception as e:
                logger.error(f"Search failed for connector {connector.id}: {e}")
                source_breakdown[connector.id] = 0

        search_time = time.time() - start_time

        # Sort and limit results
        all_matches.sort(key=lambda m: m.score, reverse=True)
        limited_matches = all_matches[: query.max_results]

        return SearchResult(
            documents=limited_matches,
            total_count=len(all_matches),
            search_time=search_time,
            source_breakdown=source_breakdown,
        )

    async def get_document(self, source_id: str, document_id: str) -> Document:
        """Get a specific document from a source.

        Args:
            source_id: The source connector ID
            document_id: The document ID within that source

        Returns:
            The requested document

        Raises:
            ValueError: If source is not found
            DocumentNotFoundError: If document is not found
        """
        if source_id not in self.connectors:
            raise ValueError(f"Unknown source: {source_id}")

        connector = self.connectors[source_id]

        if not connector.is_authenticated:
            await connector.authenticate()

        return await connector.get_document(document_id)

    async def list_sources(self, include_stats: bool = True) -> list[dict[str, Any]]:
        """List all configured sources with their status.

        Args:
            include_stats: Whether to include health and stats information

        Returns:
            List of source information dictionaries
        """
        sources = []

        for connector_id, connector in self.connectors.items():
            source_info = {
                "id": connector_id,
                "name": connector.name,
                "supported_types": [dt.value for dt in connector.supported_types],
                "enabled": connector.config.enabled if connector.config else False,
            }

            if include_stats:
                try:
                    health = await connector.health_check()
                    source_info.update(health)
                except Exception as e:
                    source_info.update({"status": "error", "error": str(e)})

            sources.append(source_info)

        return sources

    async def sync_source(self, source_id: str, force: bool = False) -> dict[str, Any]:
        """Trigger synchronization for a specific source.

        Args:
            source_id: The source connector ID to sync
            force: Whether to force a full re-sync

        Returns:
            Sync operation result

        Raises:
            ValueError: If source is not found
        """
        if source_id not in self.connectors:
            raise ValueError(f"Unknown source: {source_id}")

        connector = self.connectors[source_id]

        # TODO: Implement actual sync logic
        # For now, just return a placeholder response
        return {
            "source_id": source_id,
            "status": "completed",
            "message": f"Sync {'forced' if force else 'incremental'} for {connector.name}",
            "documents_processed": 0,  # Placeholder
        }

    async def get_configured_sources(self) -> dict[str, Any]:
        """Get configuration information for all sources.

        Returns:
            Dictionary of source configurations
        """
        configs = {}

        for connector_id, connector in self.connectors.items():
            if connector.config:
                configs[connector_id] = {
                    "name": connector.config.name,
                    "enabled": connector.config.enabled,
                    "auth_type": connector.config.auth_config.type,
                    "settings": connector.config.settings,
                }

        return configs

    async def get_index_status(self) -> dict[str, Any]:
        """Get status of search indices.

        Returns:
            Index status information
        """
        # TODO: Implement actual index status checking
        # For now, return placeholder data
        return {
            "total_documents": 0,
            "indices": {},
            "last_updated": None,
        }

    def _get_target_connectors(self, source_filter: list[str] | None) -> list[DocumentConnector]:
        """Get the list of connectors to search based on source filter.

        Args:
            source_filter: Optional list of source IDs to limit search to

        Returns:
            List of connectors to search
        """
        if source_filter:
            return [
                connector
                for connector_id, connector in self.connectors.items()
                if connector_id in source_filter and connector.config and connector.config.enabled
            ]
        else:
            return [
                connector
                for connector in self.connectors.values()
                if connector.config and connector.config.enabled
            ]

    def _build_search_options(self, query: SearchQuery, connector_id: str) -> dict[str, Any]:
        """Build connector-specific search options from search query.

        Args:
            query: The search query
            connector_id: The target connector ID

        Returns:
            Dictionary of search options for the connector
        """
        options: dict[str, Any] = {
            "max_results": query.max_results,
            "semantic_search": query.semantic_search,
        }

        if query.filters:
            # Add source-specific filters
            source_filters = query.filters.get_source_filters(connector_id)
            if source_filters:
                options["source_filters"] = source_filters

            # Add base filters
            if query.filters.base:
                options["base_filters"] = query.filters.base

            # Add custom filters
            if query.filters.custom_filters:
                options["custom_filters"] = query.filters.custom_filters

        if query.document_types:
            options["document_types"] = query.document_types

        return options
