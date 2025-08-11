"""Webhook client for the Dotloop API wrapper."""

from typing import Any, Dict, List, Optional, Set, Union

from .base_client import BaseClient
from .enums import WebhookEventType


class WebhookClient(BaseClient):
    """Client for webhook subscription and event API endpoints."""

    def list_subscriptions(self) -> Dict[str, Any]:
        """List all webhook subscriptions.

        Returns:
            Dictionary containing list of webhook subscriptions with metadata

        Raises:
            DotloopError: If the API request fails

        Example:
            ```python
            subscriptions = client.webhook.list_subscriptions()
            for subscription in subscriptions['data']:
                print(f"Subscription: {subscription['name']} (ID: {subscription['id']})")
                print(f"  URL: {subscription['url']}")
                print(f"  Events: {subscription['events']}")
            ```
        """
        return self.get("/subscription")

    def get_subscription(self, subscription_id: int) -> Dict[str, Any]:
        """Retrieve an individual webhook subscription by ID.

        Args:
            subscription_id: ID of the subscription to retrieve

        Returns:
            Dictionary containing subscription information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            subscription = client.webhook.get_subscription(subscription_id=123)
            print(f"Subscription: {subscription['data']['name']}")
            print(f"URL: {subscription['data']['url']}")
            print(f"Active: {subscription['data']['active']}")
            ```
        """
        return self.get(f"/subscription/{subscription_id}")

    def create_subscription(
        self,
        name: str,
        url: str,
        events: List[Union[WebhookEventType, str]],
        active: bool = True,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new webhook subscription.

        Args:
            name: Name of the subscription
            url: URL endpoint to receive webhook events
            events: List of event types to subscribe to
            active: Whether the subscription is active (default: True)
            description: Optional description of the subscription

        Returns:
            Dictionary containing created subscription information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            subscription = client.webhook.create_subscription(
                name="My App Webhook",
                url="https://myapp.com/webhook",
                events=[
                    WebhookEventType.LOOP_CREATED,
                    WebhookEventType.DOCUMENT_UPLOADED,
                    WebhookEventType.PARTICIPANT_ADDED
                ],
                description="Webhook for loop events"
            )
            print(f"Created subscription: {subscription['data']['id']}")
            ```
        """
        # Convert enum values to strings
        event_strings = []
        for event in events:
            if isinstance(event, WebhookEventType):
                event_strings.append(event.value)
            else:
                event_strings.append(event)

        data: Dict[str, Any] = {
            "name": name,
            "url": url,
            "events": event_strings,
            "active": active,
        }

        if description is not None:
            data["description"] = description

        return self.post("/subscription", data=data)

    def update_subscription(
        self,
        subscription_id: int,
        name: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[Union[WebhookEventType, str]]] = None,
        active: Optional[bool] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing webhook subscription.

        Args:
            subscription_id: ID of the subscription to update
            name: New name for the subscription
            url: New URL endpoint
            events: New list of event types to subscribe to
            active: Whether the subscription should be active
            description: New description

        Returns:
            Dictionary containing updated subscription information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found
            ValidationError: If parameters are invalid

        Example:
            ```python
            subscription = client.webhook.update_subscription(
                subscription_id=123,
                url="https://myapp.com/new-webhook",
                active=False
            )
            ```
        """
        data: Dict[str, Any] = {}

        if name is not None:
            data["name"] = name
        if url is not None:
            data["url"] = url
        if events is not None:
            # Convert enum values to strings
            event_strings = []
            for event in events:
                if isinstance(event, WebhookEventType):
                    event_strings.append(event.value)
                else:
                    event_strings.append(event)
            data["events"] = event_strings
        if active is not None:
            data["active"] = active
        if description is not None:
            data["description"] = description

        return self.patch(f"/subscription/{subscription_id}", data=data)

    def delete_subscription(self, subscription_id: int) -> Dict[str, Any]:
        """Delete a webhook subscription.

        Args:
            subscription_id: ID of the subscription to delete

        Returns:
            Dictionary containing deletion confirmation

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            result = client.webhook.delete_subscription(subscription_id=123)
            ```
        """
        return self.delete(f"/subscription/{subscription_id}")

    def list_events(self, subscription_id: int) -> Dict[str, Any]:
        """List events for a webhook subscription.

        Args:
            subscription_id: ID of the subscription

        Returns:
            Dictionary containing list of webhook events

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            events = client.webhook.list_events(subscription_id=123)
            for event in events['data']:
                print(f"Event: {event['type']} at {event['createdDate']}")
                print(f"  Status: {event['status']}")
                print(f"  Attempts: {event['attempts']}")
            ```
        """
        return self.get(f"/subscription/{subscription_id}/event")

    def get_event(self, subscription_id: int, event_id: int) -> Dict[str, Any]:
        """Retrieve an individual webhook event by ID.

        Args:
            subscription_id: ID of the subscription
            event_id: ID of the event to retrieve

        Returns:
            Dictionary containing event information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the event is not found

        Example:
            ```python
            event = client.webhook.get_event(subscription_id=123, event_id=456)
            print(f"Event: {event['data']['type']}")
            print(f"Payload: {event['data']['payload']}")
            print(f"Response: {event['data']['response']}")
            ```
        """
        return self.get(f"/subscription/{subscription_id}/event/{event_id}")

    def activate_subscription(self, subscription_id: int) -> Dict[str, Any]:
        """Activate a webhook subscription.

        Convenience method to set a subscription as active.

        Args:
            subscription_id: ID of the subscription to activate

        Returns:
            Dictionary containing updated subscription information

        Example:
            ```python
            subscription = client.webhook.activate_subscription(subscription_id=123)
            ```
        """
        return self.update_subscription(subscription_id, active=True)

    def deactivate_subscription(self, subscription_id: int) -> Dict[str, Any]:
        """Deactivate a webhook subscription.

        Convenience method to set a subscription as inactive.

        Args:
            subscription_id: ID of the subscription to deactivate

        Returns:
            Dictionary containing updated subscription information

        Example:
            ```python
            subscription = client.webhook.deactivate_subscription(subscription_id=123)
            ```
        """
        return self.update_subscription(subscription_id, active=False)

    def get_failed_events(self, subscription_id: int) -> Dict[str, Any]:
        """Get failed webhook events for a subscription.

        Args:
            subscription_id: ID of the subscription

        Returns:
            Dictionary containing failed events

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            failed_events = client.webhook.get_failed_events(subscription_id=123)
            print(f"Failed events: {len(failed_events['data'])}")
            for event in failed_events['data']:
                print(f"- {event['type']} failed {event['attempts']} times")
            ```
        """
        all_events = self.list_events(subscription_id)

        # Filter for failed events (assuming status indicates failure)
        failed_events = [
            event
            for event in all_events["data"]
            if event.get("status", "").upper() in ["FAILED", "ERROR", "TIMEOUT"]
        ]

        return {
            "data": failed_events,
            "meta": {
                "total": len(failed_events),
                "filtered_from": all_events["meta"]["total"],
                "subscription_id": subscription_id,
            },
        }

    def get_subscription_summary(self, subscription_id: int) -> Dict[str, Any]:
        """Get a summary of webhook events for a subscription.

        Args:
            subscription_id: ID of the subscription

        Returns:
            Dictionary containing event summary statistics

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            summary = client.webhook.get_subscription_summary(subscription_id=123)
            print(f"Total events: {summary['total_events']}")
            print(f"Successful: {summary['successful_events']}")
            print(f"Failed: {summary['failed_events']}")
            print(f"Success rate: {summary['success_rate']:.1f}%")
            ```
        """
        events = self.list_events(subscription_id)
        event_list = events["data"]

        total_events = len(event_list)
        successful_events = 0
        failed_events = 0

        event_types: Dict[str, int] = {}

        for event in event_list:
            # Count event types
            event_type = event.get("type", "UNKNOWN")
            event_types[event_type] = event_types.get(event_type, 0) + 1

            # Count success/failure
            status = event.get("status", "").upper()
            if status in ["SUCCESS", "DELIVERED", "OK"]:
                successful_events += 1
            elif status in ["FAILED", "ERROR", "TIMEOUT"]:
                failed_events += 1

        success_rate = (
            (successful_events / total_events * 100) if total_events > 0 else 0
        )

        return {
            "subscription_id": subscription_id,
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": success_rate,
            "event_types": event_types,
            "most_common_event": (
                max(event_types.items(), key=lambda x: x[1])[0] if event_types else None
            ),
        }

    def get_all_subscriptions_summary(self) -> Dict[str, Any]:
        """Get a summary of all webhook subscriptions.

        Returns:
            Dictionary containing summary statistics for all subscriptions

        Raises:
            DotloopError: If the API request fails

        Example:
            ```python
            summary = client.webhook.get_all_subscriptions_summary()
            print(f"Total subscriptions: {summary['total_subscriptions']}")
            print(f"Active subscriptions: {summary['active_subscriptions']}")
            print(f"Inactive subscriptions: {summary['inactive_subscriptions']}")
            ```
        """
        subscriptions = self.list_subscriptions()
        subscription_list = subscriptions["data"]

        total_subscriptions = len(subscription_list)
        active_subscriptions = 0
        inactive_subscriptions = 0

        subscription_urls: Set[str] = set()
        event_types: Set[str] = set()

        for subscription in subscription_list:
            # Count active/inactive
            if subscription.get("active", False) or subscription.get("isActive", False):
                active_subscriptions += 1
            else:
                inactive_subscriptions += 1

            # Collect unique URLs and event types
            if "url" in subscription:
                subscription_urls.add(subscription["url"])

            if "events" in subscription:
                for event in subscription["events"]:
                    event_types.add(event)

        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "inactive_subscriptions": inactive_subscriptions,
            "unique_urls": len(subscription_urls),
            "unique_event_types": len(event_types),
            "event_types": list(event_types),
        }
