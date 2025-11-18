#!/usr/bin/env python3
"""
Setup wizard for configuring club mappings and column mappings.
This creates a user-specific configuration file by parsing Garmin data.
"""

from pathlib import Path
from typing import Optional, Dict, List, Tuple
import json

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from InquirerPy import inquirer

from ui_helpers import create_item_table, TABLE_HEADER_STYLE

console = Console()


def load_existing_config() -> Optional[Dict]:
    """
    Load existing configuration if it exists.

    Returns:
        Optional[Dict]: Configuration dictionary if found, None otherwise
    """
    config_file = Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                console.print("[green]✓[/green] Found existing configuration")
                return config
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load existing config: {e}[/yellow]")
    return None


def configure_units(existing_config: Optional[Dict] = None) -> Dict[str, str]:
    """
    Configure distance and deviation units.

    Args:
        existing_config: Optional existing configuration to use as defaults

    Returns:
        Dict[str, str]: Dictionary with 'distance' and 'deviation' unit settings
    """
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Garmin2ShotPattern - Setup Wizard[/bold cyan]\n"
        "Configure club mappings and column settings",
        border_style="cyan"
    ))
    console.print()

    console.print("[bold]Step 1: Configure Units[/bold]")
    console.print("Select the units for distances and deviations (for display purposes).")

    # Get defaults from existing config
    default_distance = "meters"
    default_deviation = "meters"
    if existing_config and "units" in existing_config:
        default_distance = existing_config["units"].get("distance", "meters")
        default_deviation = existing_config["units"].get("deviation", "meters")
        console.print(f"[dim]Current: {default_distance} (distance), {default_deviation} (deviation)[/dim]")

    console.print()

    # Distance unit
    distance_unit = inquirer.select(
        message="Distance unit:",
        choices=[
            {"name": "Meters", "value": "meters"},
            {"name": "Yards", "value": "yards"}
        ],
        default=default_distance
    ).execute()

    console.print()

    # Deviation unit
    deviation_unit = inquirer.select(
        message="Deviation unit:",
        choices=[
            {"name": "Meters", "value": "meters"},
            {"name": "Feet", "value": "feet"},
            {"name": "Yards", "value": "yards"}
        ],
        default=default_deviation
    ).execute()

    console.print()
    console.print(f"[green]✓[/green] Units configured: {distance_unit} (distance), {deviation_unit} (deviation)")

    return {
        "distance": distance_unit,
        "deviation": deviation_unit
    }


def get_garmin_files() -> list[Path]:
    """
    Get all Garmin CSV files from data/garmin directory.

    Returns:
        list[Path]: List of Path objects for CSV files found
    """
    garmin_path = Path("data/garmin")
    if not garmin_path.exists():
        console.print("[red]Error: data/garmin directory not found![/red]")
        console.print("[yellow]Please create the directory and add some Garmin CSV files.[/yellow]")
        return []

    files = sorted(garmin_path.glob("*.csv"))
    return files


def select_sample_file(step_number: int = 2) -> Optional[Path]:
    """
    Select a sample Garmin file for configuration.

    Args:
        step_number: The step number to display (default: 2)

    Returns:
        Optional[Path]: Selected file path, or None if no files available
    """
    files = get_garmin_files()

    if not files:
        console.print("[yellow]No Garmin CSV files found in data/garmin/[/yellow]")
        console.print("[yellow]Please add at least one Garmin CSV file to continue.[/yellow]")
        return None

    console.print()
    console.print(f"[bold]Step {step_number}: Select a sample Garmin file[/bold]")
    console.print("This file will be used to detect your clubs and columns.")
    console.print()

    # Create choices for InquirerPy
    choices = []
    for file in files:
        size = file.stat().st_size
        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
        choices.append({
            "name": f"{file.name} ({size_str})",
            "value": file
        })

    selected_file = inquirer.select(
        message="Select a sample file:",
        choices=choices,
        default=files[0]
    ).execute()

    return selected_file


