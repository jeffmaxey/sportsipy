"""Dataset Builder page - step-by-step data preparation workflow."""
import logging

import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, ctx, dcc, html, no_update
from dash_iconify import DashIconify

from sportsipy_dashboard.utils.code_generator import CodeAction, CodeGenerator
from sportsipy_dashboard.utils.data_loader import SPORTS_CONFIG
from sportsipy_dashboard.utils.exporters import EXPORT_FORMATS
from sportsipy_dashboard.utils.query_manager import QueryManager, SavedQuery

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/builder", title="Dataset Builder – Sportsipy Dashboard")

_qm = QueryManager()
_gen = CodeGenerator()

OPERATORS = ["==", "!=", ">", ">=", "<", "<=", "contains", "startswith"]
STEPS = ["Select Data", "Filter", "Transform", "Export"]


def layout(**kwargs) -> dmc.Stack:
    """Render the dataset builder layout."""
    sport_options = [{"value": k, "label": v["name"]} for k, v in SPORTS_CONFIG.items()]
    format_options = [{"value": k, "label": v["label"]} for k, v in EXPORT_FORMATS.items()]

    return dmc.Stack(
        gap="lg",
        children=[
            dmc.Title("Dataset Builder", order=2),
            dmc.Stepper(
                id="builder-stepper",
                active=0,
                children=[
                    dmc.StepperStep(label=label, description=f"Step {i + 1}")
                    for i, label in enumerate(STEPS)
                ],
            ),
            html.Div(
                id="step-select-data",
                children=dmc.Paper(
                    p="lg",
                    withBorder=True,
                    radius="md",
                    children=dmc.Stack(
                        gap="md",
                        children=[
                            dmc.Title("Select Data Source", order=4),
                            dmc.Select(
                                id="builder-sport-select",
                                label="Sport",
                                data=sport_options,
                                value="mlb",
                                w=200,
                            ),
                            dmc.NumberInput(
                                id="builder-season-input",
                                label="Season Year",
                                value=2023,
                                min=1871,
                                max=2024,
                                w=150,
                            ),
                            dmc.Select(
                                id="builder-data-type",
                                label="Data Type",
                                data=[{"value": "teams", "label": "Teams"}],
                                value="teams",
                                w=200,
                            ),
                            dmc.Button(
                                "Next: Add Filters →",
                                id="step-0-next",
                                color="blue",
                                rightSection=DashIconify(icon="mdi:arrow-right", width=16),
                            ),
                        ],
                    ),
                ),
            ),
            html.Div(
                id="step-filters",
                style={"display": "none"},
                children=dmc.Paper(
                    p="lg",
                    withBorder=True,
                    radius="md",
                    children=dmc.Stack(
                        gap="md",
                        children=[
                            dmc.Title("Add Filter Conditions", order=4),
                            dmc.Stack(id="filter-rows", gap="sm"),
                            dmc.Button(
                                "+ Add Filter",
                                id="add-filter-btn",
                                variant="outline",
                                size="sm",
                                color="blue",
                            ),
                            dmc.Group(
                                mt="sm",
                                children=[
                                    dmc.Button("← Back", id="step-1-back", variant="subtle"),
                                    dmc.Button(
                                        "Next: Transform →",
                                        id="step-1-next",
                                        color="blue",
                                        rightSection=DashIconify(icon="mdi:arrow-right", width=16),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ),
            html.Div(
                id="step-transform",
                style={"display": "none"},
                children=dmc.Paper(
                    p="lg",
                    withBorder=True,
                    radius="md",
                    children=dmc.Stack(
                        gap="md",
                        children=[
                            dmc.Title("Transform Data", order=4),
                            dmc.Textarea(
                                id="sort-column-input",
                                label="Sort by column (one column name)",
                                placeholder="e.g. wins",
                                rows=1,
                            ),
                            dmc.Switch(
                                id="sort-ascending-toggle",
                                label="Ascending order",
                                checked=False,
                            ),
                            dmc.Group(
                                mt="sm",
                                children=[
                                    dmc.Button("← Back", id="step-2-back", variant="subtle"),
                                    dmc.Button(
                                        "Next: Export →",
                                        id="step-2-next",
                                        color="blue",
                                        rightSection=DashIconify(icon="mdi:arrow-right", width=16),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ),
            html.Div(
                id="step-export",
                style={"display": "none"},
                children=dmc.Paper(
                    p="lg",
                    withBorder=True,
                    radius="md",
                    children=dmc.Stack(
                        gap="md",
                        children=[
                            dmc.Title("Export & Save", order=4),
                            dmc.Select(
                                id="builder-export-format",
                                label="Export Format",
                                data=format_options,
                                value="csv",
                                w=200,
                            ),
                            dmc.TextInput(
                                id="query-name-input",
                                label="Save Query As (optional)",
                                placeholder="My MLB 2023 Query",
                            ),
                            dmc.Group(
                                children=[
                                    dmc.Button("← Back", id="step-3-back", variant="subtle"),
                                    dmc.Button(
                                        "Save Query",
                                        id="save-query-btn",
                                        color="violet",
                                        variant="outline",
                                        leftSection=DashIconify(icon="ion:bookmark", width=16),
                                    ),
                                    dmc.Button(
                                        "Export Notebook",
                                        id="export-notebook-btn",
                                        color="orange",
                                        variant="outline",
                                        leftSection=DashIconify(icon="mdi:notebook", width=16),
                                    ),
                                    dmc.Button(
                                        "Download Data",
                                        id="builder-download-btn",
                                        color="green",
                                        leftSection=DashIconify(icon="mdi:download", width=16),
                                    ),
                                ]
                            ),
                            html.Div(id="builder-status"),
                        ],
                    ),
                ),
            ),
            dmc.Stack(
                gap="xs",
                children=[
                    dmc.Title("Generated Code", order=4),
                    html.Pre(
                        id="builder-code-preview",
                        className="code-preview",
                        children="# Configure your data above",
                    ),
                ],
            ),
            dcc.Download(id="builder-download"),
            dcc.Download(id="notebook-download"),
            dcc.Store(id="builder-filter-count", data=0),
        ],
    )


@callback(
    Output("step-select-data", "style"),
    Output("step-filters", "style"),
    Output("step-transform", "style"),
    Output("step-export", "style"),
    Output("builder-stepper", "active"),
    Output("builder-code-preview", "children"),
    Input("step-0-next", "n_clicks"),
    Input("step-1-next", "n_clicks"),
    Input("step-1-back", "n_clicks"),
    Input("step-2-next", "n_clicks"),
    Input("step-2-back", "n_clicks"),
    Input("step-3-back", "n_clicks"),
    State("builder-sport-select", "value"),
    State("builder-season-input", "value"),
    State("builder-stepper", "active"),
    prevent_initial_call=True,
)
def navigate_steps(s0n, s1n, s1b, s2n, s2b, s3b, sport, season, current_step):
    """Handle stepper navigation."""
    triggered = ctx.triggered_id
    step = current_step or 0

    if triggered == "step-0-next":
        step = 1
    elif triggered == "step-1-next":
        step = 2
    elif triggered == "step-1-back":
        step = 0
    elif triggered == "step-2-next":
        step = 3
    elif triggered == "step-2-back":
        step = 1
    elif triggered == "step-3-back":
        step = 2

    show = {"display": "block"}
    hide = {"display": "none"}
    vis = [hide, hide, hide, hide]
    vis[step] = show

    _gen.clear()
    if step >= 1 and sport:
        _gen.add_action(CodeAction("load_teams", {"sport": sport, "season": season}))
    code = _gen.generate_script() if _gen.actions else "# Configure your data above"

    return vis[0], vis[1], vis[2], vis[3], step, code


@callback(
    Output("filter-rows", "children"),
    Output("builder-filter-count", "data"),
    Input("add-filter-btn", "n_clicks"),
    State("builder-filter-count", "data"),
    prevent_initial_call=True,
)
def add_filter_row(n_clicks, count):
    """Add a new filter row to the UI."""
    operator_options = [{"value": op, "label": op} for op in OPERATORS]
    new_row = dmc.Group(
        id={"type": "filter-row", "index": count},
        gap="sm",
        children=[
            dmc.TextInput(
                id={"type": "filter-col", "index": count},
                placeholder="column",
                w=160,
            ),
            dmc.Select(
                id={"type": "filter-op", "index": count},
                data=operator_options,
                value="==",
                w=120,
            ),
            dmc.TextInput(
                id={"type": "filter-val", "index": count},
                placeholder="value",
                w=160,
            ),
        ],
    )
    return [new_row], count + 1


@callback(
    Output("save-query-btn", "children"),
    Output("builder-status", "children"),
    Input("save-query-btn", "n_clicks"),
    State("query-name-input", "value"),
    State("builder-sport-select", "value"),
    State("builder-season-input", "value"),
    prevent_initial_call=True,
)
def save_builder_query(n_clicks, name, sport, season):
    """Save the current builder configuration as a query."""
    qname = name or f"{(sport or 'mlb').upper()} {season or ''} Query"
    q = SavedQuery(
        name=qname,
        sport=sport or "mlb",
        season=int(season) if season else None,
        code_actions=_gen.to_dict().get("actions", []),
    )
    _qm.save_query(q)
    return "Saved ✓", dmc.Alert(f"Query '{qname}' saved!", color="green")


@callback(
    Output("notebook-download", "data"),
    Input("export-notebook-btn", "n_clicks"),
    State("builder-sport-select", "value"),
    State("builder-season-input", "value"),
    prevent_initial_call=True,
)
def export_notebook(n_clicks, sport, season):
    """Export the current pipeline as a Jupyter notebook."""
    import json

    _gen.clear()
    if sport:
        _gen.add_action(CodeAction("load_teams", {"sport": sport, "season": season}))
    nb = _gen.generate_notebook()
    content = json.dumps(nb, indent=2)
    return {"content": content, "filename": "sportsipy_query.ipynb", "type": "application/json"}
