#!/usr/bin/env python3
"""
CLI tool for transforming Garmin shot data to ShotPattern format.
"""

from pathlib import Path
from typing import Optional, Dict, Tuple
import json
import sys

import click
import pandas as pd
from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer

from ui_helpers import create_header_panel, TABLE_HEADER_STYLE

console = Console()


def get_base_path() -> Path:
    """
    Get the base path for the application, handling both dev and bundled modes.

    Returns:
        Path: Base path for the application directory
    """
    return Path.cwd()


def create_club_stats_table(
    title: str,
    output_df: pd.DataFrame,
    distance_unit: str,
    deviation_unit: str
) -> Table:
    """
    Create a statistics table for clubs with consistent formatting.

    Args:
        title: Table title
        output_df: DataFrame containing shot data
        distance_unit: Unit for distance measurements (e.g., "meters", "yards")
        deviation_unit: Unit for deviation measurements (e.g., "meters", "feet")

    Returns:
        Table: A Rich Table object with club statistics
    """
    stats_table = Table(
        title=title,
        show_header=True,
        header_style=TABLE_HEADER_STYLE
    )
    stats_table.add_column("Club", style="cyan")
    stats_table.add_column("Type", style="yellow")
    stats_table.add_column("Target", justify="right", style="green")
    stats_table.add_column("Shots", justify="right", style="blue")
    stats_table.add_column("Avg Total", justify="right", style="magenta")
    stats_table.add_column("Min Total", justify="right", style="dim")
    stats_table.add_column("Max Total", justify="right", style="dim")
    stats_table.add_column("Avg Side", justify="right", style="magenta")
    stats_table.add_column("Min Side", justify="right", style="dim")
    stats_table.add_column("Max Side", justify="right", style="dim")

    for club in output_df["Club"].unique():
        club_data = output_df[output_df["Club"] == club]
        stats_table.add_row(
            club,
            club_data["Type"].iloc[0],
            f"{club_data['Target'].iloc[0]} {distance_unit}",
            str(len(club_data)),
            f"{club_data['Total'].mean():.1f} {distance_unit}",
            f"{club_data['Total'].min():.1f} {distance_unit}",
            f"{club_data['Total'].max():.1f} {distance_unit}",
            f"{club_data['Side'].mean():.1f} {deviation_unit}",
            f"{club_data['Side'].min():.1f} {deviation_unit}",
            f"{club_data['Side'].max():.1f} {deviation_unit}"
        )

    return stats_table


def load_config() -> Optional[Dict]:
    """
    Load user configuration from config.json.

    Returns:
        Optional[Dict]: Configuration dictionary if successful, None otherwise
    """
    base_path = get_base_path()
    config_file = base_path / "config.json"
    if not config_file.exists():
        console.print("[red]Error: config.json not found![/red]")
        console.print(f"[yellow]Looking in: {config_file}[/yellow]")
        console.print("[yellow]Please run 'make configure' first to set up your configuration.[/yellow]")
        return None

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        console.print(f"[red]Error loading config.json: {e}[/red]")
        return None


def get_garmin_files() -> list[Path]:
    """
    Get all Garmin CSV files from data/garmin directory.

    Returns:
        list[Path]: List of Path objects for CSV files found
    """
    base_path = get_base_path()
    garmin_path = base_path / "data" / "garmin"
    if not garmin_path.exists():
        console.print("[red]Error: data/garmin directory not found![/red]")
        console.print(f"[yellow]Looking in: {garmin_path}[/yellow]")
        return []

    files = sorted(garmin_path.glob("*.csv"))
    return files


def select_file() -> Optional[Path]:
    """
    Display file selection menu and return selected file.

    Returns:
        Optional[Path]: Selected file path, or None if no files available
    """
    files = get_garmin_files()

    if not files:
        console.print("[yellow]No Garmin CSV files found in data/garmin/[/yellow]")
        return None

    # Display header
    console.print()
    console.print(create_header_panel(
        "Garmin2ShotPattern",
        "Transform Garmin shot data to ShotPattern format"
    ))
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

    # Prompt for selection
    selected_file = inquirer.select(
        message="Select a Garmin file to process:",
        choices=choices,
        default=files[0]
    ).execute()

    return selected_file


