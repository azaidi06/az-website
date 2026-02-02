#!/usr/bin/env python3
"""
Scrape recent tennis match data from Tennis Abstract using Playwright.

Tennis Abstract uses JavaScript-rendered pages, so we need browser automation.
This script fetches match data for Top 25 ATP/WTA players and outputs CSV
compatible with Jeff Sackmann's tennis_atp/tennis_wta format.

Usage:
    pip install playwright pandas
    playwright install chromium
    python scrape_tennisabstract.py
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    exit(1)

import pandas as pd

# Configuration
DATA_DIR = Path(__file__).parent
OUTPUT_DIR = DATA_DIR / "top25"
RATE_LIMIT_SECONDS = 2.0
MIN_YEAR = 2025  # Only scrape matches from this year onwards

# Top 25 players with Tennis Abstract URL names
# Format: (player_id, url_name, full_name)
ATP_TOP_25 = [
    (206173, "JannikSinner", "Jannik Sinner"),
    (100644, "AlexanderZverev", "Alexander Zverev"),
    (207989, "CarlosAlcaraz", "Carlos Alcaraz"),
    (126203, "TaylorFritz", "Taylor Fritz"),
    (106421, "DaniilMedvedev", "Daniil Medvedev"),
    (134770, "AlexDeMinaur", "Alex de Minaur"),
    (104925, "NovakDjokovic", "Novak Djokovic"),
    (126094, "CasperRuud", "Casper Ruud"),
    (200282, "AndreyRublev", "Andrey Rublev"),
    (105777, "GrigorDimitrov", "Grigor Dimitrov"),
    (126774, "TommyPaul", "Tommy Paul"),
    (126205, "FrancesTiafoe", "Frances Tiafoe"),
    (208029, "HolgerRune", "Holger Rune"),
    (200005, "LorenzoMusetti", "Lorenzo Musetti"),
    (207733, "UgoHumbert", "Ugo Humbert"),
    (128034, "JackDraper", "Jack Draper"),
    (207518, "ArthurFils", "Arthur Fils"),
    (126207, "SebastianKorda", "Sebastian Korda"),
    (111575, "KarenKhachanov", "Karen Khachanov"),
    (209950, "AlexMichelsen", "Alex Michelsen"),
    (210097, "GiovanniMpetshiPerricard", "Giovanni Mpetshi Perricard"),
    (200624, "AdrianMannarino", "Adrian Mannarino"),
    (126214, "BenShelton", "Ben Shelton"),
    (200615, "FelixAugerAliassime", "Felix Auger-Aliassime"),
    (207830, "TaroDaniel", "Taro Daniel"),
]

WTA_TOP_25 = [
    (214544, "ArynaSabalenka", "Aryna Sabalenka"),
    (216347, "IgaSwiatek", "Iga Swiatek"),
    (221103, "CocoGauff", "Coco Gauff"),
    (211148, "JasminePaolini", "Jasmine Paolini"),
    (221012, "QinwenZheng", "Qinwen Zheng"),
    (214981, "JessicaPegula", "Jessica Pegula"),
    (202468, "ElenaRybakina", "Elena Rybakina"),
    (215613, "EmmaNavarro", "Emma Navarro"),
    (214082, "DariaKasatkina", "Daria Kasatkina"),
    (206252, "BeatrizHaddadMaia", "Beatriz Haddad Maia"),
    (203389, "DanielleCollins", "Danielle Collins"),
    (211651, "MirraAndreeva", "Mirra Andreeva"),
    (223670, "DianaShnaider", "Diana Shnaider"),
    (214939, "AnnaKalinskaya", "Anna Kalinskaya"),
    (211533, "DonnaVekic", "Donna Vekic"),
    (259799, "MadisonKeys", "Madison Keys"),
    (206242, "PaulaBadosa", "Paula Badosa"),
    (216146, "LinaTsurenko", "Lina Tsurenko"),
    (202499, "LindaNoskova", "Linda Noskova"),
    (201458, "MarieBouzkova", "Marie Bouzkova"),
    (201619, "KarolinaPliskova", "Karolina Pliskova"),
    (214096, "AnastasiaPavlyuchenkova", "Anastasia Pavlyuchenkova"),
    (202494, "ElinaSvitolina", "Elina Svitolina"),
    (211107, "VeronikaKudermetova", "Veronika Kudermetova"),
    (211684, "LeylaFernandez", "Leyla Fernandez"),
]


@dataclass
class Match:
    """Represents a single match with serve statistics."""
    tourney_id: str = ""
    tourney_name: str = ""
    surface: str = ""
    draw_size: str = ""
    tourney_level: str = ""
    tourney_date: str = ""
    match_num: str = ""
    winner_id: str = ""
    winner_seed: str = ""
    winner_entry: str = ""
    winner_name: str = ""
    winner_hand: str = ""
    winner_ht: str = ""
    winner_ioc: str = ""
    winner_age: str = ""
    loser_id: str = ""
    loser_seed: str = ""
    loser_entry: str = ""
    loser_name: str = ""
    loser_hand: str = ""
    loser_ht: str = ""
    loser_ioc: str = ""
    loser_age: str = ""
    score: str = ""
    best_of: str = ""
    round: str = ""
    minutes: str = ""
    w_ace: str = ""
    w_df: str = ""
    w_svpt: str = ""
    w_1stIn: str = ""
    w_1stWon: str = ""
    w_2ndWon: str = ""
    w_SvGms: str = ""
    w_bpSaved: str = ""
    w_bpFaced: str = ""
    l_ace: str = ""
    l_df: str = ""
    l_svpt: str = ""
    l_1stIn: str = ""
    l_1stWon: str = ""
    l_2ndWon: str = ""
    l_SvGms: str = ""
    l_bpSaved: str = ""
    l_bpFaced: str = ""
    winner_rank: str = ""
    winner_rank_points: str = ""
    loser_rank: str = ""
    loser_rank_points: str = ""


def get_match_columns() -> list[str]:
    """Return column names matching Sackmann's format."""
    return [
        "tourney_id", "tourney_name", "surface", "draw_size", "tourney_level",
        "tourney_date", "match_num", "winner_id", "winner_seed", "winner_entry",
        "winner_name", "winner_hand", "winner_ht", "winner_ioc", "winner_age",
        "loser_id", "loser_seed", "loser_entry", "loser_name", "loser_hand",
        "loser_ht", "loser_ioc", "loser_age", "score", "best_of", "round",
        "minutes", "w_ace", "w_df", "w_svpt", "w_1stIn", "w_1stWon", "w_2ndWon",
        "w_SvGms", "w_bpSaved", "w_bpFaced", "l_ace", "l_df", "l_svpt", "l_1stIn",
        "l_1stWon", "l_2ndWon", "l_SvGms", "l_bpSaved", "l_bpFaced", "winner_rank",
        "winner_rank_points", "loser_rank", "loser_rank_points"
    ]


