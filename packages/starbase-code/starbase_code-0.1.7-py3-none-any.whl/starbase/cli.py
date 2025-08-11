#!/usr/bin/env python3
"""Starbase - A centralized code repository manager"""

import os
import sys
import subprocess
import ast
import re
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Set, Tuple
from datetime import datetime, timedelta

# Import refactored functions from core
from starbase.core.analysis import (
    extract_local_imports,
    find_connected_components,
    detect_test_relationships,
    detect_file_versions,
    detect_name_relationships,
    analyze_file_relationships,
    trace_dependencies
)
from starbase.core.assignment import (
    load_subdirectory_config,
    analyze_project_with_subdirectories,
    assign_subdirectories_llm_with_scores,
    assign_subdirectories_llm,
    assign_subdirectories_heuristic_with_scores,
    assign_subdirectories_heuristic,
    assign_subdirectories_hybrid
)
from starbase.core.extraction import (
    extract_single_file,
    get_python_files_in_directory,
    display_group_info,
    check_existing_files,
    convert_group_to_entry_points,
    parse_package_selection,
    do_extraction,
    find_related_files,
    generate_smart_description,
    validate_and_resolve_path,
    handle_single_file_extraction,
    analyze_directory_for_extraction,
    handle_existing_file_warnings,
    handle_single_group_extraction,
    parse_group_selection,
    extract_selected_groups,
    create_entry_points_for_group
)
from starbase.core.search import (
    collect_search_results,
    display_search_results,
    handle_search_actions,
    offer_deep_search,
    process_deep_search_results,
    show_quick_actions,
    show_no_results_help,
    update_package_project_status
)
from starbase.core.file_search import (
    search_with_ripgrep,
    install_ripgrep,
    search_with_python_fallback
)
from starbase.core.catalog import (
    handle_empty_catalog,
    group_entries_by_category,
    display_catalog_groups,
    convert_entries_to_results,
    apply_filter_hint
)
from starbase.core.entry_points import find_entry_points as core_find_entry_points
from starbase.mcp_installer import MCPInstaller

# Optional imports
try:
    import toml
except ImportError:
    toml = None

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from InquirerPy import inquirer
    import tinydb
except ImportError:
    # These are only needed for CLI functionality
    typer = None
    Console = None
    Table = None
    Prompt = None
    Confirm = None
    inquirer = None
    tinydb = None
# More optional imports
try:
    from git import Repo
except ImportError:
    Repo = None

try:
    from langchain_core.prompts import PromptTemplate
    from langchain_groq import ChatGroq
    from langchain_anthropic import ChatAnthropic
except ImportError:
    PromptTemplate = None
    ChatGroq = None
    ChatAnthropic = None
# from starbase.mcp_installer import ensure_mcp_installed

# Claude Max LLM wrapper
class ClaudeMaxLLM:
    """Wrapper to use Claude Max via CLI instead of API"""
    
    def invoke(self, prompt: str) -> Any:
        """Invoke Claude using the CLI"""
        try:
            # For long prompts, we might need to use a different approach
            # But for search queries, this should work fine
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                # Create a response object that looks like the API response
                class Response:
                    def __init__(self, content):
                        self.content = content
                
                return Response(result.stdout)
            else:
                # Check for specific errors
                if result.stderr and "Credit balance is too low" in result.stderr:
                    raise Exception("Claude credits exhausted. Check your Max subscription.")
                elif result.stderr and "not authenticated" in result.stderr.lower():
                    raise Exception("Not logged into Claude. Run /login first.")
                elif result.returncode == 0 and not result.stdout:
                    # Claude ran successfully but produced no output
                    raise Exception("Claude returned empty response. Try simpler search terms.")
                else:
                    raise Exception(f"Claude error: {result.stderr or 'Unknown error'}")
                    
        except subprocess.TimeoutExpired:
            raise Exception("Claude request timed out after 30 seconds")
        except FileNotFoundError:
            raise Exception("Claude CLI not found. Install with: brew install anthropic/tap/claude")

# Only create app and console if typer is available
if typer:
    app = typer.Typer(add_completion=False, help="Starbase - Manage your code repositories")
    console = Console()
else:
    app = None
    console = None

# Configuration
CONFIG_PATH = Path.home() / ".starbase_config.toml"

DEFAULT_CONFIG = {
    "active_starbase": "prime",
    "starbases": {
        "prime": {
            "path": str(Path.home() / "starbase"),
            "description": "Prime Nexus - Central code repository"
        }
    },
    "llm_provider": "groq",
    "llm_model": "llama-3.1-8b-instant",  # Updated default model
    "api_keys": {"groq": "", "anthropic": "", "grok": ""},
    "last_choices": {}
}

