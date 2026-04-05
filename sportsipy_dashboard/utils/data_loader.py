"""Data loading utilities for sportsipy data."""
import importlib
import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

SPORTS_CONFIG = {
    "mlb": {
        "name": "MLB",
        "full_name": "Major League Baseball",
        "module": "sportsipy.mlb",
        "teams_class": "Teams",
        "has_seasons": True,
        "season_range": (1871, 2024),
        "icon": "emojione:baseball",
        "color": "#003087",
    },
    "nba": {
        "name": "NBA",
        "full_name": "National Basketball Association",
        "module": "sportsipy.nba",
        "teams_class": "Teams",
        "has_seasons": True,
        "season_range": (1947, 2024),
        "icon": "emojione:basketball",
        "color": "#C8102E",
    },
    "nfl": {
        "name": "NFL",
        "full_name": "National Football League",
        "module": "sportsipy.nfl",
        "teams_class": "Teams",
        "has_seasons": True,
        "season_range": (1966, 2024),
        "icon": "emojione:american-football",
        "color": "#013369",
    },
    "nhl": {
        "name": "NHL",
        "full_name": "National Hockey League",
        "module": "sportsipy.nhl",
        "teams_class": "Teams",
        "has_seasons": True,
        "season_range": (1918, 2024),
        "icon": "emojione:ice-hockey-stick-and-puck",
        "color": "#000000",
    },
    "ncaab": {
        "name": "NCAAB",
        "full_name": "NCAA Men's Basketball",
        "module": "sportsipy.ncaab",
        "teams_class": "Teams",
        "has_seasons": True,
        "season_range": (2010, 2024),
        "icon": "mdi:basketball",
        "color": "#FF6900",
    },
    "ncaaf": {
        "name": "NCAAF",
        "full_name": "NCAA Football",
        "module": "sportsipy.ncaaf",
        "teams_class": "Teams",
        "has_seasons": True,
        "season_range": (2000, 2024),
        "icon": "mdi:football",
        "color": "#007A33",
    },
}


def load_teams_dataframe(sport: str, season: Optional[int] = None) -> pd.DataFrame:
    """Load teams data for a sport/season as a DataFrame.

    Args:
        sport: Sport key (e.g. 'mlb', 'nba').
        season: Season year. Uses latest if None.

    Returns:
        DataFrame of team statistics.

    Raises:
        ValueError: If sport is not recognized.
        RuntimeError: If data loading fails.
    """
    if sport not in SPORTS_CONFIG:
        raise ValueError(f"Unknown sport '{sport}'. Valid options: {list(SPORTS_CONFIG)}")

    config = SPORTS_CONFIG[sport]
    logger.info("Loading %s teams for season %s", sport.upper(), season)

    try:
        teams_module = importlib.import_module(f"{config['module']}.teams")
        TeamsClass = getattr(teams_module, config["teams_class"])
        teams = TeamsClass(season) if season is not None else TeamsClass()
        frames = []
        for team in teams:
            try:
                df = team.dataframe
                if df is not None:
                    frames.append(df)
            except Exception as exc:
                logger.warning("Skipping team %s: %s", getattr(team, "abbreviation", "?"), exc)
        if not frames:
            logger.warning("No team data returned for %s %s", sport, season)
            return pd.DataFrame()
        result = pd.concat(frames, ignore_index=True)
        logger.info("Loaded %d rows for %s %s", len(result), sport, season)
        return result
    except Exception as exc:
        logger.error("Failed to load %s teams: %s", sport, exc)
        raise RuntimeError(f"Failed to load {sport} teams: {exc}") from exc


def load_player_dataframe(sport: str, team_abbr: str, season: Optional[int] = None) -> pd.DataFrame:
    """Load player stats for a team as a DataFrame.

    Args:
        sport: Sport key.
        team_abbr: Team abbreviation.
        season: Season year.

    Returns:
        DataFrame of player statistics.
    """
    if sport not in SPORTS_CONFIG:
        raise ValueError(f"Unknown sport '{sport}'.")

    config = SPORTS_CONFIG[sport]
    logger.info("Loading %s roster for team %s season %s", sport, team_abbr, season)

    try:
        roster_module = importlib.import_module(f"{config['module']}.roster")
        RosterClass = getattr(roster_module, "Roster")
        roster = RosterClass(team_abbr, year=season) if season else RosterClass(team_abbr)
        frames = []
        for player in roster.players:
            try:
                df = player.dataframe
                if df is not None:
                    frames.append(df)
            except Exception as exc:
                logger.warning("Skipping player: %s", exc)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)
    except Exception as exc:
        logger.error("Failed to load %s roster for %s: %s", sport, team_abbr, exc)
        raise RuntimeError(f"Failed to load roster: {exc}") from exc


def get_team_list(sport: str, season: Optional[int] = None) -> list[dict]:
    """Return a list of teams with name and abbreviation.

    Args:
        sport: Sport key.
        season: Season year.

    Returns:
        List of dicts with 'name' and 'abbreviation' keys.
    """
    if sport not in SPORTS_CONFIG:
        raise ValueError(f"Unknown sport '{sport}'.")

    config = SPORTS_CONFIG[sport]
    logger.info("Fetching team list for %s season %s", sport, season)

    try:
        teams_module = importlib.import_module(f"{config['module']}.teams")
        TeamsClass = getattr(teams_module, config["teams_class"])
        teams = TeamsClass(season) if season is not None else TeamsClass()
        result = []
        for team in teams:
            result.append({
                "name": getattr(team, "name", str(team)),
                "abbreviation": getattr(team, "abbreviation", ""),
            })
        return result
    except Exception as exc:
        logger.error("Failed to get team list for %s: %s", sport, exc)
        return []
