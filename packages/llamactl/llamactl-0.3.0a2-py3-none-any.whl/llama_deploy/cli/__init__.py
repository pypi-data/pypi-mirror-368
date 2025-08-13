import click
from .commands import projects, deployments, profile, health_check, serve, version
from .options import global_options


# Main CLI application
@click.group(help="LlamaDeploy CLI - Manage projects and deployments")
@global_options
def app():
    """LlamaDeploy CLI - Manage projects and deployments"""
    pass


# Add sub-commands
app.add_command(profile, name="profile")
app.add_command(projects, name="project")
app.add_command(deployments, name="deployment")

# Add health check at root level
app.add_command(health_check, name="health")

# Add serve command at root level
app.add_command(serve, name="serve")

# Add version command at root level
app.add_command(version, name="version")


# Main entry point function (called by the script)
def main() -> None:
    app()


if __name__ == "__main__":
    app()