def load_and_display_clubs(
    file_path: Path,
    config: Dict
) -> tuple[Optional[pd.DataFrame], Optional[pd.Series]]:
    """
    Load the Garmin file and display all clubs present.

    Args:
        file_path: Path to the CSV file
        config: Configuration dictionary with column mappings

    Returns:
        tuple[Optional[pd.DataFrame], Optional[pd.Series]]:
            - DataFrame with shot data
            - Series with club counts
            Returns (None, None) if loading fails
    """
    console.print()
    console.print(f"[cyan]Loading file:[/cyan] {file_path.name}")

    try:
        # Load the file (skip units row)
        df = pd.read_csv(file_path, skiprows=[1])

        console.print(f"[green]✓[/green] Loaded {len(df)} shots")
        console.print()

        # Get club column name from config
        club_column = config["column_mapping"]["Club"]
        if club_column not in df.columns:
            console.print(f"[red]Error: Column '{club_column}' not found in file[/red]")
            return None

        club_counts = df[club_column].value_counts().sort_index()

        # Display clubs table
        table = Table(
            title="⛳ Clubs in this Session",
            show_header=True,
            header_style=TABLE_HEADER_STYLE
        )
        table.add_column("Club Name", style="cyan", no_wrap=True)
        table.add_column("Shots", justify="right", style="yellow")
        table.add_column("Status", justify="center")

        # Check which clubs are mapped in config
        club_mappings = config.get("club_mappings", {})

        for club, count in club_counts.items():
            included = club in club_mappings
            status = "[green]✓ Mapped[/green]" if included else "[dim]- Excluded[/dim]"
            table.add_row(club, str(count), status)

        console.print(table)
        console.print()

        # Summary
        total_clubs = len(club_counts)
        mapped_clubs = sum(1 for club in club_counts.index if club in club_mappings)

        console.print("[bold]Summary:[/bold]")
        console.print(f"  Total clubs: {total_clubs}")
        console.print(f"  Mapped clubs: [green]{mapped_clubs}[/green]")
        console.print(f"  Excluded clubs: [dim]{total_clubs - mapped_clubs}[/dim]")

        return df, club_counts

    except Exception as e:
        console.print(f"[red]Error loading file: {e}[/red]")
        return None, None


def ask_target_distances(
    club_counts: pd.Series,
    config: Dict
) -> Dict[str, int]:
    """
    Ask user to configure target distances for each mapped club.

    Args:
        club_counts: Series with club names and shot counts
        config: Configuration dictionary with mappings and defaults

    Returns:
        Dict[str, int]: Dictionary mapping club names to target distances
    """
    # Get only mapped clubs from config
    club_mappings = config.get("club_mappings", {})
    target_distances_config = config.get("target_distances", {})
    units = config.get("units", {})
    distance_unit = units.get("distance", "meters")

    mapped_clubs = [club for club in club_counts.index if club in club_mappings]

    if not mapped_clubs:
        console.print("[yellow]No mapped clubs to configure[/yellow]")
        return {}

    console.print()
    console.print(create_header_panel(
        "Target Distance Configuration",
        f"Set target distance for each club (in {distance_unit}, default values provided)"
    ))
    console.print()

    target_distances = {}

    for club in mapped_clubs:
        # Get the ShotPattern club ID and default target distance from config
        shotpattern_club = club_mappings[club]
        default_distance = int(target_distances_config.get(shotpattern_club, 150))

        # Ask user for target distance with default
        distance_input = inquirer.number(
            message=f"{club} ({club_counts[club]} shots) - Target distance ({distance_unit}):",
            default=default_distance,
            min_allowed=0,
            max_allowed=500,
            float_allowed=False
        ).execute()

        target_distances[club] = distance_input
        console.print()

    # Display summary
    table = Table(
        title="🎯 Target Distance Summary",
        show_header=True,
        header_style=TABLE_HEADER_STYLE
    )
    table.add_column("Club", style="cyan")
    table.add_column("Shots", justify="right", style="yellow")
    table.add_column("Target Distance", justify="center", style="green")

    for club in mapped_clubs:
        table.add_row(club, str(club_counts[club]), f"{target_distances[club]} {distance_unit}")

    console.print(table)
    console.print()

    return target_distances