def detect_columns(file_path: Path) -> list[str]:
    """
    Detect all columns in the Garmin CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        list[str]: List of column names found in the file
    """
    try:
        df = pd.read_csv(file_path, skiprows=[1], nrows=5)
        return list(df.columns)
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return []


def select_column_mapping(
    columns: list[str],
    template_col: str,
    description: str,
    existing_value: Optional[str],
    fallback_index: int
) -> str:
    """
    Helper to select a column mapping with defaults.

    Args:
        columns: List of available column names
        template_col: Template column name being mapped
        description: Human-readable description of the column
        existing_value: Previously configured value (if any)
        fallback_index: Index to use as default if existing_value not found

    Returns:
        str: Selected column name
    """
    choices = [{"name": col, "value": col} for col in columns]

    # Determine default value
    if existing_value in columns:
        default = existing_value
    elif len(columns) > fallback_index:
        default = columns[fallback_index]
    else:
        default = None

    console.print(f"[bold yellow]Select the column containing {description}:[/bold yellow]")
    selected = inquirer.select(
        message=f"{template_col} column:",
        choices=choices,
        default=default
    ).execute()
    console.print()
    return selected


def configure_columns(
    existing_config: Optional[Dict] = None,
    step_number: int = 3
) -> tuple[Optional[Path], Optional[Dict[str, str]]]:
    """
    Configure which Garmin columns map to template columns.

    Args:
        existing_config: Optional existing configuration to use as defaults
        step_number: The step number to display (default: 3)

    Returns:
        tuple[Optional[Path], Optional[Dict[str, str]]]:
            - File path used for detection
            - Dictionary mapping template columns to Garmin columns
            Returns (None, None) if configuration fails
    """
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Step {step_number}: Column Mapping[/bold cyan]\n"
        "Map Garmin columns to ShotPattern template columns",
        border_style="cyan"
    ))
    console.print()

    file_path = select_sample_file(step_number)
    if not file_path:
        return None, None

    console.print()
    console.print(f"[cyan]Analyzing file:[/cyan] {file_path.name}")

    columns = detect_columns(file_path)
    if not columns:
        return None, None

    console.print(f"[green]✓[/green] Found {len(columns)} columns")
    console.print()

    # Display detected columns
    console.print(create_item_table("📋 Detected Columns", columns, "Column Name"))
    console.print()

    # Get defaults from existing config
    existing_columns = {}
    if existing_config and "column_mapping" in existing_config:
        existing_columns = existing_config["column_mapping"]
        console.print("[dim]Using existing column mappings as defaults[/dim]")
        console.print()

    # Map required columns using helper function
    column_mapping = {
        "Club": select_column_mapping(columns, "Club", "club names", existing_columns.get("Club"), 0),
        "Total": select_column_mapping(columns, "Total", "total distance", existing_columns.get("Total"), 1),
        "Side": select_column_mapping(columns, "Side", "side deviation", existing_columns.get("Side"), 2)
    }

    console.print("[green]✓[/green] Column mapping configured")
    console.print()

    return file_path, column_mapping


def detect_clubs(file_path: Path, club_column: str) -> list[str]:
    """
    Detect all unique clubs in the Garmin file.

    Args:
        file_path: Path to the CSV file
        club_column: Name of the column containing club names

    Returns:
        list[str]: Sorted list of unique club names
    """
    try:
        df = pd.read_csv(file_path, skiprows=[1])
        if club_column not in df.columns:
            console.print(f"[red]Error: Column '{club_column}' not found![/red]")
            return []

        clubs = df[club_column].dropna().unique().tolist()
        return sorted(clubs)
    except Exception as e:
        console.print(f"[red]Error reading clubs: {e}[/red]")
        return []


def get_shotpattern_clubs() -> list[Dict[str, str]]:
    """
    Get list of available ShotPattern club identifiers.

    Returns:
        list[Dict[str, str]]: List of dictionaries with 'name' and 'value' keys
    """
    from enums import ShotPatternClub

    clubs = []
    for club in ShotPatternClub:
        clubs.append({
            "name": f"{club.name}",
            "value": club.value
        })
    return clubs


