#!/usr/bin/env python3
"""Wrapper for installed starbase package - imports from main starbase.py"""

import sys
from pathlib import Path

# Add the parent directory to path so we can import starbase.py
package_dir = Path(__file__).parent
starbase_root = package_dir.parent.parent  # Go up to project root

# Add to path and import
sys.path.insert(0, str(starbase_root))
import starbase

def main():
    """Entry point for installed package"""
    starbase.main()

if __name__ == "__main__":
    main()