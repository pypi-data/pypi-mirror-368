"""Synchronous client for the Moderately AI API."""

import os
from typing import Any, Dict, Optional, Union

import httpx

from ._base_client import BaseClient, RetryConfig
from .resources import (
    AgentExecutions,
    Agents,
    Datasets,
    Files,
    PipelineConfigurationVersions,
    PipelineExecutions,
    Pipelines,
    Teams,
    Users,
)
from .types import HTTPMethod


class ModeratelyAI(BaseClient):
    """Synchronous client for the Moderately AI API.

    Example:
        ```python
        import moderatelyai_sdk

        # Initialize with environment variables (recommended)
        client = moderatelyai_sdk.ModeratelyAI()  # reads MODERATELY_API_KEY and MODERATELY_TEAM_ID

        # Or initialize with explicit parameters
        client = moderatelyai_sdk.ModeratelyAI(
            team_id="your-team-id",
            api_key="your-api-key"
        )

        # Or mix environment and explicit
        client = moderatelyai_sdk.ModeratelyAI(team_id="your-team-id")  # reads MODERATELY_API_KEY from env

        # Use the client - team_id is automatically added to requests
        users = client.users.list()  # automatically filtered to your team
        dataset = client.datasets.create(name="My Data")  # created in your team
        pipeline = client.pipelines.create(name="Data Pipeline")  # created in your team
        file = client.files.upload(file_path="data.csv", name="Training Data")  # uploaded to your team
        ```
    """

    def __init__(
        self,
        *,
        team_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None] = None,
        max_retries: int = 3,
        retry_config: Optional[RetryConfig] = None,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        """Initialize the Moderately AI client.

        Args:
            team_id: The team ID to scope all API requests to. If not provided, will read from MODERATELY_TEAM_ID environment variable.
            api_key: Your API key. If not provided, will read from MODERATELY_API_KEY environment variable.
            base_url: Override the default base URL for the API. Defaults to https://api.moderately.ai.
            timeout: Request timeout in seconds. Defaults to 30 seconds.
            max_retries: Maximum number of retries. Defaults to 3.
            retry_config: Advanced retry configuration. If provided, max_retries is ignored.
            default_headers: Default headers to include with every request.
            default_query: Default query parameters to include with every request.
            http_client: Custom httpx client instance. If provided, other HTTP options are ignored.

        Raises:
            ValueError: If no API key or team ID is provided via parameter or environment variable.
        """
        if api_key is None:
            api_key = os.environ.get("MODERATELY_API_KEY")

        if team_id is None:
            team_id = os.environ.get("MODERATELY_TEAM_ID")

        if api_key is None:
            raise ValueError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MODERATELY_API_KEY environment variable"
            )

        if team_id is None:
            raise ValueError(
                "The team_id client option must be set either by passing team_id to the client or by setting the MODERATELY_TEAM_ID environment variable"
            )

        if base_url is None:
            base_url = "https://api.moderately.ai"

        if timeout is None:
            timeout = 30.0

        # Store team_id for automatic filtering
        self.team_id = team_id

        # Add team_ids filter to default query parameters for list endpoints
        if default_query is None:
            default_query = {}

        # Add teamIds as a default query parameter (API expects camelCase)
        default_query = {**default_query, "teamIds": [team_id]}

        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_config=retry_config,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            team_id=team_id,
        )

        # Initialize resource groups
        self.users = Users(self)
        self.teams = Teams(self)
        self.agents = Agents(self)
        self.agent_executions = AgentExecutions(self)
        self.datasets = Datasets(self)
        self.pipelines = Pipelines(self)
        self.pipeline_configuration_versions = PipelineConfigurationVersions(self)
        self.pipeline_executions = PipelineExecutions(self)
        self.files = Files(self)

    def _make_request(
        self,
        method: HTTPMethod,
        path: str,
        *,
        cast_type: type,
        body: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a synchronous HTTP request."""
        return self._request(
            method=method,
            path=path,
            cast_type=cast_type,
            body=body,
            options=options or {},
        )

    def __enter__(self) -> "ModeratelyAI":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        if hasattr(self, "_client"):
            self._client.close()