class StarbaseManager:
    """Manages starbase configuration and operations"""
    
    def __init__(self):
        self.config = self.load_config()
        self.ensure_active_starbase()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration or create new one"""
        if CONFIG_PATH.exists():
            return toml.load(CONFIG_PATH)
            
        # First run - create default config
        console.print(f"[cyan]🚀 Welcome to Starbase! Initializing Prime Nexus at ~/starbase...[/cyan]")
        self.save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
        
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to disk"""
        if config is None:
            config = self.config
        with open(CONFIG_PATH, "w") as f:
            toml.dump(config, f)
            
    def ensure_active_starbase(self):
        """Ensure the active starbase directory exists"""
        starbase_path = Path(self.get_active_path())
        if not starbase_path.exists():
            console.print(f"[yellow]Creating starbase directory at {starbase_path}...[/yellow]")
            starbase_path.mkdir(parents=True, exist_ok=True)
            # Initialize git repo
            try:
                Repo.init(starbase_path)
                console.print(f"[green]✓ Initialized git repository[/green]")
            except Exception as e:
                console.print(f"[yellow]Note: Could not initialize git: {e}[/yellow]")
                
    def get_active_name(self) -> str:
        """Get the name of the active starbase"""
        return self.config.get("active_starbase", "prime")
        
    def get_active_path(self) -> str:
        """Get the path of the active starbase"""
        active = self.get_active_name()
        return os.path.expanduser(self.config["starbases"][active]["path"])
        
    def get_db_path(self) -> Path:
        """Get the database path for the active starbase"""
        return Path(self.get_active_path()) / "catalog.json"
        
    def create_starbase(self, name: str, path: Optional[str] = None, description: Optional[str] = None):
        """Create a new starbase"""
        if name in self.config["starbases"]:
            console.print(f"[red]Starbase '{name}' already exists![/red]")
            return False
            
        if path is None:
            path = str(Path.home() / f"starbase-{name}")
        path = os.path.expanduser(path)
        
        if description is None:
            description = f"Starbase for {name}"
            
        self.config["starbases"][name] = {
            "path": path,
            "description": description
        }
        self.save_config()
        
        # Create directory
        Path(path).mkdir(parents=True, exist_ok=True)
        
        # Initialize git
        try:
            Repo.init(path)
            console.print(f"[green]✓ Created starbase '{name}' at {path}[/green]")
        except Exception as e:
            console.print(f"[yellow]Created starbase but could not init git: {e}[/yellow]")
            
        return True
        
    def switch_starbase(self, name: str):
        """Switch to a different starbase"""
        if name not in self.config["starbases"]:
            console.print(f"[red]Starbase '{name}' does not exist![/red]")
            return False
            
        self.config["active_starbase"] = name
        self.save_config()
        self.ensure_active_starbase()
        console.print(f"[green]✓ Switched to starbase '{name}' at {self.get_active_path()}[/green]")
        return True
        
    def list_starbases(self):
        """List all starbases"""
        table = Table(title="Starbases")
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("Active", style="magenta")
        
        for name, info in self.config["starbases"].items():
            is_active = "✓" if name == self.get_active_name() else ""
            table.add_row(name, info["path"], info["description"], is_active)
            
        console.print(table)

# Create global manager instance only if running as main/CLI
if __name__ == "__main__" or (typer and tinydb):
    manager = StarbaseManager()
    # TinyDB setup with pretty printing and error recovery
    try:
        db = tinydb.TinyDB(manager.get_db_path(), indent=2, separators=(',', ': '))
    except (json.JSONDecodeError, ValueError) as e:
        # Database is corrupted, recover by backing up and creating new
        db_path = manager.get_db_path()
        backup_path = db_path.with_suffix('.json.corrupted')
        
        if console:
            console.print(f"[yellow]⚠️  Database corrupted. Backing up to {backup_path}[/yellow]")
        
        # Back up corrupted file
        if db_path.exists():
            shutil.move(str(db_path), str(backup_path))
        
        # Create fresh database
        db = tinydb.TinyDB(db_path, indent=2, separators=(',', ': '))
        
        if console:
            console.print("[green]✓ Created fresh database. Previous data backed up.[/green]")
else:
    manager = None
    db = None

# LLM setup helper
def get_llm(provider=None, model=None):
    if not manager:
        return None
    config = manager.config
    provider = provider or config["llm_provider"]
    model = model or config["llm_model"]
    
    if provider == "groq":
        api_key = config["api_keys"].get("groq") or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("No Groq API key found. Run 'starbase configure' or set GROQ_API_KEY")
        return ChatGroq(api_key=api_key, model=model)
        
    elif provider == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(model=model)
        
    elif provider == "claude":
        api_key = config["api_keys"].get("claude")
        
        # Handle special Claude sessions - USE THEM!
        if api_key in ["CLAUDE_CODE_SESSION", "CLAUDE_MAX_SESSION"]:
            # Return wrapper that uses Claude CLI
            console.print("[dim]Using Claude Max for semantic search...[/dim]")
            return ClaudeMaxLLM()
        
        # For API key users only
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            
        if not api_key:
            raise ValueError("No Claude API key found. Run 'starbase configure'")
            
        return ChatAnthropic(api_key=api_key, model=model)
        
    elif provider == "grok":
        # Placeholder for Grok/xAI implementation
        raise NotImplementedError("Grok provider not yet implemented")
    else:
        raise ValueError(f"Unknown provider: {provider}")

# Interactive menu
def main_menu():
    choices = [
        "⚡ PDM Operations", "🔧 Extract from Messy Code", "🔍 Search Catalog",
        "💾 Database Operations", "🌿 Git Operations", "📦 Install from Starbase",
        "⚙️ Configure", "🚀 Starbase Management", "🛑 Exit"
    ]
    
    # Use last choice if available
    last_choice = manager.config.get("last_choices", {}).get("main_menu")
    if last_choice and last_choice in choices:
        choices.remove(last_choice)
        choices.insert(0, last_choice)
    
    selection = inquirer.select(
        message=f"🌟 STARBASE {manager.get_active_name().upper()} COMMAND CENTER",
        choices=choices,
    ).execute()
    
    # Save last choice
    manager.config["last_choices"]["main_menu"] = selection
    manager.save_config()
    
    if selection == "⚡ PDM Operations":
        pdm_menu()
    elif selection == "🔧 Extract from Messy Code":
        extract_menu()
    elif selection == "🔍 Search Catalog":
        search_menu()
    elif selection == "💾 Database Operations":
        db_menu()
    elif selection == "🌿 Git Operations":
        git_menu()
    elif selection == "📦 Install from Starbase":
        install_menu()
    elif selection == "⚙️ Configure":
        configure()
    elif selection == "🚀 Starbase Management":
        starbase_menu()
    
    return selection

