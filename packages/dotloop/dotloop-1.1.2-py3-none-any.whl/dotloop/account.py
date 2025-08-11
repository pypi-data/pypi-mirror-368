"""Account client for the Dotloop API wrapper."""

from typing import Any, Dict

from .base_client import BaseClient


class AccountClient(BaseClient):
    """Client for account API endpoints."""

    def get_account(self) -> Dict[str, Any]:
        """Retrieve the current account details.

        Returns:
            Dictionary containing account information

        Raises:
            DotloopError: If the API request fails

        Example:
            ```python
            account = client.account.get_account()
            print(f"Account ID: {account['data']['id']}")
            print(
                f"Name: {account['data']['firstName']} "
                f"{account['data']['lastName']}"
            )
            ```
        """
        return self.get("/account")
