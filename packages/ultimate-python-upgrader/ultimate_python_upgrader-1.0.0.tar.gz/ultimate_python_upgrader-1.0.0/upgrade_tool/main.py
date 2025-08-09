import subprocess
import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

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
):
    """
    Checks for and upgrades outdated Python packages.
    """
    # Use the utility function to get outdated packages
    outdated_packages = get_outdated_packages()
    
    if not outdated_packages:
        console.print("[bold green]✨ All packages are up to date! ✨[/bold green]")
        raise typer.Exit()

    # --- Filtering Logic ---
    if packages_to_upgrade:
        # User specified which packages to upgrade
        name_to_pkg = {pkg['name'].lower(): pkg for pkg in outdated_packages}
        target_packages = [name_to_pkg[name.lower()] for name in packages_to_upgrade if name.lower() in name_to_pkg]
    else:
        # Default to all outdated packages
        target_packages = outdated_packages

    if exclude:
        # Exclude packages specified by the user (case-insensitive)
        exclude_set = {name.lower() for name in exclude}
        target_packages = [pkg for pkg in target_packages if pkg['name'].lower() not in exclude_set]

    if not target_packages:
        console.print("[bold yellow]No packages match the specified criteria for upgrade.[/bold yellow]")
        raise typer.Exit()

    # --- Display and Confirmation ---
    # Use the utility function to generate the table
    table = generate_packages_table(target_packages, title="Outdated Python Packages")
    console.print(table)

    if dry_run:
        console.print("\n[bold yellow]--dry-run enabled. No packages will be upgraded.[/bold yellow]")
        raise typer.Exit()

    if not yes:
        # Use Typer's confirmation prompt
        try:
            confirmed = typer.confirm("\nProceed with the upgrade?")
            if not confirmed:
                console.print("Upgrade cancelled by user.")
                raise typer.Exit()
        except typer.Abort:
            console.print("\nUpgrade cancelled by user.")
            raise typer.Exit()
            
    # --- Execution Logic ---
    console.print("\n[bold blue]Starting upgrade process...[/bold blue]")
    
    # Define a rich Progress bar
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )

    with progress:
        upgrade_task = progress.add_task("[green]Upgrading...", total=len(target_packages))
        success_count = 0
        fail_count = 0
        
        for pkg in target_packages:
            pkg_name = pkg['name']
            progress.update(upgrade_task, description=f"Upgrading [bold cyan]{pkg_name}[/bold cyan]...")
            
            try:
                # Execute the pip upgrade command
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--upgrade", pkg_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                progress.console.print(f"  ✅ [green]Successfully upgraded {pkg_name} to {pkg['latest_version']}[/green]")
                success_count += 1
            except subprocess.CalledProcessError:
                progress.console.print(f"  ❌ [red]Failed to upgrade {pkg_name}[/red]")
                fail_count += 1
            
            progress.advance(upgrade_task)

    # --- Summary Report ---
    console.print("\n--- [bold]Upgrade Complete[/bold] ---")
    console.print(f"[green]Successfully upgraded:[/green] {success_count} packages")
    if fail_count > 0:
        console.print(f"[red]Failed to upgrade:[/red] {fail_count} packages")
    console.print("--------------------------")


# This makes the script runnable directly, though it's meant to be installed via the entry point
if __name__ == "__main__":
    app()