def configure_club_mappings(
    file_path: Path,
    club_column: str,
    units: Dict[str, str],
    existing_config: Optional[Dict] = None,
    step_number: int = 4
) -> tuple[Dict[str, str], Dict[str, int]]:
    """
    Configure which Garmin clubs map to ShotPattern clubs.

    Args:
        file_path: Path to the CSV file with club data
        club_column: Name of the column containing club names
        units: Dictionary with distance and deviation units
        existing_config: Optional existing configuration to use as defaults
        step_number: The step number to display (default: 4)

    Returns:
        tuple[Dict[str, str], Dict[str, int]]:
            - Dictionary mapping Garmin club names to ShotPattern identifiers
            - Dictionary mapping ShotPattern identifiers to target distances
    """
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Step {step_number}: Club Mapping[/bold cyan]\n"
        "Map your Garmin clubs to ShotPattern identifiers",
        border_style="cyan"
    ))
    console.print()

    console.print(f"[cyan]Detecting clubs in:[/cyan] {file_path.name}")

    garmin_clubs = detect_clubs(file_path, club_column)
    if not garmin_clubs:
        return {}, {}

    console.print(f"[green]✓[/green] Found {len(garmin_clubs)} unique clubs")
    console.print()

    # Display detected clubs
    console.print(create_item_table("⛳ Detected Clubs", garmin_clubs, "Garmin Club Name"))
    console.print()

    # Get existing mappings
    existing_club_mappings = {}
    existing_target_distances = {}
    if existing_config:
        existing_club_mappings = existing_config.get("club_mappings", {})
        existing_target_distances = existing_config.get("target_distances", {})
        if existing_club_mappings:
            console.print("[dim]Using existing club mappings as defaults[/dim]")
            console.print()

    # Get available ShotPattern clubs
    shotpattern_clubs = get_shotpattern_clubs()

    # Map each club
    club_mappings = {}
    target_distances = {}

    console.print("[bold]Map each Garmin club to a ShotPattern identifier:[/bold]")
    console.print("[dim]You can skip clubs that you don't want to include in the analysis.[/dim]")
    console.print()

    for garmin_club in garmin_clubs:
        console.print(f"[bold cyan]{garmin_club}[/bold cyan]")

        # Check if already mapped
        already_mapped = garmin_club in existing_club_mappings
        default_include = already_mapped  # If previously mapped, default to True

        # Ask if user wants to map this club
        should_map = inquirer.confirm(
            message=f"Include '{garmin_club}' in analysis?",
            default=default_include
        ).execute()

        if not should_map:
            console.print("[dim]Skipped[/dim]")
            console.print()
            continue

        # Get default values from existing config
        default_shotpattern = existing_club_mappings.get(garmin_club, None)
        default_distance = 150
        if default_shotpattern and default_shotpattern in existing_target_distances:
            default_distance = int(existing_target_distances[default_shotpattern])

        # Select ShotPattern club
        shotpattern_club = inquirer.select(
            message="Map to ShotPattern club:",
            choices=shotpattern_clubs,
            default=default_shotpattern
        ).execute()

        # Ask for target distance with unit display
        distance_unit_label = units["distance"]
        target_distance = inquirer.number(
            message=f"Default target distance ({distance_unit_label}):",
            default=int(default_distance),
            min_allowed=0,
            max_allowed=500,
            float_allowed=False
        ).execute()

        club_mappings[garmin_club] = shotpattern_club
        target_distances[shotpattern_club] = target_distance

        console.print(f"[green]✓[/green] Mapped to {shotpattern_club} (target: {target_distance} {distance_unit_label})")
        console.print()

    return club_mappings, target_distances

