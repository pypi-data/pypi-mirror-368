#!/usr/bin/env python3
"""
Minimal wrapper that includes starbase.py source for installed package.
This avoids maintaining duplicate code.
"""

import sys
import os
from pathlib import Path

# Get the actual starbase.py content from the package
package_dir = Path(__file__).parent
starbase_source = package_dir / "starbase_main.py"

# Read and execute the main starbase code
if starbase_source.exists():
    # If we packaged starbase.py as starbase_main.py
    exec(open(starbase_source).read())
else:
    # Fallback: try to import from the development location
    # This shouldn't happen in a properly installed package
    import importlib.util
    dev_starbase = Path(__file__).parent.parent.parent / "starbase.py"
    if dev_starbase.exists():
        spec = importlib.util.spec_from_file_location("starbase", dev_starbase)
        starbase = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(starbase)
        
        # Make all starbase exports available
        for name in dir(starbase):
            if not name.startswith('_'):
                globals()[name] = getattr(starbase, name)
    else:
        raise ImportError("Could not find starbase.py source code")

# The main() function should now be available from the executed code
if __name__ == "__main__":
    main()