def ask_shot_types(
    club_counts: pd.Series,
    config: Dict
) -> Dict[str, str]:
    """
    Ask user to define shot type (tee shot or approach) for each mapped club.

    Args:
        club_counts: Series with club names and shot counts
        config: Configuration dictionary with club mappings

    Returns:
        Dict[str, str]: Dictionary mapping club names to shot types ("Tee" or "Approach")
    """
    # Get only mapped clubs from config
    club_mappings = config.get("club_mappings", {})
    mapped_clubs = [club for club in club_counts.index if club in club_mappings]

    if not mapped_clubs:
        console.print("[yellow]No mapped clubs to configure[/yellow]")
        return {}

    console.print()
    console.print(create_header_panel(
        "Shot Type Configuration",
        "Define whether shots are tee shots or approach shots"
    ))
    console.print()

    shot_types = {}

    for club in mapped_clubs:
        choice = inquirer.select(
            message=f"{club} ({club_counts[club]} shots) - Select shot type:",
            choices=[
                {"name": "🏌️  Tee shot", "value": "Tee"},
                {"name": "🎯 Approach shot", "value": "Approach"}
            ],
            default="Approach"
        ).execute()

        shot_types[club] = choice
        console.print()

    # Display summary
    table = Table(
        title="📋 Shot Type Summary",
        show_header=True,
        header_style=TABLE_HEADER_STYLE
    )
    table.add_column("Club", style="cyan")
    table.add_column("Shots", justify="right", style="yellow")
    table.add_column("Type", justify="center", style="green")

    for club in mapped_clubs:
        table.add_row(club, str(club_counts[club]), shot_types[club])

    console.print(table)
    console.print()

    return shot_types


