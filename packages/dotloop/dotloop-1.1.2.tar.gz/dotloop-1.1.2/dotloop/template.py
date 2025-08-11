"""Template client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class TemplateClient(BaseClient):
    """Client for loop template API endpoints."""

    def list_loop_templates(self, profile_id: int) -> Dict[str, Any]:
        """List all loop templates for a profile.

        Args:
            profile_id: ID of the profile

        Returns:
            Dictionary containing list of loop templates with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            templates = client.template.list_loop_templates(profile_id=123)
            for template in templates['data']:
                print(f"Template: {template['name']} (ID: {template['id']})")
                print(f"  Type: {template['type']}")
                print(f"  Created: {template['createdDate']}")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop-template")

    def get_loop_template(self, profile_id: int, template_id: int) -> Dict[str, Any]:
        """Retrieve an individual loop template by ID.

        Args:
            profile_id: ID of the profile
            template_id: ID of the template to retrieve

        Returns:
            Dictionary containing template information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the template is not found

        Example:
            ```python
            template = client.template.get_loop_template(
                profile_id=123,
                template_id=456
            )
            print(f"Template: {template['data']['name']}")
            print(f"Description: {template['data']['description']}")
            print(f"Task Lists: {len(template['data']['taskLists'])}")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop-template/{template_id}")

    def get_templates_by_type(
        self, profile_id: int, template_type: str
    ) -> Dict[str, Any]:
        """Get templates filtered by type.

        Args:
            profile_id: ID of the profile
            template_type: Type of template to filter for (e.g., 'PURCHASE', 'LISTING')

        Returns:
            Dictionary containing filtered templates

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            purchase_templates = client.template.get_templates_by_type(
                profile_id=123,
                template_type="PURCHASE"
            )

            print(f"Purchase templates: {len(purchase_templates['data'])}")
            for template in purchase_templates['data']:
                print(f"- {template['name']}")
            ```
        """
        all_templates = self.list_loop_templates(profile_id)

        # Filter by template type
        filtered_templates = [
            template
            for template in all_templates["data"]
            if template.get("type", "").upper() == template_type.upper()
        ]

        return {
            "data": filtered_templates,
            "meta": {
                "total": len(filtered_templates),
                "filtered_from": all_templates["meta"]["total"],
                "template_type": template_type,
            },
        }

    def get_default_templates(self, profile_id: int) -> Dict[str, Any]:
        """Get default/system templates for a profile.

        Args:
            profile_id: ID of the profile

        Returns:
            Dictionary containing default templates

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            default_templates = client.template.get_default_templates(profile_id=123)

            print(f"Default templates: {len(default_templates['data'])}")
            for template in default_templates['data']:
                print(f"- {template['name']} ({template['type']})")
            ```
        """
        all_templates = self.list_loop_templates(profile_id)

        # Filter for default/system templates (assuming they have a specific flag or naming)
        default_templates = [
            template
            for template in all_templates["data"]
            if template.get("isDefault", False) or template.get("isSystem", False)
        ]

        return {
            "data": default_templates,
            "meta": {
                "total": len(default_templates),
                "filtered_from": all_templates["meta"]["total"],
            },
        }

    def get_custom_templates(self, profile_id: int) -> Dict[str, Any]:
        """Get custom/user-created templates for a profile.

        Args:
            profile_id: ID of the profile

        Returns:
            Dictionary containing custom templates

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            custom_templates = client.template.get_custom_templates(profile_id=123)

            print(f"Custom templates: {len(custom_templates['data'])}")
            for template in custom_templates['data']:
                print(f"- {template['name']} (Created: {template['createdDate']})")
            ```
        """
        all_templates = self.list_loop_templates(profile_id)

        # Filter for custom templates (not default/system)
        custom_templates = [
            template
            for template in all_templates["data"]
            if not template.get("isDefault", False)
            and not template.get("isSystem", False)
        ]

        return {
            "data": custom_templates,
            "meta": {
                "total": len(custom_templates),
                "filtered_from": all_templates["meta"]["total"],
            },
        }

    def find_template_by_name(
        self, profile_id: int, template_name: str, exact_match: bool = False
    ) -> Dict[str, Any]:
        """Find templates by name.

        Args:
            profile_id: ID of the profile
            template_name: Name to search for
            exact_match: Whether to require exact name match (default: False for partial match)

        Returns:
            Dictionary containing matching templates

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            # Find templates with "Purchase" in the name
            purchase_templates = client.template.find_template_by_name(
                profile_id=123,
                template_name="Purchase"
            )

            # Find exact template name match
            exact_template = client.template.find_template_by_name(
                profile_id=123,
                template_name="Standard Purchase Agreement",
                exact_match=True
            )
            ```
        """
        all_templates = self.list_loop_templates(profile_id)

        if exact_match:
            # Exact name match
            matching_templates = [
                template
                for template in all_templates["data"]
                if template.get("name", "").lower() == template_name.lower()
            ]
        else:
            # Partial name match
            matching_templates = [
                template
                for template in all_templates["data"]
                if template_name.lower() in template.get("name", "").lower()
            ]

        return {
            "data": matching_templates,
            "meta": {
                "total": len(matching_templates),
                "filtered_from": all_templates["meta"]["total"],
                "search_term": template_name,
                "exact_match": exact_match,
            },
        }

    def get_template_summary(self, profile_id: int) -> Dict[str, Any]:
        """Get a summary of available templates for a profile.

        Args:
            profile_id: ID of the profile

        Returns:
            Dictionary containing template summary statistics

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the profile is not found

        Example:
            ```python
            summary = client.template.get_template_summary(profile_id=123)
            print(f"Total templates: {summary['total_templates']}")
            print(f"Template types: {list(summary['template_types'].keys())}")
            print(f"Default templates: {summary['default_templates']}")
            print(f"Custom templates: {summary['custom_templates']}")
            ```
        """
        all_templates = self.list_loop_templates(profile_id)
        templates = all_templates["data"]

        total_templates = len(templates)

        # Analyze template types
        template_types: Dict[str, int] = {}
        default_count = 0
        custom_count = 0

        for template in templates:
            # Count template types
            template_type = template.get("type", "UNKNOWN")
            template_types[template_type] = template_types.get(template_type, 0) + 1

            # Count default vs custom
            if template.get("isDefault", False) or template.get("isSystem", False):
                default_count += 1
            else:
                custom_count += 1

        return {
            "total_templates": total_templates,
            "template_types": template_types,
            "default_templates": default_count,
            "custom_templates": custom_count,
            "most_common_type": (
                max(template_types.items(), key=lambda x: x[1])[0]
                if template_types
                else None  # pragma: no cover
            ),
        }