def starbase_menu():
    """Starbase management menu"""
    choices = [
        "🌟 List All Starbases", "🚀 Switch Starbase", "✨ Create New Starbase",
        "📍 Show Current Starbase", "🔙 Back to Main Menu"
    ]
    
    selection = inquirer.select(
        message="Starbase Command Center",
        choices=choices,
    ).execute()
    
    if selection == "🌟 List All Starbases":
        manager.list_starbases()
        input("\nPress Enter to continue...")
    elif selection == "🚀 Switch Starbase":
        names = list(manager.config["starbases"].keys())
        name = inquirer.select(
            message="Select destination starbase:",
            choices=names,
        ).execute()
        manager.switch_starbase(name)
        input("\nPress Enter to continue...")
    elif selection == "✨ Create New Starbase":
        name = Prompt.ask("Enter starbase designation")
        path = Prompt.ask("Enter coordinates (path) [leave empty for auto]", default="")
        desc = Prompt.ask("Enter starbase mission brief", default=f"Starbase {name.upper()} - Code Repository")
        if path == "":
            path = None
        manager.create_starbase(name, path, desc)
        if Confirm.ask("Engage hyperdrive to new starbase?"):
            manager.switch_starbase(name)
        input("\nPress Enter to continue...")
    elif selection == "📍 Show Current Starbase":
        console.print(f"\n[cyan]🌟 Active Starbase:[/cyan] {manager.get_active_name().upper()}")
        console.print(f"[cyan]📍 Coordinates:[/cyan] {manager.get_active_path()}")
        console.print(f"[cyan]📋 Mission:[/cyan] {manager.config['starbases'][manager.get_active_name()]['description']}")
        input("\nPress Enter to continue...")

# Commands
@app.command()
def init(name: str = typer.Argument("nexus"), path: Optional[str] = None):
    """Initialize a new starbase"""
    if manager.create_starbase(name, path):
        manager.switch_starbase(name)

@app.command(name="new")
def new_starbase(name: str, path: Optional[str] = None, description: Optional[str] = None):
    """Create a new starbase"""
    manager.create_starbase(name, path, description)

@app.command(name="use")
def use_starbase(name: str):
    """Switch to a different starbase"""
    manager.switch_starbase(name)

@app.command(name="list")
def list_starbases():
    """List all starbases"""
    manager.list_starbases()

@app.command()
def current():
    """Show current active starbase"""
    console.print(f"[cyan]Active starbase:[/cyan] {manager.get_active_name()}")
    console.print(f"[cyan]Path:[/cyan] {manager.get_active_path()}")

def extract_to_isolated_package(file_path: Path, package_dir: Path) -> Dict[str, Any]:
    """Extract a file to an isolated package directory.
    
    This ensures each package gets its own dedicated directory,
    preventing file mixing between different packages.
    """
    # Ensure package directory exists
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the main file
    target_file = package_dir / file_path.name
    shutil.copy2(file_path, target_file)
    
    extracted_files = [{'source': str(file_path), 'target': str(target_file)}]
    
    # Trace dependencies if it's a Python file
    if file_path.suffix == '.py':
        dependencies = trace_dependencies(file_path)
        for dep in dependencies:
            dep_target = package_dir / dep.name
            shutil.copy2(dep, dep_target)
            extracted_files.append({'source': str(dep), 'target': str(dep_target)})
    
    # Create package manifest
    manifest = {
        'name': package_dir.name,
        'version': '0.1.0',
        'description': f'Extracted package from {file_path.name}',
        'entry_point': file_path.name,
        'files': [f['target'] for f in extracted_files],
        'extracted_at': datetime.now().isoformat(),
        'source_path': str(file_path)
    }
    
    manifest_path = package_dir / 'package.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    
    # Update catalog - use global db instance
    if db is not None:
        Query = tinydb.Query()
        
        # Update or insert catalog entry
        catalog_entry = {
            'name': package_dir.name,
            'path': package_dir.name,
            'type': 'package',
            'description': manifest['description'],
            'extracted_from': str(file_path.parent),
            'extracted_at': manifest['extracted_at']
        }
        
        db.upsert(catalog_entry, Query.name == package_dir.name)
    
    return {
        'package_name': package_dir.name,
        'package_dir': str(package_dir),
        'extracted_files': extracted_files,
        'manifest': manifest
    }


def pdm(operation: str = typer.Argument(None), args: Optional[list[str]] = typer.Option(None)):
    """Wrap PDM commands with menu if no op."""
    if not operation:
        pdm_menu()
        return
    cmd = ["pdm", operation] + (args or [])
    subprocess.run(cmd, cwd=manager.get_active_path())

@app.command()
def extract(messy_path: Optional[str] = typer.Argument(None, help="Path to extract from"), 
           remove: bool = typer.Option(False, "--remove", "-r", help="Remove source after extraction")):
    """Extract from messy code, organize and move to starbase."""
    # Use smart extraction menu for all cases
    extract_menu(messy_path)

@app.command()
def mcp():
    """Configure the current project to use the global Starbase MCP server."""
    console.print("\n[cyan]🔌 Configuring Starbase MCP Server for this project...[/cyan]")
    project_dir = Path.cwd()
    installer = MCPInstaller()
    if installer.configure_project_mcp(project_dir):
        console.print("\n[bold green]✅ Project MCP configuration complete![/bold green]")
    else:
        console.print("\n[red]❌ Project MCP configuration failed.[/red]")

@app.command(name="mcp-server", hidden=True)
def mcp_server():
    """Runs the Starbase MCP server (for use by Claude tools)."""
    try:
        from src.starbase.mcp_server import main as mcp_main
        mcp_main()
    except ImportError:
        if console:
            console.print("[red]Could not start MCP server. Please run 'starbase global-install'.[/red]")
        else:
            print("Could not start MCP server. Please run 'starbase global-install'.", file=sys.stderr)
        sys.exit(1)

@app.command()
def global_install():
    """Build and install starbase as a global command and configure MCP."""
    installer = MCPInstaller(project_root_path=Path.cwd())
    installer.install_and_configure_mcp()

