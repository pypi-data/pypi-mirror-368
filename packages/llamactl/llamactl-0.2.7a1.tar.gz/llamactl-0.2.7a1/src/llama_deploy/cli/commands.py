import os
import subprocess
from pathlib import Path
from typing import Optional

import click
from llama_deploy.appserver.client import Client as ApiserverClient
from llama_deploy.core.config import DEFAULT_DEPLOYMENT_FILE_PATH
from llama_deploy.core.schema.deployments import DeploymentUpdate
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from tenacity import RetryError, Retrying, stop_after_attempt, wait_fixed

from .client import get_client
from .config import config_manager
from .interactive_prompts.utils import (
    confirm_action,
    select_deployment,
    select_profile,
)
from .options import global_options
from .textual.deployment_form import create_deployment_form, edit_deployment_form
from .textual.profile_form import create_profile_form, edit_profile_form

RETRY_WAIT_SECONDS = 1
console = Console()


# Create sub-applications for organizing commands
@click.group(help="Manage profiles", no_args_is_help=True)
@global_options
def profile() -> None:
    """Manage profiles"""
    pass


@click.group(help="Manage projects", no_args_is_help=True)
@global_options
def projects() -> None:
    """Manage projects"""
    pass


@click.group(help="Manage deployments", no_args_is_help=True)
@global_options
def deployments() -> None:
    """Manage deployments"""
    pass


# Profile commands
@profile.command("create")
@global_options
@click.option("--name", help="Profile name")
@click.option("--api-url", help="API server URL")
@click.option("--project-id", help="Default project ID")
def create_profile(
    name: Optional[str], api_url: Optional[str], project_id: Optional[str]
) -> None:
    """Create a new profile"""
    try:
        # If all required args are provided via CLI, skip interactive mode
        if name and api_url:
            # Use CLI args directly
            profile = config_manager.create_profile(name, api_url, project_id)
            rprint(f"[green]Created profile '{profile.name}'[/green]")

            # Automatically switch to the new profile
            config_manager.set_current_profile(name)
            rprint(f"[green]Switched to profile '{name}'[/green]")
            return

        # Use interactive creation
        profile = create_profile_form()
        if profile is None:
            rprint("[yellow]Cancelled[/yellow]")
            return

        try:
            rprint(f"[green]Created profile '{profile.name}'[/green]")

            # Automatically switch to the new profile
            config_manager.set_current_profile(profile.name)
            rprint(f"[green]Switched to profile '{profile.name}'[/green]")
        except Exception as e:
            rprint(f"[red]Error creating profile: {e}[/red]")
            raise click.Abort()

    except ValueError as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@profile.command("list")
