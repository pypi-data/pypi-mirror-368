"""Document client for the Dotloop API wrapper."""

import io
from typing import Any, Dict, Optional, Union

from .base_client import BaseClient


class DocumentClient(BaseClient):
    """Client for document API endpoints.

    Notes:
        Dotloop API v2 scopes documents under folders. While historical root
        document endpoints exist, many accounts return 404 for loop-root
        document paths. Prefer folder-scoped methods. The legacy methods in
        this client accept an optional `folder_id` to route to the correct
        folder-scoped endpoints when provided.
    """

    def list_documents(
        self, profile_id: int, loop_id: int, folder_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """List documents in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            folder_id: ID of the folder to list documents from. If provided,
                the folder-scoped API is used and is recommended.

        Returns:
            Dictionary containing list of documents with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            documents = client.document.list_documents(profile_id=123, loop_id=456)
            for document in documents['data']:
                print(f"Document: {document['name']} (ID: {document['id']})")
            ```
        """
        if folder_id is not None:
            return self.get(
                f"/profile/{profile_id}/loop/{loop_id}/folder/{folder_id}/document"
            )

        # Legacy root listing (may 404 for many accounts)
        try:
            return self.get(f"/profile/{profile_id}/loop/{loop_id}/document")
        except Exception as exc:  # Keep behavior but improve guidance on 404
            from .exceptions import NotFoundError

            if isinstance(exc, NotFoundError):
                raise NotFoundError(
                    "Resource not found: Document listing at loop root returned 404. "
                    "Try using folder-scoped listing via folder_id or list_folders() first.",
                    status_code=exc.status_code,
                    response_data=exc.response_data,
                )
            raise  # pragma: no cover

    def get_document(
        self,
        profile_id: int,
        loop_id: int,
        document_id: int,
        folder_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Retrieve an individual document by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            document_id: ID of the document to retrieve
            folder_id: ID of the folder the document resides in. If provided,
                the folder-scoped API is used and is recommended.

        Returns:
            Dictionary containing document information including metadata and download URL

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the document is not found

        Example:
            ```python
            document = client.document.get_document(
                profile_id=123,
                loop_id=456,
                document_id=789
            )
            print(f"Document: {document['data']['name']}")
            print(f"Download URL: {document['data']['downloadUrl']}")
            ```
        """
        if folder_id is not None:
            return self.get(
                f"/profile/{profile_id}/loop/{loop_id}/folder/{folder_id}/document/{document_id}"
            )
        return self.get(f"/profile/{profile_id}/loop/{loop_id}/document/{document_id}")

    def list_documents_in_folder(
        self, profile_id: int, loop_id: int, folder_id: int
    ) -> Dict[str, Any]:
        """List all documents in a specific folder.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            folder_id: ID of the folder

        Returns:
            Dictionary containing list of documents with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the folder is not found

        Example:
            ```python
            documents = client.document.list_documents_in_folder(
                profile_id=123, loop_id=456, folder_id=789
            )
            ```
        """
        return self.list_documents(
            profile_id=profile_id, loop_id=loop_id, folder_id=folder_id
        )

    def get_document_in_folder(
        self, profile_id: int, loop_id: int, folder_id: int, document_id: int
    ) -> Dict[str, Any]:
        """Retrieve a document by ID within a specific folder.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            folder_id: ID of the folder
            document_id: ID of the document to retrieve

        Returns:
            Dictionary containing document information including metadata and download URL

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the document is not found

        Example:
            ```python
            document = client.document.get_document_in_folder(
                profile_id=123, loop_id=456, folder_id=789, document_id=111
            )
            ```
        """
        return self.get_document(
            profile_id=profile_id,
            loop_id=loop_id,
            document_id=document_id,
            folder_id=folder_id,
        )

    def upload_document(
        self,
        profile_id: int,
        loop_id: int,
        file_content: Union[bytes, io.IOBase],
        filename: str,
        folder_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a document to a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            file_content: File content as bytes or file-like object
            filename: Name of the file
            folder_id: ID of the folder to upload to (optional)
            description: Description of the document (optional)

        Returns:
            Dictionary containing uploaded document information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            # Upload from file
            with open("contract.pdf", "rb") as f:
                document = client.document.upload_document(
                    profile_id=123,
                    loop_id=456,
                    file_content=f.read(),
                    filename="contract.pdf",
                    description="Purchase contract"
                )

            # Upload to specific folder
            document = client.document.upload_document(
                profile_id=123,
                loop_id=456,
                file_content=file_bytes,
                filename="inspection_report.pdf",
                folder_id=789,
                description="Home inspection report"
            )
            ```
        """
        from urllib.parse import urljoin

        import requests

        # Build URL (prefer folder-scoped when folder_id provided)
        if folder_id is not None:
            url = self._build_url(
                f"/profile/{profile_id}/loop/{loop_id}/folder/{folder_id}/document"
            )
        else:
            url = self._build_url(f"/profile/{profile_id}/loop/{loop_id}/document")

        # Prepare headers (exclude Content-Type for multipart)
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }

        # Prepare form data
        files = {"file": (filename, file_content)}
        data = {}
        if description is not None:
            data["description"] = description

        try:
            response = requests.post(
                url, files=files, data=data, headers=headers, timeout=self._timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            from .exceptions import DotloopError

            raise DotloopError(f"Request failed: {str(e)}")

    def upload_document_to_folder(
        self,
        profile_id: int,
        loop_id: int,
        folder_id: int,
        file_content: Union[bytes, io.IOBase],
        filename: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a document to a specific folder in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            folder_id: ID of the folder to upload to
            file_content: File content as bytes or file-like object
            filename: Name of the file
            description: Description of the document (optional)

        Returns:
            Dictionary containing uploaded document information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            document = client.document.upload_document_to_folder(
                profile_id=123,
                loop_id=456,
                folder_id=789,
                file_content=file_bytes,
                filename="inspection_report.pdf",
            )
            ```
        """
        return self.upload_document(
            profile_id=profile_id,
            loop_id=loop_id,
            file_content=file_content,
            filename=filename,
            folder_id=folder_id,
            description=description,
        )

    def upload_document_from_file(
        self,
        profile_id: int,
        loop_id: int,
        file_path: str,
        folder_id: Optional[int] = None,
        description: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a document from a file path.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            file_path: Path to the file to upload
            folder_id: ID of the folder to upload to (optional)
            description: Description of the document (optional)
            filename: Custom filename (optional, defaults to file basename)

        Returns:
            Dictionary containing uploaded document information

        Raises:
            DotloopError: If the API request fails
            FileNotFoundError: If the file doesn't exist
            ValidationError: If parameters are invalid

        Example:
            ```python
            document = client.document.upload_document_from_file(
                profile_id=123,
                loop_id=456,
                file_path="/path/to/contract.pdf",
                description="Purchase contract"
            )
            ```
        """
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if filename is None:
            filename = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            return self.upload_document(
                profile_id=profile_id,
                loop_id=loop_id,
                file_content=f,
                filename=filename,
                folder_id=folder_id,
                description=description,
            )

    def download_document(
        self,
        profile_id: int,
        loop_id: int,
        document_id: int,
        folder_id: Optional[int] = None,
    ) -> bytes:
        """Download a document's content.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            document_id: ID of the document to download
            folder_id: ID of the folder the document resides in. If provided,
                the folder-scoped API is used to resolve the download URL.

        Returns:
            Document content as bytes

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the document is not found

        Example:
            ```python
            # Download document content
            content = client.document.download_document(
                profile_id=123,
                loop_id=456,
                document_id=789
            )

            # Save to file
            with open("downloaded_document.pdf", "wb") as f:
                f.write(content)
            ```
        """
        import requests

        # First get document info to get download URL
        document_info = self.get_document(
            profile_id=profile_id,
            loop_id=loop_id,
            document_id=document_id,
            folder_id=folder_id,
        )
        download_url = document_info["data"].get("downloadUrl")

        if not download_url:
            from .exceptions import DotloopError

            raise DotloopError("Document download URL not available")

        # Download the file content
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        try:
            response = requests.get(
                download_url, headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            from .exceptions import DotloopError

            raise DotloopError(f"Download failed: {str(e)}")

    def download_document_in_folder(
        self,
        profile_id: int,
        loop_id: int,
        folder_id: int,
        document_id: int,
    ) -> bytes:
        """Download a document that lives in a specific folder.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            folder_id: ID of the folder the document resides in
            document_id: ID of the document to download

        Returns:
            Document content as bytes

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the document is not found
        """
        return self.download_document(
            profile_id=profile_id,
            loop_id=loop_id,
            document_id=document_id,
            folder_id=folder_id,
        )

    def download_document_to_file(
        self,
        profile_id: int,
        loop_id: int,
        document_id: int,
        file_path: str,
        folder_id: Optional[int] = None,
    ) -> None:
        """Download a document and save it to a file.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            document_id: ID of the document to download
            file_path: Path where to save the downloaded file
            folder_id: ID of the folder the document resides in (optional)

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the document is not found

        Example:
            ```python
            client.document.download_document_to_file(
                profile_id=123,
                loop_id=456,
                document_id=789,
                file_path="/path/to/save/document.pdf"
            )
            ```
        """
        content = self.download_document(
            profile_id=profile_id,
            loop_id=loop_id,
            document_id=document_id,
            folder_id=folder_id,
        )

        with open(file_path, "wb") as f:
            f.write(content)

    def resolve_owner_profile_id(self, profile_id: int, loop_id: int) -> int:
        """Resolve the owner profile ID for a loop if provided by the API.

        Some loops require the owner's profileId when accessing folders/documents.
        This helper fetches the loop and returns `ownerProfileId` if present,
        otherwise falls back to the provided `profile_id`.

        Args:
            profile_id: Known profile ID context
            loop_id: Loop ID

        Returns:
            The resolved owner profile ID to use for folder/document access

        Raises:
            DotloopError: If the loop fetch fails
        """
        loop_info = self.get(f"/profile/{profile_id}/loop/{loop_id}")
        owner_id = loop_info.get("data", {}).get("ownerProfileId")
        return int(owner_id) if owner_id is not None else int(profile_id)
