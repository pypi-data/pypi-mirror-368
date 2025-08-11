"""
Subdirectory assignment functions for starbase.

This module contains functions for assigning subdirectories to groups
using various approaches (LLM, heuristic, hybrid).
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any
from .analysis import extract_local_imports, analyze_file_relationships


def load_subdirectory_config() -> Dict:
    """Load subdirectory assignment configuration."""
    # Try to load from file if toml is available
    try:
        import toml
        config_path = Path(__file__).parent.parent / "config" / "subdirectory_assignment.toml"
        if config_path.exists():
            return toml.load(config_path)
    except ImportError:
        pass
    except Exception:
        pass
    
    # Default configuration
    return {
        "assignment": {"method": "heuristic"},
        "hybrid": {"strategy": "weighted", "llm_weight": 0.3, "heuristic_weight": 0.7}
    }


def analyze_project_with_subdirectories(root_path: Path, config: Dict = None) -> List[Dict[str, Any]]:
    """
    Two-step analysis:
    1. Group top-level Python files using existing logic
    2. Assign subdirectories to top-level groups
    """
    if config is None:
        config = load_subdirectory_config()
    
    # Step 1: Get top-level groups using existing logic
    top_level_files = list(root_path.glob("*.py"))
    top_level_groups = analyze_file_relationships(top_level_files)
    
    if not top_level_groups:
        # No top-level groups, fall back to single group
        return [{
            'name': root_path.name,
            'type': 'project',
            'files': [],
            'main_file': None,
            'test_files': [],
            'versions': {},
            'subdirectories': {}
        }]
    
    # Add subdirectories tracking to each group
    for group in top_level_groups:
        group['subdirectories'] = []
    
    # Step 2: Process each subdirectory
    subdirs = [d for d in root_path.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    # Choose assignment method based on config
    method = config.get('assignment', {}).get('method', 'heuristic')
    
    if method == 'llm':
        assignments = assign_subdirectories_llm(subdirs, top_level_groups, root_path)
    elif method == 'hybrid':
        assignments = assign_subdirectories_hybrid(subdirs, top_level_groups, root_path, config)
    else:  # heuristic
        assignments = assign_subdirectories_heuristic(subdirs, top_level_groups, root_path)
    
    # Apply assignments
    for subdir, group_idx in assignments.items():
        if 0 <= group_idx < len(top_level_groups):
            top_level_groups[group_idx]['subdirectories'].append(subdir)
            
            # Collect all Python files from this subdirectory
            py_files = list(subdir.rglob("*.py"))
            py_files = [f for f in py_files if '__pycache__' not in str(f)]
            top_level_groups[group_idx]['files'].extend(py_files)
    
    return top_level_groups


def assign_subdirectories_llm_with_scores(subdirs: List[Path], groups: List[Dict], root_path: Path) -> Tuple[Dict[Path, int], Dict[Path, List[float]]]:
    """Assign subdirectories to groups using token similarity (LLM approach) and return scores."""
    try:
        from extractors.token_similarity import TokenSimilarityAnalyzer
        analyzer = TokenSimilarityAnalyzer()
    except ImportError:
        # Fallback if token similarity not available
        return {}, {}
    
    assignments = {}
    all_scores = {}
    
    for subdir in subdirs:
        # Get all Python files in subdirectory
        py_files = list(subdir.rglob("*.py"))
        py_files = [f for f in py_files if '__pycache__' not in str(f)]
        
        if not py_files:
            assignments[subdir] = 0  # Default to first group
            all_scores[subdir] = [0.0] * len(groups)
            continue
        
        best_score = -1
        best_group_idx = 0
        group_scores = []
        
        for idx, group in enumerate(groups):
            similarities = []
            
            # Compare subdirectory files with group files
            for sub_file in py_files[:5]:  # Sample up to 5 files
                for group_file in group['files'][:5]:  # Sample up to 5 files
                    if group_file.suffix == '.py':
                        sim = analyzer.calculate_similarity(sub_file, group_file)
                        similarities.append(sim)
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            group_scores.append(avg_similarity)
            
            if avg_similarity > best_score:
                best_score = avg_similarity
                best_group_idx = idx
        
        assignments[subdir] = best_group_idx
        all_scores[subdir] = group_scores
    
    return assignments, all_scores


def assign_subdirectories_llm(subdirs: List[Path], groups: List[Dict], root_path: Path) -> Dict[Path, int]:
    """Assign subdirectories to groups using token similarity (LLM approach)."""
    assignments, _ = assign_subdirectories_llm_with_scores(subdirs, groups, root_path)
    return assignments


def assign_subdirectories_heuristic_with_scores(subdirs: List[Path], groups: List[Dict], root_path: Path) -> Tuple[Dict[Path, int], Dict[Path, List[float]]]:
    """Assign subdirectories to groups using heuristic rules and return scores."""
    assignments = {}
    all_scores = {}
    
    for subdir in subdirs:
        group_scores = []
        
        for idx, group in enumerate(groups):
            score = 0.0
            
            # 1. Check import relationships
            py_files = list(subdir.rglob("*.py"))
            py_files = [f for f in py_files if '__pycache__' not in str(f)]
            
            for py_file in py_files[:10]:  # Check up to 10 files
                imports = extract_local_imports(py_file)
                for imp in imports:
                    # Check if import points to files in this group
                    for group_file in group['files']:
                        if group_file.name == imp.name:
                            score += 10.0
                            break
            
            # 2. Name similarity
            subdir_name = subdir.name.lower()
            group_name = group['name'].lower()
            
            # Direct name match
            if group_name in subdir_name or subdir_name in group_name:
                score += 20.0
            
            # Partial match
            elif any(part in group_name for part in subdir_name.split('_')):
                score += 10.0
            elif any(part in subdir_name for part in group_name.split('_')):
                score += 10.0
            
            # 3. Special cases
            if subdir.name == 'tests' and 'test' in group_name:
                score += 15.0
            elif subdir.name == 'tests' and group['test_files']:
                score += 10.0
            elif subdir.name in ['src', 'lib'] and group['name'] == root_path.name:
                score += 15.0
            elif subdir.name == 'config' and 'config' in group_name:
                score += 20.0
            elif subdir.name == 'utils' and any('util' in f.stem for f in group['files']):
                score += 10.0
            
            # 4. Test file relationships
            for py_file in py_files:
                if 'test_' in py_file.name or '_test' in py_file.name:
                    # Check if this tests something in the group
                    test_base = py_file.stem.replace('test_', '').replace('_test', '')
                    if any(test_base in f.stem for f in group['files']):
                        score += 15.0
                        break
            
            group_scores.append(score)
        
        # Find best group
        best_idx = 0
        best_score = group_scores[0] if group_scores else 0
        for idx, score in enumerate(group_scores):
            if score > best_score:
                best_score = score
                best_idx = idx
        
        assignments[subdir] = best_idx
        all_scores[subdir] = group_scores
    
    return assignments, all_scores


def assign_subdirectories_heuristic(subdirs: List[Path], groups: List[Dict], root_path: Path) -> Dict[Path, int]:
    """Assign subdirectories to groups using heuristic rules (non-LLM approach)."""
    assignments, _ = assign_subdirectories_heuristic_with_scores(subdirs, groups, root_path)
    return assignments


def assign_subdirectories_hybrid(subdirs: List[Path], groups: List[Dict], root_path: Path, config: Dict) -> Dict[Path, int]:
    """Assign subdirectories using hybrid approach combining LLM and heuristic."""
    llm_assignments, llm_scores = assign_subdirectories_llm_with_scores(subdirs, groups, root_path)
    heur_assignments, heur_scores = assign_subdirectories_heuristic_with_scores(subdirs, groups, root_path)
    
    strategy = config.get('hybrid', {}).get('strategy', 'weighted')
    llm_weight = config.get('hybrid', {}).get('llm_weight', 0.3)
    heur_weight = config.get('hybrid', {}).get('heuristic_weight', 0.7)
    
    final_assignments = {}
    
    for subdir in subdirs:
        if strategy == 'vote':
            # If both agree, use that; otherwise use heuristic
            if llm_assignments[subdir] == heur_assignments[subdir]:
                final_assignments[subdir] = llm_assignments[subdir]
            else:
                final_assignments[subdir] = heur_assignments[subdir]
        elif strategy == 'weighted':
            # Combine scores with weights
            combined_scores = []
            for i in range(len(groups)):
                # Normalize scores
                llm_score = llm_scores[subdir][i] if i < len(llm_scores[subdir]) else 0
                heur_score = heur_scores[subdir][i] / 100.0 if i < len(heur_scores[subdir]) else 0  # Normalize heuristic scores
                combined = llm_weight * llm_score + heur_weight * heur_score
                combined_scores.append(combined)
            
            # Find best combined score
            best_idx = combined_scores.index(max(combined_scores))
            final_assignments[subdir] = best_idx
        elif strategy == 'max':
            # Use the assignment with higher confidence
            llm_max = max(llm_scores[subdir]) if llm_scores[subdir] else 0
            heur_max = max(heur_scores[subdir]) / 100.0 if heur_scores[subdir] else 0
            if llm_max > heur_max:
                final_assignments[subdir] = llm_assignments[subdir]
            else:
                final_assignments[subdir] = heur_assignments[subdir]
        else:  # average
            # Average the assignments if they differ
            if llm_assignments.get(subdir) == heur_assignments.get(subdir):
                final_assignments[subdir] = llm_assignments[subdir]
            else:
                # Use heuristic as tiebreaker
                final_assignments[subdir] = heur_assignments[subdir]
    
    return final_assignments