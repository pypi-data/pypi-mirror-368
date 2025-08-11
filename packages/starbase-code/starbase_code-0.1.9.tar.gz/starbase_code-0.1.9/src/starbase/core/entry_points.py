"""
Entry point detection and analysis functionality.

This module contains functions for finding and analyzing Python entry points.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console


def find_entry_points(path: Path, console: Optional[Console] = None) -> List[Dict[str, Any]]:
    """Find Python entry points using AST analysis."""
    entry_points = []
    
    for py_file in get_valid_python_files(path):
        entry_point = analyze_file_for_entry_point(py_file, console)
        if entry_point:
            entry_points.append(entry_point)
    
    # Sort by priority, then by modification time
    entry_points.sort(key=lambda x: (-x['priority'], -x['mtime']))
    return entry_points


def get_valid_python_files(path: Path) -> List[Path]:
    """Get Python files excluding virtual environments."""
    py_files = []
    for py_file in path.glob("*.py"):
        if not any(part in {'.venv', 'venv', '__pycache__'} for part in py_file.parts):
            py_files.append(py_file)
    return py_files


def analyze_file_for_entry_point(py_file: Path, console: Optional[Console] = None) -> Optional[Dict[str, Any]]:
    """Analyze a single Python file to determine if it's an entry point."""
    try:
        content = py_file.read_text()
        tree = ast.parse(content)
        
        # Gather entry point indicators
        indicators = gather_entry_point_indicators(content, tree)
        
        # Calculate priority
        priority = calculate_entry_point_priority(py_file, indicators)
        
        # Only consider files with positive priority or main block
        if priority > 0 or indicators['has_main_block']:
            return create_entry_point_info(py_file, content, indicators, priority)
        
        return None
        
    except Exception as e:
        if console:
            console.print(f"[dim]Skipped {py_file.name}: {e}[/dim]")
        return None


def gather_entry_point_indicators(content: str, tree: ast.AST) -> Dict[str, Any]:
    """Gather various indicators that suggest a file is an entry point."""
    return {
        'has_main_block': check_for_main_block(tree),
        'has_app_run': check_for_app_run_pattern(content),
        'has_cli_decorator': check_for_cli_decorators(content),
        'import_count': count_imports(tree),
        'line_count': len(content.splitlines())
    }


def check_for_main_block(tree: ast.AST) -> bool:
    """Check if the AST contains if __name__ == "__main__": pattern."""
    for node in ast.walk(tree):
        if (isinstance(node, ast.If) and 
            isinstance(node.test, ast.Compare) and
            isinstance(node.test.left, ast.Name) and
            node.test.left.id == "__name__"):
            return True
    return False


def check_for_app_run_pattern(content: str) -> bool:
    """Check for common app.run() or main() patterns."""
    return "app.run(" in content or "main()" in content


def check_for_cli_decorators(content: str) -> bool:
    """Check for common CLI framework decorators."""
    return "@app.command" in content or "@click.command" in content


def count_imports(tree: ast.AST) -> int:
    """Count the number of import statements."""
    return len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])


def calculate_entry_point_priority(py_file: Path, indicators: Dict[str, Any]) -> int:
    """Calculate priority score for potential entry point."""
    priority = 0
    
    # Indicator-based scoring
    if indicators['has_main_block']:
        priority += 10
    if indicators['has_app_run']:
        priority += 8
    if indicators['has_cli_decorator']:
        priority += 7
    
    # Filename-based scoring
    priority += score_filename(py_file.name.lower())
    
    return priority


def score_filename(filename: str) -> int:
    """Score filename for entry point likelihood."""
    score = 0
    
    # Positive indicators
    if "main" in filename:
        score += 5
    if "app" in filename:
        score += 4
    if "run" in filename:
        score += 3
    
    # Negative indicators
    if "test" in filename:
        score -= 5
    
    return score


def create_entry_point_info(py_file: Path, content: str, indicators: Dict[str, Any], priority: int) -> Dict[str, Any]:
    """Create entry point information dictionary."""
    return {
        'file': py_file,
        'priority': priority,
        'line_count': indicators['line_count'],
        'import_count': indicators['import_count'],
        'mtime': py_file.stat().st_mtime,
        'has_main': indicators['has_main_block'],
        'type': determine_entry_point_type(indicators)
    }


def determine_entry_point_type(indicators: Dict[str, Any]) -> str:
    """Determine the type of entry point based on indicators."""
    if indicators['has_cli_decorator']:
        return 'cli'
    elif indicators['has_main_block']:
        return 'script'
    else:
        return 'app'