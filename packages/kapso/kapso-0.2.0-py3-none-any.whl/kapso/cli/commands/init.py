"""
Implementation of the init command for the Kapso CLI.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress

from kapso.cli.services.project import ProjectService

app = typer.Typer(name="init", help="Initialize a new Kapso project.")
console = Console()

@app.callback(invoke_without_command=True)
def init(
    ctx: typer.Context,
    path: str = typer.Argument(
        ".",
        help="Path to create the project in."
    ),
    template: str = typer.Option(
        "basic",
        "--template",
        "-t",
        help="Template to use for the project (basic, support, knowledge-base)."
    ),
):
    """
    Initialize a new Kapso project.
    
    Creates a new project directory with the necessary files to get started.
    """
    # If subcommand was invoked, we skip this
    if ctx.invoked_subcommand is not None:
        return
        
    common_options = ctx.obj
    verbose = common_options.verbose if common_options else False
    config_file = common_options.config_file if common_options else "kapso.yaml"
    
    if verbose:
        console.print("Verbose mode enabled")
        console.print(f"Using config file: {config_file}")
    
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        console.print(f"Creating directory: {project_path}")
        project_path.mkdir(parents=True)
    
    if any(project_path.iterdir()):
        console.print("[yellow]Warning: Directory is not empty.[/yellow]")
        if not typer.confirm("Continue anyway?"):
            console.print("Aborted.")
            return
    
    project_service = ProjectService()
    
    with Progress() as progress:
        task = progress.add_task("Creating project...", total=5)
        
        (project_path / "knowledge").mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        progress.update(task, advance=1)
        
        project_service.create_example_agent(project_path, template)
        progress.update(task, advance=1)
        
        project_service.create_example_test(project_path, template)
        progress.update(task, advance=1)
        
        project_service.create_kapso_yaml(project_path, template)
        progress.update(task, advance=1)
        
        project_service.create_env_example(project_path)
        progress.update(task, advance=1)
    
    console.print(f"[green]Project initialized successfully at: {project_path}[/green]")
    console.print("To get started, run:")
    if path != ".":
        console.print(f"  cd {path}")
    console.print("  kapso run")