def save_configuration(
    units: Dict[str, str],
    column_mapping: Dict[str, str],
    club_mappings: Dict[str, str],
    target_distances: Dict[str, int]
) -> Path:
    """
    Save the configuration to a JSON file.

    Args:
        units: Dictionary with distance and deviation units
        column_mapping: Dictionary mapping template columns to Garmin columns
        club_mappings: Dictionary mapping Garmin clubs to ShotPattern identifiers
        target_distances: Dictionary mapping ShotPattern clubs to target distances

    Returns:
        Path: Path to the saved configuration file
    """
    config = {
        "units": units,
        "column_mapping": column_mapping,
        "club_mappings": club_mappings,
        "target_distances": target_distances
    }

    config_file = Path("config.json")

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    console.print()
    console.print("[green]✅ Configuration saved successfully![/green]")
    console.print(f"[cyan]Configuration file:[/cyan] {config_file}")
    console.print()

    return config_file


def display_summary(
    units: Dict[str, str],
    column_mapping: Dict[str, str],
    club_mappings: Dict[str, str],
    target_distances: Dict[str, int]
) -> None:
    """
    Display a summary of the configuration.

    Args:
        units: Dictionary with distance and deviation units
        column_mapping: Dictionary mapping template columns to Garmin columns
        club_mappings: Dictionary mapping Garmin clubs to ShotPattern identifiers
        target_distances: Dictionary mapping ShotPattern clubs to target distances
    """
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Configuration Summary[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # Units summary
    console.print("[bold]Units:[/bold]")
    units_table = Table(show_header=True, header_style=TABLE_HEADER_STYLE)
    units_table.add_column("Measurement", style="yellow")
    units_table.add_column("Unit", style="cyan")

    units_table.add_row("Distance", units["distance"])
    units_table.add_row("Deviation", units["deviation"])

    console.print(units_table)
    console.print()

    # Column mapping summary
    console.print("[bold]Column Mappings:[/bold]")
    col_table = Table(show_header=True, header_style=TABLE_HEADER_STYLE)
    col_table.add_column("Template Column", style="yellow")
    col_table.add_column("→", style="dim")
    col_table.add_column("Garmin Column", style="cyan")

    for key, value in column_mapping.items():
        col_table.add_row(key, "→", value)

    console.print(col_table)
    console.print()

    # Club mapping summary
    distance_unit_label = units["distance"]
    console.print("[bold]Club Mappings:[/bold]")
    club_table = Table(show_header=True, header_style=TABLE_HEADER_STYLE)
    club_table.add_column("Garmin Club", style="cyan")
    club_table.add_column("→", style="dim")
    club_table.add_column("ShotPattern Club", style="yellow")
    club_table.add_column("Target Distance", style="green", justify="right")

    for garmin_club, shotpattern_club in club_mappings.items():
        target = target_distances.get(shotpattern_club, 0)
        club_table.add_row(garmin_club, "→", shotpattern_club, f"{target} {distance_unit_label}")

    console.print(club_table)
    console.print()


def main() -> None:
    """Run the setup wizard."""
    try:
        # Load existing configuration if available
        existing_config = load_existing_config()

        # Step 1: Configure units
        units = configure_units(existing_config)

        # Step 2 & 3: Configure columns
        file_path, column_mapping = configure_columns(existing_config, step_number=3)
        if not file_path or not column_mapping:
            console.print("[red]Setup cancelled - could not configure columns[/red]")
            return

        # Step 4: Configure club mappings
        club_mappings, target_distances = configure_club_mappings(
            file_path,
            column_mapping["Club"],
            units,
            existing_config,
            step_number=4
        )
        if not club_mappings:
            console.print("[yellow]No clubs mapped - setup incomplete[/yellow]")
            return

        # Display summary
        display_summary(units, column_mapping, club_mappings, target_distances)

        # Save configuration
        save_configuration(units, column_mapping, club_mappings, target_distances)

        console.print("[bold green]✅ Setup complete![/bold green]")
        console.print()
        console.print("[cyan]Next steps:[/cyan]")
        console.print("  1. Review config.json to verify your settings")
        console.print("  2. Run the transformer: make run")
        console.print()

    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Setup cancelled by user[/yellow]")
    except Exception as e:
        console.print()
        console.print(f"[red]Error during setup: {e}[/red]")


if __name__ == "__main__":
    main()
