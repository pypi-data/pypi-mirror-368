"""Profile client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class ProfileClient(BaseClient):
    """Client for profile API endpoints."""

    def list_profiles(self) -> Dict[str, Any]:
        """List all profiles associated with the user.

        Returns:
            Dictionary containing list of profiles with metadata

        Raises:
            DotloopError: If the API request fails

        Example:
            ```python
            profiles = client.profile.list_profiles()
            for profile in profiles['data']:
                print(f"Profile: {profile['name']} (ID: {profile['id']})")
            ```
        """
        return self.get("/profile")

    def get_profile(self, profile_id: int) -> Dict[str, Any]:
        """Retrieve an individual profile by ID.

        Args:
            profile_id: ID of the profile to retrieve

        Returns:
            Dictionary containing profile information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            profile = client.profile.get_profile(123)
            print(f"Profile: {profile['data']['name']}")
            ```
        """
        return self.get(f"/profile/{profile_id}")

    def create_profile(
        self,
        name: str,
        company: Optional[str] = None,
        phone: Optional[str] = None,
        fax: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new profile.

        Args:
            name: Profile name
            company: Company name
            phone: Phone number
            fax: Fax number
            address: Address line
            city: City
            state: State
            zip_code: ZIP code
            country: Country

        Returns:
            Dictionary containing created profile information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            profile = client.profile.create_profile(
                name="John Doe",
                company="Real Estate Co",
                phone="+1 (555) 123-4567",
                address="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001"
            )
            ```
        """
        data: Dict[str, Any] = {"name": name}

        if company is not None:
            data["company"] = company
        if phone is not None:
            data["phone"] = phone
        if fax is not None:
            data["fax"] = fax
        if address is not None:
            data["address"] = address
        if city is not None:
            data["city"] = city
        if state is not None:
            data["state"] = state
        if zip_code is not None:
            data["zipCode"] = zip_code
        if country is not None:
            data["country"] = country

        return self.post("/profile", data=data)

    def update_profile(
        self,
        profile_id: int,
        name: Optional[str] = None,
        company: Optional[str] = None,
        phone: Optional[str] = None,
        fax: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing profile by ID.

        Args:
            profile_id: ID of the profile to update
            name: Profile name
            company: Company name
            phone: Phone number
            fax: Fax number
            address: Address line
            city: City
            state: State
            zip_code: ZIP code
            country: Country

        Returns:
            Dictionary containing updated profile information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found
            ValidationError: If parameters are invalid

        Example:
            ```python
            profile = client.profile.update_profile(
                profile_id=123,
                name="John Smith",
                company="New Real Estate Co"
            )
            ```
        """
        data: Dict[str, Any] = {}

        if name is not None:
            data["name"] = name
        if company is not None:
            data["company"] = company
        if phone is not None:
            data["phone"] = phone
        if fax is not None:
            data["fax"] = fax
        if address is not None:
            data["address"] = address
        if city is not None:
            data["city"] = city
        if state is not None:
            data["state"] = state
        if zip_code is not None:
            data["zipCode"] = zip_code
        if country is not None:
            data["country"] = country

        return self.patch(f"/profile/{profile_id}", data=data)