@app.command()
def update():
    """Update starbase to the latest version from PyPI."""
    import subprocess
    import shutil
    
    console.print("\n[cyan]🔄 Updating starbase to latest version...[/cyan]")
    
    pipx_path = shutil.which("pipx")
    if pipx_path:
        try:
            # First uninstall existing version
            console.print("[dim]Uninstalling current version...[/dim]")
            subprocess.run([pipx_path, "uninstall", "starbase-code"], capture_output=True, text=True)
            
            # Install latest from PyPI
            console.print("[dim]Installing latest version from PyPI...[/dim]")
            result = subprocess.run([pipx_path, "install", "starbase-code"], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Run MCP installer to ensure Claude Desktop integration
                console.print("\n[cyan]🔗 Ensuring Claude Desktop integration...[/cyan]")
                installer = MCPInstaller(project_root_path=Path.cwd())
                installer._ensure_standard_path_access("starbase")
                installer._update_claude_config()
                installer._update_claude_code_config()
                
                console.print("\n[bold green]✅ Starbase updated successfully![/bold green]")
                console.print("[dim]Restart your terminal or Claude Desktop to use the new version.[/dim]")
            else:
                console.print(f"[red]❌ Update failed: {result.stderr}[/red]")
                console.print("[yellow]Try running: pipx install starbase-code[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Update error: {e}[/red]")
            console.print("[yellow]Try running: pipx install starbase-code[/yellow]")
    else:
        console.print("[red]❌ pipx not found. Install pipx first:[/red]")
        console.print("  macOS: [cyan]brew install pipx[/cyan]")
        console.print("  Linux: [cyan]sudo apt install pipx[/cyan]")
        console.print("  Or:    [cyan]python3 -m pip install --user pipx[/cyan]")





def search_in_catalog(query: str) -> List[Dict]:
    """Search catalog database for matches"""
    Query = tinydb.Query()
    results = []
    seen_paths = set()
    
    # 1. Exact name match (highest priority)
    exact = db.search(Query.name == query)
    for r in exact:
        if r.get('path') not in seen_paths:
            r['match_type'] = 'exact'
            r['match_context'] = 'Name matches exactly'
            results.append(r)
            seen_paths.add(r.get('path'))
    
    # 2. Name contains query
    name_matches = db.search(Query.name.matches(f".*{re.escape(query)}.*", flags=re.IGNORECASE))
    for r in name_matches:
        if r.get('path') not in seen_paths:
            r['match_type'] = 'name'
            r['match_context'] = f"Name contains '{query}'"
            results.append(r)
            seen_paths.add(r.get('path'))
    
    # 3. Path contains query
    path_matches = db.search(Query.path.matches(f".*{re.escape(query)}.*", flags=re.IGNORECASE))
    for r in path_matches:
        if r.get('path') not in seen_paths:
            r['match_type'] = 'path'
            r['match_context'] = f"Path contains '{query}'"
            results.append(r)
            seen_paths.add(r.get('path'))
    
    # 4. Description contains query
    desc_matches = db.search(Query.description.matches(f".*{re.escape(query)}.*", flags=re.IGNORECASE))
    for r in desc_matches:
        if r.get('path') not in seen_paths:
            r['match_type'] = 'description'
            r['match_context'] = f"Description contains '{query}'"
            results.append(r)
            seen_paths.add(r.get('path'))
    
    return results

def search_file_contents(query: str, limit: int = 10) -> List[Dict]:
    """Search actual file contents in starbase"""
    starbase_path = Path(manager.get_active_path())
    
    # Try ripgrep first
    results = search_with_ripgrep(query, starbase_path, limit)
    
    if results is None:
        # Ripgrep not available, try to install
        if install_ripgrep(console):
            # Try again after installation
            results = search_with_ripgrep(query, starbase_path, limit)
        
        if results is None:
            # Fall back to Python search
            results = search_with_python_fallback(query, starbase_path, limit)
    
    return results or []

def search_with_ast(query: str, limit: int = 10) -> List[Dict]:
    """Search for functions and classes using AST"""
    starbase_path = Path(manager.get_active_path())
    results = []
    
    for py_file in starbase_path.rglob("*.py"):
        if any(part in {'.venv', 'venv', '__pycache__'} for part in py_file.parts):
            continue
            
        try:
            content = py_file.read_text()
            tree = ast.parse(content)
            
            # Get package name from path
            rel_path = py_file.relative_to(starbase_path)
            package_name = rel_path.parts[0] if rel_path.parts else py_file.stem
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and query.lower() in node.name.lower():
                    results.append({
                        'name': package_name,
                        'path': str(rel_path),
                        'match_type': 'function',
                        'match_context': f"Function: {node.name}",
                        'line_number': node.lineno
                    })
                elif isinstance(node, ast.ClassDef) and query.lower() in node.name.lower():
                    results.append({
                        'name': package_name,
                        'path': str(rel_path),
                        'match_type': 'class',
                        'match_context': f"Class: {node.name}",
                        'line_number': node.lineno
                    })
                    
            if len(results) >= limit:
                break
                
        except Exception:
            continue
    
    return results

@app.command()
def search(query: str, 
          deep: bool = typer.Option(False, "--deep", "-d", help="Search file contents too"),
          debug: bool = typer.Option(False, "--debug", help="Show detailed search results")):
    """Intelligent search across starbase with actionable results"""
    # Collect search results using helper function
    packages, _ = collect_search_results(query, search_in_catalog, search_with_ast)
    
    # Update project status for all packages
    update_package_project_status(packages, manager)
    
    # Process deep search if requested
    if deep and packages:
        process_deep_search_results(packages, query, search_file_contents)
    
    # Display results and handle actions
    if packages:
        sorted_packages = display_search_results(packages, console, debug)
        show_quick_actions(console)
        
        # Handle user actions in interactive mode
        if not debug:
            choice = Prompt.ask("\nSelect package number for actions (or Enter to skip)", default="")
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sorted_packages):
                    pkg_name, pkg_info = sorted_packages[idx]
                    show_package_actions(pkg_name, pkg_info['path'], pkg_info['is_project'])
    else:
        show_no_results_help(console)


