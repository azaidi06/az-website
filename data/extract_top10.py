#!/usr/bin/env python3
"""Extract all data for top 10 ATP and WTA players."""

import csv
import os
from pathlib import Path

# Top 10 player IDs (as of Dec 30, 2024)
ATP_TOP_10 = [206173, 100644, 207989, 126203, 106421, 134770, 104925, 126094, 200282, 105777]
WTA_TOP_10 = [214544, 216347, 221103, 211148, 221012, 214981, 202468, 215613, 214082, 206252]

DATA_DIR = Path(__file__).parent
OUTPUT_DIR = DATA_DIR / "top10"
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_players(tour: str, player_ids: list[int]) -> list[dict]:
    """Extract player info for given IDs."""
    players = []
    player_file = DATA_DIR / f"tennis_{tour}" / f"{tour}_players.csv"

    with open(player_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['player_id']) in player_ids:
                players.append(row)
    return players


def extract_rankings(tour: str, player_ids: list[int]) -> list[dict]:
    """Extract all rankings history for given player IDs."""
    rankings = []
    rankings_dir = DATA_DIR / f"tennis_{tour}"

    # Get all ranking files
    ranking_files = sorted(rankings_dir.glob(f"{tour}_rankings*.csv"))

    for rf in ranking_files:
        with open(rf, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['player']) in player_ids:
                    rankings.append(row)
    return rankings


def extract_matches(tour: str, player_ids: list[int]) -> list[dict]:
    """Extract all matches where any of the players participated."""
    matches = []
    matches_dir = DATA_DIR / f"tennis_{tour}"

    # Get all match files
    match_files = sorted(matches_dir.glob(f"{tour}_matches_*.csv"))

    for mf in match_files:
        with open(mf, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                winner_id = int(row.get('winner_id', 0) or 0)
                loser_id = int(row.get('loser_id', 0) or 0)
                if winner_id in player_ids or loser_id in player_ids:
                    matches.append(row)
    return matches


def write_csv(data: list[dict], output_path: Path):
    """Write list of dicts to CSV."""
    if not data:
        print(f"  No data to write for {output_path}")
        return

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"  Wrote {len(data)} rows to {output_path.name}")


def main():
    for tour, player_ids in [('atp', ATP_TOP_10), ('wta', WTA_TOP_10)]:
        print(f"\n{'='*50}")
        print(f"Processing {tour.upper()} Top 10")
        print('='*50)

        tour_dir = OUTPUT_DIR / tour
        tour_dir.mkdir(exist_ok=True)

        # Extract player info
        print("\nExtracting player info...")
        players = extract_players(tour, player_ids)
        write_csv(players, tour_dir / f"{tour}_top10_players.csv")

        # Extract rankings history
        print("\nExtracting rankings history...")
        rankings = extract_rankings(tour, player_ids)
        write_csv(rankings, tour_dir / f"{tour}_top10_rankings.csv")

        # Extract match history
        print("\nExtracting match history...")
        matches = extract_matches(tour, player_ids)
        write_csv(matches, tour_dir / f"{tour}_top10_matches.csv")

        print(f"\n{tour.upper()} extraction complete!")


if __name__ == "__main__":
    main()
