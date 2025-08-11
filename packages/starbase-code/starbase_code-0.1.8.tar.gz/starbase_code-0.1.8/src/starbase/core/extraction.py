"""
Extraction helper functions for starbase.

This module contains functions to help with code extraction logic,
breaking down the complex extract_menu function into smaller pieces.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set
from datetime import datetime
import shutil
import json
import tinydb

from .analysis import extract_local_imports, trace_dependencies


def extract_single_file(path: Path) -> Dict[str, Any]:
    """Create entry point for single file extraction."""
    content = path.read_text()
    return {
        'file': path,
        'priority': 10,
        'line_count': len(content.splitlines()),
        'import_count': 0,
        'mtime': path.stat().st_mtime,
        'has_main': '__main__' in content,
        'type': 'script' if path.suffix == '.py' else 'file'
    }


def get_python_files_in_directory(path: Path) -> Tuple[List[Path], int]:
    """Get Python files in directory and count files in subdirectories."""
    py_files = list(path.glob("*.py"))
    
    # Get subdirectories
    subdirs = [d for d in path.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    # Count files in subdirectories
    py_files_in_subdirs = 0
    for subdir in subdirs:
        py_files_in_subdirs += len(list(subdir.rglob("*.py")))
    
    return py_files, py_files_in_subdirs


def display_group_info(group: Dict[str, Any], index: int, path: Path, console: Any) -> None:
    """Display information about a single group."""
    # Show group header
    total_py_files = len([f for f in group['files'] if f.suffix == '.py'])
    if group['type'] == 'connected' or total_py_files > 1:
        console.print(f"{index}️⃣  [bold]{group['name']}[/bold] - {total_py_files} files")
    else:
        console.print(f"{index}️⃣  [bold]{group['name']}[/bold] - standalone")
    
    # Show top-level files in group first
    top_level_files = [f for f in group['files'] if f.parent == path]
    for file in top_level_files:
        display_file_info(file, group, console)
    
    # Show subdirectories if any
    if group.get('subdirectories'):
        for subdir in group['subdirectories']:
            subdir_files = [f for f in group['files'] if str(subdir) in str(f)]
            if subdir_files:
                console.print(f"   📁 {subdir.name}/ ({len(subdir_files)} files)")
    
    # Show version information if any
    if group.get('versions'):
        for file, versions in group['versions'].items():
            console.print(f"   [dim]⚠️  Has {len(versions)} old version(s): {', '.join(v.name for v in versions)}[/dim]")
            console.print(f"      [dim]These will be skipped during extraction[/dim]")
    
    console.print()


def display_file_info(file: Path, group: Dict[str, Any], console: Any) -> None:
    """Display information about a single file within a group."""
    is_main = file == group['main_file']
    is_test = file in group.get('test_files', [])
    
    if is_main:
        prefix = "   📍"
    elif is_test:
        prefix = "   🧪"
    else:
        prefix = "   📄"
        
    console.print(f"{prefix} {file.name}")
    
    # Show import relationships if connected group
    if group['type'] == 'connected' and not is_main:
        local_imports = extract_local_imports(file)
        imports_in_group = [f.name for f in local_imports if f in group['files']]
        if imports_in_group:
            console.print(f"      → imports: {', '.join(imports_in_group)}")


def check_existing_files(groups: List[Dict[str, Any]], check_starbase_status) -> List[Dict[str, Any]]:
    """Check if any files already exist in starbase."""
    existing_warnings = []
    for group in groups:
        for file in group['files']:
            status = check_starbase_status(file)
            if status['exists']:
                existing_warnings.append({
                    'file': file,
                    'group': group['name'],
                    'status': status
                })
    return existing_warnings


def convert_group_to_entry_points(group: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert a group to entry points format for do_extraction."""
    entry_points = []
    for file in group['files']:
        entry_points.append({
            'file': file,
            'priority': 10 if file == group['main_file'] else 5,
            'line_count': len(file.read_text().splitlines()),
            'import_count': 0,
            'mtime': file.stat().st_mtime,
            'has_main': file == group['main_file'],
            'type': 'script'
        })
    return entry_points


