"""
Core analysis functions for starbase.

This module contains functions for analyzing file relationships,
extracting imports, and finding connected components in codebases.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


def extract_local_imports(py_file: Path) -> Set[Path]:
    """Extract only local file imports from a Python file using AST."""
    local_imports = set()
    
    try:
        content = py_file.read_text()
        tree = ast.parse(content)
        file_dir = py_file.parent
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    # Check if it's a local file
                    local_file = file_dir / f"{module_name}.py"
                    if local_file.exists() and local_file != py_file:
                        local_imports.add(local_file)
                        
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:  # Relative import
                    # Handle relative imports like "from . import module"
                    if node.module:
                        local_file = file_dir / f"{node.module}.py"
                        if local_file.exists() and local_file != py_file:
                            local_imports.add(local_file)
                    # Handle "from . import name"
                    for alias in node.names:
                        local_file = file_dir / f"{alias.name}.py"
                        if local_file.exists() and local_file != py_file:
                            local_imports.add(local_file)
                elif node.module and not node.module.startswith(('sys', 'os', 'json', 'pathlib')):
                    # Check if it's a local module (not a standard library)
                    module_parts = node.module.split('.')
                    local_file = file_dir / f"{module_parts[0]}.py"
                    if local_file.exists() and local_file != py_file:
                        local_imports.add(local_file)
    except:
        pass
    
    return local_imports


def extract_functions_and_classes(py_file: Path) -> tuple[List[str], List[str]]:
    """Extract function and class names from a Python file using AST."""
    functions = []
    classes = []
    
    try:
        content = py_file.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
    except:
        pass
    
    return functions, classes


def find_connected_components(import_map: Dict[Path, Set[Path]]) -> List[Set[Path]]:
    """Find connected components in the import graph using DFS."""
    visited = set()
    components = []
    
    def build_graph(import_map):
        """Build bidirectional graph from import map."""
        graph = {file: set() for file in import_map}
        
        # Add reverse edges to make graph bidirectional
        for file, imports in import_map.items():
            for imported in imports:
                if imported in graph:
                    graph[imported].add(file)
                    graph[file].add(imported)
        
        return graph
    
    def dfs(node, graph, component):
        """Depth-first search to find connected component."""
        visited.add(node)
        component.add(node)
        
        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor, graph, component)
    
    graph = build_graph(import_map)
    
    for node in graph:
        if node not in visited:
            component = set()
            dfs(node, graph, component)
            if component:
                components.append(component)
    
    return components


def detect_test_relationships(files: List[Path]) -> Dict[Path, Path]:
    """Map test files to their tested modules."""
    test_map = {}
    
    for file in files:
        if file.suffix != '.py':
            continue
            
        stem = file.stem
        
        # Check for test_ prefix
        if stem.startswith('test_'):
            base_name = stem[5:]  # Remove 'test_'
            
            # Look for direct match
            for candidate in files:
                if candidate.stem == base_name:
                    test_map[file] = candidate
                    break
                    
            # If no direct match, check imports to find what it tests
            if file not in test_map:
                try:
                    imports = extract_local_imports(file)
                    # Also check for mentions in the file content
                    content = file.read_text()
                    for candidate in files:
                        # Check if imported or mentioned
                        if candidate in imports or candidate.stem in content:
                            test_map[file] = candidate
                            break
                except:
                    pass
                    
        # Check for _test suffix  
        elif stem.endswith('_test'):
            base_name = stem[:-5]  # Remove '_test'
            
            # Look for direct match
            for candidate in files:
                if candidate.stem == base_name:
                    test_map[file] = candidate
                    break
    
    return test_map


def detect_file_versions(files: List[Path]) -> Dict[Path, List[Path]]:
    """Detect version patterns in files."""
    # Version patterns to detect
    version_patterns = [
        '_old', '_new', '_v2', '_v3', '_backup', '_copy', 
        '_original', '_updated', '_fixed', '_temp', '_test'
    ]
    
    versioned_files = {}
    version_groups = {}
    
    # Pass 1: Identify all versioned files
    for file in files:
        if file.suffix != '.py':
            continue
            
        stem = file.stem
        
        # Check if this file has a version suffix
        for pattern in version_patterns:
            if pattern in stem:
                # Extract base name
                base_name = stem.split(pattern)[0]
                versioned_files[file] = base_name
                break
    
    # Pass 2: Group versioned files with their main files
    for versioned_file, base_name in versioned_files.items():
        # Find the main file
        main_file = None
        for candidate in files:
            if candidate.suffix == '.py' and candidate.stem == base_name:
                main_file = candidate
                break
        
        if main_file:
            if main_file not in version_groups:
                version_groups[main_file] = []
            version_groups[main_file].append(versioned_file)
        else:
            # No main file exists, so the versioned file stands alone
            # Don't create a version group for it
            pass
    
    return version_groups


def detect_name_relationships(files: List[Path]) -> Dict[Path, List[Path]]:
    """Detect files related by naming patterns."""
    relationships = {}
    
    for file in files:
        if file.suffix != '.py':
            continue
            
        stem = file.stem
        
        # Skip version suffixes
        if any(suffix in stem for suffix in ['_old', '_v2', '_backup', '_copy']):
            continue
        
        # Check for underscore-separated prefixes
        if '_' in stem:
            parts = stem.split('_')
            prefix = parts[0]
            
            # Look for base file (e.g., cc4_monitor → cc4)
            for candidate in files:
                if candidate.suffix != '.py' or candidate == file:
                    continue
                    
                if candidate.stem == prefix:
                    if candidate not in relationships:
                        relationships[candidate] = []
                    relationships[candidate].append(file)
    
    return relationships


def analyze_semantic_relationships(files: List[Path], groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze semantic relationships through comments and code content.
    This is an intermediate phase that can merge smaller groups into larger ones
    based on references in comments, docstrings, and string literals.
    """
    # Build a map of group names to group indices for quick lookup
    group_name_to_idx = {g['name']: i for i, g in enumerate(groups)}
    
    # Track which groups reference which other groups
    references = defaultdict(lambda: defaultdict(int))  # references[from_idx][to_idx] = count
    
    # Analyze each file for references to other groups
    for group_idx, group in enumerate(groups):
        for file in group['files']:
            if file.suffix != '.py':
                continue
                
            try:
                content = file.read_text().lower()  # Case-insensitive analysis
                
                # Check for references to other groups
                for other_idx, other_group in enumerate(groups):
                    if other_idx == group_idx:  # Skip self-references
                        continue
                        
                    other_name = other_group['name'].lower()
                    
                    # Count occurrences in comments, docstrings, and strings
                    # Weight different types of occurrences
                    weight = 0
                    
                    # First, count all occurrences including comments (which AST misses)
                    # Split by lines to properly count in comments
                    lines = content.split('\n')
                    for line in lines:
                        if other_name in line:
                            # Check if it's in a comment
                            if '#' in line and other_name in line[line.index('#'):]:
                                weight += 1  # Comment reference
                            else:
                                weight += 1  # Code/string reference
                    
                    # Additionally, parse AST for more specific weighting
                    try:
                        tree = ast.parse(file.read_text())
                        
                        # Check module docstring
                        if ast.get_docstring(tree) and other_name in ast.get_docstring(tree).lower():
                            weight += 2  # Module docstring reference is extra strong
                        
                        # Check function/class docstrings
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(node):
                                if other_name in ast.get_docstring(node).lower():
                                    weight += 1  # Function/class docstring
                    except:
                        pass  # We already have the line-based count
                    
                    if weight > 0:
                        references[group_idx][other_idx] += weight
                        
            except:
                continue
    
    # Determine which groups should be merged based on references
    # Strategy: Small groups that heavily reference larger groups should be absorbed
    merged_groups = []
    absorbed = set()
    
    # Sort groups by size (number of files) to process larger groups first
    sorted_group_indices = sorted(range(len(groups)), key=lambda i: len(groups[i]['files']), reverse=True)
    
    for idx in sorted_group_indices:
        if idx in absorbed:
            continue
            
        group = groups[idx].copy()  # Create a copy to avoid modifying original
        group_size = len(group['files'])
        
        # Check if any smaller groups should be absorbed into this one
        for other_idx in range(len(groups)):
            if other_idx == idx or other_idx in absorbed:
                continue
                
            other_group = groups[other_idx]
            other_size = len(other_group['files'])
            
            # Absorption criteria:
            # 1. The other group must be smaller
            # 2. The other group must reference this group significantly
            # 3. The reference weight must be above a threshold relative to group sizes
            if other_size < group_size:
                ref_weight = references[other_idx].get(idx, 0)
                
                # Dynamic threshold based on the size ratio
                # Smaller groups need fewer references to be absorbed
                size_ratio = other_size / group_size
                
                # More lenient thresholds:
                # - Single file groups: 1 reference is enough
                # - Small groups (2-5 files): 1 reference per file
                # - Larger groups: require more evidence
                if other_size == 1:
                    threshold = 1  # Any reference is enough for standalone files
                elif other_size <= 5:
                    threshold = other_size  # One reference per file
                else:
                    threshold = int(1.5 * other_size)  # Need more evidence for larger groups
                
                if ref_weight >= threshold:
                    # Additional check: Does the larger group reference the smaller one?
                    reverse_ref = references[idx].get(other_idx, 0)
                    
                    # If there's mutual reference or strong one-way reference, merge
                    # For single files, don't require mutual reference
                    if reverse_ref > 0 or ref_weight >= threshold * 2 or other_size == 1:
                        # Absorb the smaller group
                        group['files'].extend(other_group['files'])
                        
                        # Merge other attributes
                        if 'test_files' in group and 'test_files' in other_group:
                            group['test_files'].extend(other_group['test_files'])
                        
                        if 'versions' in group and 'versions' in other_group:
                            group['versions'].update(other_group['versions'])
                        
                        # Update type
                        group['type'] = 'connected'
                        
                        # Mark as absorbed
                        absorbed.add(other_idx)
                        
                        # Log the merge for debugging
                        print(f"Merging '{other_group['name']}' into '{group['name']}' (weight: {ref_weight})")
        
        merged_groups.append(group)
    
    # Add any groups that weren't absorbed and aren't already in merged_groups
    merged_group_names = {g['name'] for g in merged_groups}
    for idx in range(len(groups)):
        if idx not in absorbed and groups[idx]['name'] not in merged_group_names:
            merged_groups.append(groups[idx])
    
    return merged_groups


