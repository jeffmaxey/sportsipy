"""Home / landing page for Sportsipy Dashboard."""
import dash
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from sportsipy_dashboard.utils.data_loader import SPORTS_CONFIG
from sportsipy_dashboard.utils.query_manager import QueryManager

dash.register_page(__name__, path="/", title="Sportsipy Dashboard")

_qm = QueryManager()


def _sport_card(sport_key: str, config: dict) -> dmc.Card:
    """Build a sport summary card."""
    return dmc.Card(
        className="sport-card",
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"cursor": "pointer"},
        children=[
            dmc.CardSection(
                dmc.Group(
                    justify="center",
                    p="md",
                    style={"background": config["color"] + "15"},
                    children=[
                        DashIconify(icon=config["icon"], width=48),
                    ],
                )
            ),
            dmc.Stack(
                p="md",
                gap=4,
                children=[
                    dmc.Text(config["name"], fw=700, size="lg"),
                    dmc.Text(config["full_name"], size="sm", c="dimmed"),
                    dmc.Text(
                        f"Seasons: {config['season_range'][0]}–{config['season_range'][1]}",
                        size="xs",
                        c="dimmed",
                    ),
                    dmc.Anchor(
                        dmc.Button("Explore →", size="xs", mt=4, color="blue", variant="light"),
                        href=f"/explorer?sport={sport_key}",
                        style={"textDecoration": "none"},
                    ),
                ],
            ),
        ],
    )


def layout() -> dmc.Stack:
    """Render the home page layout."""
    sport_cards = [
        dmc.GridCol(_sport_card(k, v), span={"base": 12, "sm": 6, "md": 4})
        for k, v in SPORTS_CONFIG.items()
    ]

    recent_queries = _qm.load_queries()
    recent_section_children: list = []
    if recent_queries:
        for q in sorted(recent_queries, key=lambda x: x.updated_at, reverse=True)[:5]:
            recent_section_children.append(
                dmc.Paper(
                    p="sm",
                    withBorder=True,
                    radius="sm",
                    children=dmc.Group(
                        justify="space-between",
                        children=[
                            dmc.Stack(
                                gap=2,
                                children=[
                                    dmc.Text(q.name, fw=600, size="sm"),
                                    dmc.Text(
                                        f"{q.sport.upper()} • {q.season or 'latest'} • {q.updated_at[:10]}",
                                        size="xs",
                                        c="dimmed",
                                    ),
                                ],
                            ),
                            dmc.Anchor(
                                dmc.Button("Load", size="xs", variant="subtle"),
                                href=f"/queries?id={q.id}",
                                style={"textDecoration": "none"},
                            ),
                        ],
                    ),
                )
            )
    else:
        recent_section_children.append(
            dmc.Text(
                "No saved queries yet. Start exploring to save your first query!",
                c="dimmed",
                size="sm",
            )
        )

    return dmc.Stack(
        gap="xl",
        children=[
            dmc.Paper(
                p="xl",
                radius="lg",
                style={
                    "background": "linear-gradient(135deg, #1971c2 0%, #0c8599 100%)",
                    "color": "white",
                },
                children=dmc.Stack(
                    align="center",
                    gap="sm",
                    children=[
                        DashIconify(icon="mdi:chart-bar", width=60, color="white"),
                        dmc.Title("Sportsipy Dashboard", order=1, style={"color": "white"}),
                        dmc.Text(
                            "Explore sports statistics from MLB, NBA, NFL, NHL, NCAAB, NCAAF, and more.",
                            size="lg",
                            style={"color": "rgba(255,255,255,0.9)", "textAlign": "center"},
                        ),
                        dmc.Group(
                            mt="md",
                            children=[
                                dmc.Anchor(
                                    dmc.Button(
                                        "Start Exploring",
                                        size="md",
                                        color="white",
                                        variant="outline",
                                        leftSection=DashIconify(icon="ion:search", width=18),
                                    ),
                                    href="/explorer",
                                    style={"textDecoration": "none"},
                                ),
                                dmc.Anchor(
                                    dmc.Button(
                                        "Build Dataset",
                                        size="md",
                                        color="white",
                                        variant="filled",
                                        style={"background": "rgba(255,255,255,0.2)"},
                                        leftSection=DashIconify(icon="ion:construct", width=18),
                                    ),
                                    href="/builder",
                                    style={"textDecoration": "none"},
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Title("Browse by Sport", order=2),
                    dmc.Grid(children=sport_cards, gutter="md"),
                ],
            ),
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        justify="space-between",
                        children=[
                            dmc.Title("Recent Queries", order=2),
                            dmc.Anchor(
                                dmc.Button("View All", size="xs", variant="subtle"),
                                href="/queries",
                                style={"textDecoration": "none"},
                            ),
                        ],
                    ),
                    dmc.Stack(gap="xs", children=recent_section_children),
                ],
            ),
        ],
    )
