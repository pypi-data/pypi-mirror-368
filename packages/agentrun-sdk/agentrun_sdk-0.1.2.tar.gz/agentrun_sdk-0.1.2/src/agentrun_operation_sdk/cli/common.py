from typing import NoReturn, Optional
import typer
from rich.console import Console

console = Console()

def _handle_error(message: str, exception: Optional[Exception] = None) -> NoReturn:
    """Handle errors with consistent formatting and exit."""
    console.print(f"[red]❌ {message}[/red]")
    if exception:
        raise typer.Exit(1) from exception
    else:
        raise typer.Exit(1)

def _print_success(message: str) -> None:
    """Print success message with consistent formatting."""
    console.print(f"[green]✓[/green] {message}")

def _handle_warn(message: str) -> None:
    """Handle errors with consistent formatting and exit."""
    console.print(f"⚠️  {message}", new_line_start=True, style="bold yellow underline")