"""Data explorer page - browse team and player stats."""
import logging

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html, no_update
from dash_iconify import DashIconify

from sportsipy_dashboard.utils.code_generator import CodeAction, CodeGenerator
from sportsipy_dashboard.utils.data_loader import SPORTS_CONFIG, load_teams_dataframe
from sportsipy_dashboard.utils.exporters import EXPORT_FORMATS, export_dataframe

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/explorer", title="Explorer – Sportsipy Dashboard")

_gen = CodeGenerator()


def layout(sport: str = "mlb", **kwargs) -> dmc.Stack:
    """Render the explorer page layout."""
    sport_options = [
        {"value": k, "label": v["name"]} for k, v in SPORTS_CONFIG.items()
    ]
    format_options = [
        {"value": k, "label": v["label"]} for k, v in EXPORT_FORMATS.items()
    ]

    return dmc.Stack(
        gap="md",
        children=[
            dmc.Title("Data Explorer", order=2),
            dmc.Paper(
                p="md",
                withBorder=True,
                radius="md",
                children=dmc.Group(
                    gap="md",
                    align="flex-end",
                    children=[
                        dmc.Select(
                            id="sport-select",
                            label="Sport",
                            data=sport_options,
                            value=sport,
                            w=150,
                            searchable=True,
                        ),
                        dmc.NumberInput(
                            id="season-input",
                            label="Season",
                            value=2023,
                            min=1871,
                            max=2024,
                            w=120,
                        ),
                        dmc.Select(
                            id="data-type-select",
                            label="Data Type",
                            data=[
                                {"value": "teams", "label": "Teams"},
                                {"value": "players", "label": "Players"},
                            ],
                            value="teams",
                            w=150,
                        ),
                        dmc.Button(
                            "Load Data",
                            id="load-data-btn",
                            leftSection=DashIconify(icon="mdi:database-refresh", width=16),
                            color="blue",
                        ),
                        dmc.Button(
                            "Export",
                            id="export-btn",
                            leftSection=DashIconify(icon="mdi:download", width=16),
                            color="green",
                            variant="outline",
                        ),
                        dmc.Anchor(
                            dmc.Button(
                                "Build Dataset",
                                leftSection=DashIconify(icon="ion:construct", width=16),
                                color="violet",
                                variant="outline",
                            ),
                            href="/builder",
                            style={"textDecoration": "none"},
                        ),
                    ],
                ),
            ),
            html.Div(id="explorer-alert"),
            dag.AgGrid(
                id="teams-grid",
                rowData=[],
                columnDefs=[],
                defaultColDef={
                    "resizable": True,
                    "flex": 1,
                    "minWidth": 100,
                    "filter": True,
                    "sortable": True,
                },
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": 20,
                    "rowSelection": "multiple",
                    "animateRows": True,
                },
                style={"height": "500px"},
            ),
            dmc.Stack(
                gap="xs",
                children=[
                    dmc.Button(
                        "Toggle Code Preview",
                        id="toggle-code-btn",
                        variant="subtle",
                        size="xs",
                        leftSection=DashIconify(icon="mdi:code-braces", width=16),
                    ),
                    dmc.Collapse(
                        id="code-collapse",
                        children=html.Pre(
                            id="code-preview",
                            className="code-preview",
                            children="# Load data to see generated code",
                        ),
                    ),
                ],
            ),
            dmc.Modal(
                id="export-modal",
                title="Export Data",
                children=[
                    dmc.Select(
                        id="export-format-select",
                        label="Format",
                        data=format_options,
                        value="csv",
                        mb="md",
                    ),
                    dmc.Button(
                        "Download",
                        id="download-btn",
                        leftSection=DashIconify(icon="mdi:download", width=16),
                        color="green",
                    ),
                ],
            ),
            dcc.Download(id="download-data"),
        ],
    )


@callback(
    Output("teams-grid", "rowData"),
    Output("teams-grid", "columnDefs"),
    Output("code-preview", "children"),
    Output("explorer-alert", "children"),
    Input("load-data-btn", "n_clicks"),
    State("sport-select", "value"),
    State("season-input", "value"),
    prevent_initial_call=True,
)
def update_teams_grid(n_clicks, sport, season):
    """Load data into the AG Grid and update code preview."""
    if not sport:
        return no_update, no_update, no_update, dmc.Alert("Please select a sport.", color="yellow")

    try:
        df = load_teams_dataframe(sport, int(season) if season else None)
    except Exception as exc:
        logger.error("Failed to load data: %s", exc)
        alert = dmc.Alert(
            f"Failed to load data: {exc}",
            color="red",
            icon=DashIconify(icon="mdi:alert-circle"),
        )
        return [], [], "# Error loading data", alert

    if df.empty:
        return [], [], "# No data returned", dmc.Alert("No data returned.", color="yellow")

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str)

    row_data = df.to_dict("records")
    col_defs = [
        {"field": col, "filter": True, "sortable": True, "resizable": True}
        for col in df.columns
    ]

    _gen.clear()
    _gen.add_action(CodeAction("load_teams", {"sport": sport, "season": season}))
    code = _gen.generate_script()

    return row_data, col_defs, code, html.Div()


@callback(
    Output("code-collapse", "opened"),
    Input("toggle-code-btn", "n_clicks"),
    State("code-collapse", "opened"),
    prevent_initial_call=True,
)
def toggle_code(n_clicks, opened):
    """Toggle the code preview panel."""
    return not opened


@callback(
    Output("export-modal", "opened"),
    Input("export-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_export_modal(n_clicks):
    """Open the export modal."""
    return True


@callback(
    Output("download-data", "data"),
    Output("export-modal", "opened", allow_duplicate=True),
    Input("download-btn", "n_clicks"),
    State("export-format-select", "value"),
    State("teams-grid", "rowData"),
    prevent_initial_call=True,
)
def trigger_download(n_clicks, fmt, row_data):
    """Export the current grid data and trigger a browser download."""
    import base64

    import pandas as pd

    if not row_data or not fmt:
        return no_update, no_update

    df = pd.DataFrame(row_data)
    try:
        data_bytes, filename, mime = export_dataframe(df, fmt)
    except Exception as exc:
        logger.error("Export failed: %s", exc)
        return no_update, False

    b64 = base64.b64encode(data_bytes).decode()
    return {"base64": True, "content": b64, "filename": filename, "type": mime}, False
