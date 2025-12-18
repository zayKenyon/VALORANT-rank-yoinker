#!/usr/bin/env python3
"""
Mock Test Runner for VALORANT Rank Yoinker (macOS Testing)

This script runs the application in mock mode, simulating different game states
and scenarios without requiring VALORANT to be running.

Usage:
    python run_mock_test.py [--state STATE] [--scenario SCENARIO] [--seed SEED]

Arguments:
    --state: Game state to simulate (menus, pregame, ingame) [default: ingame]
    --scenario: Test scenario to use (mixed, high_elo, new_players) [default: mixed]
    --seed: Random seed for reproducible data [default: 42]
    --cycles: Number of refresh cycles to run [default: 3]

Examples:
    python run_mock_test.py --state ingame --scenario mixed
    python run_mock_test.py --state pregame --seed 123
    python run_mock_test.py --state menus --cycles 1

Custom for macOS development - standalone test runner.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def setup_mock_mode():
    """Enable mock mode in configuration."""
    config_path = Path("config.json")

    # Load or create config
    if config_path.exists():
        with open(config_path, "r") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print("Warning: config.json is invalid, creating new one")
                config = {}
    else:
        config = {}

    # Enable mock mode
    config["mock_mode"] = True
    config["cooldown"] = 5  # 5 second refresh for testing

    # Write config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    print(f"✓ Mock mode enabled in config.json")


def run_test(state: str, scenario: str, seed: int, cycles: int):
    """Run the mock test.

    Args:
        state: Game state (menus, pregame, ingame)
        scenario: Test scenario
        seed: Random seed
        cycles: Number of refresh cycles
    """
    print("=" * 60)
    print("VALORANT Rank Yoinker - Mock Test Runner")
    print("=" * 60)
    print(f"Game State: {state.upper()}")
    print(f"Scenario: {scenario}")
    print(f"Random Seed: {seed}")
    print(f"Refresh Cycles: {cycles}")
    print("=" * 60)
    print()

    # Set environment variables for mock system
    os.environ["MOCK_MODE"] = "1"
    os.environ["MOCK_STATE"] = state.upper()
    os.environ["MOCK_SCENARIO"] = scenario
    os.environ["MOCK_SEED"] = str(seed)
    os.environ["MOCK_CYCLES"] = str(cycles)

    # Import and patch the application
    try:
        print("Initializing mock system...")
        import mock_data
        import mock_requests

        # Set seed for reproducible data
        mock_data.MockDataGenerator(seed=seed)

        print("✓ Mock system initialized")
        print()

        # Import main components
        print("Loading application...")

        # We can't easily run the full main.py due to platform dependencies,
        # so we'll simulate the key parts
        simulate_application(state, scenario, seed)

    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Make sure all requirements are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def simulate_application(state: str, scenario: str, seed: int):
    """Simulate the application with mock data.

    Args:
        state: Game state
        scenario: Scenario name
        seed: Random seed
    """
    from mock_data import MockDataGenerator
    from mock_requests import MockRequests
    from colr import color
    from rich.table import Table as RichTable
    from rich.console import Console as RichConsole
    from src.constants import NUMBERTORANKS

    # Initialize mock data generator
    gen = MockDataGenerator(seed=seed)

    # Initialize console with truecolor support
    console = RichConsole(color_system="truecolor")

    # Helper function to convert ANSI color codes to Rich markup
    def ansi_to_console(line):
        """Convert colr ANSI codes to Rich markup."""
        if "\x1b[38;2;" not in line:
            return line
        string_to_return = ""
        strings = line.split("\x1b[38;2;")
        del strings[0]
        for string in strings:
            splits = string.split("m", 1)
            rgb = [int(i) for i in splits[0].split(";")]
            original_strings = splits[1].split("\x1b[0m")
            string_to_return += (
                f"[rgb({rgb[0]},{rgb[1]},{rgb[2]})]{'[/]'.join(original_strings)}"
            )
        return string_to_return

    print(f"\n{'=' * 60}")
    print(f"Simulating {state.upper()} state")
    print(f"{'=' * 60}\n")

    if state.lower() == "ingame":
        # Generate in-game data
        coregame_stats = gen.generate_coregame_stats()

        # Create table
        table = RichTable(title=f"[bold]VALORANT Status: In-Game[/bold]")
        table.title_style = "bold"

        # Add columns
        table.add_column("Agent", justify="center")
        table.add_column("Name", justify="center")
        table.add_column("Rank", justify="center")
        table.add_column("RR", justify="center")
        table.add_column("Peak", justify="center")
        table.add_column("HS%", justify="center")
        table.add_column("W/R", justify="center")
        table.add_column("Level", justify="center")

        # Get players
        players = coregame_stats["Players"]

        # Sort by team and level
        players.sort(key=lambda p: (p["TeamID"], -p["PlayerIdentity"]["AccountLevel"]))

        last_team = None

        for player in players:
            puuid = player["Subject"]

            # Generate data for this player
            if puuid not in gen.player_cache:
                gen.player_cache[puuid] = {
                    "rank": gen.generate_rank_data(),
                    "stats": gen.generate_player_stats(),
                    "agent": player["CharacterID"]
                }

            player_data = gen.player_cache[puuid]
            rank_data = player_data["rank"]
            stats_data = player_data["stats"]

            # Generate name
            name_data = gen.generate_player_name()

            # Add separator between teams
            if last_team and last_team != player["TeamID"]:
                table.add_row("", "", "", "", "", "", "", "")

            last_team = player["TeamID"]

            # Determine colors using colr
            if player["TeamID"] == "Blue":
                name_colored = color(f"{name_data['GameName']}#{name_data['TagLine']}", fore=(154, 222, 255))
            else:
                name_colored = color(f"{name_data['GameName']}#{name_data['TagLine']}", fore=(221, 68, 68))

            # Add player row
            agent_name = "Unknown"  # Simplified for demo

            # Get proper rank names with colors from NUMBERTORANKS
            rank_tier = rank_data["rank"]
            rank_tier = max(0, min(27, rank_tier))  # Clamp to valid range
            rank_name_colored = NUMBERTORANKS[rank_tier]

            peak_rank_tier = rank_data["peakrank"]
            peak_rank_tier = max(0, min(27, peak_rank_tier))
            peak_rank_colored = NUMBERTORANKS[peak_rank_tier]

            table.add_row(
                agent_name,
                ansi_to_console(name_colored),
                ansi_to_console(rank_name_colored),
                str(rank_data["rr"]),
                ansi_to_console(peak_rank_colored),
                f"{stats_data['hs']}%",
                f"{rank_data['wr']}% ({rank_data['numberofgames']})",
                str(player["PlayerIdentity"]["AccountLevel"])
            )

        # Display table
        console.print(table)

        # Show match info
        print(f"\nMatch ID: {coregame_stats['MatchID']}")
        print(f"Map: {coregame_stats['MapID'].split('/')[-1]}")
        print(f"Server: {coregame_stats.get('GamePodID', 'N/A')}")
        print(f"Players: {len(players)}")

    elif state.lower() == "pregame":
        # Generate pregame data
        pregame_stats = gen.generate_pregame_stats()

        # Create table
        table = RichTable(title="[bold]VALORANT Status: Agent Select[/bold]")

        # Add columns
        table.add_column("Agent", justify="center")
        table.add_column("Name", justify="center")
        table.add_column("Rank", justify="center")
        table.add_column("Peak", justify="center")
        table.add_column("Level", justify="center")
        table.add_column("Status", justify="center")

        players = pregame_stats["AllyTeam"]["Players"]

        for player in players:
            puuid = player["Subject"]

            # Generate data
            if puuid not in gen.player_cache:
                gen.player_cache[puuid] = {
                    "rank": gen.generate_rank_data(),
                    "stats": gen.generate_player_stats(),
                    "agent": player["CharacterID"]
                }

            player_data = gen.player_cache[puuid]
            rank_data = player_data["rank"]

            name_data = gen.generate_player_name()

            # Color player name
            name_colored = color(f"{name_data['GameName']}#{name_data['TagLine']}", fore=(154, 222, 255))

            # Get proper rank names with colors
            rank_tier = max(0, min(27, rank_data["rank"]))
            rank_name_colored = NUMBERTORANKS[rank_tier]

            peak_rank_tier = max(0, min(27, rank_data["peakrank"]))
            peak_rank_colored = NUMBERTORANKS[peak_rank_tier]

            # Selection status with colors
            status_text = player.get("CharacterSelectionState", "")
            if status_text == "locked":
                status_colored = color("Locked", fore=(24, 148, 82))  # Green
            elif status_text == "selected":
                status_colored = color("Selected", fore=(197, 186, 63))  # Yellow
            else:
                status_colored = color("Not Selected", fore=(221, 68, 68))  # Red

            table.add_row(
                "Unknown",
                ansi_to_console(name_colored),
                ansi_to_console(rank_name_colored),
                ansi_to_console(peak_rank_colored),
                str(player["PlayerIdentity"]["AccountLevel"]),
                ansi_to_console(status_colored)
            )

        console.print(table)

        print(f"\nMatch ID: {pregame_stats['ID']}")
        print(f"Map: {pregame_stats['MapID'].split('/')[-1]}")
        print(f"Queue: {pregame_stats.get('QueueID', 'competitive')}")

    elif state.lower() == "menus":
        # Generate menu state
        print("Simulating lobby/menu state...")
        print()

        presence_data = gen.generate_presence_data("MENUS")

        print(f"Party Size: {presence_data[0].get('partySize', 1)}")
        print(f"Queue: {presence_data[0].get('queueId', 'competitive')}")
        print(f"Account Level: {presence_data[0].get('accountLevel', 100)}")

        print("\n[Status: In Lobby - Waiting for queue]")

    print(f"\n{'=' * 60}")
    print("Mock test complete!")
    print(f"{'=' * 60}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Mock test runner for VALORANT Rank Yoinker"
    )

    parser.add_argument(
        "--state",
        choices=["menus", "pregame", "ingame"],
        default="ingame",
        help="Game state to simulate (default: ingame)"
    )

    parser.add_argument(
        "--scenario",
        choices=["mixed", "high_elo", "new_players", "random"],
        default="mixed",
        help="Test scenario (default: mixed)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible data (default: 42)"
    )

    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of refresh cycles (default: 1)"
    )

    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only setup mock mode in config, don't run test"
    )

    args = parser.parse_args()

    # Setup mock mode
    setup_mock_mode()

    if args.setup_only:
        print("Mock mode setup complete. Run 'python main.py' to start.")
        return

    # Run test
    run_test(args.state, args.scenario, args.seed, args.cycles)


if __name__ == "__main__":
    main()
