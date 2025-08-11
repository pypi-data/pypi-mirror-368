#!/usr/bin/env python3
"""MCP Server Auto-Installer for Starbase"""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Optional imports for functionality moved from starbase.py
try:
    import toml
except ImportError:
    toml = None

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
except ImportError:
    Console, Panel, Syntax, Prompt, Confirm = None, None, None, None, None

console = Console() if Console else None

class MCPInstaller:
    """Handles MCP server installation and configuration for starbase."""

    def __init__(self, project_root_path: Optional[Path] = None):
        """
        Args:
            project_root_path: Path to the root of the starbase project source code.
        """
        self.project_root_path = Path(project_root_path) if project_root_path else Path.cwd()

    def is_globally_installed(self) -> bool:
        """Check if the 'starbase' command is available in the system's PATH."""
        return shutil.which("starbase") is not None
    
    def _cleanup_broken_installations(self, package_name: str):
        """Remove any broken or old installations of the package."""
        if package_name != "starbase":
            return  # Only cleanup starbase for now
        
        console.print("\n[cyan]🧹 Checking for old or broken installations...[/cyan]")
        
        # Check for pipx installation
        pipx_path = shutil.which("pipx")
        if pipx_path:
            try:
                # Check if starbase is installed via pipx
                result = subprocess.run([pipx_path, "list"], capture_output=True, text=True)
                if "starbase" in result.stdout:
                    console.print("[yellow]Found existing pipx installation. Removing...[/yellow]")
                    subprocess.run([pipx_path, "uninstall", "starbase"], capture_output=True)
                    console.print("[green]✓ Removed old pipx installation[/green]")
            except:
                pass  # Ignore errors during cleanup
        
        # Check for symlinks in standard locations
        standard_paths = ["/usr/local/bin/starbase", "/opt/homebrew/bin/starbase"]
        for path in standard_paths:
            if Path(path).exists():
                console.print(f"[yellow]Found old symlink at {path}. This may require sudo to remove.[/yellow]")
    
    def _ensure_standard_path_access(self, package_name: str):
        """Ensure the command is accessible in standard paths for Claude Desktop."""
        if package_name != "starbase":
            return
        
        # Check if Claude Desktop is installed
        claude_desktop_exists = False
        if sys.platform == "darwin":
            claude_desktop_exists = Path("/Applications/Claude.app").exists()
        elif sys.platform == "win32":
            # Check common Windows install locations
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Anthropic\Claude") as key:
                    claude_desktop_exists = True
            except:
                claude_desktop_exists = Path(os.environ.get("PROGRAMFILES", "") + r"\Claude\Claude.exe").exists()
        
        if not claude_desktop_exists:
            # Claude Desktop not installed, skip this step
            return
        
        console.print("\n[cyan]🔗 Claude Desktop detected. Setting up integration...[/cyan]")
        
        # Find where starbase was installed
        starbase_path = shutil.which("starbase")
        if not starbase_path:
            console.print("[red]Warning: Could not find starbase in PATH after installation[/red]")
            return
        
        # Check if it's already in a standard location
        standard_paths = ["/usr/local/bin", "/opt/homebrew/bin", "/usr/bin"]
        starbase_dir = Path(starbase_path).parent
        
        if str(starbase_dir) in standard_paths:
            console.print(f"[green]✓ Starbase already accessible to Claude Desktop at {starbase_path}[/green]")
            return
        
        # Create symlink in /usr/local/bin for Claude Desktop
        symlink_path = Path("/usr/local/bin/starbase")
        
        console.print(f"[yellow]Creating symlink for Claude Desktop integration...[/yellow]")
        console.print(f"[dim]Linking {starbase_path} → {symlink_path}[/dim]")
        
        try:
            # First try without sudo (unlikely to work but worth trying)
            symlink_path.unlink(missing_ok=True)
            symlink_path.symlink_to(starbase_path)
            console.print(f"[green]✓ Created symlink at {symlink_path}[/green]")
            console.print("[green]✓ Claude Desktop integration complete![/green]")
        except PermissionError:
            # Need sudo - just do it
            console.print("[yellow]Administrator access required for Claude Desktop integration.[/yellow]")
            console.print("[dim]You may be prompted for your password.[/dim]")
            
            try:
                # Remove old symlink if it exists
                subprocess.run(["sudo", "rm", "-f", str(symlink_path)], capture_output=True)
                # Create new symlink
                result = subprocess.run(
                    ["sudo", "ln", "-sf", str(starbase_path), str(symlink_path)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    console.print(f"[green]✓ Created symlink at {symlink_path}[/green]")
                    console.print("[green]✓ Claude Desktop integration complete![/green]")
                    console.print("[dim]Restart Claude Desktop to use the starbase MCP server.[/dim]")
                else:
                    console.print(f"[red]Failed to create symlink: {result.stderr}[/red]")
                    console.print("\n[yellow]To complete Claude Desktop integration manually, run:[/yellow]")
                    console.print(f"[cyan]sudo ln -sf {starbase_path} {symlink_path}[/cyan]")
            except Exception as e:
                console.print(f"[red]Error running sudo: {e}[/red]")
                console.print("\n[yellow]To complete Claude Desktop integration manually, run:[/yellow]")
                console.print(f"[cyan]sudo ln -sf {starbase_path} {symlink_path}[/cyan]")

    def install_and_configure_mcp(self, package_name: str = "starbase") -> bool:
        """
        Main function to perform a full global installation and MCP configuration.
        """
        if not console:
            print("Rich console components not available. Please run 'pip install rich'.")
            return False
            
        console.print(f"\n[cyan]🚀 Starting global installation and MCP configuration for '{package_name}'...[/cyan]")

        # Step 0: Clean up any broken installations first
        self._cleanup_broken_installations(package_name)

        # Step 1: Install the package globally
        install_success = self._install_package_globally(package_name)
        if not install_success:
            console.print(f"[red]❌ Global installation for '{package_name}' failed. Aborting MCP configuration.[/red]")
            return False
        
        console.print(f"[green]✓ '{package_name}' package installed successfully.[/green]")

        # Step 1.5: Ensure starbase is accessible in standard paths for Claude Desktop
        self._ensure_standard_path_access(package_name)

        # Step 2: Configure Claude clients to use the new MCP server
        console.print("\n[cyan]⚙️  Configuring Claude clients for MCP access...[/cyan]")
        desktop_updated = self._update_claude_config()
        cli_updated = self._update_claude_code_config()

        if desktop_updated or cli_updated:
            console.print("\n[green]✓ Claude Desktop and/or Claude Code CLI configurations updated.[/green]")
            console.print("[dim]Restart Claude clients to see the changes.[/dim]")
        else:
            console.print("\n[dim]Claude configurations already up to date.[/dim]")
        
        console.print("\n[bold green]✅ Starbase installation and MCP configuration complete![/bold green]")
        return True

    def _prepare_package_for_global_install(self, package_path: Path, package_name: str) -> bool:
        """Prepares a package for global installation by ensuring proper configuration."""
        pyproject_path = self.project_root_path / "pyproject.toml"
        
        if not toml:
            console.print("[red]TOML library not found. Please run 'pip install toml'.[/red]")
            return False
            
        if not pyproject_path.exists():
            console.print(f"[red]No pyproject.toml found at {pyproject_path}[/red]")
            return False

        try:
            pyproject_data = toml.load(pyproject_path)
        except Exception as e:
            console.print(f"[red]Error reading pyproject.toml: {e}[/red]")
            return False

        if "project" not in pyproject_data:
            console.print("[red]Invalid pyproject.toml: missing [project] section[/red]")
            return False

        # Ensure console scripts are defined for the main 'starbase' package
        if package_name == "starbase" and "scripts" not in pyproject_data.get("project", {}):
            console.print("[yellow]Adding missing console script entry for 'starbase' to pyproject.toml[/yellow]")
            pyproject_data["project"]["scripts"] = {"starbase": "starbase:app"}
            with open(pyproject_path, 'w') as f:
                toml.dump(pyproject_data, f)
        
        return True

    def _install_package_globally(self, package_name: str, method: str = "auto") -> bool:
        """
        Automated, multi-step installation of the package from the local project source.
        Tries pipx -> sudo pipx -> pip, with user prompts for elevated permissions.
        """
        package_path = self.project_root_path

        console.print(f"\n[cyan]Preparing '{package_name}' for global installation from {package_path}...[/cyan]")
        if not self._prepare_package_for_global_install(package_path, package_name):
            return False

        console.print(f"\n[cyan]Building package with PDM...[/cyan]")
        original_dir = Path.cwd()
        os.chdir(package_path)

        try:
            # Build the package
            subprocess.run(["pdm", "build"], check=True, capture_output=True, text=True)
            
            dist_dir = package_path / "dist"
            wheels = list(dist_dir.glob("*.whl"))
            if not wheels:
                console.print("[red]❌ No wheel file found after PDM build.[/red]")
                return False
            
            wheel_path = wheels[-1]
            console.print(f"\n[green]✓ Package built successfully: {wheel_path.name}[/green]")

            # --- Start of the new automated installation logic ---

            # 1. Try pipx
            pipx_path = shutil.which("pipx")
            if pipx_path:
                console.print("\n[cyan]🚀 Phase 1: `pipx` found. Attempting recommended installation...[/cyan]")
                try:
                    pipx_command = [pipx_path, "install", "--force", str(wheel_path)]
                    subprocess.run(pipx_command, check=True, capture_output=True, text=True)
                    console.print("[bold green]✅ Success! Starbase installed globally via pipx.[/bold green]")
                    console.print("[dim]Please restart your terminal for changes to take effect.[/dim]")
                    return True
                except subprocess.CalledProcessError as e:
                    if "permission" in e.stderr.lower() or "denied" in e.stderr.lower():
                        console.print("[yellow]⚠️ pipx installation failed due to a permission error.[/yellow]")
                        # 2. Try sudo pipx
                        if Confirm.ask("[bold yellow]Do you want to attempt the installation again with administrator privileges (sudo)?[/bold yellow]"):
                            console.print("\n[cyan]🚀 Phase 2: Attempting installation with `sudo pipx`...[/cyan]")
                            try:
                                sudo_pipx_command = ["sudo", pipx_path, "install", "--force", str(wheel_path)]
                                console.print(f"[dim]Running command: {' '.join(sudo_pipx_command)}[/dim]")
                                console.print("[dim]Your OS may ask for your password.[/dim]")
                                subprocess.run(sudo_pipx_command, check=True, capture_output=True, text=True)
                                console.print("[bold green]✅ Success! Starbase installed globally via sudo pipx.[/bold green]")
                                console.print("[dim]Please restart your terminal for changes to take effect.[/dim]")
                                return True
                            except subprocess.CalledProcessError as sudo_e:
                                console.print(f"[red]❌ `sudo pipx` failed.[/red]")
                                # Fall through to pip
                    else:
                        console.print(f"[red]❌ `pipx` failed for a reason other than permissions.[/red]")
                        # Fall through to pip
            else:
                console.print("[yellow]⚠️ Recommended tool `pipx` not found.[/yellow]")
                # Offer to install pipx (informational, not executed)
                if Confirm.ask("[bold yellow]Do you want to see instructions for installing pipx?[/bold yellow]"):
                     console.print("\nTo install pipx, use one of the following commands:")
                     console.print("  - On macOS (with Homebrew): [cyan]brew install pipx[/cyan]")
                     console.print("  - On Linux (Debian/Ubuntu): [cyan]sudo apt install pipx[/cyan]")
                     console.print("  - With Python's pip:       [cyan]python3 -m pip install --user pipx && python3 -m pipx ensurepath[/cyan]")
                     console.print("After installing, please re-run the starbase command.")
                     return False # End the process here to let user install pipx

            # 3. Fallback to pip
            console.print("\n[cyan]🚀 Phase 3: Falling back to `pip` for installation...[/cyan]")
            try:
                pip_command = [
                    sys.executable, "-m", "pip", "install", "--user",
                    "--force-reinstall", "--break-system-packages", str(wheel_path.absolute())
                ]
                subprocess.run(pip_command, check=True, capture_output=True, text=True)
                console.print("[bold green]✅ Success! Starbase installed globally via pip.[/bold green]")
                console.print("[dim]Please restart your terminal for changes to take effect.[/dim]")
                return True
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ `pip` installation failed.[/red]")
                console.print(f"[red]STDERR: {e.stderr}[/red]")

            # 4. Final Failure
            console.print("\n[bold red]❌ All automated installation methods have failed.[/bold red]")
            console.print("You can try to install the package manually. Please run one of the following commands:")
            console.print(f"  - Recommended: [cyan]pipx install --force {wheel_path.absolute()}[/cyan]")
            console.print(f"  - Alternative: [cyan]pip install --user --force-reinstall --break-system-packages {wheel_path.absolute()}[/cyan]")
            return False

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Build failed:[/red]")
            console.print(f"[red]STDOUT: {e.stdout}[/red]")
            console.print(f"[red]STDERR: {e.stderr}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]An unexpected error occurred during build: {e}[/red]")
            return False
        finally:
            os.chdir(original_dir)

    def configure_project_mcp(self, project_path: Optional[Path] = None) -> bool:
        """Configure starbase MCP server for a specific Claude Code project."""
        project_path = Path(project_path) if project_path else Path.cwd()
        mcp_config_path = project_path / ".mcp.json"
        
        config = {"mcpServers": {}}
        if mcp_config_path.exists():
            try:
                with open(mcp_config_path, 'r') as f:
                    config = json.load(f)
                    if "mcpServers" not in config:
                        config["mcpServers"] = {}
            except json.JSONDecodeError:
                config = {"mcpServers": {}}

        starbase_config = {
            "type": "stdio",
            "command": "starbase",
            "args": ["mcp-server"]
        }

        if "starbase" in config.get("mcpServers", {}) and config["mcpServers"]["starbase"] == starbase_config:
            console.print("[dim]Starbase MCP server already configured for this project.[/dim]")
            return True

        config["mcpServers"]["starbase"] = starbase_config
        
        try:
            with open(mcp_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            console.print(f"\n[green]✓ Configured starbase MCP server for project: {project_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error configuring project MCP: {e}[/red]")
            return False

    def _get_claude_desktop_config_path(self) -> Path:
        if sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif sys.platform == "win32":
            return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
        else:
            return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

    def _ensure_claude_config_exists(self) -> Dict[str, Any]:
        config_path = self._get_claude_desktop_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _update_claude_config(self) -> bool:
        """Update Claude Desktop config to use the global 'starbase mcp-server' command."""
        config = self._ensure_claude_config_exists()
        config_path = self._get_claude_desktop_config_path()
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        starbase_config = {
            "command": "starbase",
            "args": ["mcp-server"]
        }
        
        if "starbase" in config.get("mcpServers", {}) and config["mcpServers"]["starbase"] == starbase_config:
            return False

        config["mcpServers"]["starbase"] = starbase_config
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[red]Error updating Claude Desktop config: {e}[/red]")
            return False

    def _get_claude_code_config_path(self) -> Path:
        return Path.home() / ".claude.json"

    def _update_claude_code_config(self) -> bool:
        """Update Claude Code CLI config to use the global 'starbase mcp-server' command."""
        config_path = self._get_claude_code_config_path()
        config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                config = {}

        if "mcpServers" not in config:
            config["mcpServers"] = {}
            
        starbase_config = {
            "type": "stdio",
            "command": "starbase",
            "args": ["mcp-server"]
        }

        if "starbase" in config.get("mcpServers", {}) and config["mcpServers"]["starbase"] == starbase_config:
            return False

        config["mcpServers"]["starbase"] = starbase_config
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[red]Error updating Claude Code config: {e}[/red]")
            return False