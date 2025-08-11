"""Folder client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class FolderClient(BaseClient):
    """Client for folder API endpoints."""

    def list_folders(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """List all folders in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing list of folders with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            folders = client.folder.list_folders(profile_id=123, loop_id=456)
            for folder in folders['data']:
                print(f"Folder: {folder['name']} (ID: {folder['id']})")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop/{loop_id}/folder")

    def get_folder(
        self, profile_id: int, loop_id: int, folder_id: int
    ) -> Dict[str, Any]:
        """Retrieve an individual folder by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            folder_id: ID of the folder to retrieve

        Returns:
            Dictionary containing folder information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the folder is not found

        Example:
            ```python
            folder = client.folder.get_folder(
                profile_id=123,
                loop_id=456,
                folder_id=789
            )
            print(f"Folder: {folder['data']['name']}")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop/{loop_id}/folder/{folder_id}")

    def create_folder(
        self,
        profile_id: int,
        loop_id: int,
        name: str,
    ) -> Dict[str, Any]:
        """Create a new folder in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            name: Name of the folder

        Returns:
            Dictionary containing created folder information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            folder = client.folder.create_folder(
                profile_id=123,
                loop_id=456,
                name="Inspection Documents"
            )
            print(f"Created folder: {folder['data']['name']}")
            ```
        """
        data: Dict[str, Any] = {"name": name}
        return self.post(f"/profile/{profile_id}/loop/{loop_id}/folder", data=data)

    def update_folder(
        self,
        profile_id: int,
        loop_id: int,
        folder_id: int,
        name: str,
    ) -> Dict[str, Any]:
        """Update an existing folder by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            folder_id: ID of the folder to update
            name: New name for the folder

        Returns:
            Dictionary containing updated folder information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the folder is not found
            ValidationError: If parameters are invalid

        Example:
            ```python
            folder = client.folder.update_folder(
                profile_id=123,
                loop_id=456,
                folder_id=789,
                name="Updated Folder Name"
            )
            ```
        """
        data: Dict[str, Any] = {"name": name}
        return self.patch(
            f"/profile/{profile_id}/loop/{loop_id}/folder/{folder_id}", data=data
        )