def browse_with_filter(filter_hint: Optional[str] = None) -> List[Dict]:
    """Browse catalog with optional filtering"""
    all_entries = db.all()
    
    if not all_entries:
        starbase_path = Path(manager.get_active_path())
        handle_empty_catalog(starbase_path, console)
        return []
    
    # Apply filter hint (e.g., sort by recent)
    filtered_entries = apply_filter_hint(all_entries, filter_hint)
    
    # Group entries by category
    groups = group_entries_by_category(filtered_entries)
    
    # Display grouped catalog
    total_shown = display_catalog_groups(groups, console)
    console.print(f"[dim]Total: {len(all_entries)} items in catalog[/dim]")
    
    # Convert to result format
    return convert_entries_to_results(all_entries)

def get_available_groq_models(api_key: str) -> List[str]:
    """Fetch available Groq models from API"""
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Try to get models from Groq API
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
        
        if response.status_code == 200:
            models_data = response.json()
            # Extract model IDs and filter for text generation models
            models = []
            for model in models_data.get("data", []):
                model_id = model.get("id", "")
                # Filter out whisper and other non-text models
                if model_id and not model_id.startswith("whisper"):
                    models.append(model_id)
            
            return sorted(models) if models else None
        else:
            return None
    except Exception:
        return None

def mask_api_key(key: str) -> str:
    """Mask API key showing only first few and last 6 characters"""
    if not key or len(key) < 10:
        return key
    return f"{key[:3]}...{key[-6:]}"

def get_env_api_key(provider: str) -> Optional[str]:
    """Get API key from environment variables"""
    env_map = {
        "groq": "GROQ_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "grok": "GROK_API_KEY"
    }
    return os.environ.get(env_map.get(provider, ""))

@app.command()
def configure():
    """Configure starbase settings, LLM, etc."""
    config = manager.config
    
    # LLM Provider
    provider = inquirer.select(
        message="🤖 Select LLM provider:",
        choices=["groq", "ollama", "claude", "grok"],
        default=config["llm_provider"]
    ).execute()
    
    config["llm_provider"] = provider
    
    # Model selection for Groq
    if provider == "groq":
        # Check if we have API key to fetch models
        api_key = config["api_keys"].get("groq", "") or os.environ.get("GROQ_API_KEY")
        
        if api_key:
            # Try to fetch available models
            groq_models = get_available_groq_models(api_key)
            if groq_models:
                model = inquirer.select(
                    message="Select Groq model:",
                    choices=groq_models,
                    default=config.get("llm_model", "llama-3.1-8b-instant")
                ).execute()
                config["llm_model"] = model
            else:
                # Fallback to manual entry
                console.print("[yellow]Could not fetch models. Using default list.[/yellow]")
                model = inquirer.select(
                    message="Select Groq model:",
                    choices=["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it"],
                    default=config.get("llm_model", "llama-3.1-8b-instant")
                ).execute()
                config["llm_model"] = model
        else:
            # No API key yet, use default list
            model = inquirer.select(
                message="Select Groq model (get API key first for full list):",
                choices=["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it"],
                default=config.get("llm_model", "llama-3.1-8b-instant")
            ).execute()
            config["llm_model"] = model
    
    # API Keys
    if provider in ["groq", "claude", "grok"]:
        # Check environment variable first
        env_key = get_env_api_key(provider)
        current_key = config["api_keys"].get(provider, "")
        
        # Special handling for Claude
        if provider == "claude":
            console.print("\n[cyan]🤖 Claude Configuration[/cyan]")
            console.print("\nFor Claude Max users (recommended):")
            console.print("  • No API key needed - uses your Claude session")
            console.print("  • Unlimited usage with your Max plan")
            console.print("  • Just make sure you're logged in via /login\n")
            
            auth_choices = [
                "Use Claude Max (no API key needed)",
                "Use API key (for non-Max users)"
            ]
            
            auth_method = inquirer.select(
                message="Choose authentication method:",
                choices=auth_choices,
            ).execute()
            
            if auth_method == "Use Claude Max (no API key needed)":
                config["api_keys"][provider] = "CLAUDE_MAX_SESSION"
                manager.save_config()
                console.print("\n[green]✓ Configured for Claude Max![/green]")
                console.print("Make sure you're logged in:")
                console.print("  1. Run: claude /status")
                console.print("  2. If not logged in, run: /login")
                return
        
        # Determine default key and display
        default_key = env_key or current_key
        
        if env_key:
            console.print(f"[green]✓ Found {provider.upper()} API key in environment[/green]")
        
        # Show masked version of default if available
        if default_key:
            console.print(f"[dim]Default: {mask_api_key(default_key)}[/dim]")
            key = Prompt.ask(
                f"Enter {provider} API key (press Enter to use default)",
                default=default_key,
                show_default=False
            )
        else:
            key = Prompt.ask(f"Enter {provider} API key")
        
        config["api_keys"][provider] = key
    
    manager.save_config()
    console.print("[green]✓ Configuration saved![/green]")

# Helper menus (simplified versions)
def pdm_menu():
    """PDM operations menu"""
    ops = ["add", "remove", "list", "update", "build", "run", "Back"]
    op = inquirer.select(message="Select PDM operation:", choices=ops).execute()
    if op != "Back":
        subprocess.run(["pdm", op], cwd=manager.get_active_path())

def find_entry_points(path: Path) -> List[Dict]:
    """Find Python entry points using AST analysis"""
    return core_find_entry_points(path, console)

def detect_duplicates(entry_points: List[Dict]) -> Dict:
    """Detect potential duplicate files"""
    duplicates = {}
    
    # Group by similar names
    name_groups = {}
    for ep in entry_points:
        base_name = ep['file'].stem.replace('_old', '').replace('_v2', '').replace('_copy', '')
        base_name = base_name.replace('codelibmanager', 'starbase').replace('codelib', 'starbase')
        if base_name not in name_groups:
            name_groups[base_name] = []
        name_groups[base_name].append(ep)
    
    # Find actual duplicates
    for base_name, files in name_groups.items():
        if len(files) > 1:
            # Sort by priority and mtime to find the "main" one
            files.sort(key=lambda x: (-x['priority'], -x['mtime']))
            main_file = files[0]
            older_files = files[1:]
            
            duplicates[main_file['file']] = [
                {
                    'file': old['file'],
                    'reason': f"older version ({old['line_count']} lines vs {main_file['line_count']} lines)"
                    if old['line_count'] < main_file['line_count']
                    else f"older ({old['file'].name} modified {int((main_file['mtime'] - old['mtime']) / 86400)} days earlier)"
                }
                for old in older_files
            ]
    
    return duplicates

