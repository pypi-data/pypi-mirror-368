"""Loop-It client for the Dotloop API wrapper."""

from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient
from .enums import LoopStatus, ParticipantRole, TransactionType


class LoopItClient(BaseClient):
    """Client for Loop-It API endpoints."""

    def create_loop(
        self,
        name: str,
        transaction_type: Union[TransactionType, str],
        status: Union[LoopStatus, str],
        profile_id: Optional[int] = None,
        street_name: Optional[str] = None,
        street_number: Optional[str] = None,
        unit: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        county: Optional[str] = None,
        country: Optional[str] = None,
        participants: Optional[List[Dict[str, Any]]] = None,
        template_id: Optional[int] = None,
        mls_property_id: Optional[str] = None,
        mls_id: Optional[str] = None,
        mls_agent_id: Optional[str] = None,
        nrds_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new loop using the Loop-It API.

        This API makes it easy to create a new Loop and populate various details
        into the loop, including participant contact data, property information, etc.

        Args:
            name: Name of the loop (max 200 chars)
            transaction_type: Type of transaction
            status: Status of the loop
            profile_id: ID of the profile the loop will be created in
            street_name: Street name
            street_number: Street number
            unit: Unit number
            city: City
            state: State
            zip_code: ZIP code
            county: County
            country: Country
            participants: List of participant dictionaries with fullName, email, role
            template_id: Loop Template ID
            mls_property_id: MLS Property ID
            mls_id: MLS ID required to search listing
            mls_agent_id: MLS Agent ID
            nrds_id: NRDS ID

        Returns:
            Dictionary containing created loop information with loopUrl

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            loop = client.loop_it.create_loop(
                name="John Doe Property",
                transaction_type=TransactionType.PURCHASE_OFFER,
                status=LoopStatus.PRE_OFFER,
                street_number="123",
                street_name="Main St",
                city="San Francisco",
                state="CA",
                zip_code="94105",
                participants=[
                    {
                        "fullName": "John Doe",
                        "email": "john@example.com",
                        "role": "BUYER"
                    }
                ],
                profile_id=123
            )
            print(f"Loop created: {loop['data']['loopUrl']}")
            ```
        """
        # Convert enums to strings
        if isinstance(transaction_type, TransactionType):
            transaction_type = transaction_type.value
        if isinstance(status, LoopStatus):
            status = status.value

        data: Dict[str, Any] = {
            "name": name,
            "transactionType": transaction_type,
            "status": status,
        }

        # Add optional property information
        if street_name is not None:
            data["streetName"] = street_name
        if street_number is not None:
            data["streetNumber"] = street_number
        if unit is not None:
            data["unit"] = unit
        if city is not None:
            data["city"] = city
        if state is not None:
            data["state"] = state
        if zip_code is not None:
            data["zipCode"] = zip_code
        if county is not None:
            data["county"] = county
        if country is not None:
            data["country"] = country

        # Add participants
        if participants is not None:
            # Validate and convert participant roles if needed
            processed_participants = []
            for participant in participants:
                processed_participant = participant.copy()
                if "role" in processed_participant:
                    role = processed_participant["role"]
                    if isinstance(role, ParticipantRole):
                        processed_participant["role"] = role.value
                processed_participants.append(processed_participant)
            data["participants"] = processed_participants

        # Add optional template and MLS information
        if template_id is not None:
            data["templateId"] = template_id
        if mls_property_id is not None:
            data["mlsPropertyId"] = mls_property_id
        if mls_id is not None:
            data["mlsId"] = mls_id
        if mls_agent_id is not None:
            data["mlsAgentId"] = mls_agent_id
        if nrds_id is not None:
            data["nrdsId"] = nrds_id

        # Build query parameters
        params: Dict[str, Any] = {}
        if profile_id is not None:
            params["profile_id"] = profile_id

        return self.post("/loop-it", data=data, params=params)