def review_and_remove_shots(output_df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """
    Allow user to review and remove individual shots from the dataset.

    Args:
        output_df: DataFrame containing shot data

    Returns:
        tuple[pd.DataFrame, bool]:
            - Updated DataFrame (with or without removed shots)
            - Boolean flag indicating if any shots were removed
    """
    console.print()

    # Ask if user wants to review shots
    review = inquirer.confirm(
        message="Would you like to review and remove specific shots?",
        default=False
    ).execute()

    if not review:
        return output_df, False  # Return flag indicating no changes

    console.print()
    console.print(create_header_panel(
        "Shot Review & Removal",
        "Review shots by club and select which ones to remove"
    ))
    console.print()

    shots_to_remove = []

    # Process each club
    for club in sorted(output_df["Club"].unique()):
        club_data = output_df[output_df["Club"] == club].copy()
        club_data = club_data.reset_index(drop=False)  # Keep original index

        console.print(f"\n[bold cyan]{club}[/bold cyan] - {len(club_data)} shots")
        console.print()

        # Display all shots for this club
        shots_table = Table(
            show_header=True,
            header_style=TABLE_HEADER_STYLE,
            title=f"📊 {club} Shots"
        )
        shots_table.add_column("#", style="dim", width=4)
        shots_table.add_column("Type", style="yellow")
        shots_table.add_column("Target", justify="right", style="green")
        shots_table.add_column("Total", justify="right", style="cyan")
        shots_table.add_column("Side", justify="right", style="magenta")

        # Create choices for selection
        choices = []
        for idx, (_, row) in enumerate(club_data.iterrows(), 1):
            # Convert Target to int/float if it's a string
            target_val = row['Target']
            if isinstance(target_val, str):
                try:
                    target_val = float(target_val)
                except (ValueError, TypeError):
                    target_val = 0

            shots_table.add_row(
                str(idx),
                str(row["Type"]),
                f"{target_val:.0f}m",
                f"{float(row['Total']):.2f}m",
                f"{float(row['Side']):.2f}m"
            )
            choices.append({
                "name": f"#{idx:2d}  Total: {float(row['Total']):6.2f}m  Side: {float(row['Side']):6.2f}m",
                "value": row["index"]  # Original DataFrame index
            })

        console.print(shots_table)
        console.print()

        # Ask user to select shots to remove
        if len(club_data) > 0:
            remove = inquirer.confirm(
                message=f"Remove any shots from {club}?",
                default=False
            ).execute()

            if remove:
                selected = inquirer.checkbox(
                    message="Select shots to REMOVE (use Space to select, Enter to confirm):",
                    choices=choices,
                    instruction="(Space: select, Enter: confirm)",
                ).execute()

                if selected:
                    shots_to_remove.extend(selected)
                    console.print(f"[yellow]Marked {len(selected)} shot(s) for removal[/yellow]")
                else:
                    console.print("[green]No shots removed[/green]")
            else:
                console.print("[green]Keeping all shots[/green]")

        console.print()

    # Remove selected shots
    if shots_to_remove:
        original_count = len(output_df)
        output_df = output_df.drop(index=shots_to_remove).reset_index(drop=True)
        console.print()
        console.print(f"[bold green]✓[/bold green] Removed {original_count - len(output_df)} shot(s)")
        console.print(f"[bold]Final dataset:[/bold] {len(output_df)} shots")
        console.print()
        return output_df, True  # Return flag indicating shots were removed
    else:
        console.print("[green]No shots removed - keeping all data[/green]")
        console.print()
        return output_df, False  # Return flag indicating no changes



def transform_and_export(
    df: pd.DataFrame,
    target_distances: Dict[str, int],
    shot_types: Dict[str, str],
    source_file: Path,
    config: Dict
) -> None:
    """
    Transform the data and export to CSV in template format.

    Args:
        df: DataFrame with raw Garmin data
        target_distances: Dictionary mapping club names to target distances
        shot_types: Dictionary mapping club names to shot types
        source_file: Path to the source CSV file
        config: Configuration dictionary with mappings and units
    """
    console.print()
    console.print(create_header_panel(
        "Data Transformation",
        "Mapping Garmin data to ShotPattern format"
    ))
    console.print()

    # Get mappings from config
    club_mappings = config.get("club_mappings", {})
    column_mapping = config.get("column_mapping", {})
    units = config.get("units", {})
    distance_unit = units.get("distance", "meters")
    deviation_unit = units.get("deviation", "meters")

    # Filter to only mapped clubs
    club_col = column_mapping["Club"]
    df_filtered = df[df[club_col].isin(club_mappings.keys())].copy()

    # Map club names to ShotPattern IDs
    df_filtered["Club"] = df_filtered[club_col].map(club_mappings)

    # Add Type column based on user configuration
    df_filtered["Type"] = df_filtered[club_col].map(shot_types)

    # Add Target column based on user configuration
    df_filtered["Target"] = df_filtered[club_col].map(target_distances)

    # Rename distance columns
    df_filtered = df_filtered.rename(columns={
        column_mapping["Total"]: "Total",
        column_mapping["Side"]: "Side"
    })

    # Select and reorder columns to match template
    output_df = df_filtered[["Club", "Type", "Target", "Total", "Side"]].copy()

    # Ensure numeric columns are proper types
    output_df["Target"] = pd.to_numeric(output_df["Target"], errors='coerce')
    output_df["Total"] = pd.to_numeric(output_df["Total"], errors='coerce')
    output_df["Side"] = pd.to_numeric(output_df["Side"], errors='coerce')

    # Round numeric columns to 2 decimal places
    output_df["Total"] = output_df["Total"].round(2)
    output_df["Side"] = output_df["Side"].round(2)

    # Display preview
    console.print(f"[green]✓[/green] Transformed {len(output_df)} shots")
    console.print()

    # Show preview table
    preview_table = Table(
        title="📊 Data Preview (first 10 rows)",
        show_header=True,
        header_style=TABLE_HEADER_STYLE
    )
    for col in output_df.columns:
        preview_table.add_column(col, style="cyan")

    for _, row in output_df.head(10).iterrows():
        preview_table.add_row(*[str(val) for val in row])

    console.print(preview_table)
    console.print()

    # Statistics by club
    console.print(create_club_stats_table("📈 Statistics by Club", output_df, distance_unit, deviation_unit))
    console.print()

    # Review and remove shots if desired
    output_df, shots_removed = review_and_remove_shots(output_df)

    # Recalculate statistics only if shots were actually removed
    if shots_removed and len(output_df) > 0:
        console.print()
        console.print("[bold cyan]Updated Statistics After Review:[/bold cyan]")
        console.print()
        console.print()

        console.print(create_club_stats_table("📈 Final Statistics by Club", output_df, distance_unit, deviation_unit))
        console.print()

    # Ask for export confirmation
    export = inquirer.confirm(
        message="Export to CSV file?",
        default=True
    ).execute()

    if not export:
        console.print("[yellow]Export cancelled[/yellow]")
        return

    # Create output directory
    base_path = get_base_path()
    output_dir = base_path / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_name = source_file.stem
    output_file = output_dir / f"{source_name}_transformed_{timestamp}.csv"

    # Export to CSV
    output_df.to_csv(output_file, index=False)

    console.print()
    console.print("[green]✅ Successfully exported to:[/green]")
    console.print(f"   {output_file}")
    console.print()


@click.command()
def main() -> None:
    """Transform Garmin shot data to ShotPattern format."""
    # Load configuration
    config = load_config()
    if not config:
        return

    # Step 1: Select file
    file_path = select_file()
    if not file_path:
        return

    # Step 2: Load and display clubs
    df, club_counts = load_and_display_clubs(file_path, config)
    if df is None:
        return

    # Step 3: Ask for target distances
    target_distances = ask_target_distances(club_counts, config)
    if not target_distances:
        return

    # Step 4: Ask for shot types
    shot_types = ask_shot_types(club_counts, config)
    if not shot_types:
        return

    # Step 5: Transform and export
    transform_and_export(df, target_distances, shot_types, file_path, config)


if __name__ == "__main__":
    main()