def format_timestamp(mtime: float) -> str:
    """Format timestamp in human-friendly way"""
    dt = datetime.fromtimestamp(mtime)
    now = datetime.now()
    
    if dt.date() == now.date():
        return f"today at {dt.strftime('%H:%M')}"
    elif dt.date() == (now - timedelta(days=1)).date():
        return f"yesterday at {dt.strftime('%H:%M')}"
    elif (now - dt).days < 7:
        return f"{dt.strftime('%A at %H:%M')}"
    else:
        return dt.strftime('%Y-%m-%d')


def check_starbase_status(source_path: Path) -> Dict:
    """Check if this code already exists in starbase"""
    starbase_path = Path(manager.get_active_path())
    
    # Check various possible locations
    potential_locations = [
        starbase_path / source_path.name,  # Direct file
        starbase_path / source_path.parent.name,  # Project directory
    ]
    
    # If we're in a subdirectory, check if the parent project is in starbase
    if source_path.parent != Path.home() and source_path.parent.name not in ['.', '..']:
        potential_locations.append(starbase_path / source_path.parent.name)
    
    for loc in potential_locations:
        if loc.exists():
            if loc.is_file():
                source_mtime = source_path.stat().st_mtime
                starbase_mtime = loc.stat().st_mtime
            else:
                # For directories, check the main file
                main_file = loc / source_path.name
                if main_file.exists():
                    source_mtime = source_path.stat().st_mtime
                    starbase_mtime = main_file.stat().st_mtime
                else:
                    continue
            
            return {
                'exists': True,
                'path': loc,
                'is_newer': starbase_mtime > source_mtime,
                'time_diff': abs(starbase_mtime - source_mtime)
            }
    
    return {'exists': False}



def ensure_mcp_installed(starbase_path: Path):
    """Stub for MCP installation - currently disabled"""
    pass


def do_extraction(entry_points: List[Dict], source_path: Path, include_deps: bool = True, package_name: str = None):
    """Wrapper for the actual extraction function that passes required dependencies"""
    from starbase.core.extraction import do_extraction as core_do_extraction
    
    # Call the core extraction function with all required dependencies
    extracted_files = core_do_extraction(
        entry_points=entry_points,
        source_path=source_path,
        include_deps=include_deps,
        package_name=package_name,
        manager=manager,
        db=db,
        console=console
    )
    
    # Handle MCP installation if needed
    if extracted_files:
        starbase_path = Path(manager.get_active_path())
        ensure_mcp_installed(starbase_path)
    
    return extracted_files

def extract_menu(initial_path: Optional[str] = None):
    """Extract code menu with smart analysis"""
    # Validate and resolve path
    path = validate_and_resolve_path(initial_path, console)
    if not path:
        return
    
    # Handle single file extraction
    if path.is_file():
        handle_single_file_extraction(path, console, do_extraction)
        return
    
    if not path.is_dir():
        console.print("[red]Invalid path![/red]")
        return
    
    console.print(f"\n[cyan]🔍 Analyzing {path}...[/cyan]")
    
    # Analyze directory for groups
    groups = analyze_directory_for_extraction(path, console)
    if not groups:
        return
    
    # Display grouped packages
    console.print(f"\nFound {len(groups)} logical package{'s' if len(groups) != 1 else ''}:\n")
    for i, group in enumerate(groups, 1):
        display_group_info(group, i, path, console)
    
    # Check existing files
    existing_warnings = check_existing_files(groups, check_starbase_status)
    if not handle_existing_file_warnings(existing_warnings, console):
        return
    
    # Handle extraction based on number of groups
    if len(groups) == 1:
        handle_single_group_extraction(groups[0], path, console, do_extraction)
    else:
        # Multiple packages - let user select
        selection = Prompt.ask("\nSelect packages to extract (e.g., 1,3 or 1-3 or 'all')", default="all")
        selected_indices = parse_group_selection(selection, len(groups))
        
        if selected_indices:
            selected_groups = [groups[i-1] for i in selected_indices]
            extract_selected_groups(selected_groups, path, console, do_extraction)
        else:
            console.print("[red]Invalid selection![/red]")

def show_package_actions(package_name: str, package_path: str, is_project: bool = False):
    """Wrapper for show_package_actions from starbase.core.menus"""
    from starbase.core.menus import show_package_actions as core_show_package_actions
    
    core_show_package_actions(
        package_name=package_name,
        package_path=package_path,
        is_project=is_project,
        manager=manager,
        db=db,
        console=console,
        Prompt=Prompt,
        Confirm=Confirm,
        view_file=view_file
    )

def view_file(file_path: Path, max_lines: int = 50):
    """View contents of a file with syntax highlighting"""
    if not file_path.exists():
        console.print("[red]File not found![/red]")
        return
    
    try:
        from rich.syntax import Syntax
        
        content = file_path.read_text()
        lines = content.splitlines()
        
        if len(lines) > max_lines:
            # Show first part with option to see more
            syntax = Syntax('\n'.join(lines[:max_lines]), "python", theme="monokai", line_numbers=True)
            console.print(syntax)
            console.print(f"\n[dim]... {len(lines) - max_lines} more lines ...[/dim]")
            
            if Confirm.ask("Show entire file?"):
                syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
                console.print(syntax)
        else:
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            console.print(syntax)
    except Exception as e:
        # Fallback to simple display
        console.print(f"[yellow]Could not syntax highlight: {e}[/yellow]")
        content = file_path.read_text()
        lines = content.splitlines()[:max_lines]
        for i, line in enumerate(lines, 1):
            console.print(f"{i:4d} | {line}")

