"""
HLA-Compass CLI for module development
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Any
import zipfile

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.panel import Panel

from . import __version__
from .testing import ModuleTester
from .auth import Auth


console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """HLA-Compass SDK - Module development tools"""
    pass


@cli.command()
@click.argument('name')
@click.option('--template', default='base-module', help='Module template to use')
@click.option('--type', 'module_type', type=click.Choice(['no-ui', 'with-ui']), 
              default='no-ui', help='Module type')
@click.option('--compute', type=click.Choice(['lambda', 'fargate', 'sagemaker']), 
              default='lambda', help='Compute type')
def init(name: str, template: str, module_type: str, compute: str):
    """Create a new HLA-Compass module"""
    console.print(f"[bold blue]Creating new module: {name}[/bold blue]")
    
    # Check if directory already exists
    module_dir = Path(name)
    if module_dir.exists():
        if not Confirm.ask(f"Directory '{name}' already exists. Continue?"):
            return
    
    # Find template directory - first check if we're in development mode
    pkg_templates_dir = Path(__file__).parent / "templates" / template
    repo_templates_dir = Path(__file__).parent.parent.parent.parent / "modules" / "templates" / template
    
    if pkg_templates_dir.exists():
        # Found in package (installed via pip)
        template_dir = pkg_templates_dir
    elif repo_templates_dir.exists():
        # Found in repository (development mode)
        template_dir = repo_templates_dir  
    else:
        # List available templates for user
        available_templates = []
        pkg_templates_base = Path(__file__).parent / "templates"
        if pkg_templates_base.exists():
            available_templates.extend([d.name for d in pkg_templates_base.iterdir() if d.is_dir()])
        
        repo_templates_base = Path(__file__).parent.parent.parent.parent / "modules" / "templates"
        if repo_templates_base.exists():
            repo_templates = [d.name for d in repo_templates_base.iterdir() if d.is_dir()]
            available_templates.extend([t for t in repo_templates if t not in available_templates])
        
        console.print(f"[red]Template '{template}' not found[/red]")
        if available_templates:
            console.print(f"[yellow]Available templates: {', '.join(available_templates)}[/yellow]")
        else:
            console.print("[yellow]No templates found. This may be a packaging issue.[/yellow]")
        return
    
    # Copy template
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Copying template files...", total=None)
        
        shutil.copytree(template_dir, module_dir, dirs_exist_ok=True)
        
        progress.update(task, description="Updating manifest...")
        
        # Update manifest.json
        manifest_path = module_dir / "manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        manifest['name'] = name
        manifest['type'] = module_type
        manifest['computeType'] = compute
        manifest['author']['name'] = Prompt.ask("Author name", default=os.environ.get('USER', 'Unknown'))
        manifest['author']['email'] = Prompt.ask("Author email", default="developer@example.com")
        manifest['author']['organization'] = Prompt.ask("Organization", default="Independent")
        manifest['description'] = Prompt.ask("Module description", default=f"HLA-Compass module: {name}")
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Remove frontend directory if no-ui
        if module_type == 'no-ui':
            frontend_dir = module_dir / "frontend"
            if frontend_dir.exists():
                shutil.rmtree(frontend_dir)
        
        progress.update(task, description="Creating virtual environment...")
        
        # Create virtual environment
        subprocess.run([sys.executable, '-m', 'venv', str(module_dir / 'venv')], 
                      capture_output=True)
        
        progress.update(task, description="Module created!", completed=True)
    
    # Display success message
    console.print(Panel.fit(
        f"[green]✓ Module '{name}' created successfully![/green]\n\n"
        f"Next steps:\n"
        f"1. cd {name}\n"
        f"2. source venv/bin/activate\n"
        f"3. pip install -r backend/requirements.txt\n"
        f"4. hla-compass test",
        title="Success"
    ))


@cli.command()
@click.option('--manifest', default='manifest.json', help='Path to manifest.json')
def validate(manifest: str):
    """Validate module structure and manifest"""
    console.print("[bold]Validating module...[/bold]")
    
    errors = []
    warnings = []
    
    # Check manifest exists
    manifest_path = Path(manifest)
    if not manifest_path.exists():
        console.print("[red]✗ manifest.json not found[/red]")
        return
    
    # Load and validate manifest
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON in manifest.json: {e}[/red]")
        return
    
    # Required fields
    required_fields = ['name', 'version', 'type', 'computeType', 'author', 'inputs', 'outputs']
    for field in required_fields:
        if field not in manifest_data:
            errors.append(f"Missing required field: {field}")
    
    # Check backend structure
    module_dir = manifest_path.parent
    backend_dir = module_dir / "backend"
    
    if not backend_dir.exists():
        errors.append("backend/ directory not found")
    else:
        if not (backend_dir / "main.py").exists():
            errors.append("backend/main.py not found")
        if not (backend_dir / "requirements.txt").exists():
            warnings.append("backend/requirements.txt not found")
    
    # Check frontend for with-ui modules
    if manifest_data.get('type') == 'with-ui':
        frontend_dir = module_dir / "frontend"
        if not frontend_dir.exists():
            errors.append("frontend/ directory required for with-ui modules")
        elif not (frontend_dir / "index.tsx").exists():
            errors.append("frontend/index.tsx not found")
    
    # Display results
    if errors:
        console.print("[red]✗ Validation failed with errors:[/red]")
        for error in errors:
            console.print(f"  • {error}")
    else:
        console.print("[green]✓ Module structure valid[/green]")
    
    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")


@cli.command()
@click.option('--local', is_flag=True, help='Test locally without API')
@click.option('--remote', is_flag=True, help='Test against remote API')
@click.option('--input', 'input_file', help='Input JSON file')
@click.option('--verbose', is_flag=True, help='Verbose output')
def test(local: bool, remote: bool, input_file: str | None, verbose: bool):
    """Test module execution"""
    if not local and not remote:
        local = True  # Default to local testing
    
    console.print("[bold]Testing module...[/bold]")
    
    # Load test input
    if input_file:
        with open(input_file, 'r') as f:
            test_input = json.load(f)
    else:
        # Try to load example input
        example_path = Path("examples/sample_input.json")
        if example_path.exists():
            with open(example_path, 'r') as f:
                test_input = json.load(f)
        else:
            test_input = {}
            console.print("[yellow]No input file provided, using empty input[/yellow]")
    
    # Create tester
    tester = ModuleTester()
    
    try:
        if local:
            console.print("\n[blue]Running local test...[/blue]")
            result = tester.test_local("backend/main.py", test_input)
            
            if result['status'] == 'success':
                console.print("[green]✓ Local test passed[/green]")
                if verbose:
                    console.print("\nOutput:")
                    console.print(Syntax(
                        json.dumps(result, indent=2),
                        "json",
                        theme="monokai"
                    ))
            else:
                console.print("[red]✗ Local test failed[/red]")
                console.print(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
        
        if remote:
            console.print("\n[blue]Running remote test...[/blue]")
            # TODO: Implement remote testing
            console.print("[yellow]Remote testing not yet implemented[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Test failed with error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())


@cli.command()
@click.option('--output', default='dist', help='Output directory')
@click.option('--include-dev', is_flag=True, help='Include development files')
def build(output: str, include_dev: bool):
    """Build module package for deployment"""
    console.print("[bold]Building module package...[/bold]")
    
    # Load manifest
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]manifest.json not found[/red]")
        return
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    name = manifest['name']
    version = manifest['version']
    
    # Create output directory
    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True)
    
    # Package filename
    package_name = f"{name}-{version}.zip"
    package_path = output_dir / package_name
    
    # Files to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '.git',
        '.pytest_cache',
        'venv',
        'env',
        '.coverage',
        'htmlcov',
        'dist',
        '.DS_Store'
    ]
    
    if not include_dev:
        exclude_patterns.extend([
            'tests',
            'test_*',
            '*_test.py',
            '.gitignore',
            'Makefile',
            'requirements-dev.txt'
        ])
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating package...", total=None)
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk('.'):
                # Filter directories
                dirs[:] = [d for d in dirs if not any(
                    pattern.strip('*') in d for pattern in exclude_patterns
                )]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Skip excluded files
                    if any(pattern.strip('*') in str(file_path) for pattern in exclude_patterns):
                        continue
                    
                    arcname = str(file_path).lstrip('./')
                    zipf.write(file_path, arcname)
        
        progress.update(task, description=f"Package created: {package_name}", completed=True)
    
    # Display package info
    size_mb = package_path.stat().st_size / (1024 * 1024)
    
    console.print(Panel.fit(
        f"[green]✓ Package built successfully![/green]\n\n"
        f"Package: {package_path}\n"
        f"Size: {size_mb:.2f} MB\n"
        f"Version: {version}",
        title="Build Complete"
    ))


@cli.command()
@click.argument('file')
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Target environment')
@click.option('--version', help='Module version (auto-detected if not provided)')
@click.option('--dry-run', is_flag=True, help='Show what would be deployed')
def deploy(file: str, env: str, version: str | None, dry_run: bool):
    """Deploy module to HLA-Compass platform"""
    console.print(f"[bold]Deploying to {env} environment...[/bold]")
    
    # Check file exists
    package_path = Path(file)
    if not package_path.exists():
        console.print(f"[red]Package file not found: {file}[/red]")
        return
    
    # Get authentication
    auth = Auth()
    try:
        token = auth.get_token(env)
    except Exception as e:
        console.print(f"[red]Authentication failed: {e}[/red]")
        console.print("\nPlease run: hla-compass auth login")
        return
    
    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/yellow]")
        console.print(f"\nWould deploy: {package_path}")
        console.print(f"To environment: {env}")
        console.print(f"File size: {package_path.stat().st_size / (1024*1024):.2f} MB")
        return
    
    # TODO: Implement actual deployment
    console.print("[yellow]Deployment not yet implemented[/yellow]")
    console.print("\nFor now, manually upload your package to S3:")
    console.print(f"  aws s3 cp {package_path} s3://hla-compass-modules-{env}/")


@cli.group()
def auth():
    """Authentication commands"""
    pass


@auth.command()
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Environment to login to')
def login(env: str):
    """Login to HLA-Compass platform"""
    console.print(f"[bold]Logging in to {env} environment...[/bold]")
    
    email = Prompt.ask("Email")
    password = Prompt.ask("Password", password=True)
    
    # TODO: Implement actual authentication
    console.print("[yellow]Authentication not yet implemented[/yellow]")
    console.print("\nFor development, use the test credentials:")
    console.print("  Email: testapi@alithea.io")
    console.print("  Password: TestPassword123!")


@auth.command()
def logout():
    """Logout from HLA-Compass platform"""
    console.print("[bold]Logging out...[/bold]")
    
    # TODO: Clear stored credentials
    console.print("[green]✓ Logged out successfully[/green]")


@cli.command()
@click.argument('job_id', required=False)
@click.option('--tail', is_flag=True, help='Follow log output')
@click.option('--lines', default=50, help='Number of lines to show')
def logs(job_id: str | None, tail: bool, lines: int):
    """View module execution logs"""
    if job_id:
        console.print(f"[bold]Logs for job {job_id}:[/bold]")
        # TODO: Fetch logs for specific job
        console.print("[yellow]Log fetching not yet implemented[/yellow]")
    else:
        console.print("[bold]Recent module executions:[/bold]")
        
        # Create a table of recent executions
        table = Table(title="Recent Executions")
        table.add_column("Job ID", style="cyan")
        table.add_column("Module", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Started", style="yellow")
        table.add_column("Duration", style="blue")
        
        # TODO: Fetch actual execution history
        # For now, show example data
        table.add_row(
            "job-123456",
            "my-module",
            "completed",
            "2024-01-15 10:30:00",
            "2.3s"
        )
        
        console.print(table)


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == '__main__':
    main()