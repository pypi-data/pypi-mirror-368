"""Main client for the Dotloop API wrapper."""

from typing import Optional

from .account import AccountClient
from .activity import ActivityClient
from .contact import ContactClient
from .document import DocumentClient
from .folder import FolderClient
from .loop import LoopClient
from .loop_detail import LoopDetailClient
from .loop_it import LoopItClient
from .participant import ParticipantClient
from .profile import ProfileClient
from .task import TaskClient
from .template import TemplateClient
from .webhook import WebhookClient


class DotloopClient:
    """Main client for the Dotloop API.

    This client provides access to all Dotloop API endpoints through
    specialized client instances.

    Example:
        ```python
        from dotloop import DotloopClient

        # Initialize with API key
        client = DotloopClient(api_key="your_api_key")

        # Or use environment variable DOTLOOP_API_KEY
        client = DotloopClient()

        # Access different endpoints
        account = client.account.get_account()
        profiles = client.profile.list_profiles()
        loops = client.loop.list_loops(profile_id=123)
        loop = client.loop_it.create_loop(...)
        contacts = client.contact.list_contacts()

        # Loop management
        details = client.loop_detail.get_loop_details(profile_id=123, loop_id=456)
        folders = client.folder.list_folders(profile_id=123, loop_id=456)
        documents = client.document.list_documents(profile_id=123, loop_id=456)
        participants = client.participant.list_participants(profile_id=123, loop_id=456)

        # Task and activity management
        tasks = client.task.list_task_lists(profile_id=123, loop_id=456)
        activity = client.activity.list_loop_activity(profile_id=123, loop_id=456)
        templates = client.template.list_loop_templates(profile_id=123)

        # Webhook management
        webhooks = client.webhook.list_subscriptions()

        # OAuth authentication (separate client)
        # auth_client = AuthClient(client_id="...", client_secret="...", redirect_uri="...")
        # auth_url = auth_client.get_authorization_url(scope=["account", "profile"])
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the Dotloop client.

        Args:
            api_key: API access token for authentication
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

        # Initialize client instances
        self._account_client: Optional[AccountClient] = None
        self._profile_client: Optional[ProfileClient] = None
        self._loop_client: Optional[LoopClient] = None
        self._loop_detail_client: Optional[LoopDetailClient] = None
        self._loop_it_client: Optional[LoopItClient] = None
        self._contact_client: Optional[ContactClient] = None
        self._folder_client: Optional[FolderClient] = None
        self._document_client: Optional[DocumentClient] = None
        self._participant_client: Optional[ParticipantClient] = None
        self._task_client: Optional[TaskClient] = None
        self._activity_client: Optional[ActivityClient] = None
        self._template_client: Optional[TemplateClient] = None
        self._webhook_client: Optional[WebhookClient] = None

    @property
    def account(self) -> AccountClient:
        """Access to account endpoints.

        Returns:
            AccountClient instance
        """
        if self._account_client is None:
            self._account_client = AccountClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._account_client

    @property
    def profile(self) -> ProfileClient:
        """Access to profile endpoints.

        Returns:
            ProfileClient instance
        """
        if self._profile_client is None:
            self._profile_client = ProfileClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._profile_client

    @property
    def loop(self) -> LoopClient:
        """Access to loop endpoints.

        Returns:
            LoopClient instance
        """
        if self._loop_client is None:
            self._loop_client = LoopClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._loop_client

    @property
    def loop_it(self) -> LoopItClient:
        """Access to Loop-It endpoints.

        Returns:
            LoopItClient instance
        """
        if self._loop_it_client is None:
            self._loop_it_client = LoopItClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._loop_it_client

    @property
    def contact(self) -> ContactClient:
        """Access to contact endpoints.

        Returns:
            ContactClient instance
        """
        if self._contact_client is None:
            self._contact_client = ContactClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._contact_client

    @property
    def loop_detail(self) -> LoopDetailClient:
        """Access to loop detail endpoints.

        Returns:
            LoopDetailClient instance
        """
        if self._loop_detail_client is None:
            self._loop_detail_client = LoopDetailClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._loop_detail_client

    @property
    def folder(self) -> FolderClient:
        """Access to folder endpoints.

        Returns:
            FolderClient instance
        """
        if self._folder_client is None:
            self._folder_client = FolderClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._folder_client

    @property
    def document(self) -> DocumentClient:
        """Access to document endpoints.

        Returns:
            DocumentClient instance
        """
        if self._document_client is None:
            self._document_client = DocumentClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._document_client

    @property
    def participant(self) -> ParticipantClient:
        """Access to participant endpoints.

        Returns:
            ParticipantClient instance
        """
        if self._participant_client is None:
            self._participant_client = ParticipantClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._participant_client

    @property
    def task(self) -> TaskClient:
        """Access to task and task list endpoints.

        Returns:
            TaskClient instance
        """
        if self._task_client is None:
            self._task_client = TaskClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._task_client

    @property
    def activity(self) -> ActivityClient:
        """Access to activity endpoints.

        Returns:
            ActivityClient instance
        """
        if self._activity_client is None:
            self._activity_client = ActivityClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._activity_client

    @property
    def template(self) -> TemplateClient:
        """Access to template endpoints.

        Returns:
            TemplateClient instance
        """
        if self._template_client is None:
            self._template_client = TemplateClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._template_client

    @property
    def webhook(self) -> WebhookClient:
        """Access to webhook endpoints.

        Returns:
            WebhookClient instance
        """
        if self._webhook_client is None:
            self._webhook_client = WebhookClient(
                api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
            )
        return self._webhook_client
