"""
Implementation of the functions commands for the Kapso CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from kapso.cli.services.auth_service import AuthService
from kapso.cli.services.api_service import ApiManager
from kapso.cli.utils.project_config import get_project_id

app = typer.Typer(name="functions", help="Manage Kapso Functions")
console = Console()


def ensure_authenticated_and_project():
    """Ensure user is authenticated and optionally has a project selected."""
    auth_service = AuthService()
    
    # Check if we have KAPSO_API_KEY environment variable
    if "KAPSO_API_KEY" not in os.environ and not auth_service.is_authenticated():
        console.print("[yellow]You need to be logged in to manage functions.[/yellow]")
        console.print("Run 'kapso login' first.")
        sys.exit(1)
    
    # Get project ID - not required when using KAPSO_API_KEY
    project_id = get_project_id()
    if not project_id and "KAPSO_API_KEY" not in os.environ:
        console.print("[yellow]No project ID found. Run 'kapso init' to set up a project.[/yellow]")
        sys.exit(1)
        
    return auth_service, project_id


@app.command()
def push(
    file_path: str = typer.Argument(..., help="Path to the JavaScript function file"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Function name (defaults to filename)")
):
    """
    Upload a JavaScript function to Kapso.
    
    Creates a new function if it doesn't exist, or updates an existing one.
    """
    auth_service, project_id = ensure_authenticated_and_project()
    api_manager = ApiManager(auth_service)
    api_client = api_manager.project(project_id)
    
    # Check if file exists
    file_path = Path(file_path)
    if not file_path.exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        sys.exit(1)
    
    if not file_path.suffix == '.js':
        console.print("[red]Error: File must be a JavaScript file (.js)[/red]")
        sys.exit(1)
    
    # Read the file content
    try:
        with open(file_path, 'r') as f:
            code = f.read()
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        sys.exit(1)
    
    # Determine function name
    if not name:
        name = file_path.stem  # filename without extension
    
    console.print(f"Uploading function: {name}...")
    
    try:
        # Check if function already exists by listing all functions
        response = api_client.get("functions")
        functions = response.get('data', [])
        
        existing_function = None
        for func in functions:
            if func.get('name') == name:
                existing_function = func
                break
        
        if existing_function:
            # Update existing function
            console.print(f"Updating existing function: {name}")
            function_data = {
                "name": name,
                "code": code
            }
            response = api_client.patch(f"functions/{existing_function['id']}", {"function": function_data})
            function = response.get('data', response)
            
            # Deploy the updated function
            deploy_response = api_client.post(f"functions/{function['id']}/deploy", {})
            console.print(f"[green]Function updated: {name} ✓[/green]")
        else:
            # Create new function
            console.print(f"Creating new function: {name}")
            function_data = {
                "name": name,
                "code": code,
                "description": f"Function uploaded via CLI from {file_path.name}"
            }
            response = api_client.post("functions", {"function": function_data})
            function = response.get('data', response)
            
            # Deploy the new function
            deploy_response = api_client.post(f"functions/{function['id']}/deploy", {})
            console.print(f"[green]Function created: {name} ✓[/green]")
        
        # Show the function URL
        if function.get('endpoint_url'):
            console.print(f"URL: {function['endpoint_url']}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def list():
    """List all functions in the current project."""
    auth_service, project_id = ensure_authenticated_and_project()
    api_manager = ApiManager(auth_service)
    api_client = api_manager.project(project_id)
    
    try:
        response = api_client.get("functions")
        functions = response.get('data', [])
        
        if not functions:
            console.print("[yellow]No functions found in this project.[/yellow]")
            return
        
        # Create a table
        table = Table(title="Functions")
        table.add_column("NAME", style="cyan")
        table.add_column("STATUS", style="green")
        table.add_column("UPDATED", style="dim")
        table.add_column("INVOKE URL", style="blue")
        
        for func in functions:
            status = func.get('status', 'unknown')
            if status == 'deployed':
                status_display = "[green]deployed[/green]"
            elif status == 'error':
                status_display = "[red]error[/red]"
            else:
                status_display = "[yellow]draft[/yellow]"
            
            # Format updated_at
            updated_at = func.get('updated_at', '')
            if updated_at:
                # Simple relative time formatting
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    now = datetime.now(dt.tzinfo)
                    diff = now - dt
                    
                    if diff.days > 0:
                        updated_display = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
                    elif diff.seconds > 3600:
                        hours = diff.seconds // 3600
                        updated_display = f"{hours} hour{'s' if hours > 1 else ''} ago"
                    else:
                        minutes = diff.seconds // 60
                        updated_display = f"{minutes} min ago"
                except:
                    updated_display = updated_at
            else:
                updated_display = "-"
            
            # Get the endpoint URL
            endpoint_url = func.get('endpoint_url', '')
            if endpoint_url and status == 'deployed':
                url_display = endpoint_url
            else:
                url_display = "-"
            
            table.add_row(
                func.get('name', 'Unnamed'),
                status_display,
                updated_display,
                url_display
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def pull(
    name: str = typer.Argument(..., help="Function name to download"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (defaults to functions/<name>.js)")
):
    """Download a function from Kapso."""
    auth_service, project_id = ensure_authenticated_and_project()
    api_manager = ApiManager(auth_service)
    api_client = api_manager.project(project_id)
    
    try:
        # Find the function by name
        response = api_client.get("functions")
        functions = response.get('data', [])
        
        target_function = None
        for func in functions:
            if func.get('name') == name:
                target_function = func
                break
        
        if not target_function:
            console.print(f"[red]Error: Function '{name}' not found[/red]")
            sys.exit(1)
        
        # Get the full function details
        response = api_client.get(f"functions/{target_function['id']}")
        function = response.get('data', response)
        
        # Determine output path
        if not output:
            # Create functions directory if it doesn't exist
            functions_dir = Path("functions")
            functions_dir.mkdir(exist_ok=True)
            output_path = functions_dir / f"{name}.js"
        else:
            output_path = Path(output)
            # Create parent directories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the function code
        with open(output_path, 'w') as f:
            f.write(function.get('code', ''))
        
        console.print(f"[green]Downloaded to: {output_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()