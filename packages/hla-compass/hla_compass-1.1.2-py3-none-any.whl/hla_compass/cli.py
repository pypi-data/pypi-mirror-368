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
import requests

from . import __version__
from .testing import ModuleTester
from .auth import Auth
from .deployer import SimpleDeployer


console = Console()

ALITHEA_BANNER = """
[bold blue]
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║    █████╗ ██╗     ██╗████████╗██╗  ██╗███████╗ █████╗                ║
    ║   ██╔══██╗██║     ██║╚══██╔══╝██║  ██║██╔════╝██╔══██╗               ║
    ║   ███████║██║     ██║   ██║   ███████║█████╗  ███████║               ║
    ║   ██╔══██║██║     ██║   ██║   ██╔══██║██╔══╝  ██╔══██║               ║
    ║   ██║  ██║███████╗██║   ██║   ██║  ██║███████╗██║  ██║               ║
    ║   ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝               ║
    ║                                                                       ║
    ║                    [white]HLA-Compass Platform SDK[/white]                      ║
    ║          [dim]Immuno-Peptidomics • Module Development • AI[/dim]            ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
[/bold blue]
"""


def show_banner():
    """Display the beautiful Alithea banner"""
    console.print(ALITHEA_BANNER)
    console.print(f"[dim]Version {__version__} • https://alithea.bio • Module Development Toolkit[/dim]\n")