@global_options
def list_profiles() -> None:
    """List all profiles"""
    try:
        profiles = config_manager.list_profiles()
        current_name = config_manager.get_current_profile_name()

        if not profiles:
            rprint("[yellow]No profiles found[/yellow]")
            rprint("Create one with: [cyan]llamactl profile create[/cyan]")
            return

        table = Table(title="Profiles")
        table.add_column("Name", style="cyan")
        table.add_column("API URL", style="green")
        table.add_column("Active Project", style="yellow")
        table.add_column("Current", style="magenta")

        for profile in profiles:
            is_current = "✓" if profile.name == current_name else ""
            active_project = profile.active_project_id or "-"
            table.add_row(profile.name, profile.api_url, active_project, is_current)

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@profile.command("switch")
@global_options
@click.argument("name", required=False)
def switch_profile(name: Optional[str]) -> None:
    """Switch to a different profile"""
    try:
        name = select_profile(name)
        if not name:
            rprint("[yellow]No profile selected[/yellow]")
            return

        profile = config_manager.get_profile(name)
        if not profile:
            rprint(f"[red]Profile '{name}' not found[/red]")
            raise click.Abort()

        config_manager.set_current_profile(name)
        rprint(f"[green]Switched to profile '{name}'[/green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@profile.command("delete")
@global_options
@click.argument("name", required=False)
def delete_profile(name: Optional[str]) -> None:
    """Delete a profile"""
    try:
        name = select_profile(name)
        if not name:
            rprint("[yellow]No profile selected[/yellow]")
            return

        profile = config_manager.get_profile(name)
        if not profile:
            rprint(f"[red]Profile '{name}' not found[/red]")
            raise click.Abort()

        if config_manager.delete_profile(name):
            rprint(f"[green]Deleted profile '{name}'[/green]")
        else:
            rprint(f"[red]Profile '{name}' not found[/red]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@profile.command("edit")
@global_options
@click.argument("name", required=False)
def edit_profile(name: Optional[str]) -> None:
    """Edit a profile"""
    try:
        name = select_profile(name)
        if not name:
            rprint("[yellow]No profile selected[/yellow]")
            return

        # Get current profile
        maybe_profile = config_manager.get_profile(name)
        if not maybe_profile:
            rprint(f"[red]Profile '{name}' not found[/red]")
            raise click.Abort()
        profile = maybe_profile

        # Use the interactive edit menu
        updated = edit_profile_form(profile)
        if updated is None:
            rprint("[yellow]Cancelled[/yellow]")
            return

        try:
            current_profile = config_manager.get_current_profile()
            if not current_profile or current_profile.name != updated.name:
                config_manager.set_current_profile(updated.name)
                rprint(f"[green]Updated profile '{profile.name}'[/green]")
        except Exception as e:
            rprint(f"[red]Error updating profile: {e}[/red]")
            raise click.Abort()

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


# Projects commands
@projects.command("list")
@global_options
def list_projects() -> None:
    """List all projects with deployment counts"""
    try:
        client = get_client()
        projects = client.list_projects()

        if not projects:
            rprint("[yellow]No projects found[/yellow]")
            return

        table = Table(title="Projects")
        table.add_column("Project ID", style="cyan")
        table.add_column("Deployments", style="green")

        for project in projects:
            project_id = project.project_id
            deployment_count = project.deployment_count
            table.add_row(project_id, str(deployment_count))

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


# Health check command (at root level)
@click.command()
@global_options
def health_check() -> None:
    """Check if the API server is healthy"""
    try:
        client = get_client()
        health = client.health_check()

        status = health.get("status", "unknown")
        if status == "ok":
            rprint("[green]API server is healthy[/green]")
        else:
            rprint(f"[yellow]API server status: {status}[/yellow]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


# Deployments commands
@deployments.command("list")
@global_options
def list_deployments() -> None:
    """List deployments for the configured project"""
    try:
        client = get_client()
        deployments = client.list_deployments()

        if not deployments:
            rprint(
                f"[yellow]No deployments found for project {client.project_id}[/yellow]"
            )
            return

        table = Table(title=f"Deployments for project {client.project_id}")
        table.add_column("Name", style="cyan")
        table.add_column("ID", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Repository", style="blue")
        table.add_column("Deployment File", style="magenta")
        table.add_column("Git Ref", style="white")
        table.add_column("PAT", style="red")
        table.add_column("Secrets", style="bright_green")

        for deployment in deployments:
            name = deployment.name
            deployment_id = deployment.id
            status = deployment.status
            repo_url = deployment.repo_url
            deployment_file_path = deployment.deployment_file_path
            git_ref = deployment.git_ref
            has_pat = "✓" if deployment.has_personal_access_token else "-"
            secret_names = deployment.secret_names
            secrets_display = str(len(secret_names)) if secret_names else "-"

            table.add_row(
                name,
                deployment_id,
                status,
                repo_url,
                deployment_file_path,
                git_ref,
                has_pat,
                secrets_display,
            )

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("get")
@global_options
@click.argument("deployment_id", required=False)
def get_deployment(deployment_id: Optional[str]) -> None:
    """Get details of a specific deployment"""
    try:
        client = get_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        deployment = client.get_deployment(deployment_id)

        table = Table(title=f"Deployment: {deployment.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("ID", deployment.id)
        table.add_row("Project ID", deployment.project_id)
        table.add_row("Status", deployment.status)
        table.add_row("Repository", deployment.repo_url)
        table.add_row("Deployment File", deployment.deployment_file_path)
        table.add_row("Git Ref", deployment.git_ref)
        table.add_row("Has PAT", str(deployment.has_personal_access_token))

        apiserver_url = deployment.apiserver_url
        if apiserver_url:
            table.add_row("API Server URL", str(apiserver_url))

        secret_names = deployment.secret_names
        if secret_names:
            table.add_row("Secrets", ", ".join(secret_names))

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("create")
@global_options
@click.option("--repo-url", help="HTTP(S) Git Repository URL")
@click.option("--name", help="Deployment name")
@click.option("--deployment-file-path", help="Path to deployment file")
@click.option("--git-ref", help="Git reference (branch, tag, or commit)")
@click.option(
    "--personal-access-token", help="Git Personal Access Token (HTTP Basic Auth)"
)
def create_deployment(
    repo_url: Optional[str],
    name: Optional[str],
    deployment_file_path: Optional[str],
    git_ref: Optional[str],
    personal_access_token: Optional[str],
) -> None:
    """Create a new deployment"""

    # Use interactive creation
    deployment_form = create_deployment_form()
    if deployment_form is None:
        rprint("[yellow]Cancelled[/yellow]")
        return

    rprint(
        f"[green]Created deployment: {deployment_form.name} (id: {deployment_form.id})[/green]"
    )


@deployments.command("delete")
@global_options
@click.argument("deployment_id", required=False)
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def delete_deployment(deployment_id: Optional[str], confirm: bool) -> None:
    """Delete a deployment"""
    try:
        client = get_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        if not confirm:
            if not confirm_action(f"Delete deployment '{deployment_id}'?"):
                rprint("[yellow]Cancelled[/yellow]")
                return

        client.delete_deployment(deployment_id)
        rprint(f"[green]Deleted deployment: {deployment_id}[/green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("edit")
@global_options
@click.argument("deployment_id", required=False)
def edit_deployment(deployment_id: Optional[str]) -> None:
    """Interactively edit a deployment"""
    try:
        client = get_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        # Get current deployment details
        current_deployment = client.get_deployment(deployment_id)

        # Use the interactive edit form
        updated_deployment = edit_deployment_form(current_deployment)
        if updated_deployment is None:
            rprint("[yellow]Cancelled[/yellow]")
            return

        rprint(
            f"[green]Successfully updated deployment: {updated_deployment.name}[/green]"
        )

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@deployments.command("refresh")
@global_options
@click.argument("deployment_id", required=False)
def refresh_deployment(deployment_id: Optional[str]) -> None:
    """Refresh a deployment with the latest code from its git reference"""
    try:
        client = get_client()

        deployment_id = select_deployment(deployment_id)
        if not deployment_id:
            rprint("[yellow]No deployment selected[/yellow]")
            return

        # Get current deployment details to show what we're refreshing
        current_deployment = client.get_deployment(deployment_id)
        deployment_name = current_deployment.name
        old_git_sha = current_deployment.git_sha or ""

        # Create an empty update to force git SHA refresh with spinner
        with console.status(f"Refreshing {deployment_name}..."):
            deployment_update = DeploymentUpdate()
            updated_deployment = client.update_deployment(
                deployment_id, deployment_update, force_git_sha_update=True
            )

        # Show the git SHA change with short SHAs
        new_git_sha = updated_deployment.git_sha or ""
        old_short = old_git_sha[:7] if old_git_sha else "none"
        new_short = new_git_sha[:7] if new_git_sha else "none"

        if old_git_sha == new_git_sha:
            rprint(f"No changes: already at {new_short}")
        else:
            rprint(f"Updated: {old_short} → {new_short}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()


@click.command("serve")
@click.argument(
    "deployment_file",
    required=False,
    default=DEFAULT_DEPLOYMENT_FILE_PATH,
    type=click.Path(dir_okay=False, resolve_path=True, path_type=Path),  # type: ignore
)
@global_options
def serve(deployment_file: Path) -> None:
    """Run llama_deploy API Server in the foreground. If no deployment_file is provided, will look for a llama_deploy.yaml in the current directory."""
    if not deployment_file.exists():
        rprint(f"[red]Deployment file '{deployment_file}' not found[/red]")
        raise click.Abort()

    try:
        env = os.environ.copy()
        env["LLAMA_DEPLOY_APISERVER_DEPLOYMENTS_PATH"] = str(deployment_file.parent)

        client = ApiserverClient()

        uvicorn_p = subprocess.Popen(
            [
                "uvicorn",
                "llama_deploy.appserver.app:app",
                "--host",
                "localhost",
                "--port",
                "4501",
            ],
            env=env,
        )

        retrying = Retrying(
            stop=stop_after_attempt(5), wait=wait_fixed(RETRY_WAIT_SECONDS)
        )
        try:
            for attempt in retrying:
                with attempt:
                    client.sync.apiserver.deployments.create(
                        deployment_file.open("rb"),
                        base_path=deployment_file.parent,
                        local=True,
                    )
        except RetryError as e:
            uvicorn_p.terminate()
            last: Optional[BaseException] = e.last_attempt.exception(0)
            last_msg = ""
            if last is not None:
                last_msg = ": " + (
                    str(last.message) if hasattr(last, "message") else str(last)
                )
            raise click.ClickException(f"Failed to create deployment{last_msg}")

        uvicorn_p.wait()

    except KeyboardInterrupt:
        print("Shutting down...")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        raise click.Abort()
