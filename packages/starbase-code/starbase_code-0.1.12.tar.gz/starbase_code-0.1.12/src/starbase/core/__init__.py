"""
Core functionality for starbase.

This package contains pure functions for analysis, grouping, extraction,
and assignment without any CLI dependencies.
"""

from .analysis import analyze_file_relationships
from .assignment import (
    analyze_project_with_subdirectories,
    assign_subdirectories_llm_with_scores,
    assign_subdirectories_heuristic_with_scores
)

__all__ = [
    'analyze_file_relationships',
    'analyze_project_with_subdirectories',
    'assign_subdirectories_llm_with_scores',
    'assign_subdirectories_heuristic_with_scores'
]