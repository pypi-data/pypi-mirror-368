"""
Catalog browsing and management functionality.

This module contains functions for browsing and organizing catalog entries.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console


def handle_empty_catalog(starbase_path: Path, console: Console) -> List[Path]:
    """Handle the case when catalog is empty and suggest uncataloged files.
    
    Returns:
        List of uncataloged Python files found
    """
    console.print("[yellow]📚 Catalog is empty![/yellow]")
    console.print("\nThe catalog tracks what you've extracted to starbase.")
    console.print("To add items:")
    console.print("  • Use 'Extract from Messy Code' to add existing projects")
    console.print("  • Files are added to catalog when extracted")
    
    # Find uncataloged Python files
    py_files = find_uncataloged_files(starbase_path)
    
    if py_files:
        display_uncataloged_files(py_files, starbase_path, console)
    
    return py_files


def find_uncataloged_files(starbase_path: Path) -> List[Path]:
    """Find Python files that are not in the catalog.
    
    Returns:
        List of Python files excluding venv directories
    """
    py_files = list(starbase_path.rglob("*.py"))
    # Exclude venv files from count
    return [f for f in py_files if not any(part in {'.venv', 'venv', '__pycache__'} for part in f.parts)]


def display_uncataloged_files(py_files: List[Path], starbase_path: Path, console: Console) -> None:
    """Display information about uncataloged files."""
    console.print(f"\n[yellow]⚠️  Found {len(py_files)} Python files in starbase not in catalog![/yellow]")
    console.print("\n[green]Run 'starbase index' to add them to the catalog[/green]")
    console.print("\nShowing first 10 uncataloged files:")
    
    for f in py_files[:10]:
        console.print(f"  • {f.relative_to(starbase_path)}")
    
    if len(py_files) > 10:
        console.print(f"  [dim]...and {len(py_files) - 10} more[/dim]")


def categorize_entry(entry: Dict[str, Any]) -> str:
    """Categorize a catalog entry based on name and path patterns.
    
    Returns:
        Category name for the entry
    """
    name = entry.get('name', '').lower()
    path = entry.get('path', '').lower()
    
    if 'test' in name or 'spec' in name:
        return 'Tests'
    elif name.endswith(('.yaml', '.yml', '.toml', '.json', '.env')):
        return 'Config Files'
    elif 'main' in name or 'app' in name or 'run' in name:
        return 'Entry Points'
    elif 'lib' in path or 'utils' in name or 'helper' in name:
        return 'Libraries/Utilities'
    else:
        return 'Other Modules'


def group_entries_by_category(entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group catalog entries by their categories.
    
    Returns:
        Dictionary mapping category names to lists of entries
    """
    groups = {}
    
    for entry in entries:
        category = categorize_entry(entry)
        if category not in groups:
            groups[category] = []
        groups[category].append(entry)
    
    return groups


def display_catalog_groups(groups: Dict[str, List[Dict[str, Any]]], console: Console) -> int:
    """Display grouped catalog entries.
    
    Returns:
        Total number of entries shown
    """
    console.print("\n[cyan]📚 Starbase Catalog[/cyan]\n")
    
    total_shown = 0
    
    for category, entries in sorted(groups.items()):
        if entries:
            total_shown += display_category_entries(category, entries, console)
    
    return total_shown


def display_category_entries(category: str, entries: List[Dict[str, Any]], console: Console, max_show: int = 5) -> int:
    """Display entries for a single category.
    
    Returns:
        Number of entries shown
    """
    console.print(f"[yellow]{category} ({len(entries)} items):[/yellow]")
    
    shown = 0
    for entry in entries[:max_show]:
        desc = truncate_description(entry.get('description', 'No description'))
        console.print(f"  • {entry['name']} - {desc}")
        shown += 1
    
    if len(entries) > max_show:
        console.print(f"  [dim]...and {len(entries) - max_show} more[/dim]")
    
    console.print()
    return shown


def truncate_description(description: str, max_length: int = 50) -> str:
    """Truncate description to maximum length."""
    if len(description) > max_length:
        return description[:max_length] + '...'
    return description


def convert_entries_to_results(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert catalog entries to search result format."""
    return [{
        'name': e.get('name', ''),
        'path': e.get('path', ''),
        'match_type': 'browse',
        'match_context': e.get('description', 'Browsing catalog')
    } for e in entries]


def apply_filter_hint(entries: List[Dict[str, Any]], filter_hint: Optional[str]) -> List[Dict[str, Any]]:
    """Apply optional filter hint to entries.
    
    Currently supports 'recent' filter to sort by timestamp.
    """
    if not filter_hint or not entries:
        return entries
    
    if 'recent' in filter_hint.lower():
        # Sort by timestamp, most recent first
        return sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return entries