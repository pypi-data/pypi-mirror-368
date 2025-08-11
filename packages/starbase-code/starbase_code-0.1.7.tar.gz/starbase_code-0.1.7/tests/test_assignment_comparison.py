"""
Test subdirectory assignment approaches (LLM vs heuristic vs hybrid)
using REAL starbase functions and REAL data.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
from datetime import datetime

# Add parent directory to path so we can import starbase
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import REAL functions from starbase and core modules
from starbase import manager
from core.analysis import analyze_file_relationships
from core.assignment import (
    analyze_project_with_subdirectories,
    assign_subdirectories_llm,
    assign_subdirectories_heuristic,
    assign_subdirectories_hybrid,
    load_subdirectory_config
)

# For comparison metrics
# Removed calculate_assignment_score as we're analyzing groups directly


# Removed format_results function as we're not using it anymore


def create_report_table(results: Dict[str, Any]) -> List[str]:
    """Create a markdown table with real measurements."""
    lines = []
    
    # Header
    lines.append("# Subdirectory Assignment Comparison Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project: {results['project_path']}")
    lines.append("")
    
    # Summary of groups
    lines.append("## Groups Found")
    lines.append("| Group | Type | Total Files | Top-Level Files | Subdirectories |")
    lines.append("|-------|------|-------------|-----------------|----------------|")
    
    # Use the first method's groups as reference
    ref_groups = results.get('heuristic', {}).get('groups', results['groups'])
    for group in ref_groups:
        top_level_files = len([f for f in group['files'] if f.parent == Path(results['project_path'])])
        subdir_count = len(group.get('subdirectories', []))
        lines.append(f"| {group['name']} | {group.get('type', 'unknown')} | {len(group['files'])} | {top_level_files} | {subdir_count} |")
    lines.append("")
    
    # Extract subdirectory info from groups
    all_subdirs = set()
    subdir_info = {}
    
    for method_data in results.values():
        if isinstance(method_data, dict) and 'groups' in method_data:
            for group in method_data['groups']:
                if 'subdirectories' in group:
                    for subdir in group['subdirectories']:
                        all_subdirs.add(subdir)
                        if subdir not in subdir_info:
                            py_files = [f for f in group['files'] if f.parent == subdir or any(parent == subdir for parent in f.parents)]
                            subdir_info[subdir] = {
                                'file_count': len(py_files),
                                'has_init': (subdir / '__init__.py').exists()
                            }
    
    lines.append("## Subdirectories with Python Files")
    lines.append("| Directory | Python Files | Has __init__.py |")
    lines.append("|-----------|--------------|-----------------|")
    for subdir in sorted(all_subdirs, key=lambda x: x.name):
        info = subdir_info.get(subdir, {'file_count': 0, 'has_init': False})
        lines.append(f"| {subdir.name} | {info['file_count']} | {'Yes' if info['has_init'] else 'No'} |")
    lines.append("")
    
    # Assignment results comparison
    lines.append("## Assignment Results by Method")
    lines.append("| Method | Total Groups | Total Files | Subdirs Assigned |")
    lines.append("|--------|--------------|-------------|------------------|")
    
    for method in ['heuristic', 'llm', 'hybrid']:
        if method in results and results[method]:
            groups = results[method]['groups']
            total_files = sum(len(g['files']) for g in groups)
            total_subdirs = sum(len(g.get('subdirectories', [])) for g in groups)
            lines.append(f"| {method.capitalize()} | {len(groups)} | {total_files} | {total_subdirs} |")
    lines.append("")
    
    # Detailed assignments
    lines.append("## Detailed Group Assignments by Method")
    
    for method in ['heuristic', 'llm', 'hybrid']:
        if method not in results or not results[method]:
            continue
            
        lines.append(f"\n### {method.capitalize()} Method")
        groups = results[method]['groups']
        
        for idx, group in enumerate(groups):
            lines.append(f"\n**Group {idx}: {group['name']} ({len(group['files'])} files total)**")
            
            # Show subdirectories
            if 'subdirectories' in group and group['subdirectories']:
                lines.append("Subdirectories:")
                for subdir in sorted(group['subdirectories'], key=lambda x: x.name):
                    subdir_files = len([f for f in group['files'] if f.parent == subdir or any(parent == subdir for parent in f.parents)])
                    lines.append(f"- {subdir.name} ({subdir_files} files)")
            else:
                lines.append("No subdirectories assigned")
    
    lines.append("")
    
    # Differences analysis
    lines.append("## Differences Analysis")
    
    if 'heuristic' in results and 'llm' in results:
        h_assign = results['heuristic']['assignments']
        l_assign = results['llm']['assignments']
        
        differences = []
        for subdir in results['subdirs_with_files']:
            h_group = h_assign.get(subdir, -1)
            l_group = l_assign.get(subdir, -1)
            if h_group != l_group:
                differences.append({
                    'subdir': subdir,
                    'heuristic': h_group,
                    'llm': l_group,
                    'files': results['subdirs_with_files'][subdir]['file_count']
                })
        
        if differences:
            lines.append(f"\nFound {len(differences)} subdirectories assigned differently:")
            lines.append("| Subdirectory | Files | Heuristic → | LLM → | Correct? |")
            lines.append("|--------------|-------|-------------|-------|----------|")
            
            for diff in differences:
                h_group_name = results['groups'][diff['heuristic']]['name'] if 0 <= diff['heuristic'] < len(results['groups']) else "Invalid"
                l_group_name = results['groups'][diff['llm']]['name'] if 0 <= diff['llm'] < len(results['groups']) else "Invalid"
                
                # Determine which is likely correct based on group sizes
                h_group_size = len(results['groups'][diff['heuristic']]['files']) if 0 <= diff['heuristic'] < len(results['groups']) else 0
                l_group_size = len(results['groups'][diff['llm']]['files']) if 0 <= diff['llm'] < len(results['groups']) else 0
                
                likely_correct = "Heuristic" if h_group_size > l_group_size else "LLM"
                
                lines.append(f"| {diff['subdir'].name} | {diff['files']} | {h_group_name} | {l_group_name} | {likely_correct} |")
        else:
            lines.append("\nNo differences - all methods produced identical assignments!")
    
    lines.append("")
    
    # Real measurements summary
    lines.append("## Summary of Real Measurements")
    lines.append("| Metric | Description | Value |")
    lines.append("|--------|-------------|-------|")
    
    # Use heuristic method as reference
    if 'heuristic' in results and results['heuristic']:
        ref_groups = results['heuristic']['groups']
        total_subdirs = len(all_subdirs)
        total_subdir_files = sum(subdir_info[s]['file_count'] for s in all_subdirs if s in subdir_info)
        total_files = sum(len(g['files']) for g in ref_groups)
        
        lines.append(f"| Total Groups | Number of groups (including standalone) | {len(ref_groups)} |")
        lines.append(f"| Total Files | All Python files in project | {total_files} |")
        lines.append(f"| Total Subdirectories | Subdirectories with Python files | {total_subdirs} |")
        lines.append(f"| Files in Subdirectories | Python files in all subdirectories | {total_subdir_files} |")
        lines.append(f"| Largest Group | Files in the largest group | {max(len(g['files']) for g in ref_groups)} |")
        
        # Count group types
        connected = sum(1 for g in ref_groups if g.get('type') == 'connected')
        standalone = sum(1 for g in ref_groups if g.get('type') == 'standalone')
        lines.append(f"| Connected Groups | Groups with multiple related files | {connected} |")
        lines.append(f"| Standalone Groups | Single file groups | {standalone} |")
    
    return lines


def extract_assignments_from_groups(groups: List[Dict]) -> Dict[Path, int]:
    """Extract subdirectory assignments from groups."""
    assignments = {}
    for idx, group in enumerate(groups):
        if 'subdirectories' in group:
            for subdir in group['subdirectories']:
                assignments[subdir] = idx
    return assignments


def print_group_summary(groups: List[Dict]) -> None:
    """Print summary of groups with their subdirectories."""
    for idx, group in enumerate(groups):
        print(f"\nGroup {idx}: {group['name']} ({len(group['files'])} files)")
        if 'subdirectories' in group and group['subdirectories']:
            for subdir in group['subdirectories']:
                subdir_files = len([f for f in group['files'] if f.parent == subdir or any(parent == subdir for parent in f.parents)])
                print(f"  - {subdir.name} ({subdir_files} files)")


def compare_assignment_methods(project_path: Path):
    """Compare LLM vs heuristic vs hybrid subdirectory assignment."""
    print(f"\nAnalyzing project: {project_path}")
    
    # Store all results for report generation
    results = {
        'project_path': str(project_path),
        'groups': [],
        'subdirs_with_files': {},
    }
    
    # Call the EXACT SAME FUNCTION that extract_menu calls!
    print("\nAnalyzing directory with subdirectories...")
    
    # This is what analyze_directory_for_extraction does when subdirs exist
    groups = analyze_project_with_subdirectories(project_path)
    results['groups'] = groups
    
    print(f"\nFound {len(groups)} groups:")
    for i, group in enumerate(groups):
        group_type = f"({group['type']})" if 'type' in group else ""
        print(f"  {i+1}. {group['name']} - {len(group['files'])} files {group_type}")
    
    # The groups already have subdirectories assigned by analyze_project_with_subdirectories
    # Extract subdirectory info for reporting
    subdirs_with_files = {}
    all_subdirs = set()
    
    for group in groups:
        if 'subdirectories' in group:
            for subdir in group['subdirectories']:
                all_subdirs.add(subdir)
                py_files = [f for f in group['files'] if f.parent == subdir or any(parent == subdir for parent in f.parents)]
                if py_files:
                    subdirs_with_files[subdir] = {
                        'file_count': len(py_files),
                        'files': py_files,
                        'has_init': (subdir / '__init__.py').exists()
                    }
    
    results['subdirs_with_files'] = subdirs_with_files
    
    print(f"\nSubdirectories already assigned to groups:")
    for subdir, info in subdirs_with_files.items():
        print(f"  - {subdir.name} ({info['file_count']} files)")
    
    # Since we're comparing assignment methods, we need to test different configs
    # But we already have the default assignments from analyze_project_with_subdirectories
    print("\nComparing assignment methods by re-running with different configs...")
    
    # Get just the top-level groups for comparison
    py_files = list(project_path.glob("*.py"))
    top_level_groups = analyze_file_relationships(py_files)
    
    # For comparison, we need to test the assignment functions directly
    # This simulates what would happen with different config settings
    
    # Method A: Heuristic (this is the default)
    print("\n--- HEURISTIC method (default) ---")
    config = {'assignment': {'method': 'heuristic'}}
    heuristic_groups = analyze_project_with_subdirectories(project_path, config)
    results['heuristic'] = {
        'groups': heuristic_groups,
        'assignments': extract_assignments_from_groups(heuristic_groups)
    }
    print_group_summary(heuristic_groups)
    
    # Method B: LLM
    try:
        print("\n--- LLM method ---")
        config = {'assignment': {'method': 'llm'}}
        llm_groups = analyze_project_with_subdirectories(project_path, config)
        results['llm'] = {
            'groups': llm_groups,
            'assignments': extract_assignments_from_groups(llm_groups)
        }
        print_group_summary(llm_groups)
    except Exception as e:
        print(f"LLM method failed: {e}")
        results['llm'] = None
    
    # Method C: Hybrid
    if results.get('llm'):
        print("\n--- HYBRID method ---")
        config = {'assignment': {'method': 'hybrid'}, 'hybrid': {'strategy': 'weighted', 'llm_weight': 0.3, 'heuristic_weight': 0.7}}
        hybrid_groups = analyze_project_with_subdirectories(project_path, config)
        results['hybrid'] = {
            'groups': hybrid_groups,
            'assignments': extract_assignments_from_groups(hybrid_groups)
        }
        print_group_summary(hybrid_groups)
    
    # Compare results
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    
    # Show differences in assignments
    if results.get('llm') and results.get('heuristic'):
        h_assignments = results['heuristic']['assignments']
        l_assignments = results['llm']['assignments']
        
        all_subdirs = set(h_assignments.keys()) | set(l_assignments.keys())
        differences = []
        
        for subdir in all_subdirs:
            h_group = h_assignments.get(subdir, -1)
            l_group = l_assignments.get(subdir, -1)
            if h_group != l_group:
                differences.append({
                    'subdir': subdir,
                    'heuristic': h_group,
                    'llm': l_group
                })
        
        if differences:
            print(f"\nFound {len(differences)} subdirectories assigned differently:")
            for diff in differences:
                h_group_name = results['heuristic']['groups'][diff['heuristic']]['name'] if diff['heuristic'] >= 0 else "None"
                l_group_name = results['llm']['groups'][diff['llm']]['name'] if diff['llm'] >= 0 else "None"
                print(f"  {diff['subdir'].name}:")
                print(f"    Heuristic → Group {diff['heuristic']} ({h_group_name})")
                print(f"    LLM       → Group {diff['llm']} ({l_group_name})")
        else:
            print("\nNo differences - all methods assigned subdirectories identically!")
    
    # Generate and write the report
    print("\nGenerating comprehensive report...")
    report_lines = create_report_table(results)
    report_path = project_path / 'testreport.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"Report written to: {report_path}")


def main():
    """Run comparison test on a real project."""
    # Test on the current directory or a specific test project
    import argparse
    parser = argparse.ArgumentParser(description='Compare subdirectory assignment methods')
    parser.add_argument('path', nargs='?', default='.', help='Path to project to analyze')
    args = parser.parse_args()
    
    project_path = Path(args.path).resolve()
    if not project_path.exists():
        print(f"Error: Path {project_path} does not exist!")
        return
    
    compare_assignment_methods(project_path)


if __name__ == "__main__":
    main()