def parse_round(round_str: str) -> str:
    """Convert Tennis Abstract round format to Sackmann format."""
    round_map = {
        "F": "F",
        "SF": "SF",
        "QF": "QF",
        "R16": "R16",
        "R32": "R32",
        "R64": "R64",
        "R128": "R128",
        "RR": "RR",
        "BR": "BR",
        "1R": "R128",
        "2R": "R64",
        "3R": "R32",
        "4R": "R16",
    }
    return round_map.get(round_str.strip(), round_str)


def parse_surface(surface_str: str) -> str:
    """Normalize surface names."""
    surface_str = surface_str.lower().strip()
    if "hard" in surface_str:
        return "Hard"
    elif "clay" in surface_str:
        return "Clay"
    elif "grass" in surface_str:
        return "Grass"
    elif "carpet" in surface_str:
        return "Carpet"
    return surface_str.title()


def parse_date(date_str: str) -> tuple[str, int]:
    """Parse date string and return (YYYYMMDD format, year)."""
    # Format from Tennis Abstract: "19-Jan-2026"
    formats = [
        "%d-%b-%Y",  # 19-Jan-2026
        "%Y-%m-%d",
        "%d %b %Y",
        "%b %d, %Y",
        "%Y/%m/%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y%m%d"), dt.year
        except ValueError:
            continue
    return "", 0


def parse_time_to_minutes(time_str: str) -> str:
    """Convert time string like '2:23' to minutes."""
    try:
        parts = time_str.strip().split(':')
        if len(parts) == 2:
            hours = int(parts[0])
            mins = int(parts[1])
            return str(hours * 60 + mins)
    except (ValueError, IndexError):
        pass
    return ""