def search_menu(debug: bool = False):
    """Enhanced search menu with actionable results"""
    query = Prompt.ask("Search for")
    
    # Collect all results using the new helper
    packages, all_results = collect_search_results(query, search_in_catalog, search_with_ast)
    
    # Update is_project flag for each package
    starbase_path = Path(manager.get_active_path())
    for pkg_name, pkg_info in packages.items():
        full_path = starbase_path / pkg_info['path']
        pkg_info['is_project'] = full_path.is_dir()
    
    # Display results
    sorted_packages = display_search_results(packages, console, debug)
    
    if sorted_packages:
        # Handle user actions
        handle_search_actions(sorted_packages, show_package_actions)
        
        # Offer deep search
        offer_deep_search(query, console, search_file_contents, debug)
    else:
        if Confirm.ask("\nWould you like to browse the catalog instead?"):
            browse_with_filter()

def db_menu():
    """Database operations menu"""
    console.print("[yellow]Database operations not yet implemented[/yellow]")

def git_menu():
    """Git operations menu"""
    console.print("[yellow]Git operations not yet implemented[/yellow]")

def install_menu():
    """Install from starbase menu"""
    console.print("[yellow]Install operations not yet implemented[/yellow]")

@app.command()
def claude(prompt: str = typer.Argument(None)):
    """Quick Claude query using your Max account"""
    if not prompt:
        console.print("[yellow]Usage: starbase claude 'your question here'[/yellow]")
        return
    
    try:
        # Just run claude command directly - it handles Max auth internally
        console.print(f"[dim]Using Claude Max session...[/dim]")
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0 and result.stdout:
            console.print(result.stdout)
        elif result.stderr:
            if "Credit balance is too low" in result.stderr:
                console.print("[yellow]⚠️  Not using Claude Max session[/yellow]")
                console.print("\nTo use your Claude Max account:")
                console.print("  1. Run: claude /status")
                console.print("  2. If not logged in, run: /login")
                console.print("  3. Try again after logging in")
            elif "not authenticated" in result.stderr.lower():
                console.print("[yellow]Not logged into Claude[/yellow]")
                console.print("\nTo login: /login")
            else:
                console.print(f"[red]Error: {result.stderr}[/red]")
                
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out after 60 seconds[/red]")
    except FileNotFoundError:
        console.print("[red]Claude CLI not found. Install with: brew install anthropic/tap/claude[/red]")

