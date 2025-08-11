"""
File content search functionality for starbase.

This module provides functions for searching within file contents,
with support for ripgrep and Python fallback.
"""

import json
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Optional


def search_with_ripgrep(query: str, starbase_path: Path, limit: int) -> Optional[List[Dict]]:
    """Search files using ripgrep if available.
    
    Returns:
        List of results if successful, None if ripgrep not available
    """
    try:
        rg_cmd = [
            "rg", "-i", "--json", 
            "--max-count", "3",  # Max 3 matches per file
            "--type", "py",  # Python files only for now
            query, 
            str(starbase_path)
        ]
        
        result = subprocess.run(rg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return parse_ripgrep_output(result.stdout, limit)
        
        return []
        
    except FileNotFoundError:
        return None  # Ripgrep not available


def parse_ripgrep_output(output: str, limit: int) -> List[Dict]:
    """Parse ripgrep JSON output into result dictionaries."""
    results = []
    
    for line in output.strip().split('\n'):
        if not line:
            continue
            
        try:
            match = json.loads(line)
            if match.get('type') == 'match':
                result = extract_match_data(match)
                if result:
                    results.append(result)
                    
                    if len(results) >= limit:
                        break
        except json.JSONDecodeError:
            continue
    
    return results


def extract_match_data(match: Dict) -> Optional[Dict]:
    """Extract relevant data from a ripgrep match."""
    data = match.get('data', {})
    path_text = data.get('path', {}).get('text', '')
    
    if not path_text:
        return None
        
    path = Path(path_text)
    line_num = data.get('line_number')
    line_content = data.get('lines', {}).get('text', '').strip()
    
    return {
        'name': path.name,
        'path': str(path),
        'match_type': 'content',
        'match_context': f"Line {line_num}: {line_content[:60]}...",
        'line_number': line_num
    }


def install_ripgrep(console) -> bool:
    """Attempt to install ripgrep based on platform.
    
    Returns:
        True if installation successful, False otherwise
    """
    console.print("[yellow]Ripgrep not found. Installing for better search performance...[/yellow]")
    
    system = platform.system().lower()
    
    try:
        if system == "darwin":  # macOS
            return install_ripgrep_macos(console)
        elif system == "linux":
            return install_ripgrep_linux(console)
        elif system == "windows":
            return install_ripgrep_windows(console)
        else:
            console.print("[yellow]Unknown platform. Please install ripgrep manually.[/yellow]")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[yellow]Auto-install failed. Using Python fallback search...[/yellow]")
        return False


def install_ripgrep_macos(console) -> bool:
    """Install ripgrep on macOS using Homebrew."""
    subprocess.run(["brew", "install", "ripgrep"], check=True)
    console.print("[green]✓ Ripgrep installed successfully![/green]")
    return True


def install_ripgrep_linux(console) -> bool:
    """Install ripgrep on Linux using available package manager."""
    if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
        subprocess.run(["sudo", "apt", "install", "-y", "ripgrep"], check=True)
    elif subprocess.run(["which", "dnf"], capture_output=True).returncode == 0:
        subprocess.run(["sudo", "dnf", "install", "-y", "ripgrep"], check=True)
    else:
        console.print("[yellow]Please install ripgrep manually for your Linux distribution[/yellow]")
        return False
    
    console.print("[green]✓ Ripgrep installed successfully![/green]")
    return True


def install_ripgrep_windows(console) -> bool:
    """Install ripgrep on Windows."""
    console.print("[yellow]Please install ripgrep via scoop: scoop install ripgrep[/yellow]")
    return False


def search_with_python_fallback(query: str, starbase_path: Path, limit: int) -> List[Dict]:
    """Fallback Python-based search when ripgrep is not available."""
    results = []
    
    for py_file in starbase_path.rglob("*.py"):
        if should_skip_file(py_file):
            continue
            
        file_results = search_in_file(py_file, query, limit - len(results))
        results.extend(file_results)
        
        if len(results) >= limit:
            break
    
    return results


def should_skip_file(file_path: Path) -> bool:
    """Check if a file should be skipped during search."""
    skip_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules'}
    return any(part in skip_dirs for part in file_path.parts)


def search_in_file(file_path: Path, query: str, max_results: int) -> List[Dict]:
    """Search for query in a single file."""
    results = []
    
    try:
        content = file_path.read_text()
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            if query.lower() in line.lower():
                results.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'match_type': 'content',
                    'match_context': f"Line {i}: {line.strip()[:60]}...",
                    'line_number': i
                })
                
                if len(results) >= max_results:
                    break
                    
    except Exception:
        pass  # Skip files that can't be read
    
    return results