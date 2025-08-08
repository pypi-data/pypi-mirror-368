import logging
from typing import List, Optional

import httpx
from llama_deploy.core.schema.deployments import (
    DeploymentCreate,
    DeploymentResponse,
    DeploymentsListResponse,
    DeploymentUpdate,
)
from llama_deploy.core.schema.git_validation import (
    RepositoryValidationRequest,
    RepositoryValidationResponse,
)
from llama_deploy.core.schema.projects import ProjectSummary, ProjectsListResponse
from rich.console import Console

from .config import config_manager


class LlamaDeployClient:
    """HTTP client for communicating with the LlamaDeploy control plane API"""

    def __init__(
        self, base_url: Optional[str] = None, project_id: Optional[str] = None
    ):
        """Initialize the client with a configured profile"""
        self.console = Console()

        # Get profile data
        profile = config_manager.get_current_profile()
        if not profile:
            self.console.print("\n[bold red]No profile configured![/bold red]")
            self.console.print("\nTo get started, create a profile with:")
            self.console.print("[cyan]llamactl profile create[/cyan]")
            raise SystemExit(1)

        # Use profile data with optional overrides
        self.base_url = base_url or profile.api_url
        self.project_id = project_id or profile.active_project_id

        if not self.base_url:
            raise ValueError("API URL is required")

        if not self.project_id:
            raise ValueError("Project ID is required")

        self.base_url = self.base_url.rstrip("/")

        # Create persistent client with event hooks
        self.client = httpx.Client(
            base_url=self.base_url, event_hooks={"response": [self._handle_response]}
        )

    def _handle_response(self, response: httpx.Response) -> None:
        """Handle response middleware - warnings and error conversion"""
        # Check for warnings in response headers
        if "X-Warning" in response.headers:
            self.console.print(
                f"[yellow]Warning: {response.headers['X-Warning']}[/yellow]"
            )

        # Convert httpx errors to our current exception format
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Try to parse JSON error response
            try:
                response.read()  # need to collect streaming data before calling json
                error_data = e.response.json()
                if isinstance(error_data, dict) and "detail" in error_data:
                    error_message = error_data["detail"]
                else:
                    error_message = str(error_data)
            except (ValueError, KeyError):
                # Fallback to raw response text
                error_message = e.response.text

            raise Exception(f"HTTP {e.response.status_code}: {error_message}") from e
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}") from e

    # Health check
    def health_check(self) -> dict:
        """Check if the API server is healthy"""
        response = self.client.get("/health")
        return response.json()

    # Projects
    def list_projects(self) -> List[ProjectSummary]:
        """List all projects with deployment counts"""
        response = self.client.get("/projects/")
        projects_response = ProjectsListResponse.model_validate(response.json())
        return [project for project in projects_response.projects]

    # Deployments
    def list_deployments(self) -> List[DeploymentResponse]:
        """List deployments for the configured project"""
        response = self.client.get(f"/{self.project_id}/deployments/")
        deployments_response = DeploymentsListResponse.model_validate(response.json())
        return [deployment for deployment in deployments_response.deployments]

    def get_deployment(self, deployment_id: str) -> DeploymentResponse:
        """Get a specific deployment"""
        response = self.client.get(f"/{self.project_id}/deployments/{deployment_id}")
        deployment = DeploymentResponse.model_validate(response.json())
        return deployment

    def create_deployment(
        self,
        deployment_data: DeploymentCreate,
    ) -> DeploymentResponse:
        """Create a new deployment"""

        response = self.client.post(
            f"/{self.project_id}/deployments/",
            json=deployment_data.model_dump(exclude_none=True),
        )
        deployment = DeploymentResponse.model_validate(response.json())
        return deployment

    def delete_deployment(self, deployment_id: str) -> None:
        """Delete a deployment"""
        self.client.delete(f"/{self.project_id}/deployments/{deployment_id}")

    def update_deployment(
        self,
        deployment_id: str,
        update_data: DeploymentUpdate,
        force_git_sha_update: bool = False,
    ) -> DeploymentResponse:
        """Update an existing deployment"""

        params = {}
        if force_git_sha_update:
            params["force_git_sha_update"] = True

        response = self.client.patch(
            f"/{self.project_id}/deployments/{deployment_id}",
            json=update_data.model_dump(),
            params=params,
        )
        deployment = DeploymentResponse.model_validate(response.json())
        return deployment

    def validate_repository(
        self,
        repo_url: str,
        deployment_id: str | None = None,
        pat: str | None = None,
    ) -> RepositoryValidationResponse:
        """Validate a repository URL"""
        logging.info(
            f"Validating repository with params: {repo_url}, {deployment_id}, {pat}"
        )
        response = self.client.post(
            f"/{self.project_id}/deployments/validate-repository",
            json=RepositoryValidationRequest(
                repository_url=repo_url,
                deployment_id=deployment_id,
                pat=pat,
            ).model_dump(),
        )
        logging.info(f"Response: {response.json()}")
        return RepositoryValidationResponse.model_validate(response.json())


# Global client factory function
def get_client(
    base_url: Optional[str] = None, project_id: Optional[str] = None
) -> LlamaDeployClient:
    """Get a client instance with optional overrides"""
    return LlamaDeployClient(base_url=base_url, project_id=project_id)
