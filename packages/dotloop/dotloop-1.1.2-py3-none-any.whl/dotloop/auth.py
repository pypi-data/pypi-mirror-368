"""Authentication client for the Dotloop API wrapper."""

from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from .base_client import BaseClient


class AuthClient(BaseClient):
    """Client for OAuth authentication endpoints."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the AuthClient with OAuth credentials.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            api_key: API access token (optional for OAuth endpoints)
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

        # OAuth uses a different base URL
        if base_url is None:
            self._oauth_base_url = "https://auth.dotloop.com"
        else:
            self._oauth_base_url = base_url.replace(
                "api-gateway.dotloop.com", "auth.dotloop.com"
            )

    def get_authorization_url(
        self, scope: Optional[List[str]] = None, state: Optional[str] = None
    ) -> str:
        """Generate OAuth authorization URL.

        Args:
            scope: List of permission scopes to request
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL for user to visit

        Example:
            ```python
            auth_client = AuthClient(
                client_id="your_client_id",
                client_secret="your_client_secret",
                redirect_uri="https://yourapp.com/callback"
            )

            auth_url = auth_client.get_authorization_url(
                scope=["account", "profile", "loop"],
                state="random_state_string"
            )
            print(f"Visit: {auth_url}")
            ```
        """
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
        }

        if scope:
            params["scope"] = " ".join(scope)
        if state:
            params["state"] = state

        query_string = urlencode(params)
        return f"{self._oauth_base_url}/oauth/authorize?{query_string}"

    def exchange_code_for_token(
        self, authorization_code: str, grant_type: str = "authorization_code"
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            authorization_code: Authorization code received from callback
            grant_type: OAuth grant type (default: "authorization_code")

        Returns:
            Dictionary containing access token and refresh token

        Raises:
            DotloopError: If the token exchange fails
            ValidationError: If the authorization code is invalid

        Example:
            ```python
            # After user visits auth URL and you receive the code
            tokens = auth_client.exchange_code_for_token(
                authorization_code="received_auth_code"
            )

            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            expires_in = tokens['expires_in']
            ```
        """
        data = {
            "grant_type": grant_type,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "redirect_uri": self._redirect_uri,
            "code": authorization_code,
        }

        # Use OAuth base URL for token endpoint
        from urllib.parse import urljoin

        import requests

        url = urljoin(self._oauth_base_url, "/oauth/token")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                url, data=data, headers=headers, timeout=self._timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            from .exceptions import DotloopError

            raise DotloopError(f"Token exchange failed: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: Refresh token received during initial authorization

        Returns:
            Dictionary containing new access token and refresh token

        Raises:
            DotloopError: If the token refresh fails
            ValidationError: If the refresh token is invalid

        Example:
            ```python
            new_tokens = auth_client.refresh_access_token(
                refresh_token="your_refresh_token"
            )

            new_access_token = new_tokens['access_token']
            new_refresh_token = new_tokens['refresh_token']
            ```
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": refresh_token,
        }

        # Use OAuth base URL for token endpoint
        from urllib.parse import urljoin

        import requests

        url = urljoin(self._oauth_base_url, "/oauth/token")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                url, data=data, headers=headers, timeout=self._timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            from .exceptions import DotloopError

            raise DotloopError(f"Token refresh failed: {str(e)}")

    def revoke_token(
        self, token: str, token_type_hint: str = "access_token"
    ) -> Dict[str, Any]:
        """Revoke an access or refresh token.

        Args:
            token: Token to revoke (access_token or refresh_token)
            token_type_hint: Hint about token type ("access_token" or "refresh_token")

        Returns:
            Dictionary containing revocation confirmation

        Raises:
            DotloopError: If the token revocation fails

        Example:
            ```python
            # Revoke access token
            result = auth_client.revoke_token(
                token="access_token_to_revoke",
                token_type_hint="access_token"
            )

            # Revoke refresh token
            result = auth_client.revoke_token(
                token="refresh_token_to_revoke",
                token_type_hint="refresh_token"
            )
            ```
        """
        data = {
            "token": token,
            "token_type_hint": token_type_hint,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        # Use OAuth base URL for revoke endpoint
        from urllib.parse import urljoin

        import requests

        url = urljoin(self._oauth_base_url, "/oauth/token/revoke")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                url, data=data, headers=headers, timeout=self._timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            from .exceptions import DotloopError

            raise DotloopError(f"Token revocation failed: {str(e)}")

    def validate_token(self, access_token: str) -> Dict[str, Any]:
        """Validate an access token by making a test API call.

        Args:
            access_token: Access token to validate

        Returns:
            Dictionary containing validation result and token info

        Raises:
            DotloopError: If the token validation fails
            AuthenticationError: If the token is invalid

        Example:
            ```python
            validation = auth_client.validate_token("access_token_to_validate")

            if validation['valid']:
                print("Token is valid")
                print(f"Expires in: {validation['expires_in']} seconds")
            else:
                print("Token is invalid")
            ```
        """
        # Create a temporary client with the token to test
        from .account import AccountClient

        try:
            test_client = AccountClient(api_key=access_token, base_url=self._base_url)
            account_info = test_client.get_account()

            return {"valid": True, "account_info": account_info, "token": access_token}
        except Exception as e:
            return {"valid": False, "error": str(e), "token": access_token}

    def get_oauth_flow_helper(
        self, scope: Optional[List[str]] = None, state: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a complete OAuth flow helper with URLs and instructions.

        Args:
            scope: List of permission scopes to request
            state: Optional state parameter for CSRF protection

        Returns:
            Dictionary containing OAuth flow information and instructions

        Example:
            ```python
            oauth_flow = auth_client.get_oauth_flow_helper(
                scope=["account", "profile", "loop"],
                state="csrf_protection_string"
            )

            print("OAuth Flow Instructions:")
            print(f"1. Visit: {oauth_flow['authorization_url']}")
            print("2. User authorizes your application")
            print("3. User is redirected to your callback URL with authorization code")
            print("4. Exchange the code for tokens using exchange_code_for_token()")
            ```
        """
        auth_url = self.get_authorization_url(scope=scope, state=state)

        return {
            "authorization_url": auth_url,
            "redirect_uri": self._redirect_uri,
            "client_id": self._client_id,
            "scope": scope or [],
            "state": state,
            "instructions": [
                "1. Direct user to the authorization_url",
                "2. User authorizes your application",
                "3. User is redirected to redirect_uri with authorization code",
                "4. Extract 'code' parameter from callback URL",
                "5. Call exchange_code_for_token() with the authorization code",
                "6. Store the returned access_token and refresh_token",
                "7. Use access_token for API calls",
                "8. Use refresh_token to get new access_token when needed",
            ],
        }
