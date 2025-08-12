from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import typer
import rich

if TYPE_CHECKING:
    from collections.abc import Callable


console = rich.get_console()
create_app = typer.Typer(
    name="create",
    help="🛠️ Create new models, detectors, and environments from templates",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@create_app.command(name="model")
def cli_create_model(
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Name for the new model organism (alphanumeric and underscores only)",
        rich_help_panel="📋 Required",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing model organism if it exists",
        rich_help_panel="🔧 Options",
    ),
) -> None:
    """
    🛠️ Create a new model organism from the default template.
    """
    from bench_af.util import create_new_model_organism, list_model_organisms
    _handle_resource_creation(name, "model organism", list_model_organisms, create_new_model_organism, "models", force)


@create_app.command(name="detector")
def cli_create_detector(
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Name for the new detector (alphanumeric and underscores only)",
        rich_help_panel="📋 Required",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing detector if it exists",
        rich_help_panel="🔧 Options",
    ),
) -> None:
    """
    🛠️ Create a new detector from the default template.
    """
    from bench_af.util import create_new_detector, list_detectors
    _handle_resource_creation(
        name, "detector", list_detectors, create_new_detector, "detectors", force
    )


@create_app.command(name="environment")
def cli_create_environment(
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Name for the new environment (alphanumeric and underscores only)",
        rich_help_panel="📋 Required",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing environment if it exists",
        rich_help_panel="🔧 Options",
    ),
) -> None:
    """
    🛠️ Create a new environment from the default template.
    """
    from bench_af.util import create_new_environment, list_environments
    _handle_resource_creation(name, "environment", list_environments, create_new_environment, "environments", force)


@create_app.command(name="config")
def cli_create_config(
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Name for the config to orchestrate a new experiment",
        rich_help_panel="📋 Required",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing environment if it exists",
        rich_help_panel="🔧 Options",
    ),
) -> None:
    """
    🛠️ Create a new config from the default template.
    """
    from bench_af.util import create_new_config, list_configs
    _handle_resource_creation(name, "config", list_configs, create_new_config, "configs", force)


def _handle_resource_creation(
    name: str,
    resource_type: Literal["model organism", "detector", "environment", "config"],
    list_func: Callable[[], list[str]],
    create_func: Callable[[str], None],
    directory_name: Literal["models", "detectors", "environments", "configs"],
    force: bool = False,
) -> None:
    """
    Helper function to handle the common resource creation workflow.

    Args:
        name: Name of the resource to create
        resource_type: Name of the resource type
        list_func: Function to list existing resources
        create_func: Function to create the new resource
        directory_name: Directory where resources are stored
        force: Whether to overwrite existing resources
    """
    import shutil

    console.print(f"🛠️  [bold blue]Creating new {resource_type}:[/bold blue] [cyan]{name}[/cyan]")


    # Validate name format
    if not name.replace("_", "").replace("-", "").isalnum():
        console.print(
            "❌ [bold red]Invalid name format![/bold red]", style="red")
        console.print(
            f"💡 {resource_type.title()} names should contain only letters, numbers, underscores and dashes",
            style="dim",
        )
        raise typer.Exit(1)

    # Check if resource already exists
    existing_resources = list_func()
    if name in existing_resources:
        console.print(
            f"⚠️  [yellow]{resource_type.title()} '{name}' already exists![/yellow]"
        )
        if force:
            console.print(
                f"💡 Overwriting existing {resource_type}.", style="dim")
            shutil.rmtree(f"{directory_name}/{name}", ignore_errors=True)
        else:
            console.print(
                "💡 Use --force to overwrite, or choose a different name.", style="dim"
            )
            raise typer.Exit(1)

    # Create the resource
    create_func(name)

    # Success messages
    console.print(
        f"✅ [bold green]Successfully created {resource_type}:[/bold green] [cyan]{name}[/cyan]"
    )
    console.print(
        f"📁 Template files are available in: [dim]{directory_name}/{name}/[/dim]"
    )
    console.print(
        f"💡 Edit the template files to implement your {resource_type}.", style="dim"
    )
