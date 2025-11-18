"""
Shared UI helpers and constants for Garmin2ShotPattern.
Contains common styling, table creation utilities, and display functions.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# UI Style Constants
TABLE_HEADER_STYLE = "bold magenta"
BORDER_STYLE_CYAN = "cyan"
COLOR_SUCCESS = "green"
COLOR_WARNING = "yellow"
COLOR_ERROR = "red"
COLOR_INFO = "cyan"
COLOR_DIM = "dim"


def create_header_panel(title: str, subtitle: str, border_style: str = BORDER_STYLE_CYAN) -> Panel:
    """
    Create a consistent header panel.

    Args:
        title: The main title text
        subtitle: The subtitle/description text
        border_style: The border style (default: cyan)

    Returns:
        Panel: A Rich Panel object with formatted header
    """
    return Panel.fit(
        f"[bold {border_style}]{title}[/bold {border_style}]\n{subtitle}",
        border_style=border_style
    )


def create_item_table(title: str, items: list, item_name: str = "Item") -> Table:
    """
    Create a numbered table for displaying items.

    Args:
        title: Table title
        items: List of items to display
        item_name: Column name for items (default: "Item")

    Returns:
        Table: A Rich Table object with numbered items
    """
    table = Table(title=title, show_header=True, header_style=TABLE_HEADER_STYLE)
    table.add_column("#", style=COLOR_DIM, width=4)
    table.add_column(item_name, style=COLOR_INFO)

    for idx, item in enumerate(items, 1):
        table.add_row(str(idx), str(item))

    return table


def create_mapping_table(mappings: dict, col1_name: str = "From", col2_name: str = "To") -> Table:
    """
    Create a table showing key-value mappings with an arrow.

    Args:
        mappings: Dictionary of key-value pairs to display
        col1_name: Name for first column (default: "From")
        col2_name: Name for second column (default: "To")

    Returns:
        Table: A Rich Table object showing the mappings
    """
    table = Table(show_header=True, header_style=TABLE_HEADER_STYLE)
    table.add_column(col1_name, style=COLOR_WARNING)
    table.add_column("→", style=COLOR_DIM)
    table.add_column(col2_name, style=COLOR_INFO)

    for key, value in mappings.items():
        table.add_row(key, "→", str(value))

    return table


def create_stats_table(title: str, headers: list) -> Table:
    """
    Create a statistics table with predefined styling.

    Args:
        title: Table title
        headers: List of tuples (column_name, style, justify)
                 e.g., [("Club", "cyan", "left"), ("Shots", "blue", "right")]

    Returns:
        Table: A Rich Table object configured with the specified headers
    """
    table = Table(title=title, show_header=True, header_style=TABLE_HEADER_STYLE)

    for header in headers:
        name = header[0]
        style = header[1] if len(header) > 1 else None
        justify = header[2] if len(header) > 2 else "left"
        table.add_column(name, style=style, justify=justify)

    return table


def print_app_header(console: Console, subtitle: str = "") -> None:
    """
    Display a fancy ASCII art application header.

    Args:
        console: Rich Console instance for printing
        subtitle: Optional subtitle text to display below the header
    """
    console.print()
    console.print("  [bold red]  ___                _       [/bold red] [bold yellow]___[/bold yellow]   [bold green] ___ _        _              _   _                [/bold green]")
    console.print("  [bold red] / __|__ _ _ _ _ __ (_)_ _  [/bold red] [bold yellow]|_  )[/bold yellow]  [bold green]/ __| |_  ___| |_ _ __  __ _| |_| |_ ___ _ _ _ _  [/bold green]")
    console.print("  [bold red]| (_ / _` | '_| '  \\| | ' \\ [/bold red]  [bold yellow]/ /[/bold yellow]   [bold green]\\__ \\ ' \\/ _ \\  _| '_ \\/ _` |  _|  _/ -_) '_| ' \\ [/bold green]")
    console.print("  [bold red] \\___\\__,_|_| |_|_|_|_|_||_|[/bold red] [bold yellow]/___| [/bold yellow][bold green] |___/_||_\\___/\\__| .__/\\__,_|\\__|\\__\\___|_| |_||_|[/bold green]")
    console.print("                                                     [bold green]|_|[/bold green]                              ")
    console.print()
    console.print("               [dim]Transform Garmin Golf Data to ShotPattern[/dim]".center(90))
    console.print()

    if subtitle:
        console.print(f"[bold yellow]{subtitle.center(90)}[/bold yellow]")
        console.print()



