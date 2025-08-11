"""Contact client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class ContactClient(BaseClient):
    """Client for contact API endpoints."""

    def list_contacts(self) -> Dict[str, Any]:
        """List all contacts.

        Returns:
            Dictionary containing list of contacts with metadata

        Raises:
            DotloopError: If the API request fails

        Example:
            ```python
            contacts = client.contact.list_contacts()
            for contact in contacts['data']:
                print(f"Contact: {contact['name']} (ID: {contact['id']})")
            ```
        """
        return self.get("/contact")

    def get_contact(self, contact_id: int) -> Dict[str, Any]:
        """Retrieve an individual contact by ID.

        Args:
            contact_id: ID of the contact to retrieve

        Returns:
            Dictionary containing contact information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the contact is not found

        Example:
            ```python
            contact = client.contact.get_contact(123)
            print(f"Contact: {contact['data']['name']}")
            ```
        """
        return self.get(f"/contact/{contact_id}")

    def create_contact(
        self,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new contact.

        Args:
            first_name: First name
            last_name: Last name
            email: Email address
            phone: Phone number
            company: Company name
            address: Address line
            city: City
            state: State
            zip_code: ZIP code
            country: Country

        Returns:
            Dictionary containing created contact information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            contact = client.contact.create_contact(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="+1 (555) 123-4567",
                company="Real Estate Co"
            )
            ```
        """
        data: Dict[str, Any] = {
            "firstName": first_name,
            "lastName": last_name,
        }

        if email is not None:
            data["email"] = email
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

        return self.post("/contact", data=data)

    def update_contact(
        self,
        contact_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing contact by ID.

        Args:
            contact_id: ID of the contact to update
            first_name: First name
            last_name: Last name
            email: Email address
            phone: Phone number
            company: Company name
            address: Address line
            city: City
            state: State
            zip_code: ZIP code
            country: Country

        Returns:
            Dictionary containing updated contact information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the contact is not found
            ValidationError: If parameters are invalid

        Example:
            ```python
            contact = client.contact.update_contact(
                contact_id=123,
                email="newemail@example.com",
                phone="+1 (555) 987-6543"
            )
            ```
        """
        data: Dict[str, Any] = {}

        if first_name is not None:
            data["firstName"] = first_name
        if last_name is not None:
            data["lastName"] = last_name
        if email is not None:
            data["email"] = email
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

        return self.patch(f"/contact/{contact_id}", data=data)

    def delete_contact(self, contact_id: int) -> Dict[str, Any]:
        """Delete a contact by ID.

        Args:
            contact_id: ID of the contact to delete

        Returns:
            Dictionary containing deletion confirmation

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the contact is not found

        Example:
            ```python
            result = client.contact.delete_contact(123)
            ```
        """
        return self.delete(f"/contact/{contact_id}")
