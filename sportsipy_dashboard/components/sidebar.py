"""Sidebar component with sport selection."""
import dash_mantine_components as dmc
from dash_iconify import DashIconify

SPORT_LINKS = [
    {"label": "MLB", "sport": "mlb", "icon": "emojione:baseball", "color": "#003087"},
    {"label": "NBA", "sport": "nba", "icon": "emojione:basketball", "color": "#C8102E"},
    {"label": "NFL", "sport": "nfl", "icon": "emojione:american-football", "color": "#013369"},
    {"label": "NHL", "sport": "nhl", "icon": "emojione:ice-hockey-stick-and-puck", "color": "#000000"},
    {"label": "NCAAB", "sport": "ncaab", "icon": "mdi:basketball", "color": "#FF6900"},
    {"label": "NCAAF", "sport": "ncaaf", "icon": "mdi:football", "color": "#007A33"},
    {"label": "FB", "sport": "fb", "icon": "emojione:soccer-ball", "color": "#1a5276"},
]


def create_sidebar(active_sport: str = "") -> dmc.Stack:
    """Create a sidebar with sport navigation links."""
    links = [
        dmc.NavLink(
            label=s["label"],
            leftSection=DashIconify(icon=s["icon"], width=20),
            href=f"/explorer?sport={s['sport']}",
            active=(active_sport == s["sport"]),
            style={"borderRadius": "6px"},
        )
        for s in SPORT_LINKS
    ]
    return dmc.Stack(
        className="sidebar-nav",
        gap=4,
        children=[
            dmc.Text("Sports", fw=600, size="xs", c="dimmed", mb=4),
            *links,
        ],
    )
