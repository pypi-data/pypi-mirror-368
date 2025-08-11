"""
Menu functions for starbase.

This module contains the interactive menu functions that have high
cyclomatic complexity due to their nature of handling multiple user choices.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import shutil
import subprocess
import os
import tinydb


def show_package_actions(package_name: str, package_path: str, is_project: bool, 
                        manager, db, console, Prompt, Confirm,
                        prepare_package_for_global_install,
                        install_package_globally, view_file):
    """Show available actions for a package and handle user selection
    
    Args:
        package_name: Name of the package
        package_path: Path to the package relative to starbase
        is_project: Whether this is a project directory
        manager: StarbaseManager instance
        db: TinyDB database instance
        console: Rich Console instance
        Prompt: Rich Prompt class
        Confirm: Rich Confirm class
        prepare_package_for_global_install: Function to prepare package
        install_package_globally: Function to install globally
        view_file: Function to view file contents
    """
    starbase_path = Path(manager.get_active_path())
    full_path = starbase_path / package_path
    
    console.print(f"\n[cyan]📦 Package: {package_name}[/cyan]")
    console.print(f"[dim]Location: {package_path}[/dim]")
    
    # Show available actions
    console.print("\n[yellow]Available Actions:[/yellow]")
    console.print("1. Install with PDM")
    console.print("2. Copy to current directory")
    console.print("3. View source code")
    console.print("4. Show package info")
    console.print("5. Build and install globally")
    console.print("6. Cancel")
    
    choice = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4", "5", "6"], default="6")
    
    if choice == "1":
        # Install with PDM
        if is_project and full_path.is_dir():
            # For projects, we need to install from the directory
            console.print(f"\n[cyan]Installing {package_name} with PDM...[/cyan]")
            console.print(f"[dim]Command: pdm add {full_path}[/dim]\n")
            
            # Check if we're in a PDM project
            if not (Path.cwd() / "pyproject.toml").exists():
                console.print("[yellow]⚠️  No pyproject.toml found in current directory![/yellow]")
                console.print("Initialize a PDM project first with: pdm init")
                return
            
            # Run PDM add
            subprocess.run(["pdm", "add", str(full_path)])
        else:
            # For single files, suggest manual approach
            console.print(f"\n[yellow]This is a single file. To use it:[/yellow]")
            console.print(f"1. Copy to your project: cp {full_path} .")
            console.print(f"2. Import in your code: from {package_name.replace('.py', '')} import ...")
    
    elif choice == "2":
        # Copy to current directory
        console.print(f"\n[cyan]Copying {package_name} to current directory...[/cyan]")
        
        if full_path.is_dir():
            # Copy entire directory
            target = Path.cwd() / package_name
            if target.exists():
                if not Confirm.ask(f"{package_name} already exists. Overwrite?"):
                    return
                shutil.rmtree(target)
            
            shutil.copytree(full_path, target)
            console.print(f"[green]✓ Copied directory to {target}[/green]")
        else:
            # Copy single file
            target = Path.cwd() / full_path.name
            if target.exists():
                if not Confirm.ask(f"{full_path.name} already exists. Overwrite?"):
                    return
            
            shutil.copy2(full_path, target)
            console.print(f"[green]✓ Copied to {target}[/green]")
    
    elif choice == "3":
        # View source code
        if full_path.is_dir():
            # Show main files in directory
            py_files = list(full_path.glob("*.py"))[:5]
            if py_files:
                console.print(f"\n[cyan]Main files in {package_name}:[/cyan]")
                for i, f in enumerate(py_files, 1):
                    console.print(f"{i}. {f.name}")
                
                file_choice = Prompt.ask("Select file to view", default="1")
                try:
                    file_idx = int(file_choice) - 1
                    if 0 <= file_idx < len(py_files):
                        view_file(py_files[file_idx])
                except:
                    pass
            else:
                console.print("[yellow]No Python files found in directory[/yellow]")
        else:
            view_file(full_path)
    
    elif choice == "4":
        # Show package info
        Query = tinydb.Query()
        entries = db.search(Query.path == package_path)
        if entries:
            entry = entries[0]
            console.print(f"\n[cyan]Package Information:[/cyan]")
            console.print(f"Name: {entry.get('name', 'Unknown')}")
            console.print(f"Type: {entry.get('type', 'Unknown')}")
            console.print(f"Description: {entry.get('description', 'No description')}")
            
            # File count and size calculated from actual directory
            if full_path.exists() and full_path.is_dir():
                file_count = len(list(full_path.rglob('*.*')))
                total_size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
                console.print(f"Files: {file_count}")
                console.print(f"Size: {total_size / 1024:.1f} KB")
            if entry.get('extracted_from'):
                console.print(f"Source: {entry.get('extracted_from')}")
            if entry.get('extracted_at'):
                console.print(f"Added: {entry.get('extracted_at')[:10]}")
    
    elif choice == "5":
        # Build and install globally
        console.print(f"\n[cyan]🌍 Global Installation - {package_name}[/cyan]")
        
        # Check if package has pyproject.toml
        if not is_project or not (full_path / "pyproject.toml").exists():
            console.print("[red]This package cannot be installed globally.[/red]")
            console.print("[yellow]Global installation requires a proper Python project with pyproject.toml[/yellow]")
            return
        
        # Prepare and install
        if prepare_package_for_global_install(full_path, package_name):
            # Offer installation methods
            console.print("\n[yellow]Select installation method:[/yellow]")
            console.print("1. Automatic (recommended)")
            console.print("2. PDM global install")
            console.print("3. Pip user install")
            console.print("4. Manual symlink")
            console.print("5. Cancel")
            
            method_choice = Prompt.ask("Method", choices=["1", "2", "3", "4", "5"], default="1")
            
            if method_choice == "5":
                return
            
            method_map = {
                "1": "auto",
                "2": "pdm",
                "3": "pip",
                "4": "symlink"
            }
            
            method = method_map[method_choice]
            
            # Save current directory
            original_dir = Path.cwd()
            
            try:
                # Perform installation
                if install_package_globally(full_path, package_name, method):
                    console.print(f"\n[green]🎉 {package_name} is now available globally![/green]")
                else:
                    console.print(f"\n[red]Failed to install {package_name} globally.[/red]")
            finally:
                # Always return to original directory
                os.chdir(original_dir)