def analyze_file_relationships(files: List[Path]) -> List[Dict[str, Any]]:
    """Analyze relationships between files to suggest logical groupings."""
    # Step 1: Build import map
    import_map = {}
    for file in files:
        if file.suffix == '.py':
            imports = extract_local_imports(file)
            # Only include imports that are in our file list
            import_map[file] = imports.intersection(set(files))
    
    # Step 2: Detect different types of relationships
    test_map = detect_test_relationships(files)
    version_groups = detect_file_versions(files)
    name_relationships = detect_name_relationships(files)
    
    # Step 3: Find connected components from imports
    # Only create components for files that have imports or are imported
    components = find_connected_components(import_map)
    
    # Step 4: Merge all relationships into enhanced components
    # Add test files to their tested modules' components
    for test_file, tested_file in test_map.items():
        # Find which component contains the tested file
        found = False
        for component in components:
            if tested_file in component:
                component.add(test_file)
                found = True
                break
        
        # If tested file isn't in any component, create new component
        if not found:
            for i, component in enumerate(components):
                if test_file in component and tested_file not in component:
                    # Add tested file to test file's component
                    component.add(tested_file)
                    found = True
                    break
            
            if not found:
                # Create new component with both files
                components.append({test_file, tested_file})
    
    # Add name-related files to their base components
    for base_file, related_files in name_relationships.items():
        # Find which component contains the base file
        base_component = None
        for component in components:
            if base_file in component:
                base_component = component
                break
        
        # Find components containing related files
        related_components = []
        for related_file in related_files:
            for component in components:
                if related_file in component and component != base_component:
                    related_components.append(component)
        
        if base_component:
            # Add related files to base component
            base_component.update(related_files)
            # Merge any components that contained the related files
            for comp in related_components:
                base_component.update(comp)
                components.remove(comp)
        else:
            # Create new component
            new_component = {base_file}
            new_component.update(related_files)
            # Remove any components that contained the related files
            for comp in related_components:
                new_component.update(comp)
                components.remove(comp)
            components.append(new_component)
    
    # Step 5: Create groups from enhanced components
    groups = []
    grouped_files = set()
    versioned_files = set()
    
    # Collect all versioned files to exclude from main groups
    for versions in version_groups.values():
        versioned_files.update(versions)
    
    # Collect ALL files that are in ANY component (to prevent duplicates)
    all_component_files = set()
    for component in components:
        all_component_files.update(component)
    
    for component in components:
        # Skip if all files are versioned
        if component.issubset(versioned_files):
            continue
            
        # Remove versioned files from component
        component_files = component - versioned_files
        if not component_files:
            continue
            
        # Skip if this component is already grouped
        if component_files.issubset(grouped_files):
            continue
        
        # Find the most credible main file in the group
        main_file = None
        highest_score = -1
        
        for file in component_files:
            score = 0
            try:
                content = file.read_text()
                
                # Score based on credibility indicators
                if 'if __name__ == "__main__"' in content:
                    score += 100  # Strong indicator
                    
                if '@app.command' in content or '@click.command' in content:
                    score += 50  # CLI entry point
                    
                # Count how many other files in the group import this one
                imported_by_count = 0
                for other_file in component_files:
                    if other_file != file:
                        other_imports = extract_local_imports(other_file)
                        if file in other_imports:
                            imported_by_count += 1
                score += imported_by_count * 10
                
                # Check for main-like patterns in content
                if 'def main(' in content or 'async def main(' in content:
                    score += 20
                    
                # Prefer non-test files
                if not file.stem.startswith('test_'):
                    score += 5
                    
                # Prefer base files in name relationships
                # If this file is the base for other files in the group, prefer it
                for other in component_files:
                    if other != file and '_' in other.stem:
                        prefix = other.stem.split('_')[0]
                        if file.stem == prefix:
                            score += 30  # Significant boost for being a base file
                            
            except:
                pass
            
            if score > highest_score:
                highest_score = score
                main_file = file
        
        # Fallback if no file scored
        if not main_file:
            main_file = next(iter(component_files))
        
        group_name = main_file.stem
        
        # Collect version info for files in this group
        versions = {}
        for file in component_files:
            if file in version_groups:
                versions[file] = version_groups[file]
        
        groups.append({
            'name': group_name,
            'main_file': main_file,
            'files': list(component_files),
            'type': 'connected' if len(component_files) > 1 else 'standalone',
            'versions': versions,
            'test_files': [f for f in component_files if f in test_map]
        })
        grouped_files.update(component_files)
    
    # Step 6: Handle ungrouped files (excluding versioned and files in components)
    ungrouped = [f for f in files if f not in all_component_files and f not in versioned_files and f.suffix == '.py']
    
    for file in ungrouped:
        # Check if this file has versions
        versions = {}
        if file in version_groups:
            versions[file] = version_groups[file]
            
        groups.append({
            'name': file.stem,
            'main_file': file,
            'files': [file],
            'type': 'standalone',
            'versions': versions,
            'test_files': []
        })
    
    # Step 7: NEW - Analyze semantic relationships to potentially merge groups
    # This is the intermediate phase that looks at comments, docstrings, etc.
    groups = analyze_semantic_relationships(files, groups)
    
    return groups


