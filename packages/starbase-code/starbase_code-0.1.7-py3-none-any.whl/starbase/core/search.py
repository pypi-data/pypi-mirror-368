"""
Search functionality for starbase.

This module contains search-related functions with reduced complexity.
"""

from pathlib import Path
from typing import Dict, List, Any, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm


def collect_search_results(query: str, search_in_catalog, search_with_ast) -> Tuple[Dict[str, Any], List[Any]]:
    """Collect and organize search results from catalog and AST search.
    
    Returns:
        Tuple of (packages dict, all_results list for debug)
    """
    packages = {}
    all_results = []
    
    # Catalog search
    catalog_results = search_in_catalog(query)
    for r in catalog_results:
        package_name, package_info = process_catalog_result(r, packages)
        packages[package_name] = package_info
        all_results.append(r)
    
    # AST search
    ast_results = search_with_ast(query)
    for r in ast_results:
        package_name, package_info = process_ast_result(r, packages)
        packages[package_name] = package_info
        all_results.append(r)
    
    return packages, all_results


def process_catalog_result(result: Dict[str, Any], existing_packages: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Process a single catalog search result."""
    from pathlib import Path
    
    path_parts = result['path'].split('/')
    package_name = path_parts[0] if path_parts else result['name']
    
    # Check if this is a project or single file
    # Note: This requires manager to be passed in or accessed differently
    # For now, we'll assume the caller provides the full path check
    
    if package_name not in existing_packages:
        existing_packages[package_name] = {
            'name': package_name,
            'path': path_parts[0] if path_parts else result['path'],
            'is_project': False,  # Caller should update this
            'description': result.get('description', 'No description'),
            'matches': []
        }
    
    existing_packages[package_name]['matches'].append({
        'type': 'catalog',
        'context': result['match_context'],
        'full_path': result['path']
    })
    
    return package_name, existing_packages[package_name]


def process_ast_result(result: Dict[str, Any], existing_packages: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Process a single AST search result."""
    path_parts = result['path'].split('/')
    package_name = path_parts[0] if path_parts else result['name']
    
    if package_name not in existing_packages:
        existing_packages[package_name] = {
            'name': package_name,
            'path': path_parts[0],
            'is_project': False,  # Caller should update this
            'description': f"Contains {result['match_context']}",
            'matches': []
        }
    
    existing_packages[package_name]['matches'].append({
        'type': 'code',
        'context': result['match_context'],
        'line': result.get('line_number'),
        'full_path': result['path']
    })
    
    return package_name, existing_packages[package_name]


def display_search_results(packages: Dict[str, Any], console: Console, debug: bool = False) -> List[Tuple[str, Dict[str, Any]]]:
    """Display search results and return sorted packages."""
    if not packages:
        console.print("\n[yellow]No matches found.[/yellow]")
        console.print("[dim]Try searching with different terms or use --deep for content search[/dim]")
        return []
    
    console.print(f"\n[green]Found {len(packages)} matching package(s):[/green]\n")
    
    # Sort packages by relevance (more matches = more relevant)
    sorted_packages = sorted(packages.items(), key=lambda x: len(x[1]['matches']), reverse=True)
    
    for i, (pkg_name, pkg_info) in enumerate(sorted_packages[:10], 1):
        display_single_package(i, pkg_name, pkg_info, console, debug)
    
    return sorted_packages


def display_single_package(index: int, pkg_name: str, pkg_info: Dict[str, Any], console: Console, debug: bool):
    """Display a single package result."""
    # Show package name prominently
    if pkg_info['is_project']:
        console.print(f"[cyan]{index}. 📁 {pkg_name}[/cyan] (project)")
    else:
        console.print(f"[cyan]{index}. 📄 {pkg_name}[/cyan] (file)")
    
    # Show description
    console.print(f"   {pkg_info['description']}")
    
    # Show match summary
    if debug:
        display_match_details(pkg_info['matches'], console)
    else:
        match_count = len(pkg_info['matches'])
        console.print(f"   [dim]({match_count} match{'es' if match_count > 1 else ''})[/dim]")
    
    console.print()


def display_match_details(matches: List[Dict[str, Any]], console: Console, max_show: int = 3):
    """Display match details for debug mode."""
    for match in matches[:max_show]:
        if match['type'] == 'catalog':
            console.print(f"   [dim]• {match['context']}[/dim]")
        else:
            line_info = f":{match['line']}" if match.get('line') else ""
            console.print(f"   [dim]• {match['context']}{line_info}[/dim]")
    
    if len(matches) > max_show:
        console.print(f"   [dim]• ...and {len(matches) - max_show} more matches[/dim]")


def handle_search_actions(sorted_packages: List[Tuple[str, Dict[str, Any]]], show_package_actions) -> None:
    """Handle user selection and actions for search results."""
    if not sorted_packages:
        return
    
    if len(sorted_packages) == 1:
        if Confirm.ask("Show actions for this package?", default=True):
            pkg_name, pkg_info = sorted_packages[0]
            show_package_actions(pkg_name, pkg_info['path'], pkg_info['is_project'])
    else:
        choice = Prompt.ask("\nSelect package number (or 'q' to quit)", default="q")
        if choice != 'q' and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(sorted_packages):
                pkg_name, pkg_info = sorted_packages[idx]
                show_package_actions(pkg_name, pkg_info['path'], pkg_info['is_project'])


def offer_deep_search(query: str, console: Console, search_file_contents, debug: bool = False):
    """Offer deep content search if needed."""
    if not debug and Confirm.ask("\nSearch file contents too?", default=False):
        content_results = search_file_contents(query)
        if content_results:
            console.print("\n[cyan]Additional content matches:[/cyan]")
            for r in content_results[:5]:
                console.print(f"  • {r['name']}:{r['line_number']} - {r['match_context']}")
                if debug:
                    console.print(f"    [dim]{r['path']}[/dim]")


def process_deep_search_results(packages: Dict[str, Any], query: str, search_file_contents) -> None:
    """Process deep search results and add to existing packages."""
    content_results = search_file_contents(query)
    for r in content_results:
        path_parts = r['path'].split('/')
        package_name = path_parts[0] if path_parts else r['name']
        
        if package_name in packages:
            packages[package_name]['matches'].append({
                'type': 'content',
                'context': r['match_context'],
                'line': r.get('line_number'),
                'full_path': r['path']
            })


def show_quick_actions(console: Console) -> None:
    """Show quick actions help text."""
    console.print("[yellow]Quick Actions:[/yellow]")
    console.print(f"• To install: [cyan]starbase install <number>[/cyan]")
    console.print(f"• To view: [cyan]starbase view <number>[/cyan]")
    console.print(f"• For more options: Select a package number above")


def show_no_results_help(console: Console) -> None:
    """Show help text when no results found."""
    console.print("\n[yellow]No matches found.[/yellow]")
    console.print("\nTry:")
    console.print("  • Using --deep flag to search file contents")
    console.print("  • Using partial words (e.g., 'auth' instead of 'authentication')")
    console.print("  • Checking if the code is in a different starbase")


def update_package_project_status(packages: Dict[str, Any], manager) -> None:
    """Update is_project flag for all packages based on file system check."""
    from pathlib import Path
    
    starbase_path = Path(manager.get_active_path())
    for pkg_info in packages.values():
        full_path = starbase_path / pkg_info['path']
        pkg_info['is_project'] = full_path.is_dir()