def parse_package_selection(selection: str, total_groups: int) -> List[int]:
    """Parse user selection string for packages."""
    if selection.lower() == 'all':
        return list(range(1, total_groups + 1))
    
    selected_indices = []
    for part in selection.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            selected_indices.extend(range(start, end + 1))
        else:
            selected_indices.append(int(part))
    
    # Filter valid indices
    return [i for i in selected_indices if 0 < i <= total_groups]


def find_related_files(py_file: Path) -> List[str]:
    """Find bash scripts, configs, etc. related to this file"""
    base_name = py_file.stem
    related = []
    
    # Check for shell scripts with same base name
    for ext in ['', '.sh', '.bash']:
        script = py_file.parent / (base_name + ext)
        if script.exists() and script != py_file and script.is_file():
            # Check if executable
            import os
            if os.access(script, os.X_OK) or script.suffix in ['.sh', '.bash']:
                related.append(script.name)
    
    # For package isolation, only include config files if the file is the main entry point
    # or if we're extracting a whole directory
    # Don't automatically include project-wide configs for single file extractions
    
    return related[:5]  # Limit display


def generate_smart_description(project_path: Path, entry_points: List[Dict] = None) -> str:
    """Generate a simple description by analyzing the code"""
    # Simple fallback - just describe what we extracted
    if entry_points and len(entry_points) == 1:
        file_path = entry_points[0]['file']
        return f"Extracted {file_path.name} - Python script"
    elif entry_points:
        return f"Python project with {len(entry_points)} entry points"
    else:
        return "Extracted code package"


