"""Loop detail client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class LoopDetailClient(BaseClient):
    """Client for loop detail API endpoints."""

    def get_loop_details(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """Retrieve loop details by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing detailed loop information including property address,
            financials, contract dates, and other loop-specific data

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            details = client.loop_detail.get_loop_details(
                profile_id=123,
                loop_id=456
            )

            # Access property information
            property_info = details['data']['Property Address']
            print(f"Address: {property_info['Street Number']} {property_info['Street Name']}")

            # Access financial information
            financials = details['data']['Financials']
            print(f"Sale Price: ${financials['Purchase/Sale Price']}")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop/{loop_id}/detail")

    def update_loop_details(
        self, profile_id: int, loop_id: int, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update loop details by ID.

        This API allows partial updates of loop details including property address,
        financials, contract dates, and other loop-specific information.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            details: Dictionary containing the detail sections to update

        Returns:
            Dictionary containing updated loop details

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found
            ValidationError: If the details format is invalid

        Example:
            ```python
            # Update property address
            updated_details = client.loop_detail.update_loop_details(
                profile_id=123,
                loop_id=456,
                details={
                    "Property Address": {
                        "Street Number": "456",
                        "Street Name": "Oak Avenue",
                        "City": "Los Angeles",
                        "State/Prov": "CA",
                        "Zip/Postal Code": "90210"
                    },
                    "Financials": {
                        "Purchase/Sale Price": "750000",
                        "Sale Commission Rate": "6"
                    }
                }
            )
            ```
        """
        return self.patch(f"/profile/{profile_id}/loop/{loop_id}/detail", data=details)

    def update_property_address(
        self,
        profile_id: int,
        loop_id: int,
        street_number: Optional[str] = None,
        street_name: Optional[str] = None,
        unit_number: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        county: Optional[str] = None,
        country: Optional[str] = None,
        mls_number: Optional[str] = None,
        parcel_tax_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update property address information for a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            street_number: Street number
            street_name: Street name
            unit_number: Unit number
            city: City
            state: State/Province
            zip_code: ZIP/Postal code
            county: County
            country: Country
            mls_number: MLS number
            parcel_tax_id: Parcel/Tax ID

        Returns:
            Dictionary containing updated loop details

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            updated_details = client.loop_detail.update_property_address(
                profile_id=123,
                loop_id=456,
                street_number="789",
                street_name="Pine Street",
                city="San Francisco",
                state="CA",
                zip_code="94105"
            )
            ```
        """
        property_address: Dict[str, str] = {}

        if street_number is not None:
            property_address["Street Number"] = street_number
        if street_name is not None:
            property_address["Street Name"] = street_name
        if unit_number is not None:
            property_address["Unit Number"] = unit_number
        if city is not None:
            property_address["City"] = city
        if state is not None:
            property_address["State/Prov"] = state
        if zip_code is not None:
            property_address["Zip/Postal Code"] = zip_code
        if county is not None:
            property_address["County"] = county
        if country is not None:
            property_address["Country"] = country
        if mls_number is not None:
            property_address["MLS Number"] = mls_number
        if parcel_tax_id is not None:
            property_address["Parcel/Tax ID"] = parcel_tax_id

        details = {"Property Address": property_address}
        return self.update_loop_details(profile_id, loop_id, details)

    def update_financials(
        self,
        profile_id: int,
        loop_id: int,
        purchase_sale_price: Optional[str] = None,
        sale_commission_rate: Optional[str] = None,
        sale_commission_split_buy_percent: Optional[str] = None,
        sale_commission_split_sell_percent: Optional[str] = None,
        sale_commission_total: Optional[str] = None,
        earnest_money_amount: Optional[str] = None,
        earnest_money_held_by: Optional[str] = None,
        sale_commission_split_buy_dollar: Optional[str] = None,
        sale_commission_split_sell_dollar: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update financial information for a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            purchase_sale_price: Purchase/Sale price
            sale_commission_rate: Sale commission rate
            sale_commission_split_buy_percent: Buy side commission split percentage
            sale_commission_split_sell_percent: Sell side commission split percentage
            sale_commission_total: Total sale commission
            earnest_money_amount: Earnest money amount
            earnest_money_held_by: Who holds the earnest money
            sale_commission_split_buy_dollar: Buy side commission split in dollars
            sale_commission_split_sell_dollar: Sell side commission split in dollars

        Returns:
            Dictionary containing updated loop details

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            updated_details = client.loop_detail.update_financials(
                profile_id=123,
                loop_id=456,
                purchase_sale_price="500000",
                sale_commission_rate="6",
                earnest_money_amount="10000"
            )
            ```
        """
        financials: Dict[str, str] = {}

        if purchase_sale_price is not None:
            financials["Purchase/Sale Price"] = purchase_sale_price
        if sale_commission_rate is not None:
            financials["Sale Commission Rate"] = sale_commission_rate
        if sale_commission_split_buy_percent is not None:
            financials["Sale Commission Split % - Buy Side"] = (
                sale_commission_split_buy_percent
            )
        if sale_commission_split_sell_percent is not None:
            financials["Sale Commission Split % - Sell Side"] = (
                sale_commission_split_sell_percent
            )
        if sale_commission_total is not None:
            financials["Sale Commission Total"] = sale_commission_total
        if earnest_money_amount is not None:
            financials["Earnest Money Amount"] = earnest_money_amount
        if earnest_money_held_by is not None:
            financials["Earnest Money Held By"] = earnest_money_held_by
        if sale_commission_split_buy_dollar is not None:
            financials["Sale Commission Split $ - Buy Side"] = (
                sale_commission_split_buy_dollar
            )
        if sale_commission_split_sell_dollar is not None:
            financials["Sale Commission Split $ - Sell Side"] = (
                sale_commission_split_sell_dollar
            )

        details = {"Financials": financials}
        return self.update_loop_details(profile_id, loop_id, details)

    def update_contract_dates(
        self,
        profile_id: int,
        loop_id: int,
        contract_agreement_date: Optional[str] = None,
        closing_date: Optional[str] = None,
        inspection_date: Optional[str] = None,
        offer_date: Optional[str] = None,
        offer_expiration_date: Optional[str] = None,
        occupancy_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update contract and offer dates for a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            contract_agreement_date: Contract agreement date (MM/DD/YYYY format)
            closing_date: Closing date (MM/DD/YYYY format)
            inspection_date: Inspection date (MM/DD/YYYY format)
            offer_date: Offer date (MM/DD/YYYY format)
            offer_expiration_date: Offer expiration date (MM/DD/YYYY format)
            occupancy_date: Occupancy date (MM/DD/YYYY format)

        Returns:
            Dictionary containing updated loop details

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            updated_details = client.loop_detail.update_contract_dates(
                profile_id=123,
                loop_id=456,
                offer_date="01/15/2024",
                closing_date="02/28/2024"
            )
            ```
        """
        contract_dates: Dict[str, str] = {}
        offer_dates: Dict[str, str] = {}

        if contract_agreement_date is not None:
            contract_dates["Contract Agreement Date"] = contract_agreement_date
        if closing_date is not None:
            contract_dates["Closing Date"] = closing_date

        if inspection_date is not None:
            offer_dates["Inspection Date"] = inspection_date
        if offer_date is not None:
            offer_dates["Offer Date"] = offer_date
        if offer_expiration_date is not None:
            offer_dates["Offer Expiration Date"] = offer_expiration_date
        if occupancy_date is not None:
            offer_dates["Occupancy Date"] = occupancy_date

        details: Dict[str, Any] = {}
        if contract_dates:
            details["Contract Dates"] = contract_dates
        if offer_dates:
            details["Offer Dates"] = offer_dates

        return self.update_loop_details(profile_id, loop_id, details)