@app.command()
def index():
    """Index existing files in starbase into catalog"""
    starbase_path = Path(manager.get_active_path())
    console.print(f"[yellow]🔍 Indexing {starbase_path}...[/yellow]")
    
    indexed = 0
    skipped = 0
    updated = 0
    
    # Also index project directories
    for item in starbase_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # This looks like a project directory
            py_files = list(item.glob('*.py'))
            if py_files:
                # Check if already cataloged
                rel_path = str(item.relative_to(starbase_path))
                existing = db.search(tinydb.Query().path == rel_path)
                
                if not existing:
                    # Count all files
                    all_files = list(item.rglob('*'))
                    code_files = [f for f in all_files if f.is_file() and f.suffix in {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml'}]
                    
                    # Generate simple description
                    description = generate_smart_description(item)
                    
                    db.insert({
                        'name': item.name,
                        'path': rel_path,
                        'type': 'project',
                        'description': description,
                        'extracted_from': 'manual_scan',
                        'extracted_at': datetime.now().isoformat()
                    })
                    indexed += 1
                    console.print(f"  [dim]✓ {item.name} (project)[/dim]")
                else:
                    skipped += 1
    
    # Find individual files not in project directories
    for pattern in ['*.py', '*.js', '*.ts', '*.jsx', '*.tsx', '*.json', '*.yaml', '*.yml']:
        for file_path in starbase_path.glob(pattern):  # Only top-level files
            # Skip if in excluded directories
            if any(part in {'.venv', 'venv', '__pycache__', '.git', 'node_modules'} for part in file_path.parts):
                skipped += 1
                continue
                
            # Check if already in catalog
            rel_path = str(file_path.relative_to(starbase_path))
            existing = db.search(tinydb.Query().path == rel_path)
            if existing:
                skipped += 1
                continue
                
            # Add to catalog
            db.insert({
                'name': file_path.name,
                'path': rel_path,
                'type': 'file',
                'description': f'Standalone {file_path.suffix} file',
                'extracted_from': 'manual_scan',
                'extracted_at': datetime.now().isoformat()
            })
            indexed += 1
            console.print(f"  [dim]✓ {file_path.name}[/dim]")
            
    console.print(f"[green]✓ Indexed {indexed} new files[/green]")
    if skipped > 0:
        console.print(f"[dim]Skipped {skipped} files (already indexed or in excluded dirs)[/dim]")
    
    # Show catalog size
    total = len(db.all())
    console.print(f"\n[cyan]Catalog now contains {total} items[/cyan]")

@app.command()
def refresh_descriptions():
    """Update catalog descriptions using LLM analysis"""
    starbase_path = Path(manager.get_active_path())
    console.print("[yellow]🔄 Refreshing catalog descriptions with AI analysis...[/yellow]")
    
    updated = 0
    skipped = 0
    failed = 0
    
    all_entries = db.all()
    for entry in all_entries:
        if entry.get('type') == 'project':
            project_path = starbase_path / entry['path']
            if project_path.exists() and project_path.is_dir():
                console.print(f"\n[dim]Analyzing {entry['name']}...[/dim]")
                try:
                    new_desc = generate_smart_description(project_path)
                    
                    # Always update - LLM might generate better description
                    Query = tinydb.Query()
                    db.update({'description': new_desc}, Query.path == entry['path'])
                    updated += 1
                    console.print(f"[green]✓ {entry['name']}:[/green] {new_desc}")
                except Exception as e:
                    console.print(f"[red]✗ {entry['name']}: Failed - {e}[/red]")
                    failed += 1
            else:
                skipped += 1
        else:
            skipped += 1
    
    console.print(f"\n[green]✓ Updated {updated} descriptions[/green]")
    if failed > 0:
        console.print(f"[red]Failed to update {failed} descriptions[/red]")
    if skipped > 0:
        console.print(f"[dim]Skipped {skipped} entries (not projects)[/dim]")

@app.command()
def migrate():
    """Migrate existing codelib to starbase location"""
    current_path = Path(manager.get_active_path())
    new_path = Path.home() / "starbase"
    
    if str(current_path) == str(new_path):
        console.print("[green]Already using the standard starbase location![/green]")
        return
        
    console.print(f"[cyan]Current location:[/cyan] {current_path}")
    console.print(f"[cyan]New location:[/cyan] {new_path}")
    
    if current_path.exists() and not new_path.exists():
        if Confirm.ask(f"Move {current_path} to {new_path}?"):
            import shutil
            console.print("[yellow]Moving starbase...[/yellow]")
            shutil.move(str(current_path), str(new_path))
            
            # Update config
            active = manager.get_active_name()
            manager.config["starbases"][active]["path"] = str(new_path)
            manager.save_config()
            
            console.print("[green]✓ Starbase migrated successfully![/green]")
    elif new_path.exists():
        console.print("[red]Target location already exists! Please handle manually.[/red]")
    else:
        console.print("[yellow]No existing starbase found to migrate.[/yellow]")

@app.command()
def install(package_ref: str):
    """Quick install a package from search results (by number or name)"""
    # First try to interpret as a number from recent search
    if package_ref.isdigit():
        console.print("[yellow]Note: Package numbers are only valid immediately after a search.[/yellow]")
        console.print("Please search again or use the package name directly.")
        return
    
    # Search by name
    catalog_results = search_in_catalog(package_ref)
    if not catalog_results:
        console.print(f"[red]Package '{package_ref}' not found in starbase[/red]")
        console.print("Try searching first: starbase search <query>")
        return
    
    # Use first match
    result = catalog_results[0]
    path_parts = result['path'].split('/')
    package_name = path_parts[0] if path_parts else result['name']
    package_path = path_parts[0] if path_parts else result['path']
    
    # Check if project or file
    starbase_path = Path(manager.get_active_path())
    full_path = starbase_path / package_path
    is_project = full_path.is_dir()
    
    if is_project:
        # Install with PDM
        console.print(f"\n[cyan]Installing {package_name} with PDM...[/cyan]")
        console.print(f"[dim]Command: pdm add {full_path}[/dim]\n")
        
        # Check if we're in a PDM project
        if not (Path.cwd() / "pyproject.toml").exists():
            console.print("[yellow]⚠️  No pyproject.toml found in current directory![/yellow]")
            console.print("Initialize a PDM project first with: pdm init")
            return
        
        # Run PDM add
        subprocess.run(["pdm", "add", str(full_path)])
    else:
        # For single files, copy
        console.print(f"\n[cyan]Copying {package_name} to current directory...[/cyan]")
        target = Path.cwd() / full_path.name
        if target.exists():
            if not Confirm.ask(f"{full_path.name} already exists. Overwrite?"):
                return
        
        shutil.copy2(full_path, target)
        console.print(f"[green]✓ Copied to {target}[/green]")

@app.command()
def view(package_ref: str):
    """Quick view a package from search results (by number or name)"""
    # First try to interpret as a number from recent search
    if package_ref.isdigit():
        console.print("[yellow]Note: Package numbers are only valid immediately after a search.[/yellow]")
        console.print("Please search again or use the package name directly.")
        return
    
    # Search by name
    catalog_results = search_in_catalog(package_ref)
    if not catalog_results:
        console.print(f"[red]Package '{package_ref}' not found in starbase[/red]")
        console.print("Try searching first: starbase search <query>")
        return
    
    # Use first match
    result = catalog_results[0]
    path_parts = result['path'].split('/')
    package_name = path_parts[0] if path_parts else result['name']
    package_path = path_parts[0] if path_parts else result['path']
    
    # View the package
    starbase_path = Path(manager.get_active_path())
    full_path = starbase_path / package_path
    
    if full_path.is_dir():
        # Show main files in directory
        py_files = list(full_path.glob("*.py"))[:10]
        if py_files:
            console.print(f"\n[cyan]Files in {package_name}:[/cyan]")
            for i, f in enumerate(py_files, 1):
                size_kb = f.stat().st_size / 1024
                console.print(f"{i}. {f.name} ({size_kb:.1f} KB)")
            
            if len(list(full_path.glob("*.py"))) > 10:
                console.print(f"[dim]...and {len(list(full_path.glob('*.py'))) - 10} more files[/dim]")
            
            file_choice = Prompt.ask("\nSelect file to view (or Enter to skip)", default="")
            if file_choice.isdigit():
                file_idx = int(file_choice) - 1
                if 0 <= file_idx < len(py_files):
                    view_file(py_files[file_idx])
        else:
            console.print("[yellow]No Python files found in directory[/yellow]")
    else:
        view_file(full_path)

def ensure_mcp_globally_configured():
    """Ensures starbase is properly installed on every run."""
    # Pass the project root so the installer knows where the source is
    project_root = Path(__file__).parent.resolve()
    installer = MCPInstaller(project_root_path=project_root)
    if not installer.is_globally_installed():
        if console:
            console.print("[yellow]Starbase command not found in PATH. Auto-running global installer...[/yellow]")
            installer.install_and_configure_mcp()
            console.print("\n[bold green]✓ Auto-installation complete.[/bold green]")
            console.print("Please restart your terminal for PATH changes to take effect, then run your command again.")
        # Exit after install to ensure user restarts shell and gets new PATH
        sys.exit(0)

def main():
    """Main entry point for starbase command."""
    # Do not run the check if the command is for the mcp-server itself,
    # or if it's the global_install command, to avoid loops.
    if "mcp-server" not in sys.argv and "global-install" not in sys.argv:
        ensure_mcp_globally_configured()
    
    if len(sys.argv) == 1:
        # No arguments - run interactive menu
        while True:
            selection = main_menu()
            if selection == "🛑 Exit":
                break
    else:
        # Run CLI command
        app()

if __name__ == "__main__":
    main()