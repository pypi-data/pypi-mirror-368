import subprocess
import sys
from typing import List, Optional, Tuple

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Import the concurrent futures module for threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the refactored utility functions
from .utils import get_outdated_packages, generate_packages_table

# Initialize Rich Console for beautiful printing
console = Console()

# Create a Typer app for our CLI
app = typer.Typer(
    name="py-upgrade",
    help="An intelligent, feature-rich CLI tool to manage and upgrade Python packages.",
    add_completion=False,
)

def upgrade_package(pkg: dict) -> Tuple[str, str, bool]:
    """
    Worker function to upgrade a single package in a separate thread.
    
    Args:
        pkg: A dictionary containing package information ('name', 'latest_version').

    Returns:
        A tuple containing (package_name, latest_version, success_boolean).
    """
    pkg_name = pkg['name']
    latest_version = pkg['latest_version']
    try:
        # Execute the pip upgrade command, suppressing output
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", pkg_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return pkg_name, latest_version, True
    except subprocess.CalledProcessError:
        return pkg_name, latest_version, False

@app.command()
def upgrade(
    packages_to_upgrade: Optional[List[str]] = typer.Argument(
        None, help="Specific packages to upgrade. If not provided, all outdated packages are targeted."
    ),
    exclude: Optional[List[str]] = typer.Option(
        None, "--exclude", "-e", help="List of packages to exclude from the upgrade."
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Automatically confirm and proceed with the upgrade."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate the upgrade without making any changes."
    ),
    workers: int = typer.Option(
        10, "--workers", "-w", help="Number of concurrent workers for parallel upgrades."
    )
):
    """
    Checks for and concurrently upgrades outdated Python packages.
    """
    # --- Filtering Logic (Unchanged) ---
    outdated_packages = get_outdated_packages()
    
    if not outdated_packages:
        console.print("[bold green]✨ All packages are up to date! ✨[/bold green]")
        raise typer.Exit()

    if packages_to_upgrade:
        name_to_pkg = {pkg['name'].lower(): pkg for pkg in outdated_packages}
        target_packages = [name_to_pkg[name.lower()] for name in packages_to_upgrade if name.lower() in name_to_pkg]
    else:
        target_packages = outdated_packages

    if exclude:
        exclude_set = {name.lower() for name in exclude}
        target_packages = [pkg for pkg in target_packages if pkg['name'].lower() not in exclude_set]

    if not target_packages:
        console.print("[bold yellow]No packages match the specified criteria for upgrade.[/bold yellow]")
        raise typer.Exit()

    # --- Display and Confirmation (Unchanged) ---
    table = generate_packages_table(target_packages, title="Outdated Python Packages")
    console.print(table)

    if dry_run:
        console.print(f"\n[bold yellow]--dry-run enabled. Would upgrade {len(target_packages)} packages with {workers} workers.[/bold yellow]")
        raise typer.Exit()

    if not yes:
        try:
            confirmed = typer.confirm("\nProceed with the upgrade?")
            if not confirmed:
                console.print("Upgrade cancelled by user.")
                raise typer.Exit()
        except typer.Abort:
            console.print("\nUpgrade cancelled by user.")
            raise typer.Exit()
            
    # --- Concurrent Execution Logic (The New Engine) ---
    console.print(f"\n[bold blue]Starting parallel upgrade with {workers} workers...[/bold blue]")
    
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    )

    success_count = 0
    fail_count = 0
    
    with progress:
        upgrade_task = progress.add_task("[green]Upgrading...", total=len(target_packages))
        
        # Create a thread pool with the specified number of workers
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit an upgrade task for each package
            future_to_pkg = {executor.submit(upgrade_package, pkg): pkg for pkg in target_packages}
            
            # Process results as they complete
            for future in as_completed(future_to_pkg):
                pkg_name, latest_version, success = future.result()
                
                if success:
                    progress.console.print(f"  ✅ [green]Successfully upgraded {pkg_name} to {latest_version}[/green]")
                    success_count += 1
                else:
                    progress.console.print(f"  ❌ [red]Failed to upgrade {pkg_name}[/red]")
                    fail_count += 1
                
                # Advance the progress bar for each completed task
                progress.advance(upgrade_task)

    # --- Summary Report (Unchanged) ---
    console.print("\n--- [bold]Upgrade Complete[/bold] ---")
    console.print(f"[green]Successfully upgraded:[/green] {success_count} packages")
    if fail_count > 0:
        console.print(f"[red]Failed to upgrade:[/red] {fail_count} packages")
    console.print("--------------------------")

if __name__ == "__main__":
    app()