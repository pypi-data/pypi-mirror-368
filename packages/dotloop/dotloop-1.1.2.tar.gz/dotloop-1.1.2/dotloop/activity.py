"""Activity client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class ActivityClient(BaseClient):
    """Client for activity API endpoints."""

    def list_loop_activity(
        self,
        profile_id: int,
        loop_id: int,
        batch_size: Optional[int] = None,
        batch_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List loop activity feed.

        Retrieves the activity feed for a specific loop, showing all actions
        and events that have occurred within the loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            batch_size: Size of batch returned (default=20, max=100)
            batch_number: Batch/page number (default=1)

        Returns:
            Dictionary containing list of activity items with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            activities = client.activity.list_loop_activity(
                profile_id=123,
                loop_id=456,
                batch_size=50
            )

            print(f"Total activities: {activities['meta']['total']}")
            for activity in activities['data']:
                print(f"{activity['createdDate']}: {activity['description']}")
                print(f"  By: {activity['createdBy']['name']}")
            ```
        """
        params: Dict[str, Any] = {}

        if batch_size is not None:
            params["batch_size"] = batch_size
        if batch_number is not None:
            params["batch_number"] = batch_number

        return self.get(f"/profile/{profile_id}/loop/{loop_id}/activity", params=params)

    def get_recent_activity(
        self, profile_id: int, loop_id: int, limit: int = 10
    ) -> Dict[str, Any]:
        """Get recent activity for a loop.

        Convenience method to get the most recent activity items.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            limit: Number of recent activities to retrieve (max 100)

        Returns:
            Dictionary containing recent activity items

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            recent = client.activity.get_recent_activity(
                profile_id=123,
                loop_id=456,
                limit=5
            )

            print("Recent Activity:")
            for activity in recent['data']:
                print(f"- {activity['description']} ({activity['createdDate']})")
            ```
        """
        # Ensure limit doesn't exceed API maximum
        batch_size = min(limit, 100)

        return self.list_loop_activity(
            profile_id=profile_id,
            loop_id=loop_id,
            batch_size=batch_size,
            batch_number=1,
        )

    def get_activity_by_type(
        self,
        profile_id: int,
        loop_id: int,
        activity_type: str,
        batch_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get activity filtered by type.

        Retrieves all activity and filters by the specified type.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            activity_type: Type of activity to filter for (e.g., 'DOCUMENT_UPLOADED', 'PARTICIPANT_ADDED')
            batch_size: Size of batch to retrieve (default=100 for comprehensive search)

        Returns:
            Dictionary containing filtered activity items

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            doc_activities = client.activity.get_activity_by_type(
                profile_id=123,
                loop_id=456,
                activity_type="DOCUMENT_UPLOADED"
            )

            print(f"Document upload activities: {len(doc_activities['data'])}")
            for activity in doc_activities['data']:
                print(f"- {activity['description']} ({activity['createdDate']})")
            ```
        """
        # Get all activities (or a large batch)
        if batch_size is None:
            batch_size = 100

        all_activities = self.list_loop_activity(
            profile_id=profile_id, loop_id=loop_id, batch_size=batch_size
        )

        # Filter by activity type
        filtered_activities = [
            activity
            for activity in all_activities["data"]
            if activity.get("type", "").upper() == activity_type.upper()
        ]

        return {
            "data": filtered_activities,
            "meta": {
                "total": len(filtered_activities),
                "filtered_from": all_activities["meta"]["total"],
                "activity_type": activity_type,
            },
        }

    def get_activity_by_user(
        self,
        profile_id: int,
        loop_id: int,
        user_name: str,
        batch_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get activity filtered by user.

        Retrieves all activity and filters by the specified user.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            user_name: Name of the user to filter for
            batch_size: Size of batch to retrieve (default=100 for comprehensive search)

        Returns:
            Dictionary containing filtered activity items

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            user_activities = client.activity.get_activity_by_user(
                profile_id=123,
                loop_id=456,
                user_name="John Doe"
            )

            print(f"Activities by {user_name}: {len(user_activities['data'])}")
            for activity in user_activities['data']:
                print(f"- {activity['description']} ({activity['createdDate']})")
            ```
        """
        # Get all activities (or a large batch)
        if batch_size is None:
            batch_size = 100

        all_activities = self.list_loop_activity(
            profile_id=profile_id, loop_id=loop_id, batch_size=batch_size
        )

        # Filter by user name
        filtered_activities = [
            activity
            for activity in all_activities["data"]
            if activity.get("createdBy", {}).get("name", "").lower()
            == user_name.lower()
        ]

        return {
            "data": filtered_activities,
            "meta": {
                "total": len(filtered_activities),
                "filtered_from": all_activities["meta"]["total"],
                "user_name": user_name,
            },
        }

    def get_activity_summary(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """Get a summary of activity in a loop.

        Provides statistics about the activity in the loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing activity summary statistics

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            summary = client.activity.get_activity_summary(profile_id=123, loop_id=456)
            print(f"Total activities: {summary['total_activities']}")
            print(f"Unique users: {summary['unique_users']}")
            print(f"Activity types: {list(summary['activity_types'].keys())}")
            print(f"Most active user: {summary['most_active_user']}")
            ```
        """
        # Get all activities
        all_activities = self.list_loop_activity(
            profile_id=profile_id, loop_id=loop_id, batch_size=100
        )

        activities = all_activities["data"]
        total_activities = len(activities)

        # Analyze activity types
        activity_types: Dict[str, int] = {}
        users: Dict[str, int] = {}

        for activity in activities:
            # Count activity types
            activity_type = activity.get("type", "UNKNOWN")
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1

            # Count user activities
            user_name = activity.get("createdBy", {}).get("name", "Unknown")
            users[user_name] = users.get(user_name, 0) + 1

        # Find most active user
        most_active_user = (
            max(users.items(), key=lambda x: x[1]) if users else ("None", 0)
        )

        return {
            "total_activities": total_activities,
            "unique_users": len(users),
            "activity_types": activity_types,
            "user_activity_counts": users,
            "most_active_user": most_active_user[0],
            "most_active_user_count": most_active_user[1],
        }