def do_extraction(entry_points: List[Dict], source_path: Path, include_deps: bool, 
                 package_name: Optional[str], manager, db, console) -> List[Dict]:
    """Perform the actual extraction of files to starbase
    
    Args:
        entry_points: List of entry point dictionaries
        source_path: Source path being extracted from
        include_deps: Whether to include dependencies
        package_name: Optional package name override
        manager: StarbaseManager instance
        db: TinyDB database instance
        console: Rich Console instance
    
    Returns:
        List of extracted file dictionaries
    """
    starbase_path = Path(manager.get_active_path())
    extracted_files = []
    
    # Check if we already have an entry with this exact name
    Query = tinydb.Query()
    
    # First determine the package name
    if package_name is None:
        # Only determine package name if not provided
        if len(entry_points) == 1 and entry_points[0]['file'].is_file():
            # For single file extractions, use the file stem as package name
            package_name = entry_points[0]['file'].stem
        else:
            # For multiple files, use the first file's stem as fallback
            package_name = entry_points[0]['file'].stem
    
    # Now search for existing entry by package name
    existing_entry = db.search(Query.name == package_name)
    
    # Package name is already determined above
    
    # Get all files to extract
    all_files = set()
    for ep in entry_points:
        all_files.add(ep['file'])
        
        # Add dependencies if requested
        if include_deps:
            deps = trace_dependencies(ep['file'])
            all_files.update(deps)
            console.print(f"[dim]Found {len(deps)} dependencies for {ep['file'].name}[/dim]")
        
        # Add related files (configs, scripts)
        related = find_related_files(ep['file'])
        for rel in related:
            rel_path = ep['file'].parent / rel
            if rel_path.exists():
                all_files.add(rel_path)
    
    # Determine target structure
    # If all files are from same directory, preserve structure
    common_parent = None
    if len(all_files) > 1:
        parents = {f.parent for f in all_files}
        if len(parents) == 1:
            common_parent = list(parents)[0]
    
    # Use the package name determined earlier
    extract_name = package_name
    
    # Determine target directory
    if existing_entry:
        # Use existing directory
        target_dir = starbase_path / existing_entry[0]['path']
        console.print(f"\n[yellow]Updating existing extraction: {target_dir.name}/[/yellow]")
        # Clear existing files first
        if target_dir.exists() and target_dir.is_dir():
            for item in target_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
    else:
        # Make name unique if needed
        target_dir = starbase_path / extract_name
        counter = 1
        while target_dir.exists():
            target_dir = starbase_path / f"{extract_name}_{counter}"
            counter += 1
        console.print(f"\n[green]Extracting to: {target_dir.name}/[/green]")
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    for file in all_files:
        try:
            # Determine relative path
            if common_parent:
                rel_path = file.relative_to(common_parent)
            else:
                rel_path = file.name
            
            target_file = target_dir / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file, target_file)
            extracted_files.append({
                'source': str(file),
                'target': str(target_file.relative_to(starbase_path)),
                'size': file.stat().st_size
            })
            console.print(f"  [dim]✓ {rel_path}[/dim]")
        except Exception as e:
            console.print(f"  [red]✗ {file.name}: {e}[/red]")
    
    # Update catalog
    if extracted_files:
        # Generate simple description
        description = generate_smart_description(target_dir, entry_points)
        
        catalog_entry = {
            'name': extract_name,
            'path': str(target_dir.relative_to(starbase_path)),
            'type': 'project',
            'description': description,
            'extracted_from': str(source_path),
            'extracted_at': datetime.now().isoformat()
        }
        
        # Update or insert catalog entry based on what we found earlier
        Query = tinydb.Query()
        
        if existing_entry:
            # Update existing entry - use the correct query based on how we found it
            if existing_entry[0].get('extracted_from') == str(source_path):
                # Found by source path
                db.update(catalog_entry, Query.extracted_from == str(source_path))
            else:
                # Found by name
                db.update(catalog_entry, Query.name == existing_entry[0]['name'])
            console.print(f"[yellow]Updated existing catalog entry: {existing_entry[0]['name']}[/yellow]")
        else:
            # Add new entry
            db.insert(catalog_entry)
        
        total_size = sum(f['size'] for f in extracted_files)
        console.print(f"\n[green]✓ Extracted {len(extracted_files)} files ({total_size / 1024:.1f} KB)[/green]")
        if existing_entry:
            console.print(f"[green]✓ Updated catalog entry '{extract_name}'[/green]")
        else:
            console.print(f"[green]✓ Added to catalog as '{extract_name}'[/green]")
        
        # Show what was extracted
        if len(entry_points) > 1:
            console.print("\n[cyan]Entry points:[/cyan]")
            for ep in entry_points:
                console.print(f"  • {ep['file'].name}")
        
        if include_deps and len(all_files) > len(entry_points):
            console.print(f"\n[cyan]Included {len(all_files) - len(entry_points)} dependencies[/cyan]")
        
        # Create package.json manifest for package isolation
        manifest = {
            'name': extract_name,
            'version': '0.1.0',
            'description': description,
            'extracted_from': str(source_path),
            'extracted_at': datetime.now().isoformat(),
            'files': [f['target'] for f in extracted_files],
            'entry_points': [str(ep['file'].name) for ep in entry_points],
            'dependencies': [],
            'file_count': len(extracted_files),
            'total_size': sum(f['size'] for f in extracted_files)
        }
        
        manifest_path = target_dir / 'package.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        console.print(f"[green]✓ Created package manifest[/green]")
        
        # Note: ensure_mcp_installed is not called here - handle it in the caller if needed
    
    return extracted_files


def validate_and_resolve_path(initial_path: Optional[str], console: Any) -> Optional[Path]:
    """Validate and resolve extraction path from user input.
    
    Returns None if path is invalid.
    """
    if initial_path:
        path = Path(initial_path).resolve()
    else:
        from rich.prompt import Prompt
        path = Prompt.ask("Enter path to analyze", default=".")
        path = Path(path).resolve()
    
    if not path.exists():
        console.print("[red]Path does not exist![/red]")
        return None
    
    return path


