"""Loop client for the Dotloop API wrapper."""

from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient
from .enums import LoopSortCategory, LoopStatus, SortDirection, TransactionType


class LoopClient(BaseClient):
    """Client for loop API endpoints."""

    def list_loops(
        self,
        profile_id: int,
        batch_size: Optional[int] = None,
        batch_number: Optional[int] = None,
        sort: Optional[str] = None,
        filter_params: Optional[str] = None,
        include_details: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """List all loops associated with a profile.

        Args:
            profile_id: ID of the profile
            batch_size: Size of batch returned (default=20, max=100)
            batch_number: Batch/page number (default=1)
            sort: Sort category and direction (e.g., 'address:asc')
            filter_params: Filter string (e.g., 'updated_min=timestamp')
            include_details: Flag to include loop details with each record

        Returns:
            Dictionary containing list of loops with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            loops = client.loop.list_loops(
                profile_id=123,
                batch_size=50,
                sort="updated:desc",
                include_details=True
            )
            for loop in loops['data']:
                print(f"Loop: {loop['name']} (ID: {loop['id']})")
            ```
        """
        params: Dict[str, Any] = {}

        if batch_size is not None:
            params["batch_size"] = batch_size
        if batch_number is not None:
            params["batch_number"] = batch_number
        if sort is not None:
            params["sort"] = sort
        if filter_params is not None:
            params["filter"] = filter_params
        if include_details is not None:
            params["include_details"] = include_details

        return self.get(f"/profile/{profile_id}/loop", params=params)

    def get_loop(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """Retrieve an individual loop by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop to retrieve

        Returns:
            Dictionary containing loop information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found
            RedirectError: If the loop has been merged (301 redirect)

        Example:
            ```python
            loop = client.loop.get_loop(profile_id=123, loop_id=456)
            print(f"Loop: {loop['data']['name']}")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop/{loop_id}")

    def create_loop(
        self,
        profile_id: int,
        name: str,
        status: Union[LoopStatus, str],
        transaction_type: Union[TransactionType, str],
    ) -> Dict[str, Any]:
        """Create a new loop.

        Args:
            profile_id: ID of the profile
            name: Name of the loop (max 200 chars)
            status: Status of the loop
            transaction_type: Type of transaction

        Returns:
            Dictionary containing created loop information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            loop = client.loop.create_loop(
                profile_id=123,
                name="New Property Deal",
                status=LoopStatus.PRE_OFFER,
                transaction_type=TransactionType.PURCHASE_OFFER
            )
            ```
        """
        # Convert enums to strings
        if isinstance(status, LoopStatus):
            status = status.value
        if isinstance(transaction_type, TransactionType):
            transaction_type = transaction_type.value

        data: Dict[str, Any] = {
            "name": name,
            "status": status,
            "transactionType": transaction_type,
        }

        return self.post(f"/profile/{profile_id}/loop", data=data)

    def update_loop(
        self,
        profile_id: int,
        loop_id: int,
        name: Optional[str] = None,
        status: Optional[Union[LoopStatus, str]] = None,
        transaction_type: Optional[Union[TransactionType, str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing loop by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop to update
            name: Name of the loop (max 200 chars)
            status: Status of the loop
            transaction_type: Type of transaction

        Returns:
            Dictionary containing updated loop information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found
            ValidationError: If parameters are invalid

        Example:
            ```python
            loop = client.loop.update_loop(
                profile_id=123,
                loop_id=456,
                status=LoopStatus.SOLD
            )
            ```
        """
        data: Dict[str, Any] = {}

        if name is not None:
            data["name"] = name
        if status is not None:
            if isinstance(status, LoopStatus):
                data["status"] = status.value
            else:
                data["status"] = status
        if transaction_type is not None:
            if isinstance(transaction_type, TransactionType):
                data["transactionType"] = transaction_type.value
            else:
                data["transactionType"] = transaction_type

        return self.patch(f"/profile/{profile_id}/loop/{loop_id}", data=data)
