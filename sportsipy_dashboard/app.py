"""Main Dash application entry point for Sportsipy Dashboard."""
import logging

import dash
import dash_mantine_components as dmc
from dash import Dash, dcc, page_container

from sportsipy_dashboard.components.navbar import create_navbar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

app.layout = dmc.MantineProvider(
    id="mantine-provider",
    theme={"colorScheme": "light", "primaryColor": "blue"},
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="color-scheme-store", storage_type="local", data="light"),
        dmc.AppShell(
            header={"height": 60},
            children=[
                dmc.AppShellHeader(
                    children=create_navbar(),
                    style={"padding": "0 16px"},
                ),
                dmc.AppShellMain(
                    children=page_container,
                    style={"padding": "20px"},
                ),
            ],
        ),
    ],
)


def main() -> None:
    """Run the Sportsipy Dashboard application."""
    logger.info("Starting Sportsipy Dashboard on http://localhost:8050")
    app.run(debug=True, port=8050)


if __name__ == "__main__":
    main()
