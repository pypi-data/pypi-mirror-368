#!/usr/bin/env python3
"""
Starbase MCP Server - Provides access to all packages in ~/starbase via MCP protocol.
This module is installed with starbase and can be run directly or via wrapper.
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import defaultdict

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("MCP libraries not installed. Installing starbase will configure this automatically.", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server - Starship Command Interface
mcp = FastMCP("Starbase Alpha - Code Repository Command Interface")

# Starbase location - can be overridden by environment variable
import os
STARBASE_PATH = Path(os.environ.get('STARBASE_PATH', Path.home() / "starbase"))
CATALOG_FILE = STARBASE_PATH / "catalog.json"

def load_catalog() -> List[Dict]:
    """Load the catalog.json file"""
    if CATALOG_FILE.exists():
        try:
            with open(CATALOG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def categorize_modules(catalog: List[Dict]) -> Dict[str, List[str]]:
    """Categorize modules based on their descriptions and names."""
    categories = defaultdict(list)
    
    for entry in catalog:
        name = entry.get('name', '').lower()
        desc = entry.get('description', '').lower()
        
        # Categorize based on keywords
        if any(word in name + desc for word in ['name', 'naming', 'variable', 'convention']):
            categories['naming_patterns'].append(entry['name'])
        if any(word in name + desc for word in ['api', 'client', 'sdk', 'integration']):
            categories['api_clients'].append(entry['name'])
        if any(word in name + desc for word in ['test', 'pytest', 'unittest', 'spec']):
            categories['testing'].append(entry['name'])
        if any(word in name + desc for word in ['algorithm', 'sort', 'search', 'optimize']):
            categories['algorithms'].append(entry['name'])
        if any(word in name + desc for word in ['scrape', 'crawl', 'spider', 'extract']):
            categories['web_scraping'].append(entry['name'])
        if any(word in name + desc for word in ['auth', 'login', 'session', 'jwt', 'token']):
            categories['authentication'].append(entry['name'])
        if any(word in name + desc for word in ['data', 'database', 'sql', 'orm', 'model']):
            categories['data_management'].append(entry['name'])
        if any(word in name + desc for word in ['util', 'helper', 'tool', 'common']):
            categories['utilities'].append(entry['name'])
            
    # Remove duplicates from each category
    for cat in categories:
        categories[cat] = list(set(categories[cat]))
    
    return dict(categories)

@mcp.tool()
def hail_starbase() -> Dict[str, Any]:
    """Hailing frequencies open! Discover what modules are docked in the cargo bay.
    
    Returns complete manifest of available code modules with their capabilities.
    This is your first contact with Starbase to understand what code patterns,
    solutions, and tools are available for reuse.
    """
    catalog = load_catalog()
    
    if not catalog:
        return {
            "greeting": "Starbase Alpha responding. Cargo bay is empty.",
            "status": "operational",
            "instructions": "Run 'starbase extract' to dock code modules.",
            "manifest": {
                "total_modules": 0,
                "by_category": {},
                "capabilities": []
            }
        }
    
    # Categorize modules
    categories = categorize_modules(catalog)
    
    # Extract capabilities from descriptions
    capabilities = set()
    for entry in catalog:
        desc = entry.get('description', '').lower()
        if 'naming' in desc or 'convention' in desc:
            capabilities.add("Code naming conventions and standards")
        if 'api' in desc or 'client' in desc:
            capabilities.add("API client implementations and patterns")
        if 'test' in desc:
            capabilities.add("Testing frameworks and test utilities")
        if 'auth' in desc or 'security' in desc:
            capabilities.add("Authentication and security patterns")
        if 'data' in desc or 'database' in desc:
            capabilities.add("Data management and database patterns")
        if 'scrape' in desc or 'crawl' in desc:
            capabilities.add("Web scraping and data extraction")
    
    # Find most accessed (by file count as proxy)
    most_accessed = sorted(catalog, key=lambda x: x.get('file_count', 0), reverse=True)[:5]
    
    return {
        "greeting": f"Starbase Alpha responding. {len(catalog)} modules docked in cargo bay.",
        "status": "operational",
        "manifest": {
            "total_modules": len(catalog),
            "by_category": categories,
            "recent_additions": [entry['name'] for entry in catalog[-5:]] if len(catalog) > 5 else [entry['name'] for entry in catalog],
            "most_accessed": [entry['name'] for entry in most_accessed],
            "total_files": sum(entry.get('file_count', 0) for entry in catalog),
            "total_size_bytes": sum(entry.get('total_size', 0) for entry in catalog)
        },
        "capabilities": list(capabilities),
        "available_modules": [
            {
                "name": entry['name'],
                "description": entry.get('description', 'No description'),
                "file_count": entry.get('file_count', 0)
            } for entry in catalog
        ]
    }

@mcp.tool()
def droidsplain(task_description: str) -> Dict[str, Any]:
    """Let this droid explain what worked before! Get key patterns and lessons learned.
    
    Analyzes your task and finds relevant code patterns from the cargo bay,
    explaining what worked, what didn't, and key insights from past implementations.
    Returns digestible code snippets and aha moments.
    
    Args:
        task_description: What you're trying to implement or solve
        
    Returns:
        Analysis with relevant patterns, snippets, and lessons learned
    """
    catalog = load_catalog()
    
    if not catalog:
        return {
            "analysis": "No modules in cargo bay to analyze.",
            "suggestion": "Dock some code with 'starbase extract' first."
        }
    
    # Search for relevant modules
    task_lower = task_description.lower()
    relevant_modules = []
    
    for entry in catalog:
        name = entry.get('name', '').lower()
        desc = entry.get('description', '').lower()
        score = 0
        
        # Score relevance
        for word in task_lower.split():
            if len(word) > 2:  # Skip short words
                if word in name:
                    score += 10
                if word in desc:
                    score += 5
        
        if score > 0:
            relevant_modules.append((entry, score))
    
    # Sort by relevance
    relevant_modules.sort(key=lambda x: x[1], reverse=True)
    top_modules = relevant_modules[:3]  # Top 3 most relevant
    
    if not top_modules:
        return {
            "analysis": f"No directly relevant modules found for '{task_description}'",
            "suggestion": "Try rephrasing or browse with 'hail_starbase' first",
            "available_categories": list(categorize_modules(catalog).keys())
        }
    
    # Build response with patterns
    patterns_analysis = {
        "analysis": f"Based on '{task_description}', I found {len(top_modules)} relevant patterns",
        "relevant_modules": [mod[0]['name'] for mod in top_modules],
        "patterns_that_worked": [],
        "key_insights": [],
        "quick_start": None
    }
    
    # Extract patterns from the most relevant module
    best_module = top_modules[0][0]
    module_path = STARBASE_PATH / best_module['path']
    
    if module_path.exists():
        # Extract key patterns from the code
        patterns = extract_key_patterns(module_path, task_description)
        patterns_analysis["patterns_that_worked"] = patterns
        
        # Suggest quick start
        patterns_analysis["quick_start"] = {
            "module_to_use": best_module['name'],
            "description": best_module.get('description', ''),
            "entry_points": best_module.get('entry_points', []),
            "next_step": f"Use 'receive_transmission(\"{best_module['name']}\")' to get full source"
        }
    
    # Add insights based on module descriptions
    for mod, score in top_modules:
        desc = mod.get('description', '')
        if desc:
            patterns_analysis["key_insights"].append(f"{mod['name']}: {desc}")
    
    return patterns_analysis

def extract_key_patterns(module_path: Path, task: str) -> List[Dict[str, str]]:
    """Extract key code patterns from a module."""
    patterns = []
    
    # Handle single file or directory
    if module_path.is_file():
        files_to_analyze = [module_path]
    else:
        files_to_analyze = list(module_path.glob("*.py"))[:3]  # Analyze up to 3 files
    
    for file_path in files_to_analyze:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Find key patterns
                for i, line in enumerate(lines):
                    # Look for important markers
                    if any(marker in line.upper() for marker in ['IMPORTANT:', 'NOTE:', 'KEY:', 'AHA:', 'CRITICAL:']):
                        # Extract the pattern around this marker
                        start = max(0, i - 2)
                        end = min(len(lines), i + 5)
                        snippet = '\n'.join(lines[start:end])
                        
                        patterns.append({
                            "file": file_path.name,
                            "pattern": "Key insight found",
                            "snippet": snippet[:300],  # Limit snippet length
                            "why_important": line.strip()
                        })
                        
                    # Look for main functions or entry points
                    if 'def main(' in line or 'if __name__' in line:
                        start = i
                        end = min(len(lines), i + 10)
                        snippet = '\n'.join(lines[start:end])
                        
                        patterns.append({
                            "file": file_path.name,
                            "pattern": "Entry point pattern",
                            "snippet": snippet[:300],
                            "why_important": "Shows how to initialize and use this module"
                        })
                        
                if len(patterns) >= 3:  # Limit to 3 patterns
                    break
                    
        except (IOError, UnicodeDecodeError):
            continue
    
    return patterns[:3]  # Return max 3 patterns

@mcp.tool()
def receive_transmission(module_name: str) -> Dict[str, Any]:
    """Receive full source code transmission from the cargo bay.
    
    After discovering modules with 'hail_starbase' or getting recommendations
    from 'droidsplain', use this to receive the complete source code.
    
    Args:
        module_name: Name of the module to transmit
        
    Returns:
        Complete source code with metadata for integration
    """
    catalog = load_catalog()
    
    # Find the requested module
    module = None
    for entry in catalog:
        if entry['name'].lower() == module_name.lower():
            module = entry
            break
    
    if not module:
        return {
            "transmission_status": "failed",
            "error": f"Module '{module_name}' not found in cargo bay",
            "suggestion": "Use 'hail_starbase()' to see available modules"
        }
    
    # Get the source code
    module_path = STARBASE_PATH / module['path']
    
    if not module_path.exists():
        return {
            "transmission_status": "failed", 
            "error": f"Module files not found at {module_path}",
            "module": module_name
        }
    
    files = {}
    
    # Handle single file or directory
    if module_path.is_file():
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                files[module_path.name] = f.read()
        except Exception as e:
            return {
                "transmission_status": "partial",
                "error": f"Error reading file: {e}",
                "module": module_name
            }
    else:
        # Get all Python files
        for py_file in module_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['.venv', '__pycache__', '.pytest_cache']):
                continue
            try:
                rel_path = py_file.relative_to(module_path)
                with open(py_file, 'r', encoding='utf-8') as f:
                    files[str(rel_path)] = f.read()
            except Exception as e:
                files[str(rel_path)] = f"// Transmission error: {e}"
    
    # Extract key integration info
    entry_points = module.get('entry_points', [])
    dependencies = extract_dependencies_from_code(files)
    
    return {
        "transmission_status": "complete",
        "module": module_name,
        "description": module.get('description', ''),
        "files": files,
        "file_count": len(files),
        "total_lines": sum(len(code.split('\n')) for code in files.values()),
        "entry_points": entry_points,
        "dependencies": dependencies,
        "integration_notes": f"Module '{module_name}' transmitted successfully. {len(files)} files received.",
        "cargo_bay_path": str(module_path)
    }

def extract_dependencies_from_code(files: Dict[str, str]) -> List[str]:
    """Extract import dependencies from code files."""
    dependencies = set()
    
    for filename, code in files.items():
        # Simple regex to find imports
        import_pattern = r'(?:from\s+(\S+)\s+import|import\s+(\S+))'
        matches = re.findall(import_pattern, code)
        
        for match in matches:
            dep = match[0] or match[1]
            if dep and not dep.startswith('.'):
                # Get base package name
                base_dep = dep.split('.')[0]
                # Skip standard library modules (basic list)
                if base_dep not in ['os', 'sys', 're', 'json', 'math', 'random', 'datetime', 'pathlib', 'typing', 'collections']:
                    dependencies.add(base_dep)
    
    return sorted(list(dependencies))

@mcp.tool()
def search_packages(query: str, deep: bool = False) -> List[Dict]:
    """Search for packages in starbase using natural language.
    
    Args:
        query: Search query (supports natural language)
        deep: If True, also search file contents
        
    Returns:
        List of matching packages with scores
    """
    catalog = load_catalog()
    results = []
    
    query_lower = query.lower()
    
    # Search in catalog entries
    for entry in catalog:
        score = 0
        name = entry.get('name', '').lower()
        desc = entry.get('description', '').lower()
        
        # Exact name match
        if query_lower == name:
            score += 100
        # Name contains query
        elif query_lower in name:
            score += 50
        # Description contains query
        elif query_lower in desc:
            score += 25
        
        # Add semantic matching (simple keyword matching for now)
        keywords = query_lower.split()
        for keyword in keywords:
            if len(keyword) > 2:  # Skip very short words
                if keyword in name:
                    score += 10
                if keyword in desc:
                    score += 5
        
        if score > 0:
            results.append({
                'name': entry['name'],
                'description': entry.get('description', ''),
                'path': entry.get('path', ''),
                'score': score,
                'file_count': entry.get('file_count', 0),
                'entry_points': entry.get('entry_points', [])
            })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # If deep search, also search file contents
    if deep and results:
        for result in results[:5]:  # Limit deep search to top 5
            package_path = STARBASE_PATH / result['path']
            if package_path.exists():
                # Add snippet of code found
                preview = get_code_preview(package_path, query)
                if preview:
                    result['code_preview'] = preview
    
    return results[:10]  # Return top 10 results

@mcp.tool()
def get_package_code(package_name: str) -> Dict[str, Any]:
    """Get all source code from a package.
    
    Args:
        package_name: Name of the package to retrieve
        
    Returns:
        Dictionary with package info and all source files
    """
    catalog = load_catalog()
    
    # Find package in catalog
    package = None
    for entry in catalog:
        if entry['name'] == package_name:
            package = entry
            break
    
    if not package:
        return {"error": f"Package '{package_name}' not found in starbase"}
    
    # Read all Python files
    package_path = STARBASE_PATH / package['path']
    code_files = {}
    
    if package_path.exists():
        # Handle both directories and single files
        if package_path.is_file():
            # Single file package
            try:
                with open(package_path, 'r', encoding='utf-8') as f:
                    code_files[package_path.name] = f.read()
            except Exception as e:
                code_files[package_path.name] = f"Error reading file: {e}"
        else:
            # Directory package
            for py_file in package_path.rglob("*.py"):
                # Skip virtual environments and cache
                if any(skip in str(py_file) for skip in ['.venv', '__pycache__', '.pytest_cache']):
                    continue
                    
                try:
                    relative_path = py_file.relative_to(package_path)
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code_files[str(relative_path)] = f.read()
                except Exception as e:
                    code_files[str(relative_path)] = f"Error reading file: {e}"
    
    return {
        "package": package_name,
        "description": package.get('description', ''),
        "files": code_files,
        "entry_points": package.get('entry_points', []),
        "file_count": len(code_files),
        "path": str(package_path)
    }

@mcp.tool()
def list_all_packages(category: Optional[str] = None) -> List[Dict]:
    """List all packages in starbase with optional filtering.
    
    Args:
        category: Optional filter by category (tests, api, utilities, scrapers, other)
        
    Returns:
        List of packages with metadata
    """
    catalog = load_catalog()
    
    packages = []
    for entry in catalog:
        # Simple categorization based on name patterns
        name = entry.get('name', '').lower()
        entry_category = 'other'
        
        if 'test' in name or 'spec' in name:
            entry_category = 'tests'
        elif 'api' in name or 'client' in name or 'sdk' in name:
            entry_category = 'api'
        elif 'util' in name or 'helper' in name or 'tool' in name:
            entry_category = 'utilities'
        elif 'scrape' in name or 'crawl' in name or 'spider' in name:
            entry_category = 'scrapers'
        elif 'model' in name or 'ml' in name or 'ai' in name:
            entry_category = 'ml'
        
        if category is None or entry_category == category:
            packages.append({
                'name': entry['name'],
                'description': entry.get('description', ''),
                'category': entry_category,
                'file_count': entry.get('file_count', 0),
                'size': entry.get('total_size', 0),
                'entry_points': entry.get('entry_points', [])
            })
    
    # Sort by name for consistent output
    packages.sort(key=lambda x: x['name'])
    return packages

@mcp.tool()
def get_install_command(package_name: str, method: str = "pdm") -> Dict[str, str]:
    """Get installation instructions for a package.
    
    Args:
        package_name: Package to install
        method: Installation method (pdm, pip, poetry, copy)
        
    Returns:
        Installation command and instructions
    """
    catalog = load_catalog()
    
    # Find package
    package = None
    for entry in catalog:
        if entry['name'] == package_name:
            package = entry
            break
    
    if not package:
        return {"error": f"Package '{package_name}' not found in starbase"}
    
    package_path = STARBASE_PATH / package['path']
    absolute_path = str(package_path.absolute())
    
    # Generate appropriate install commands
    commands = {
        "pdm": f"pdm add -e {absolute_path}",
        "pip": f"pip install -e {absolute_path}",
        "copy": f"cp -r {absolute_path} ./{package_name}",
        "poetry": f"poetry add --editable {absolute_path}",
        "uv": f"uv add --editable {absolute_path}"
    }
    
    return {
        "package": package_name,
        "method": method,
        "command": commands.get(method, commands["pdm"]),
        "path": absolute_path,
        "instructions": f"Run this command in your project directory to install {package_name}",
        "entry_points": package.get('entry_points', [])
    }

def get_code_preview(package_path: Path, query: str, max_lines: int = 5) -> str:
    """Get a preview of code containing the query.
    
    Args:
        package_path: Path to package
        query: Search query
        max_lines: Maximum lines of context to show
        
    Returns:
        Code preview with context
    """
    # Handle single file
    if package_path.is_file():
        files_to_search = [package_path]
    else:
        files_to_search = package_path.rglob("*.py")
    
    for py_file in files_to_search:
        # Skip virtual environments
        if any(skip in str(py_file) for skip in ['.venv', '__pycache__', '.pytest_cache']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    # Find the line with the query
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            # Return context around the match
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            preview = '\n'.join(lines[start:end])
                            file_ref = py_file.name if package_path.is_file() else py_file.relative_to(package_path)
                            return f"Found in {file_ref}:\n{preview}"
        except (IOError, UnicodeDecodeError):
            continue
    return ""

def main():
    """Main entry point for running the MCP server."""
    print(f"Starting Starbase MCP Server", file=sys.stderr)
    print(f"Repository: {STARBASE_PATH}", file=sys.stderr)
    
    catalog_size = len(load_catalog())
    print(f"Serving {catalog_size} packages", file=sys.stderr)
    
    if catalog_size == 0:
        print("Note: Catalog is empty. Run 'starbase extract' to add packages.", file=sys.stderr)
    
    # Run the MCP server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()