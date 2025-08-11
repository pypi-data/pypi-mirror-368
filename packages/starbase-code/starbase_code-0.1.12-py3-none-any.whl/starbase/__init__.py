"""Starbase package - centralized code repository manager."""

def main():
    """Entry point for starbase command - always use root starbase.py."""
    import sys
    from pathlib import Path
    
    # The starbase.py is ALWAYS at the project root, whether dev or installed
    # In dev: /path/to/project/starbase.py
    # When installed: we need to include it in the package
    
    # Try multiple locations
    possible_locations = [
        Path(__file__).parent.parent.parent / "starbase.py",  # Dev mode
        Path(__file__).parent / "starbase.py",  # If we copy it to package dir
        Path(sys.prefix) / "starbase.py",  # Some install locations
    ]
    
    starbase_py = None
    for loc in possible_locations:
        if loc.exists():
            starbase_py = loc
            break
    
    if starbase_py:
        # Import and run starbase.py
        import importlib.util
        spec = importlib.util.spec_from_file_location("starbase_main", starbase_py)
        starbase_main = importlib.util.module_from_spec(spec)
        
        # Add parent dir to path for imports
        if str(starbase_py.parent) not in sys.path:
            sys.path.insert(0, str(starbase_py.parent))
            
        spec.loader.exec_module(starbase_main)
        starbase_main.main()
    else:
        # Last resort: try to use the cli.py (which we should remove eventually)
        try:
            from starbase.cli import main as cli_main
            cli_main()
        except ImportError:
            raise ImportError(
                "Could not find starbase.py. Package may be incorrectly installed.\n"
                "Searched locations:\n" + "\n".join(str(p) for p in possible_locations)
            )