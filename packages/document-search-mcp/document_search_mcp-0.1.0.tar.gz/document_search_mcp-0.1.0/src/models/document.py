"""Document models with source-specific metadata extensions."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DocumentType(Enum):
    """Document type enumeration."""

    GOOGLE_DOC = "google_doc"
    GOOGLE_SHEET = "google_sheet"
    GOOGLE_SLIDE = "google_slide"
    CONFLUENCE_PAGE = "confluence_page"
    CONFLUENCE_BLOG = "confluence_blog"


@dataclass
class DocumentSource:
    """Document source information."""

    type: str  # 'google_drive' | 'confluence' | 'custom'
    name: str  # Human-readable source name
    connector: str  # Connector identifier
    config: dict[str, Any] | None = None  # Source-specific configuration


@dataclass
class BaseDocumentMetadata:
    """Core metadata fields common to all document sources."""

    author: str | None = None  # Document author
    tags: list[str] | None = None  # Manual or auto-generated tags
    language: str | None = None  # Document language
    size: int | None = None  # Document size in bytes
    category: str | None = None  # Document category
    created_by: str | None = None  # Creator of the document
    last_modified_by: str | None = None  # Last person to modify the document


@dataclass
class GoogleDriveMetadata:
    """Google Drive specific metadata."""

    mime_type: str | None = None  # Google Drive MIME type
    parents: list[str] | None = None  # Parent folder IDs
    permissions: list[dict[str, Any]] | None = None
    drive_id: str | None = None  # Shared drive ID if applicable
    folder_path: str | None = None  # Full folder path
    sharing_settings: dict[str, Any] | None = None


@dataclass
class ConfluenceMetadata:
    """Confluence specific metadata."""

    space_key: str | None = None  # Confluence space
    page_id: str | None = None  # Confluence page ID
    version: int | None = None  # Page version
    labels: list[str] | None = None  # Confluence labels
    parent_page_id: str | None = None  # Parent page ID
    ancestors: list[dict[str, str]] | None = None  # Page hierarchy
    restrictions: dict[str, Any] | None = None  # View/edit restrictions


@dataclass
class DocumentMetadata:
    """Unified document metadata with source-specific extensions."""

    # Core metadata (always present)
    base: BaseDocumentMetadata

    # Source-specific metadata (populated based on document source)
    google_drive: GoogleDriveMetadata | None = None
    confluence: ConfluenceMetadata | None = None

    # Plugin/domain-specific metadata
    custom_fields: dict[str, Any] | None = field(default_factory=dict)
    schema_version: str | None = None  # Metadata schema version for compatibility

    def get_source_metadata(self, source_type: str) -> Any | None:
        """Get source-specific metadata by type."""
        return getattr(self, source_type, None)

    def add_custom_field(self, key: str, value: Any) -> None:
        """Add a custom field (typically used by plugins)."""
        if self.custom_fields is None:
            self.custom_fields = {}
        self.custom_fields[key] = value

    def get_custom_field(self, key: str, default: Any = None) -> Any:
        """Get a custom field value."""
        if self.custom_fields is None:
            return default
        return self.custom_fields.get(key, default)


@dataclass
class Document:
    """Unified document model."""

    id: str  # Unique document ID (source-specific)
    source_id: str  # Document source identifier
    source: DocumentSource  # Source information
    title: str  # Document title
    content: str  # Extracted text content
    url: str  # Document URL
    last_modified: datetime  # Last modification timestamp
    created_date: datetime  # Creation timestamp
    metadata: DocumentMetadata  # Source-specific and extracted metadata
    embedding: list[float] | None = None  # Vector representation
    type: DocumentType | None = None  # Document type classification

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source": {
                "type": self.source.type,
                "name": self.source.name,
                "connector": self.source.connector,
                "config": self.source.config,
            },
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "last_modified": self.last_modified.isoformat(),
            "created_date": self.created_date.isoformat(),
            "metadata": self._metadata_to_dict(),
            "embedding": self.embedding,
            "type": self.type.value if self.type else None,
        }

    def _metadata_to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        result = {
            "base": {
                "author": self.metadata.base.author,
                "tags": self.metadata.base.tags,
                "language": self.metadata.base.language,
                "size": self.metadata.base.size,
                "category": self.metadata.base.category,
                "created_by": self.metadata.base.created_by,
                "last_modified_by": self.metadata.base.last_modified_by,
            },
            "custom_fields": self.metadata.custom_fields,
            "schema_version": self.metadata.schema_version,
        }

        if self.metadata.google_drive:
            result["google_drive"] = {
                "mime_type": self.metadata.google_drive.mime_type,
                "parents": self.metadata.google_drive.parents,
                "permissions": self.metadata.google_drive.permissions,
                "drive_id": self.metadata.google_drive.drive_id,
                "folder_path": self.metadata.google_drive.folder_path,
                "sharing_settings": self.metadata.google_drive.sharing_settings,
            }

        if self.metadata.confluence:
            result["confluence"] = {
                "space_key": self.metadata.confluence.space_key,
                "page_id": self.metadata.confluence.page_id,
                "version": self.metadata.confluence.version,
                "labels": self.metadata.confluence.labels,
                "parent_page_id": self.metadata.confluence.parent_page_id,
                "ancestors": self.metadata.confluence.ancestors,
                "restrictions": self.metadata.confluence.restrictions,
            }

        return result
