"""Data models for the Document Search MCP Server."""

from .document import (
    BaseDocumentMetadata,
    ConfluenceMetadata,
    Document,
    DocumentMetadata,
    DocumentSource,
    DocumentType,
    GoogleDriveMetadata,
)
from .search import (
    BaseSearchFilters,
    ConfluenceFilters,
    DateRange,
    DocumentMatch,
    GoogleDriveFilters,
    SearchFilters,
    SearchQuery,
    SearchResult,
    TextMatch,
)

__all__ = [
    # Document models
    "BaseDocumentMetadata",
    "GoogleDriveMetadata",
    "ConfluenceMetadata",
    "DocumentMetadata",
    "DocumentSource",
    "DocumentType",
    "Document",
    # Search models
    "DateRange",
    "BaseSearchFilters",
    "GoogleDriveFilters",
    "ConfluenceFilters",
    "SearchFilters",
    "SearchQuery",
    "TextMatch",
    "DocumentMatch",
    "SearchResult",
]
