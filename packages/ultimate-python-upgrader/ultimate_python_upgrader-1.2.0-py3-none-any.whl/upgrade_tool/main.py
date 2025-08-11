import subprocess
import sys
import re
from typing import List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import get_outdated_packages, generate_packages_table

console = Console()

app = typer.Typer(
    name="py-upgrade",
    help="An intelligent, feature-rich CLI tool to manage and upgrade Python packages.",
    add_completion=False,
)

def check_for_conflicts(packages_to_check: List[str]) -> Optional[str]:
    """
    Performs a dry-run upgrade to detect dependency conflicts.

    Args:
        packages_to_check: A list of package names to be upgraded.

    Returns:
        A formatted string of conflict messages, or None if no conflicts are found.
    """
    console.print("\n[bold cyan]Checking for potential dependency conflicts...[/bold cyan]")
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--dry-run",
        "--upgrade",
    ] + packages_to_check

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
    )
    _, stderr = process.communicate()

    # Find the specific dependency conflict block in pip's output
    conflict_match = re.search(
        r"ERROR: pip's dependency resolver does not currently take into account all the packages that are installed\. This behaviour is the source of the following dependency conflicts\.(.+)",
        stderr,
        re.DOTALL,
    )

    if conflict_match:
        conflict_text = conflict_match.group(1).strip()
        return conflict_text
    return None

def upgrade_package(pkg: dict) -> Tuple[str, str, bool]:
    """
    Worker function to upgrade a single package in a separate thread.
    """
    pkg_name = pkg['name']
    latest_version = pkg['latest_version']
    try:
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
    ),
):
    """
    Checks for and concurrently upgrades outdated Python packages with dependency analysis.
    """
    outdated_packages = get_outdated_packages()
    
    if not outdated_packages:
        console.print("[bold green]✨ All packages are up to date! ✨[/bold green]")
        raise typer.Exit()

    # --- Filtering Logic ---
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

    table = generate_packages_table(target_packages, title="Outdated Python Packages")
    console.print(table)

    if dry_run:
        console.print(f"\n[bold yellow]--dry-run enabled. Would simulate upgrade of {len(target_packages)} packages.[/bold yellow]")
        raise typer.Exit()
        
    # --- Intelligent Dependency Analysis ---
    package_names = [pkg['name'] for pkg in target_packages]
    conflicts = check_for_conflicts(package_names)

    if conflicts:
        console.print(
            Panel.fit(
                f"[bold]The following dependency conflicts were found:[/bold]\n\n{conflicts}",
                title="[bold yellow]⚠️  Dependency Warning[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
    else:
        console.print("[bold green]✅ No dependency conflicts detected.[/bold green]")

    # --- Confirmation ---
    if not yes:
        prompt_message = "\nProceed with the upgrade?"
        if conflicts:
            prompt_message = "\nConflicts were detected. Do you still wish to proceed with the upgrade?"
        
        try:
            confirmed = typer.confirm(prompt_message)
            if not confirmed:
                console.print("Upgrade cancelled by user.")
                raise typer.Exit()
        except typer.Abort:
            console.print("\nUpgrade cancelled by user.")
            raise typer.Exit()
            
    # --- Concurrent Execution Logic ---
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
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_pkg = {executor.submit(upgrade_package, pkg): pkg for pkg in target_packages}
            
            for future in as_completed(future_to_pkg):
                pkg_name, latest_version, success = future.result()
                
                if success:
                    progress.console.print(f"  ✅ [green]Successfully upgraded {pkg_name} to {latest_version}[/green]")
                    success_count += 1
                else:
                    progress.console.print(f"  ❌ [red]Failed to upgrade {pkg_name}[/red]")
                    fail_count += 1
                
                progress.advance(upgrade_task)

    # --- Summary Report ---
    console.print("\n--- [bold]Upgrade Complete[/bold] ---")
    console.print(f"[green]Successfully upgraded:[/green] {success_count} packages")
    if fail_count > 0:
        console.print(f"[red]Failed to upgrade:[/red] {fail_count} packages")
    console.print("--------------------------")

if __name__ == "__main__":
    app()