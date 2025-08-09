"""Search models for queries, filters, and results."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .document import Document, DocumentType


@dataclass
class DateRange:
    """Date range for filtering."""

    start: datetime
    end: datetime


@dataclass
class BaseSearchFilters:
    """Core search filters applicable to all document sources."""

    authors: list[str] | None = None
    tags: list[str] | None = None
    categories: list[str] | None = None
    date_range: DateRange | None = None
    created_by: list[str] | None = None
    last_modified_by: list[str] | None = None


@dataclass
class GoogleDriveFilters:
    """Google Drive specific search filters."""

    folder_ids: list[str] | None = None
    mime_types: list[str] | None = None
    drive_ids: list[str] | None = None  # Shared drive filters
    folder_paths: list[str] | None = None  # Path-based filtering
    sharing_permissions: list[str] | None = None  # e.g., ["public", "restricted"]


@dataclass
class ConfluenceFilters:
    """Confluence specific search filters."""

    space_keys: list[str] | None = None
    labels: list[str] | None = None
    parent_page_ids: list[str] | None = None
    content_types: list[str] | None = None  # e.g., ["page", "blogpost"]
    restrictions: list[str] | None = None  # Filter by restriction level


@dataclass
class SearchFilters:
    """Unified search filters with source-specific extensions."""

    # Core filters (always available)
    base: BaseSearchFilters | None = None

    # Source-specific filters
    google_drive: GoogleDriveFilters | None = None
    confluence: ConfluenceFilters | None = None

    # Plugin/domain-specific filters
    custom_filters: dict[str, Any] | None = field(default_factory=dict)

    def get_source_filters(self, source_type: str) -> Any | None:
        """Get source-specific filters by type."""
        return getattr(self, source_type, None)

    def add_custom_filter(self, key: str, value: Any) -> None:
        """Add a custom filter (typically used by plugins)."""
        if self.custom_filters is None:
            self.custom_filters = {}
        self.custom_filters[key] = value


@dataclass
class SearchQuery:
    """Search query with filters and options."""

    query: str  # Search terms
    sources: list[str] | None = None  # Filter by document sources
    document_types: list[DocumentType] | None = None  # Filter by document types
    filters: SearchFilters | None = None
    max_results: int = 10  # Default: 10
    semantic_search: bool = True  # Enable vector search
    source_weighting: dict[str, float] | None = None  # Weight results by source

    def to_dict(self) -> dict[str, Any]:
        """Convert search query to dictionary."""
        result: dict[str, Any] = {
            "query": self.query,
            "sources": self.sources,
            "document_types": [dt.value for dt in self.document_types]
            if self.document_types
            else None,
            "max_results": self.max_results,
            "semantic_search": self.semantic_search,
            "source_weighting": self.source_weighting,
        }

        if self.filters:
            filters_dict: dict[str, Any] = {}

            if self.filters.base:
                filters_dict["base"] = {
                    "authors": self.filters.base.authors,
                    "tags": self.filters.base.tags,
                    "categories": self.filters.base.categories,
                    "date_range": {
                        "start": self.filters.base.date_range.start.isoformat(),
                        "end": self.filters.base.date_range.end.isoformat(),
                    }
                    if self.filters.base.date_range
                    else None,
                    "created_by": self.filters.base.created_by,
                    "last_modified_by": self.filters.base.last_modified_by,
                }

            if self.filters.google_drive:
                filters_dict["google_drive"] = {
                    "folder_ids": self.filters.google_drive.folder_ids,
                    "mime_types": self.filters.google_drive.mime_types,
                    "drive_ids": self.filters.google_drive.drive_ids,
                    "folder_paths": self.filters.google_drive.folder_paths,
                    "sharing_permissions": self.filters.google_drive.sharing_permissions,
                }

            if self.filters.confluence:
                filters_dict["confluence"] = {
                    "space_keys": self.filters.confluence.space_keys,
                    "labels": self.filters.confluence.labels,
                    "parent_page_ids": self.filters.confluence.parent_page_ids,
                    "content_types": self.filters.confluence.content_types,
                    "restrictions": self.filters.confluence.restrictions,
                }

            if self.filters.custom_filters:
                filters_dict["custom_filters"] = self.filters.custom_filters

            result["filters"] = filters_dict

        return result


@dataclass
class TextMatch:
    """Matched text snippet with position information."""

    text: str  # Matched text snippet
    start_index: int  # Position in document
    end_index: int


@dataclass
class DocumentMatch:
    """Document match with relevance score and highlighted sections."""

    document: Document
    score: float  # Relevance score (0-1)
    matched_sections: list[TextMatch]  # Highlighted matching sections
    source_rank: int  # Rank within source


@dataclass
class SearchResult:
    """Search results with metadata."""

    documents: list[DocumentMatch]
    total_count: int
    search_time: float
    source_breakdown: dict[str, int]  # Count by source

    def to_dict(self) -> dict[str, Any]:
        """Convert search result to dictionary."""
        return {
            "documents": [
                {
                    "document": match.document.to_dict(),
                    "score": match.score,
                    "matched_sections": [
                        {
                            "text": section.text,
                            "start_index": section.start_index,
                            "end_index": section.end_index,
                        }
                        for section in match.matched_sections
                    ],
                    "source_rank": match.source_rank,
                }
                for match in self.documents
            ],
            "total_count": self.total_count,
            "search_time": self.search_time,
            "source_breakdown": self.source_breakdown,
        }