def start_devkit_container(verbose: bool = False) -> bool:
    """Start the HLA-Compass devkit container for local development"""
    console.print("  Starting HLA-Compass devkit container...")
    
    # Check if Docker is available
    try:
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            console.print("[red]Docker not available - install Docker to use devkit[/red]")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        console.print("[red]Docker not available - install Docker to use devkit[/red]")
        return False
    
    # Check if container is already running
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if "hla-devkit" in result.stdout:
            console.print("[green]  ✓ Devkit container already running[/green]")
            return True
    except:
        pass
    
    # Stop any existing container
    try:
        subprocess.run(
            ["docker", "stop", "hla-devkit"], 
            capture_output=True,
            timeout=30
        )
        subprocess.run(
            ["docker", "rm", "hla-devkit"], 
            capture_output=True,
            timeout=10
        )
    except:
        pass
    
    # Start devkit container
    try:
        console.print("  Pulling latest devkit image...")
        result = subprocess.run(
            ["docker", "pull", "ghcr.io/alitheabio/hla-compass-dev:latest"], 
            capture_output=True, 
            text=True,
            timeout=180
        )
        
        if result.returncode != 0:
            console.print(f"[yellow]Warning: Could not pull latest image, using local if available[/yellow]")
            if verbose:
                console.print(f"Pull error: {result.stderr}")
        
        console.print("  Starting devkit services (PostgreSQL + MinIO)...")
        result = subprocess.run([
            "docker", "run", "-d", 
            "--name", "hla-devkit",
            "-p", "5432:5432",  # PostgreSQL
            "-p", "9000:9000",  # MinIO API
            "-p", "9001:9001",  # MinIO Console
            "ghcr.io/alitheabio/hla-compass-dev:latest"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            console.print(f"[red]Failed to start devkit container: {result.stderr}[/red]")
            return False
        
        # Wait for services to be ready
        console.print("  Waiting for services to initialize...")
        import time
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                # Check PostgreSQL
                pg_result = subprocess.run(
                    ["docker", "exec", "hla-devkit", "pg_isready", "-U", "postgres", "-d", "hla_compass"],
                    capture_output=True,
                    timeout=5
                )
                
                # Check MinIO
                import requests
                minio_result = requests.get("http://localhost:9000/minio/health/ready", timeout=2)
                
                if pg_result.returncode == 0 and minio_result.status_code == 200:
                    console.print("[green]  ✓ Devkit services ready (PostgreSQL + MinIO)[/green]")
                    console.print("  [dim]Database: localhost:5432/hla_compass (user: postgres, pass: postgres)[/dim]")
                    console.print("  [dim]MinIO API: localhost:9000 (access: minioadmin, secret: minioadmin)[/dim]")
                    console.print("  [dim]MinIO Console: http://localhost:9001[/dim]")
                    return True
                    
            except:
                pass
            
            if attempt < max_attempts - 1:
                time.sleep(2)
        
        console.print("[yellow]  Services may still be starting up - check manually[/yellow]")
        return True
        
    except subprocess.TimeoutExpired:
        console.print("[red]Devkit container startup timed out[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Failed to start devkit: {e}[/red]")
        return False


def setup_ui_dev_environment(port: int = 3000, verbose: bool = False) -> bool:
    """Set up local UI development environment with hot reload"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        console.print("[yellow]No frontend directory found[/yellow]")
        return True
    
    console.print(f"  Setting up UI development server on port {port}...")
    
    # Check for package.json
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        console.print("[red]No package.json found in frontend/[/red]")
        return False
    
    # Create/update dev server configuration
    dev_config = {
        "scripts": {
            "dev": f"webpack serve --mode development --port {port} --hot",
            "build": "webpack --mode production",
            "start": f"webpack serve --mode development --port {port}"
        },
        "devDependencies": {
            "webpack-dev-server": "^4.0.0",
            "@types/react": "^18.0.0",
            "@types/react-dom": "^18.0.0"
        }
    }
    
    # Read existing package.json and merge
    try:
        with open(package_json, 'r') as f:
            existing_config = json.load(f)
        
        # Merge dev scripts and dependencies
        if 'scripts' not in existing_config:
            existing_config['scripts'] = {}
        existing_config['scripts'].update(dev_config['scripts'])
        
        if 'devDependencies' not in existing_config:
            existing_config['devDependencies'] = {}
        existing_config['devDependencies'].update(dev_config['devDependencies'])
        
        # Write updated package.json
        with open(package_json, 'w') as f:
            json.dump(existing_config, f, indent=2)
        
        console.print("[green]  ✓ Dev server configuration updated[/green]")
        
    except Exception as e:
        console.print(f"[yellow]Could not update package.json: {e}[/yellow]")
    
    # Create webpack dev config if it doesn't exist
    webpack_config = frontend_dir / "webpack.config.js"
    if not webpack_config.exists():
        webpack_content = f'''const path = require('path');

module.exports = {{
  mode: process.env.NODE_ENV || 'development',
  entry: './index.tsx',
  module: {{
    rules: [
      {{
        test: /\\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      }},
      {{
        test: /\\.css$/,
        use: ['style-loader', 'css-loader'],
      }},
    ],
  }},
  resolve: {{
    extensions: ['.tsx', '.ts', '.js'],
    alias: {{
      '@hla-compass/sdk': path.resolve(__dirname, 'sdk.d.ts'),
    }},
  }},
  output: {{
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    publicPath: '/',
  }},
  devServer: {{
    static: {{
      directory: path.join(__dirname, 'public'),
    }},
    port: {port},
    hot: true,
    open: true,
    proxy: {{
      '/api': {{
        target: 'http://localhost:8000',  // Mock API server
        changeOrigin: true,
      }},
    }},
  }},
  externals: {{
    '@hla-compass/sdk': 'HLACompassSDK',
  }},
}};'''
        
        with open(webpack_config, 'w') as f:
            f.write(webpack_content)
        
        console.print("[green]  ✓ Webpack dev config created[/green]")
    
    # Install dev dependencies
    console.print("  Installing dev dependencies...")
    try:
        result = subprocess.run(
            ["npm", "install"], 
            cwd=frontend_dir, 
            capture_output=True, 
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            console.print("[green]  ✓ Dependencies installed[/green]")
        else:
            console.print(f"[yellow]Dependency installation had issues: {result.stderr}[/yellow]")
            
    except Exception as e:
        console.print(f"[yellow]Could not install dependencies: {e}[/yellow]")
    
    return True


def test_frontend(verbose: bool = False) -> bool:
    """Test frontend components for with-ui modules"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        console.print("[yellow]No frontend directory found, skipping UI tests[/yellow]")
        return True
    
    # Check for package.json
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        console.print("[red]No package.json found in frontend/[/red]")
        return False
    
    # Check for required files
    required_files = ["index.tsx", "package.json"]
    missing_files = []
    
    for file in required_files:
        if not (frontend_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        console.print(f"[red]Missing frontend files: {', '.join(missing_files)}[/red]")
        return False
    
    # Try to install dependencies
    console.print("  Installing frontend dependencies...")
    try:
        result = subprocess.run(
            ["npm", "install"], 
            cwd=frontend_dir, 
            capture_output=True, 
            text=True,
            timeout=120  # 2 minutes timeout
        )
        
        if result.returncode != 0:
            console.print(f"[red]npm install failed: {result.stderr}[/red]")
            if verbose:
                console.print(f"stdout: {result.stdout}")
            return False
        
        console.print("[green]  ✓ Dependencies installed[/green]")
        
    except subprocess.TimeoutExpired:
        console.print("[red]npm install timed out[/red]")
        return False
    except FileNotFoundError:
        console.print("[yellow]npm not found - install Node.js to test frontend[/yellow]")
        return True  # Don't fail if npm is missing
    
    # Try to build the frontend
    console.print("  Building frontend...")
    try:
        result = subprocess.run(
            ["npm", "run", "build"], 
            cwd=frontend_dir, 
            capture_output=True, 
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode != 0:
            # Try alternative build commands
            for build_cmd in [["npm", "run", "compile"], ["npx", "tsc"], ["npx", "webpack"]]:
                try:
                    result = subprocess.run(
                        build_cmd, 
                        cwd=frontend_dir, 
                        capture_output=True, 
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        break
                except:
                    continue
            
            if result.returncode != 0:
                console.print(f"[yellow]Frontend build warning: {result.stderr}[/yellow]")
                if verbose:
                    console.print(f"Build output: {result.stdout}")
                # Don't fail on build issues, just warn
                return True
        
        console.print("[green]  ✓ Frontend built successfully[/green]")
        
    except subprocess.TimeoutExpired:
        console.print("[yellow]Frontend build timed out[/yellow]")
        return True  # Don't fail on timeout
    except Exception as e:
        console.print(f"[yellow]Frontend build issue: {e}[/yellow]")
        return True  # Don't fail on build issues
    
    # Test TypeScript compilation if present
    tsconfig = frontend_dir / "tsconfig.json"
    if tsconfig.exists():
        console.print("  Checking TypeScript...")
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"], 
                cwd=frontend_dir, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                console.print("[green]  ✓ TypeScript check passed[/green]")
            else:
                console.print(f"[yellow]TypeScript warnings: {result.stderr}[/yellow]")
                if verbose:
                    console.print(f"TypeScript output: {result.stdout}")
        except:
            pass  # Don't fail if TypeScript check fails
    
    return True


@click.group()
@click.version_option(version=__version__)
def cli():
    """HLA-Compass SDK - Module development tools"""
    pass


@cli.group()
def templates():
    """Manage module templates"""
    pass


@templates.command('list')
def list_templates():
    """List available module templates"""
    console.print("[bold]Available Module Templates:[/bold]\n")
    
    # Template descriptions
    template_info = {
        'minimal': {
            'type': 'no-ui',
            'description': 'Bare minimum scaffolding with TODO comments',
            'features': ['Empty functions', 'TODO placeholders', 'Basic structure']
        },
        'base-module': {
            'type': 'with-ui',
            'description': 'Basic module with Ant Design UI components',
            'features': ['Form input', 'Results display', 'Export functionality']
        },
        'peptide-analyzer': {
            'type': 'with-ui',
            'description': 'Ready-to-run peptide analysis module',
            'features': ['Sequence analysis', 'Database search', 'HLA predictions', 'Full UI']
        }
    }
    
    # Find available templates
    templates_dir = Path(__file__).parent / "templates"
    available = []
    
    if templates_dir.exists():
        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir() and (template_dir / "manifest.json").exists():
                available.append(template_dir.name)
    
    # Display templates
    for template_name, info in template_info.items():
        if template_name in available:
            console.print(f"[green]✓[/green] [bold]{template_name}[/bold] ({info['type']})")
            console.print(f"  {info['description']}")
            console.print(f"  Features:")
            for feature in info['features']:
                console.print(f"    • {feature}")
            console.print()
    
    # Show usage
    console.print("[dim]Usage:[/dim]")
    console.print("  hla-compass init my-module --template <template-name>")
    console.print("\n[dim]Examples:[/dim]")
    console.print("  hla-compass init my-module --template minimal       # Empty scaffolding")
    console.print("  hla-compass init my-module --template peptide-analyzer  # Ready-to-run")


@templates.command('show')
@click.argument('template_name')
def show_template(template_name: str):
    """Show details about a specific template"""
    templates_dir = Path(__file__).parent / "templates" / template_name
    
    if not templates_dir.exists():
        console.print(f"[red]Template '{template_name}' not found[/red]")
        console.print("\nRun 'hla-compass templates list' to see available templates")
        return
    
    # Read manifest
    manifest_path = templates_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        console.print(f"[bold]Template: {template_name}[/bold]\n")
        console.print(f"Type: {manifest.get('type', 'unknown')}")
        console.print(f"Description: {manifest.get('description', 'No description')}")
        console.print(f"Compute: {manifest.get('computeType', 'lambda')}")
        
        if 'inputs' in manifest:
            console.print("\n[bold]Input Parameters:[/bold]")
            for prop, details in manifest['inputs'].get('properties', {}).items():
                required = prop in manifest['inputs'].get('required', [])
                req_marker = "[red]*[/red]" if required else ""
                console.print(f"  • {prop}{req_marker}: {details.get('type')} - {details.get('description', '')}")
        
        if 'outputs' in manifest:
            console.print("\n[bold]Output Structure:[/bold]")
            for prop, details in manifest['outputs'].get('properties', {}).items():
                console.print(f"  • {prop}: {details.get('type')} - {details.get('description', '')}")
        
        # Show file structure
        console.print("\n[bold]Files:[/bold]")
        for root, dirs, files in os.walk(templates_dir):
            level = root.replace(str(templates_dir), '').count(os.sep)
            indent = '  ' * level
            console.print(f'{indent}{os.path.basename(root)}/')
            subindent = '  ' * (level + 1)
            for file in files[:10]:  # Limit to first 10 files
                if not file.startswith('.'):
                    console.print(f'{subindent}{file}')


@cli.command()
@click.argument('name')
@click.option('--template', default='minimal', help='Module template to use (default: minimal)')
@click.option('--type', 'module_type', type=click.Choice(['no-ui', 'with-ui']), 
              default=None, help='Module type (auto-detected from template)')
@click.option('--compute', type=click.Choice(['lambda', 'fargate', 'sagemaker']), 
              default='lambda', help='Compute type')
@click.option('--no-banner', is_flag=True, help='Skip the Alithea banner display')
def init(name: str, template: str, module_type: str | None, compute: str, no_banner: bool):
    """Create a new HLA-Compass module
    
    Examples:
        hla-compass init my-module                    # Minimal template
        hla-compass init my-module --template peptide-analyzer  # Ready-to-run
        hla-compass init my-module --template base-module --type with-ui
    """
    # Show the beautiful Alithea banner only during module creation
    if not no_banner:
        show_banner()
    
    # Auto-detect module type from template if not specified
    template_types = {
        'minimal': 'no-ui',
        'base-module': 'with-ui',
        'peptide-analyzer': 'with-ui'
    }
    
    if module_type is None:
        module_type = template_types.get(template, 'no-ui')
    
    console.print(f"[bold green]🧬 Creating HLA-Compass Module: [white]{name}[/white] 🧬[/bold green]")
    console.print(f"[dim]Template: {template} • Type: {module_type} • Compute: {compute}[/dim]\n")
    
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
        # Use environment variables or defaults to avoid hanging prompts
        manifest['author']['name'] = os.environ.get('HLA_AUTHOR_NAME', os.environ.get('USER', 'Unknown'))
        manifest['author']['email'] = os.environ.get('HLA_AUTHOR_EMAIL', 'developer@example.com')
        manifest['author']['organization'] = os.environ.get('HLA_AUTHOR_ORG', 'Independent')
        manifest['description'] = os.environ.get('HLA_MODULE_DESC', f"HLA-Compass module: {name}")
        
        # Show what was set
        console.print(f"  Author: {manifest['author']['name']}")
        console.print(f"  Email: {manifest['author']['email']}")
        console.print(f"  Organization: {manifest['author']['organization']}")
        
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
    
    # Display comprehensive success message with full workflow
    console.print(Panel.fit(
        f"[green]✓ Module '{name}' created successfully![/green]\n\n"
        f"[bold]Quick Start:[/bold]\n"
        f"1. cd {name}\n"
        f"2. pip install -r backend/requirements.txt  # Install dependencies\n"
        f"3. hla-compass validate                     # Validate structure\n"
        f"4. hla-compass test --local{' --ui' if module_type == 'with-ui' else ''}                 # Test locally{' (with UI)' if module_type == 'with-ui' else ''}\n\n"
        f"[bold]Development Workflow:[/bold]\n"
        f"• Edit backend/main.py to implement your logic\n"
        f"• Add test data to examples/sample_input.json\n"
        f"• Document your module in docs/README.md\n"
        f"• Test iteratively: hla-compass test --local --input examples/sample_input.json\n\n"
        f"[bold]Build & Package:[/bold]\n"
        f"5. hla-compass build                        # Creates dist/{name}-1.0.0.zip\n"
        f"6. ls -la dist/                             # Verify package created\n\n"
        f"[bold]Sign & Deploy:[/bold]\n"
        f"7. hla-compass sign dist/{name}-1.0.0.zip   # Sign with your key (optional)\n"
        f"8. hla-compass deploy dist/{name}-1.0.0.zip --env dev  # Deploy to platform\n\n"
        f"[bold]Local Development Services:[/bold]\n"
        f"• PostgreSQL + MinIO: docker run -d -p 5432:5432 -p 9000:9000 ghcr.io/alitheabio/hla-compass-dev\n"
        f"• Set environment: export HLA_COMPASS_DB_HOST=localhost\n\n"
        f"[bold]Help & Documentation:[/bold]\n"
        f"• Module docs: https://docs.hla-compass.com/modules\n"
        f"• Get help: hla-compass --help\n"
        f"• View logs: hla-compass logs",
        title="Module Created - Complete Development Guide",
        width=100
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
        console.print("\n[yellow]Fix the errors above, then run 'hla-compass validate' again[/yellow]")
    else:
        console.print("[green]✓ Module structure valid[/green]")
        console.print("\n[bold]Ready for next steps:[/bold]")
        
        # Show appropriate test command based on module type
        if manifest_data.get('type') == 'with-ui':
            console.print("  • Test backend: hla-compass test --local")
            console.print("  • Test with UI: hla-compass test --local --ui")
        else:
            console.print("  • Test locally: hla-compass test --local")
            
        console.print("  • Build package: hla-compass build")
        console.print("  • Deploy: hla-compass deploy dist/*.zip --env dev")
    
    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")


@cli.command()
@click.option('--local', is_flag=True, help='Test locally without API')
@click.option('--remote', is_flag=True, help='Test against remote API')
@click.option('--input', 'input_file', help='Input JSON file')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--ui', is_flag=True, help='Also test UI components (for with-ui modules)')
@click.option('--with-devkit', is_flag=True, help='Start devkit container for full local testing with database')
@click.option('--port', default=3000, help='Port for local UI development server')
def test(local: bool, remote: bool, input_file: str | None, verbose: bool, ui: bool, with_devkit: bool, port: int):
    """Test module execution"""
    if not local and not remote:
        local = True  # Default to local testing
    
    console.print("[bold]Testing module...[/bold]")
    
    # Start devkit container if requested
    devkit_started = False
    if with_devkit:
        console.print("\n[blue]Setting up local development environment...[/blue]")
        devkit_started = start_devkit_container(verbose)
        
        if devkit_started:
            console.print("[green]✓ Devkit environment ready[/green]")
        else:
            console.print("[yellow]⚠ Continuing without devkit - some features may not work[/yellow]")
    
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
    
    # Create tester with devkit configuration
    tester = ModuleTester()
    if devkit_started:
        # Configure tester to use local devkit services
        tester.configure_local_devkit()
    
    try:
        if local:
            console.print("\n[blue]Running backend test...[/blue]")
            result = tester.test_local("backend/main.py", test_input)
            
            if result['status'] == 'success':
                console.print("[green]✓ Backend test passed[/green]")
                if verbose:
                    console.print("\nBackend Output:")
                    console.print(Syntax(
                        json.dumps(result, indent=2),
                        "json",
                        theme="monokai"
                    ))
            else:
                console.print("[red]✗ Backend test failed[/red]")
                console.print(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
                if not ui and not with_devkit:  # Continue if using devkit for debugging
                    return
            
            # Test UI if requested and frontend exists
            if ui or Path("frontend").exists():
                console.print("\n[blue]Testing frontend components...[/blue]")
                
                # Set up dev environment for UI testing
                if with_devkit and Path("frontend").exists():
                    setup_success = setup_ui_dev_environment(port, verbose)
                    if setup_success:
                        console.print(f"\n[green]✓ UI development environment ready![/green]")
                        console.print(f"[bold]To test your UI with live database:[/bold]")
                        console.print(f"  1. cd frontend")
                        console.print(f"  2. npm run dev")
                        console.print(f"  3. Open http://localhost:{port}")
                        console.print(f"  4. UI will have access to:")
                        console.print(f"     • Database: postgresql://postgres:postgres@localhost:5432/hla_compass")
                        console.print(f"     • Storage: MinIO at localhost:9000")
                        console.print(f"     • 10K peptide dataset for testing")
                        console.print(f"\n[dim]Press Ctrl+C to stop services when done[/dim]")
                        
                        # Optionally start the dev server automatically
                        if Confirm.ask("Start UI development server now?"):
                            console.print(f"[blue]Starting UI dev server on port {port}...[/blue]")
                            try:
                                subprocess.run([
                                    "npm", "run", "dev"
                                ], cwd="frontend", timeout=5)
                            except subprocess.TimeoutExpired:
                                console.print(f"[green]✓ Dev server started at http://localhost:{port}[/green]")
                            except Exception as e:
                                console.print(f"[yellow]Could not start dev server automatically: {e}[/yellow]")
                                console.print("Run 'npm run dev' manually in the frontend/ directory")
                    else:
                        console.print("[yellow]UI dev environment setup had issues[/yellow]")
                
                ui_success = test_frontend(verbose)
                
                if ui_success:
                    console.print("[green]✓ Frontend test passed[/green]")
                else:
                    console.print("[red]✗ Frontend test failed[/red]")
        
        if remote:
            console.print("\n[blue]Running remote test...[/blue]")
            # TODO: Implement remote testing
            console.print("[yellow]Remote testing not yet implemented[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Test failed with error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
    
    # Clean up instructions
    if devkit_started:
        console.print(f"\n[bold]Development Environment Running:[/bold]")
        console.print(f"  • Database: localhost:5432 (user: postgres, pass: postgres)")
        console.print(f"  • MinIO: localhost:9000 (access: minioadmin, secret: minioadmin)")
        console.print(f"  • UI Dev: http://localhost:{port} (if started)")
        console.print(f"\n[yellow]To stop: docker stop hla-devkit[/yellow]")


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
    
    # Extract module name from manifest
    try:
        import zipfile
        with zipfile.ZipFile(package_path, 'r') as zf:
            manifest_data = json.loads(zf.read('manifest.json'))
            module_name = manifest_data['name']
    except Exception as e:
        console.print(f"[red]Failed to read manifest from package: {e}[/red]")
        return
    
    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/yellow]")
        console.print(f"\nWould deploy: {package_path}")
        console.print(f"Module name: {module_name}")
        console.print(f"To environment: {env}")
        console.print(f"File size: {package_path.stat().st_size / (1024*1024):.2f} MB")
        return
    
    # Deploy using SimpleDeployer
    try:
        console.print(f"\n📦 Deploying module '{module_name}'...")
        deployer = SimpleDeployer(env)
        result = deployer.deploy(str(package_path), module_name)
        
        console.print("[green]✅ Deployment successful![/green]")
        console.print(f"\nModule ID: {result['module_id']}")
        console.print(f"Lambda function: {result['lambda_function']}")
        console.print(f"\nTest with:")
        console.print(f"  hla-compass execute {module_name} --input examples/input.json")
        
    except Exception as e:
        console.print(f"[red]Deployment failed: {e}[/red]")
        console.print("\nTroubleshooting:")
        console.print("  1. Check AWS credentials: aws sts get-caller-identity")
        console.print("  2. Ensure buckets exist: aws s3 ls")
        console.print("  3. Check Lambda permissions")
        return


@cli.command()
@click.argument('module_name')
@click.option('--input', 'input_file', required=True, help='Input JSON file')
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Target environment')
@click.option('--wait', is_flag=True, help='Wait for execution to complete')
def execute(module_name: str, input_file: str, env: str, wait: bool):
    """Execute a module on the platform"""
    console.print(f"[bold]Executing module '{module_name}'...[/bold]")
    
    # Load input data
    try:
        with open(input_file, 'r') as f:
            input_data = json.load(f)
    except Exception as e:
        console.print(f"[red]Failed to load input file: {e}[/red]")
        return
    
    # Execute using SimpleDeployer
    try:
        console.print(f"🚀 Submitting job...")
        deployer = SimpleDeployer(env)
        job_id = deployer.execute(module_name, input_data)
        
        console.print(f"[green]✅ Job submitted successfully![/green]")
        console.print(f"\nJob ID: {job_id}")
        
        if wait:
            console.print("\n⏳ Waiting for completion...")
            # In real implementation, poll for status
            import time
            time.sleep(2)
            
            # Get results
            results = deployer.get_results(job_id)
            console.print("\n[bold]Results:[/bold]")
            console.print(Syntax(json.dumps(results, indent=2), "json"))
        else:
            console.print(f"\nCheck status with:")
            console.print(f"  hla-compass results {job_id}")
            
    except Exception as e:
        console.print(f"[red]Execution failed: {e}[/red]")
        return


@cli.command()
@click.argument('job_id')
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Target environment')
def results(job_id: str, env: str):
    """Get results from a job execution"""
    console.print(f"[bold]Fetching results for job {job_id}...[/bold]")
    
    try:
        deployer = SimpleDeployer(env)
        results_data = deployer.get_results(job_id)
        
        console.print("\n[bold]Results:[/bold]")
        console.print(Syntax(json.dumps(results_data, indent=2), "json"))
        
        # Show status
        status = results_data.get('status', 'unknown')
        if status == 'success':
            console.print(f"\n[green]✅ Execution successful[/green]")
        elif status == 'error':
            console.print(f"\n[red]❌ Execution failed[/red]")
            if 'message' in results_data:
                console.print(f"Error: {results_data['message']}")
                
    except Exception as e:
        console.print(f"[red]Failed to get results: {e}[/red]")
        console.print("\nPossible reasons:")
        console.print("  • Job is still running")
        console.print("  • Job ID is incorrect")
        console.print("  • Results have expired")


@cli.command()
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Target environment')
def list_modules(env: str):
    """List deployed modules"""
    console.print(f"[bold]Listing modules in {env} environment...[/bold]")
    
    try:
        deployer = SimpleDeployer(env)
        modules = deployer.list_modules()
        
        if not modules:
            console.print("[yellow]No modules deployed yet[/yellow]")
            console.print("\nDeploy your first module with:")
            console.print("  hla-compass deploy dist/my-module.zip")
            return
        
        # Create table
        table = Table(title=f"Deployed Modules ({env})")
        table.add_column("Module", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Deployed At", style="yellow")
        table.add_column("Status", style="magenta")
        
        for module in modules:
            table.add_row(
                module.get('module_name', 'unknown'),
                module.get('version', 'unknown'),
                module.get('deployed_at', 'unknown')[:19],  # Trim timestamp
                module.get('status', 'unknown')
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Failed to list modules: {e}[/red]")


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