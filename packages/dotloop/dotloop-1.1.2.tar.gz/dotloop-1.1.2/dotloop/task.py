"""Task client for the Dotloop API wrapper."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class TaskClient(BaseClient):
    """Client for task and task list API endpoints."""

    def list_task_lists(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """List all task lists in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing list of task lists with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            task_lists = client.task.list_task_lists(profile_id=123, loop_id=456)
            for task_list in task_lists['data']:
                print(f"Task List: {task_list['name']} (ID: {task_list['id']})")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop/{loop_id}/tasklist")

    def get_task_list(
        self, profile_id: int, loop_id: int, tasklist_id: int
    ) -> Dict[str, Any]:
        """Retrieve an individual task list by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            tasklist_id: ID of the task list to retrieve

        Returns:
            Dictionary containing task list information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the task list is not found

        Example:
            ```python
            task_list = client.task.get_task_list(
                profile_id=123,
                loop_id=456,
                tasklist_id=789
            )
            print(f"Task List: {task_list['data']['name']}")
            ```
        """
        return self.get(f"/profile/{profile_id}/loop/{loop_id}/tasklist/{tasklist_id}")

    def list_tasks(
        self, profile_id: int, loop_id: int, tasklist_id: int
    ) -> Dict[str, Any]:
        """List all tasks in a task list.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            tasklist_id: ID of the task list

        Returns:
            Dictionary containing list of tasks with metadata

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the task list is not found

        Example:
            ```python
            tasks = client.task.list_tasks(
                profile_id=123,
                loop_id=456,
                tasklist_id=789
            )
            for task in tasks['data']:
                print(f"Task: {task['name']} - {task['status']}")
            ```
        """
        return self.get(
            f"/profile/{profile_id}/loop/{loop_id}/tasklist/{tasklist_id}/task"
        )

    def get_task(
        self, profile_id: int, loop_id: int, tasklist_id: int, task_id: int
    ) -> Dict[str, Any]:
        """Retrieve an individual task by ID.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop
            tasklist_id: ID of the task list
            task_id: ID of the task to retrieve

        Returns:
            Dictionary containing task information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the task is not found

        Example:
            ```python
            task = client.task.get_task(
                profile_id=123,
                loop_id=456,
                tasklist_id=789,
                task_id=101
            )
            print(f"Task: {task['data']['name']}")
            print(f"Status: {task['data']['status']}")
            print(f"Due Date: {task['data']['dueDate']}")
            ```
        """
        return self.get(
            f"/profile/{profile_id}/loop/{loop_id}/tasklist/{tasklist_id}/task/{task_id}"
        )

    def get_all_tasks_in_loop(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """Get all tasks across all task lists in a loop.

        This is a convenience method that fetches all task lists and their tasks.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing all tasks organized by task list

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            all_tasks = client.task.get_all_tasks_in_loop(profile_id=123, loop_id=456)
            for tasklist_name, tasks in all_tasks.items():
                print(f"Task List: {tasklist_name}")
                for task in tasks:
                    print(f"  - {task['name']} ({task['status']})")
            ```
        """
        # Get all task lists
        task_lists = self.list_task_lists(profile_id, loop_id)

        all_tasks = {}
        for task_list in task_lists["data"]:
            tasklist_id = task_list["id"]
            tasklist_name = task_list["name"]

            # Get tasks for this task list
            tasks = self.list_tasks(profile_id, loop_id, tasklist_id)
            all_tasks[tasklist_name] = tasks["data"]

        return all_tasks

    def get_pending_tasks(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """Get all pending/incomplete tasks in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing pending tasks organized by task list

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            pending_tasks = client.task.get_pending_tasks(profile_id=123, loop_id=456)
            total_pending = sum(len(tasks) for tasks in pending_tasks.values())
            print(f"Total pending tasks: {total_pending}")

            for tasklist_name, tasks in pending_tasks.items():
                if tasks:
                    print(f"Task List: {tasklist_name}")
                    for task in tasks:
                        print(f"  - {task['name']} (Due: {task.get('dueDate', 'No due date')})")
            ```
        """
        all_tasks = self.get_all_tasks_in_loop(profile_id, loop_id)

        pending_tasks = {}
        for tasklist_name, tasks in all_tasks.items():
            # Filter for incomplete tasks (assuming status is not "COMPLETE" or similar)
            pending = [
                task
                for task in tasks
                if task.get("status", "").upper()
                not in ["COMPLETE", "COMPLETED", "DONE"]
            ]
            if pending:
                pending_tasks[tasklist_name] = pending

        return pending_tasks

    def get_completed_tasks(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """Get all completed tasks in a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing completed tasks organized by task list

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            completed_tasks = client.task.get_completed_tasks(profile_id=123, loop_id=456)
            total_completed = sum(len(tasks) for tasks in completed_tasks.values())
            print(f"Total completed tasks: {total_completed}")

            for tasklist_name, tasks in completed_tasks.items():
                if tasks:
                    print(f"Task List: {tasklist_name}")
                    for task in tasks:
                        print(f"  - {task['name']} (Completed: {task.get('completedDate', 'Unknown')})")
            ```
        """
        all_tasks = self.get_all_tasks_in_loop(profile_id, loop_id)

        completed_tasks = {}
        for tasklist_name, tasks in all_tasks.items():
            # Filter for completed tasks
            completed = [
                task
                for task in tasks
                if task.get("status", "").upper() in ["COMPLETE", "COMPLETED", "DONE"]
            ]
            if completed:
                completed_tasks[tasklist_name] = completed

        return completed_tasks

    def get_task_summary(self, profile_id: int, loop_id: int) -> Dict[str, Any]:
        """Get a summary of task completion status for a loop.

        Args:
            profile_id: ID of the profile
            loop_id: ID of the loop

        Returns:
            Dictionary containing task summary statistics

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the loop is not found

        Example:
            ```python
            summary = client.task.get_task_summary(profile_id=123, loop_id=456)
            print(f"Total tasks: {summary['total_tasks']}")
            print(f"Completed: {summary['completed_tasks']}")
            print(f"Pending: {summary['pending_tasks']}")
            print(f"Completion rate: {summary['completion_percentage']:.1f}%")
            ```
        """
        all_tasks = self.get_all_tasks_in_loop(profile_id, loop_id)

        total_tasks = 0
        completed_tasks = 0
        pending_tasks = 0

        task_lists_summary = {}

        for tasklist_name, tasks in all_tasks.items():
            tasklist_total = len(tasks)
            tasklist_completed = len(
                [
                    task
                    for task in tasks
                    if task.get("status", "").upper()
                    in ["COMPLETE", "COMPLETED", "DONE"]
                ]
            )
            tasklist_pending = tasklist_total - tasklist_completed

            task_lists_summary[tasklist_name] = {
                "total": tasklist_total,
                "completed": tasklist_completed,
                "pending": tasklist_pending,
                "completion_percentage": (
                    (tasklist_completed / tasklist_total * 100)
                    if tasklist_total > 0
                    else 0
                ),
            }

            total_tasks += tasklist_total
            completed_tasks += tasklist_completed
            pending_tasks += tasklist_pending

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_percentage": (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            ),
            "task_lists": task_lists_summary,
        }