def handle_single_file_extraction(path: Path, console: Any, do_extraction) -> None:
    """Handle extraction of a single file."""
    from rich.prompt import Confirm
    
    console.print(f"\n[cyan]🔍 Extracting single file: {path.name}[/cyan]")
    entry_point = extract_single_file(path)
    include_deps = Confirm.ask("Include dependencies?", default=True)
    do_extraction([entry_point], path.parent, include_deps)


def analyze_directory_for_extraction(path: Path, console: Any) -> Optional[List[Dict[str, Any]]]:
    """Analyze directory and return groups or None if no files found."""
    from .analysis import analyze_file_relationships
    from .assignment import analyze_project_with_subdirectories
    
    # Get Python files and analyze
    py_files, py_files_in_subdirs = get_python_files_in_directory(path)
    
    if not py_files:
        console.print("[yellow]No Python files found in directory.[/yellow]")
        return None
    
    # Analyze file relationships for smart grouping
    if py_files_in_subdirs > 0:
        console.print(f"\n[dim]Analyzing {len(py_files)} top-level files and {py_files_in_subdirs} files in subdirectories...[/dim]")
        groups = analyze_project_with_subdirectories(path)
    else:
        console.print(f"\n[dim]Analyzing relationships between {len(py_files)} files...[/dim]")
        groups = analyze_file_relationships(py_files)
    
    return groups


def handle_existing_file_warnings(existing_warnings: List[Dict[str, Any]], console: Any) -> bool:
    """Display warnings about existing files and ask for confirmation.
    
    Returns True if user wants to continue, False otherwise.
    """
    from rich.prompt import Confirm
    
    if not existing_warnings:
        return True
    
    console.print("\n[yellow]⚠️  Some files already exist in starbase:[/yellow]")
    for warning in existing_warnings:
        console.print(f"   • {warning['file'].name} in package '{warning['group']}'")
    
    return Confirm.ask("\nContinue anyway?", default=True)


def handle_single_group_extraction(group: Dict[str, Any], path: Path, console: Any, do_extraction) -> None:
    """Handle extraction when there's only one group."""
    from rich.prompt import Confirm
    
    console.print(f"\nPackage '{group['name']}' contains {len(group['files'])} file(s)")
    if Confirm.ask("Extract this package?", default=True):
        entry_points = convert_group_to_entry_points(group)
        do_extraction(entry_points, path, include_deps=False, package_name=group['name'])


def parse_group_selection(selection: str, total_groups: int) -> List[int]:
    """Parse user selection string into list of indices."""
    selected_indices = []
    
    if selection.lower() == 'all':
        return list(range(1, total_groups + 1))
    
    for part in selection.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            selected_indices.extend(range(start, end + 1))
        else:
            selected_indices.append(int(part))
    
    # Filter valid indices
    return [i for i in selected_indices if 0 < i <= total_groups]


def extract_selected_groups(selected_groups: List[Dict[str, Any]], path: Path, console: Any, do_extraction) -> None:
    """Extract the selected groups."""
    console.print(f"\n[cyan]Extracting {len(selected_groups)} package(s)...[/cyan]")
    
    for group in selected_groups:
        console.print(f"\n📦 Extracting package '{group['name']}'...")
        entry_points = create_entry_points_for_group(group)
        do_extraction(entry_points, path, include_deps=False, package_name=group['name'])


def create_entry_points_for_group(group: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create entry points list for a group of files."""
    entry_points = []
    
    for file in group['files']:
        entry_points.append({
            'file': file,
            'priority': 10 if file == group['main_file'] else 5,
            'line_count': len(file.read_text().splitlines()),
            'import_count': 0,
            'mtime': file.stat().st_mtime,
            'has_main': file == group['main_file'],
            'type': 'script'
        })
    
    return entry_points