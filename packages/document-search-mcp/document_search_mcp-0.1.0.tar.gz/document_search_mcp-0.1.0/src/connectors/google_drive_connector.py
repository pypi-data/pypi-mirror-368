"""Google Drive connector implementation."""

import json
import logging
import os
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..models.document import (
    BaseDocumentMetadata,
    Document,
    DocumentMetadata,
    DocumentSource,
    DocumentType,
    GoogleDriveMetadata,
)
from ..models.search import DocumentMatch, TextMatch
from .base_connector import (
    AuthenticationError,
    ConnectorConfig,
    ConnectorError,
    DocumentConnector,
    DocumentNotFoundError,
    SearchError,
)

logger = logging.getLogger(__name__)


class GoogleDriveConnector(DocumentConnector):
    """Google Drive connector for searching and retrieving documents."""

    _service: Any
    _credentials: Credentials | None
    _token_file: str | None

    def __init__(self) -> None:
        """Initialize the Google Drive connector."""
        super().__init__(
            connector_id="google_drive",
            name="Google Drive",
            supported_types=[
                DocumentType.GOOGLE_DOC,
                DocumentType.GOOGLE_SHEET,
                DocumentType.GOOGLE_SLIDE,
            ],
        )
        self._service = None
        self._credentials = None
        self._token_file = None

    async def initialize(self, config: ConnectorConfig) -> None:
        """Initialize the connector with configuration."""
        await super().initialize(config)

        # Setup token file path for storing OAuth tokens
        self._token_file = config.get_setting("token_file", "google_drive_token.json")

        # Validate required settings
        if config.auth_config.type == "oauth":
            # Check if we have client_id/secret directly or a credentials file
            has_direct_creds = config.auth_config.get_credential(
                "client_id"
            ) and config.auth_config.get_credential("client_secret")
            has_creds_file = config.auth_config.get_credential("credentials_file")

            if not has_direct_creds and not has_creds_file:
                raise ValueError(
                    "OAuth requires either client_id/client_secret or credentials_file"
                )
        elif config.auth_config.type == "service_account":
            if not config.auth_config.get_credential("service_account_key"):
                raise ValueError("Missing service account key file path")

    async def authenticate(self) -> bool:
        """Authenticate with Google Drive API."""
        try:
            if not self._config or not self._config.auth_config:
                raise AuthenticationError("No authentication configuration found")

            if self._config.auth_config.type == "oauth":
                return await self._authenticate_oauth()
            elif self._config.auth_config.type == "service_account":
                return await self._authenticate_service_account()
            else:
                raise AuthenticationError(f"Unsupported auth type: {self._config.auth_config.type}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")

    async def _authenticate_oauth(self) -> bool:
        """Authenticate using OAuth 2.0."""
        if not self._config or not self._config.auth_config:
            raise AuthenticationError("No authentication configuration found")

        scopes = self._config.auth_config.scopes or [
            "https://www.googleapis.com/auth/drive.readonly"
        ]

        # Get client credentials - either directly or from file
        client_id = self._config.auth_config.get_credential("client_id")
        client_secret = self._config.auth_config.get_credential("client_secret")
        credentials_file = self._config.auth_config.get_credential("credentials_file")

        if not client_id and credentials_file:
            # Load from credentials file
            if credentials_file and not os.path.exists(credentials_file):
                raise AuthenticationError(f"Credentials file not found: {credentials_file}")

            try:
                with open(credentials_file) as f:
                    creds_data = json.load(f)

                # Handle both installed app and web app credential formats
                if "installed" in creds_data:
                    client_config = creds_data["installed"]
                elif "web" in creds_data:
                    client_config = creds_data["web"]
                else:
                    raise AuthenticationError("Invalid credentials file format")

                client_id = client_config["client_id"]
                client_secret = client_config["client_secret"]

            except (json.JSONDecodeError, KeyError) as e:
                raise AuthenticationError(f"Failed to parse credentials file: {e}")

        # Try to load existing credentials
        if self._token_file and os.path.exists(self._token_file):
            try:
                self._credentials = Credentials.from_authorized_user_file(self._token_file, scopes)
                if self._credentials and self._credentials.valid:
                    self._service = build("drive", "v3", credentials=self._credentials)
                    self._authenticated = True
                    return True
                elif (
                    self._credentials
                    and self._credentials.expired
                    and self._credentials.refresh_token
                ):
                    self._credentials.refresh(Request())
                    self._save_credentials()
                    self._service = build("drive", "v3", credentials=self._credentials)
                    self._authenticated = True
                    return True
            except Exception as e:
                logger.warning(f"Failed to load existing credentials: {e}")

        # For MCP servers, we can't do interactive OAuth
        logger.error("OAuth authentication required but no valid token found.")
        logger.error("Please run: python authenticate_google_drive.py")

        raise AuthenticationError(
            "OAuth authentication required. Please run: python authenticate_google_drive.py"
        )

    async def _authenticate_service_account(self) -> bool:
        """Authenticate using service account."""
        from google.oauth2 import service_account

        if not self._config or not self._config.auth_config:
            raise AuthenticationError("No authentication configuration found")

        key_file = self._config.auth_config.get_credential("service_account_key")
        scopes = self._config.auth_config.scopes or [
            "https://www.googleapis.com/auth/drive.readonly"
        ]

        if key_file and not os.path.exists(key_file):
            raise AuthenticationError(f"Service account key file not found: {key_file}")

        self._credentials = service_account.Credentials.from_service_account_file(
            key_file, scopes=scopes
        )

        self._service = build("drive", "v3", credentials=self._credentials)
        self._authenticated = True
        return True

    def _save_credentials(self) -> None:
        """Save OAuth credentials to file."""
        if self._credentials and self._token_file:
            with open(self._token_file, "w") as token_file:
                token_file.write(self._credentials.to_json())

    async def disconnect(self) -> None:
        """Clean up and disconnect."""
        await super().disconnect()
        self._service = None
        self._credentials = None

    async def get_documents(self, options: dict[str, Any] | None = None) -> AsyncIterator[Document]:
        """Get all documents from configured folders."""
        if not self._authenticated or not self._service:
            await self.authenticate()

        options = options or {}
        limit = options.get("limit")

        if not self._config:
            return

        folder_ids = self._config.get_setting("folder_ids", [])

        if not folder_ids:
            # Search all accessible documents
            query = "trashed=false and (mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.spreadsheet' or mimeType='application/vnd.google-apps.presentation')"
        else:
            # Search within specific folders
            folder_queries = [f"'{folder_id}' in parents" for folder_id in folder_ids]
            folder_query = " or ".join(folder_queries)
            query = f"trashed=false and ({folder_query}) and (mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.spreadsheet' or mimeType='application/vnd.google-apps.presentation')"

        page_token = None
        count = 0

        while True:
            try:
                if not self._service:
                    await self.authenticate()
                    if not self._service:
                        return

                response = (
                    self._service.files()
                    .list(
                        q=query,
                        fields="nextPageToken, files(id, name, mimeType, modifiedTime, createdTime, owners, size, parents, webViewLink)",
                        pageToken=page_token,
                        pageSize=min(100, limit - count) if limit else 100,
                    )
                    .execute()
                )

                for file_item in response.get("files", []):
                    if limit and count >= limit:
                        return

                    document = await self._file_to_document(file_item)
                    if document:
                        yield document
                        count += 1

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            except HttpError as e:
                logger.error(f"Error retrieving documents: {e}")
                break

    async def get_document(self, document_id: str) -> Document:
        """Get a specific document by ID."""
        if not self._authenticated or not self._service:
            await self.authenticate()

        try:
            if not self._service:
                await self.authenticate()
                if not self._service:
                    raise ConnectorError(f"Failed to authenticate for document {document_id}")

            # Get file metadata
            file_item = (
                self._service.files()
                .get(
                    fileId=document_id,
                    fields="id, name, mimeType, modifiedTime, createdTime, owners, size, parents, webViewLink",
                )
                .execute()
            )

            document = await self._file_to_document(file_item)
            if not document:
                raise DocumentNotFoundError(f"Document {document_id} not found or unsupported type")

            return document

        except HttpError as e:
            if e.resp.status == 404:
                raise DocumentNotFoundError(f"Document {document_id} not found")
            else:
                raise SearchError(f"Error retrieving document {document_id}: {e}")

    async def search_documents(
        self, query: str, options: dict[str, Any] | None = None
    ) -> list[DocumentMatch]:
        """Search documents in Google Drive."""
        if not self._authenticated or not self._service:
            await self.authenticate()

        options = options or {}
        limit = options.get("limit", 50)

        if not self._config:
            return []

        folder_ids = self._config.get_setting("folder_ids", [])

        # Build search query
        search_query = f"fullText contains '{query}' and trashed=false"

        if folder_ids:
            folder_queries = [f"'{folder_id}' in parents" for folder_id in folder_ids]
            folder_query = " or ".join(folder_queries)
            search_query += f" and ({folder_query})"

        # Add document type filters
        search_query += " and (mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.spreadsheet' or mimeType='application/vnd.google-apps.presentation')"

        try:
            if not self._service:
                await self.authenticate()
                if not self._service:
                    return []

            response = (
                self._service.files()
                .list(
                    q=search_query,
                    fields="files(id, name, mimeType, modifiedTime, createdTime, owners, size, parents, webViewLink)",
                    pageSize=limit,
                )
                .execute()
            )

            matches = []
            for rank, file_item in enumerate(response.get("files", [])):
                document = await self._file_to_document(file_item)
                if document:
                    # Simple relevance scoring based on title match
                    score = 0.5  # Base score
                    if query.lower() in document.title.lower():
                        score += 0.3

                    # Create text matches for snippets
                    content_snippet = (
                        document.content[:200] + "..."
                        if len(document.content) > 200
                        else document.content
                    )
                    matched_sections = [
                        TextMatch(
                            text=content_snippet, start_index=0, end_index=len(content_snippet)
                        )
                    ]

                    matches.append(
                        DocumentMatch(
                            document=document,
                            score=score,
                            matched_sections=matched_sections,
                            source_rank=rank + 1,
                        )
                    )

            # Sort by relevance score
            matches.sort(key=lambda x: x.score, reverse=True)
            return matches

        except HttpError as e:
            logger.error(f"Search error: {e}")
            raise SearchError(f"Search failed: {e}")

    async def _file_to_document(self, file_item: dict[str, Any]) -> Document | None:
        """Convert Google Drive file item to Document object."""
        try:
            # Map MIME types to document types
            mime_type_map = {
                "application/vnd.google-apps.document": DocumentType.GOOGLE_DOC,
                "application/vnd.google-apps.spreadsheet": DocumentType.GOOGLE_SHEET,
                "application/vnd.google-apps.presentation": DocumentType.GOOGLE_SLIDE,
            }

            mime_type = file_item.get("mimeType")
            doc_type = mime_type_map.get(mime_type) if mime_type else None

            if not doc_type:
                return None

            # Extract content based on document type
            file_id = file_item.get("id")
            if not file_id or not mime_type:
                return None
            content = await self._extract_content(file_id, mime_type)

            # Create metadata
            owners = file_item.get("owners", [])
            author = owners[0].get("displayName") if owners else None

            base_metadata = BaseDocumentMetadata(
                author=author,
                size=int(file_item.get("size", 0)) if file_item.get("size") else None,
                created_by=author,
            )

            google_metadata = GoogleDriveMetadata(
                mime_type=mime_type,
                parents=file_item.get("parents", []),
                drive_id=file_item.get("driveId"),
            )

            metadata = DocumentMetadata(
                base=base_metadata,
                google_drive=google_metadata,
            )

            # Create document source
            source = DocumentSource(
                type="google_drive",
                name=self.name,
                connector=self.id,
            )

            return Document(
                id=file_item["id"],
                source_id=self.id,
                source=source,
                title=file_item["name"],
                content=content,
                url=file_item["webViewLink"],
                last_modified=datetime.fromisoformat(
                    file_item["modifiedTime"].replace("Z", "+00:00")
                ),
                created_date=datetime.fromisoformat(
                    file_item["createdTime"].replace("Z", "+00:00")
                ),
                metadata=metadata,
                type=doc_type,
            )

        except Exception as e:
            logger.error(f"Error converting file to document: {e}")
            return None

    async def _extract_content(self, file_id: str, mime_type: str) -> str:
        """Extract text content from Google Drive file."""
        try:
            if not self._service:
                await self.authenticate()
                if not self._service:
                    return ""

            if mime_type == "application/vnd.google-apps.document":
                # Export as plain text
                content = (
                    self._service.files().export(fileId=file_id, mimeType="text/plain").execute()
                )
                return str(content.decode("utf-8"))

            elif mime_type == "application/vnd.google-apps.spreadsheet":
                # Export as CSV for basic content extraction
                content = (
                    self._service.files().export(fileId=file_id, mimeType="text/csv").execute()
                )
                return str(content.decode("utf-8"))

            elif mime_type == "application/vnd.google-apps.presentation":
                # Export as plain text
                content = (
                    self._service.files().export(fileId=file_id, mimeType="text/plain").execute()
                )
                return str(content.decode("utf-8"))

            else:
                return ""

        except HttpError as e:
            logger.warning(f"Failed to extract content from {file_id}: {e}")
            return ""

    async def get_last_sync_time(self) -> datetime | None:
        """Get the last synchronization timestamp."""
        sync_file = f"{self.id}_last_sync.txt"
        if os.path.exists(sync_file):
            try:
                with open(sync_file) as f:
                    timestamp_str = f.read().strip()
                    return datetime.fromisoformat(timestamp_str)
            except Exception as e:
                logger.warning(f"Failed to read sync time: {e}")
        return None

    async def set_last_sync_time(self, timestamp: datetime) -> None:
        """Set the last synchronization timestamp."""
        sync_file = f"{self.id}_last_sync.txt"
        try:
            with open(sync_file, "w") as f:
                f.write(timestamp.isoformat())
        except Exception as e:
            logger.error(f"Failed to save sync time: {e}")