def parse_result_cell(result_text: str, player_name: str) -> tuple[bool, str, str, str, str]:
    """
    Parse the result cell from Tennis Abstract.

    Format: "(4)Novak Djokovic [SRB] d. (2)Sinner"
    or: "(2)Sinner d. (8)Ben Shelton [USA]"

    Returns: (player_won, winner_name, loser_name, winner_seed, loser_seed)
    """
    # Determine if current player won
    player_won = False

    # Pattern: "d." separates winner from loser
    # Winner is on left, loser on right
    if " d. " not in result_text:
        return player_won, "", "", "", ""

    parts = result_text.split(" d. ")
    if len(parts) != 2:
        return player_won, "", "", "", ""

    winner_part = parts[0].strip()
    loser_part = parts[1].strip()

    # Extract seed (number in parentheses)
    def extract_seed(text):
        match = re.search(r'\((\d+)\)', text)
        return match.group(1) if match else ""

    # Extract name (remove seed, country code in brackets)
    def extract_name(text):
        # Remove seed like (2)
        text = re.sub(r'\(\d+\)', '', text)
        # Remove country code like [USA]
        text = re.sub(r'\[.*?\]', '', text)
        return text.strip()

    winner_seed = extract_seed(winner_part)
    loser_seed = extract_seed(loser_part)
    winner_name = extract_name(winner_part)
    loser_name = extract_name(loser_part)

    # Check if current player is winner
    # The player name might be abbreviated (e.g., "Sinner" instead of "Jannik Sinner")
    player_last_name = player_name.split()[-1].lower()
    winner_last_name = winner_name.split()[-1].lower() if winner_name else ""

    player_won = player_last_name == winner_last_name

    return player_won, winner_name, loser_name, winner_seed, loser_seed


def parse_bp_saved(bp_text: str) -> tuple[str, str]:
    """Parse break points saved like '5/8' into (saved, faced)."""
    try:
        if '/' in bp_text:
            parts = bp_text.split('/')
            return parts[0].strip(), parts[1].strip()
    except (ValueError, IndexError):
        pass
    return "", ""


