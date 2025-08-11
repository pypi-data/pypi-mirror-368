"""Participant client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional, Union

from .base_client import BaseClient
from .enums import ParticipantRole


class ParticipantClient(BaseClient):
    """Client for participant API endpoints."""

    def list_participants(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """List all participants in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing list of participants with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            participants = client.participant.list_participants(profile_id=123, loop_id=456)
            for participant in participants['data']:
                print(f"Participant: {participant['fullName']} ({participant['role']})")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop/{loop_id}/participant")

    def get_participant(
        self, profile_id: int, loop_id: int, participant_id: int
    ) -> Dict[str, Any]:
        """Retrieve an individual participant by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            participant_id: ID of the participant to retrieve

        Returns:
            Dictionary containing participant information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the participant is not found

        Example:
            ```python
            participant = client.participant.get_participant(
                profile_id=123,
                loop_id=456,
                participant_id=789
            )
            print(f"Participant: {participant['data']['fullName']}")
            ```
        """
        return self.get(
            f"/profile/{profile_id}/loop/{loop_id}/participant/{participant_id}"
        )

    def add_participant(
        self,
        profile_id: int,
        loop_id: int,
        full_name: str,
        email: str,
        role: Union[ParticipantRole, str],
        phone: Optional[str] = None,
        company: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new participant to a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            full_name: Full name of the participant
            email: Email address
            role: Role of the participant in the transaction
            phone: Phone number
            company: Company name
            address: Address line
            city: City
            state: State
            zip_code: ZIP code
            country: Country

        Returns:
            Dictionary containing created participant information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            participant = client.participant.add_participant(
                profile_id=123,
                loop_id=456,
                full_name="John Doe",
                email="john@example.com",
                role=ParticipantRole.BUYER,
                phone="+1 (555) 123-4567",
                company="ABC Corp"
            )
            ```
        """
        # Convert enum to string
        if isinstance(role, ParticipantRole):
            role = role.value

        data: Dict[str, Any] = {
            "fullName": full_name,
            "email": email,
            "role": role,
        }

        if phone is not None:
            data["phone"] = phone
        if company is not None:
            data["company"] = company
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

        return self.post(f"/profile/{profile_id}/loop/{loop_id}/participant", data=data)

    def update_participant(
        self,
        profile_id: int,
        loop_id: int,
        participant_id: int,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[Union[ParticipantRole, str]] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing participant by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            participant_id: ID of the participant to update
            full_name: Full name of the participant
            email: Email address
            role: Role of the participant in the transaction
            phone: Phone number
            company: Company name
            address: Address line
            city: City
            state: State
            zip_code: ZIP code
            country: Country

        Returns:
            Dictionary containing updated participant information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the participant is not found
            ValidationError: If parameters are invalid

        Example:
            ```python
            participant = client.participant.update_participant(
                profile_id=123,
                loop_id=456,
                participant_id=789,
                phone="+1 (555) 987-6543",
                company="New Company Name"
            )
            ```
        """
        data: Dict[str, Any] = {}

        if full_name is not None:
            data["fullName"] = full_name
        if email is not None:
            data["email"] = email
        if role is not None:
            if isinstance(role, ParticipantRole):
                data["role"] = role.value
            else:
                data["role"] = role
        if phone is not None:
            data["phone"] = phone
        if company is not None:
            data["company"] = company
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

        return self.patch(
            f"/profile/{profile_id}/loop/{loop_id}/participant/{participant_id}",
            data=data,
        )

    def remove_participant(
        self, profile_id: int, loop_id: int, participant_id: int
    ) -> Dict[str, Any]:
        """Remove a participant from a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            participant_id: ID of the participant to remove

        Returns:
            Dictionary containing removal confirmation

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the participant is not found

        Example:
            ```python
            result = client.participant.remove_participant(
                profile_id=123,
                loop_id=456,
                participant_id=789
            )
            ```
        """
        return self.delete(
            f"/profile/{profile_id}/loop/{loop_id}/participant/{participant_id}"
        )

    def add_buyer(
        self,
        profile_id: int,
        loop_id: int,
        full_name: str,
        email: str,
        phone: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a buyer participant to a loop.

        Convenience method for adding a buyer with the BUYER role.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            full_name: Full name of the buyer
            email: Email address
            phone: Phone number
            company: Company name

        Returns:
            Dictionary containing created participant information

        Example:
            ```python
            buyer = client.participant.add_buyer(
                profile_id=123,
                loop_id=456,
                full_name="John Buyer",
                email="john.buyer@example.com",
                phone="+1 (555) 123-4567"
            )
            ```
        """
        return self.add_participant(
            profile_id=profile_id,
            loop_id=loop_id,
            full_name=full_name,
            email=email,
            role=ParticipantRole.BUYER,
            phone=phone,
            company=company,
        )

    def add_seller(
        self,
        profile_id: int,
        loop_id: int,
        full_name: str,
        email: str,
        phone: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a seller participant to a loop.

        Convenience method for adding a seller with the SELLER role.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            full_name: Full name of the seller
            email: Email address
            phone: Phone number
            company: Company name

        Returns:
            Dictionary containing created participant information

        Example:
            ```python
            seller = client.participant.add_seller(
                profile_id=123,
                loop_id=456,
                full_name="Jane Seller",
                email="jane.seller@example.com",
                phone="+1 (555) 987-6543"
            )
            ```
        """
        return self.add_participant(
            profile_id=profile_id,
            loop_id=loop_id,
            full_name=full_name,
            email=email,
            role=ParticipantRole.SELLER,
            phone=phone,
            company=company,
        )

    def add_agent(
        self,
        profile_id: int,
        loop_id: int,
        full_name: str,
        email: str,
        role: Union[ParticipantRole, str],
        phone: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add an agent participant to a loop.

        Convenience method for adding agents (listing or buying agent).

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            full_name: Full name of the agent
            email: Email address
            role: Agent role (LISTING_AGENT, BUYING_AGENT, or AGENT)
            phone: Phone number
            company: Company name

        Returns:
            Dictionary containing created participant information

        Example:
            ```python
            agent = client.participant.add_agent(
                profile_id=123,
                loop_id=456,
                full_name="Bob Agent",
                email="bob.agent@realty.com",
                role=ParticipantRole.LISTING_AGENT,
                phone="+1 (555) 555-5555",
                company="ABC Realty"
            )
            ```
        """
        return self.add_participant(
            profile_id=profile_id,
            loop_id=loop_id,
            full_name=full_name,
            email=email,
            role=role,
            phone=phone,
            company=company,
        )