def trace_dependencies(py_file: Path) -> Set[Path]:
    """Trace all Python dependencies of a file including packages"""
    dependencies = set()
    to_process = {py_file}
    processed = set()
    
    while to_process:
        current = to_process.pop()
        if current in processed:
            continue
        processed.add(current)
        
        try:
            content = current.read_text()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep_name = alias.name.split('.')[0]
                        # Try both .py file and package directory
                        dep_file = current.parent / f"{dep_name}.py"
                        dep_dir = current.parent / dep_name
                        
                        if dep_file.exists() and dep_file not in processed:
                            dependencies.add(dep_file)
                            to_process.add(dep_file)
                        elif dep_dir.is_dir():
                            # Add all .py files from the package
                            for py in dep_dir.glob("**/*.py"):
                                if py not in processed:
                                    dependencies.add(py)
                                    to_process.add(py)
                                    
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Calculate base path for import
                        if node.level == 0:  # absolute import
                            module_path = current.parent
                        else:  # relative import
                            module_path = current.parent
                            for _ in range(node.level - 1):
                                module_path = module_path.parent
                        
                        # Navigate through module parts
                        parts = node.module.split('.')
                        for part in parts:
                            module_path = module_path / part
                        
                        # Check if it's a package directory
                        if module_path.is_dir():
                            # Add __init__.py if exists
                            init_file = module_path / "__init__.py"
                            if init_file.exists():
                                dependencies.add(init_file)
                            
                            # Handle specific imports from package
                            for name in node.names:
                                if name.name == '*':
                                    # Import all from package
                                    for py in module_path.glob("*.py"):
                                        if py not in processed:
                                            dependencies.add(py)
                                            to_process.add(py)
                                else:
                                    # Import specific module
                                    py_file = module_path / f"{name.name}.py"
                                    if py_file.exists() and py_file not in processed:
                                        dependencies.add(py_file)
                                        to_process.add(py_file)
                        else:
                            # Try as a .py file
                            py_file = module_path.with_suffix('.py')
                            if py_file.exists() and py_file not in processed:
                                dependencies.add(py_file)
                                to_process.add(py_file)
                    
                    elif node.level > 0:  # relative import without module
                        # Handle "from . import foo"
                        parent = current.parent
                        for _ in range(node.level - 1):
                            parent = parent.parent
                        
                        for name in node.names:
                            # Try as file
                            dep_file = parent / f"{name.name}.py"
                            if dep_file.exists() and dep_file not in processed:
                                dependencies.add(dep_file)
                                to_process.add(dep_file)
                            # Try as package
                            dep_dir = parent / name.name
                            if dep_dir.is_dir():
                                for py in dep_dir.glob("**/*.py"):
                                    if py not in processed:
                                        dependencies.add(py)
                                        to_process.add(py)
        except:
            # Skip files we can't parse
            pass
    
    return dependencies - {py_file}  # Don't include the original file