def load_player_lookup(tour: str) -> dict[str, dict]:
    """Load player info for ID lookup."""
    players = {}
    player_file = DATA_DIR / f"tennis_{tour}" / f"{tour}_players.csv"

    if not player_file.exists():
        return players

    with open(player_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Key by full name (lowercase for matching)
            name = f"{row.get('name_first', '')} {row.get('name_last', '')}".lower().strip()
            players[name] = row
            # Also key by last name only for fallback
            players[row.get('name_last', '').lower()] = row

    return players


def scrape_player_matches(
    page: Page,
    player_id: int,
    url_name: str,
    full_name: str,
    tour: str,
    player_lookup: dict[str, dict]
) -> list[dict]:
    """
    Scrape recent matches for a single player from Tennis Abstract.

    Table structure (#recent-results):
    Date | Tournament | Surface | Rd | Rk | vRk | Result | Score | DR | A% | DF% | 1stIn | 1st% | 2nd% | BPSvd | Time
    """
    matches = []
    prefix = "w" if tour == "wta" else ""
    url = f"https://www.tennisabstract.com/cgi-bin/{prefix}player.cgi?p={url_name}"

    print(f"  Scraping {full_name}: {url}")

    try:
        page.goto(url, timeout=60000, wait_until="domcontentloaded")

        # Wait for JavaScript to render the table
        page.wait_for_timeout(3000)

        # Find the recent-results table
        table = page.query_selector("#recent-results")
        if not table:
            print(f"    Warning: Could not find #recent-results table for {full_name}")
            return matches

        # Get all rows
        rows = table.query_selector_all("tr")

        for row in rows[1:]:  # Skip header row
            cells = row.query_selector_all("td")
            if len(cells) < 8:  # Need at least date through score
                continue

            try:
                cell_texts = [c.inner_text().strip() for c in cells]

                # Column mapping:
                # 0: Date, 1: Tournament, 2: Surface, 3: Rd, 4: Rk, 5: vRk, 6: Result, 7: Score
                # 8: DR, 9: A%, 10: DF%, 11: 1stIn, 12: 1st%, 13: 2nd%, 14: BPSvd, 15: Time

                date_text = cell_texts[0]
                tourney_date, year = parse_date(date_text)

                if year < MIN_YEAR:
                    continue

                match = Match()
                match.tourney_date = tourney_date
                match.tourney_name = cell_texts[1]
                match.surface = parse_surface(cell_texts[2])
                match.round = parse_round(cell_texts[3])

                # Player rank and opponent rank
                player_rank = cell_texts[4]
                opponent_rank = cell_texts[5]

                # Parse result to get winner/loser
                result_text = cell_texts[6]
                player_won, winner_name, loser_name, winner_seed, loser_seed = parse_result_cell(
                    result_text, full_name
                )

                match.score = cell_texts[7]

                # Generate tourney_id
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', match.tourney_name)
                match.tourney_id = f"{year}-{clean_name[:20]}"

                # Set winner/loser info
                if player_won:
                    match.winner_id = str(player_id)
                    match.winner_name = full_name
                    match.winner_seed = winner_seed
                    match.winner_rank = player_rank
                    match.loser_name = loser_name if loser_name else winner_name  # fallback
                    match.loser_seed = loser_seed
                    match.loser_rank = opponent_rank
                else:
                    match.loser_id = str(player_id)
                    match.loser_name = full_name
                    match.loser_seed = loser_seed
                    match.loser_rank = player_rank
                    match.winner_name = winner_name if winner_name else loser_name  # fallback
                    match.winner_seed = winner_seed
                    match.winner_rank = opponent_rank

                # Look up opponent ID from player database
                opponent_name = match.loser_name if player_won else match.winner_name
                opponent_info = player_lookup.get(opponent_name.lower(), {})
                if not opponent_info:
                    # Try last name only
                    opponent_last = opponent_name.split()[-1].lower() if opponent_name else ""
                    opponent_info = player_lookup.get(opponent_last, {})

                if opponent_info:
                    if player_won:
                        match.loser_id = opponent_info.get('player_id', '')
                    else:
                        match.winner_id = opponent_info.get('player_id', '')

                # Parse serve stats (only for current player's stats)
                # 9: A%, 10: DF%, 11: 1stIn, 12: 1st%, 13: 2nd%, 14: BPSvd, 15: Time
                if len(cell_texts) > 15:
                    # A% and DF% are percentages, need raw counts (not available directly)
                    # Store the percentages for now
                    time_str = cell_texts[15] if len(cell_texts) > 15 else ""
                    match.minutes = parse_time_to_minutes(time_str)

                    # BP Saved (format: "5/8")
                    if len(cell_texts) > 14:
                        bp_saved, bp_faced = parse_bp_saved(cell_texts[14])
                        if player_won:
                            match.w_bpSaved = bp_saved
                            match.w_bpFaced = bp_faced
                        else:
                            match.l_bpSaved = bp_saved
                            match.l_bpFaced = bp_faced

                # Convert Match to dict
                match_dict = {col: getattr(match, col, "") for col in get_match_columns()}
                matches.append(match_dict)

            except Exception as e:
                print(f"    Error parsing row: {e}")
                continue

        print(f"    Found {len(matches)} matches from {MIN_YEAR}+")

    except PlaywrightTimeout:
        print(f"    Timeout loading page for {full_name}")
    except Exception as e:
        print(f"    Error scraping {full_name}: {e}")

    return matches


def scrape_tour(tour: str, players: list[tuple[int, str, str]], max_players: int = None) -> list[dict]:
    """Scrape all matches for a tour's top players."""

    all_matches = []
    player_lookup = load_player_lookup(tour)

    players_to_scrape = players[:max_players] if max_players else players

    print(f"\nScraping {tour.upper()} Top {len(players_to_scrape)} players...")
    print(f"Looking for matches from {MIN_YEAR} onwards\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        for player_id, url_name, full_name in players_to_scrape:
            matches = scrape_player_matches(
                page, player_id, url_name, full_name, tour, player_lookup
            )
            all_matches.extend(matches)

            # Rate limiting
            time.sleep(RATE_LIMIT_SECONDS)

        browser.close()

    return all_matches


def deduplicate_matches(matches: list[dict]) -> list[dict]:
    """Remove duplicate matches (same match scraped from both players)."""
    seen = set()
    unique = []

    for match in matches:
        # Create a unique key - use sorted names to handle same match from both perspectives
        names = sorted([match.get('winner_name', ''), match.get('loser_name', '')])
        key = (
            match.get('tourney_date', ''),
            match.get('tourney_name', ''),
            match.get('round', ''),
            names[0],
            names[1],
        )

        if key not in seen and any(key):
            seen.add(key)
            unique.append(match)

    return unique


def merge_with_existing(new_matches: list[dict], existing_file: Path) -> list[dict]:
    """Merge new matches with existing data, avoiding duplicates."""

    if not existing_file.exists():
        return new_matches

    # Load existing matches
    existing = pd.read_csv(existing_file)
    existing_records = existing.to_dict('records')

    # Create set of existing match keys
    existing_keys = set()
    for match in existing_records:
        names = sorted([str(match.get('winner_name', '')), str(match.get('loser_name', ''))])
        key = (
            str(match.get('tourney_date', '')),
            str(match.get('tourney_name', '')),
            str(match.get('round', '')),
            names[0],
            names[1],
        )
        existing_keys.add(key)

    # Filter new matches to only truly new ones
    truly_new = []
    for match in new_matches:
        names = sorted([str(match.get('winner_name', '')), str(match.get('loser_name', ''))])
        key = (
            str(match.get('tourney_date', '')),
            str(match.get('tourney_name', '')),
            str(match.get('round', '')),
            names[0],
            names[1],
        )
        if key not in existing_keys:
            truly_new.append(match)

    print(f"  Found {len(truly_new)} new matches to add")

    # Combine and sort by date
    all_matches = existing_records + truly_new
    all_matches.sort(key=lambda x: str(x.get('tourney_date', '')))

    return all_matches


def save_matches(matches: list[dict], output_file: Path):
    """Save matches to CSV file."""
    if not matches:
        print(f"  No matches to save")
        return

    columns = get_match_columns()

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for match in matches:
            row = {col: match.get(col, '') for col in columns}
            writer.writerow(row)

    print(f"  Saved {len(matches)} matches to {output_file.name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scrape Tennis Abstract for recent match data")
    parser.add_argument("--tour", choices=["atp", "wta", "both"], default="both",
                        help="Which tour to scrape")
    parser.add_argument("--max-players", type=int, default=None,
                        help="Maximum number of players to scrape (for testing)")
    parser.add_argument("--no-merge", action="store_true",
                        help="Don't merge with existing data")
    args = parser.parse_args()

    print("=" * 60)
    print("Tennis Abstract Scraper")
    print(f"Scraping matches from {MIN_YEAR} onwards")
    print("=" * 60)

    # Ensure output directories exist
    (OUTPUT_DIR / "atp").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "wta").mkdir(parents=True, exist_ok=True)

    if args.tour in ["atp", "both"]:
        # Scrape ATP
        atp_matches = scrape_tour("atp", ATP_TOP_25, args.max_players)
        atp_matches = deduplicate_matches(atp_matches)

        atp_output = OUTPUT_DIR / "atp" / "atp_top25_matches_scraped.csv"
        existing_atp = OUTPUT_DIR / "atp" / "atp_top25_matches.csv"

        # Save scraped data separately first
        save_matches(atp_matches, atp_output)

        # Optionally merge with existing
        if not args.no_merge and atp_matches and existing_atp.exists():
            merged = merge_with_existing(atp_matches, existing_atp)
            save_matches(merged, existing_atp)

        print()

    if args.tour in ["wta", "both"]:
        # Scrape WTA
        wta_matches = scrape_tour("wta", WTA_TOP_25, args.max_players)
        wta_matches = deduplicate_matches(wta_matches)

        wta_output = OUTPUT_DIR / "wta" / "wta_top25_matches_scraped.csv"
        existing_wta = OUTPUT_DIR / "wta" / "wta_top25_matches.csv"

        save_matches(wta_matches, wta_output)

        if not args.no_merge and wta_matches and existing_wta.exists():
            merged = merge_with_existing(wta_matches, existing_wta)
            save_matches(merged, existing_wta)

    print("\n" + "=" * 60)
    print("Scraping complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
