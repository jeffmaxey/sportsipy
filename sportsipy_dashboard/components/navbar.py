"""Top navigation bar component."""
import dash_mantine_components as dmc
from dash_iconify import DashIconify


NAV_LINKS = [
    {"label": "Home", "href": "/", "icon": "ion:home"},
    {"label": "Explorer", "href": "/explorer", "icon": "ion:search"},
    {"label": "Dataset Builder", "href": "/builder", "icon": "ion:construct"},
    {"label": "Saved Queries", "href": "/queries", "icon": "ion:bookmark"},
]


def create_navbar() -> dmc.Group:
    """Create the top navigation bar."""
    nav_items = [
        dmc.Anchor(
            dmc.Button(
                dmc.Group(
                    [
                        DashIconify(icon=link["icon"], width=18),
                        dmc.Text(link["label"], size="sm"),
                    ],
                    gap=6,
                ),
                variant="subtle",
                color="gray",
            ),
            href=link["href"],
            style={"textDecoration": "none"},
        )
        for link in NAV_LINKS
    ]

    return dmc.Group(
        justify="space-between",
        align="center",
        style={"height": "60px", "width": "100%"},
        children=[
            dmc.Group(
                gap=8,
                children=[
                    DashIconify(icon="mdi:chart-bar", width=28, color="#1971c2"),
                    dmc.Text(
                        "Sportsipy Dashboard",
                        fw=700,
                        size="lg",
                        style={"color": "#1971c2"},
                    ),
                ],
            ),
            dmc.Group(gap=4, children=nav_items),
            dmc.ActionIcon(
                id="color-scheme-toggle",
                children=DashIconify(icon="radix-icons:sun", width=20),
                variant="subtle",
                size="lg",
                title="Toggle color scheme",
            ),
        ],
    )
