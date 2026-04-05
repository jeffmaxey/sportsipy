"""Saved Queries page - browse and manage saved queries."""
import logging

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html, no_update
from dash_iconify import DashIconify

from sportsipy_dashboard.utils.code_generator import CodeGenerator
from sportsipy_dashboard.utils.query_manager import QueryManager

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/queries", title="Saved Queries – Sportsipy Dashboard")

_qm = QueryManager()


def _queries_to_rows(queries) -> list[dict]:
    """Convert SavedQuery objects to AG Grid row dicts."""
    return [
        {
            "id": q.id,
            "name": q.name,
            "sport": q.sport.upper(),
            "season": q.season or "latest",
            "filters": len(q.filters),
            "columns": len(q.columns),
            "updated_at": q.updated_at[:10],
        }
        for q in queries
    ]


COL_DEFS = [
    {"field": "name", "headerName": "Query Name", "flex": 2},
    {"field": "sport", "headerName": "Sport", "flex": 1},
    {"field": "season", "headerName": "Season", "flex": 1},
    {"field": "filters", "headerName": "Filters", "flex": 1},
    {"field": "columns", "headerName": "Columns", "flex": 1},
    {"field": "updated_at", "headerName": "Last Updated", "flex": 1},
]


def layout(**kwargs) -> dmc.Stack:
    """Render the saved queries page."""
    queries = _qm.load_queries()
    rows = _queries_to_rows(queries)

    return dmc.Stack(
        gap="md",
        children=[
            dmc.Group(
                justify="space-between",
                children=[
                    dmc.Title("Saved Queries", order=2),
                    dmc.Group(
                        gap="sm",
                        children=[
                            dmc.Button(
                                "Delete Selected",
                                id="delete-query-btn",
                                color="red",
                                variant="outline",
                                leftSection=DashIconify(icon="mdi:delete", width=16),
                            ),
                            dmc.Button(
                                "Load Selected",
                                id="load-query-btn",
                                color="blue",
                                leftSection=DashIconify(icon="mdi:play", width=16),
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(id="queries-alert"),
            dag.AgGrid(
                id="queries-grid",
                rowData=rows,
                columnDefs=COL_DEFS,
                defaultColDef={"sortable": True, "filter": True, "resizable": True, "flex": 1},
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": 15,
                    "rowSelection": "single",
                    "animateRows": True,
                },
                style={"height": "400px"},
            ),
            dmc.Paper(
                id="query-detail-panel",
                p="lg",
                withBorder=True,
                radius="md",
                style={"display": "none"},
                children=dmc.Stack(
                    gap="sm",
                    children=[
                        dmc.Title("Query Details", order=4),
                        dmc.Text(id="query-detail-name", fw=600),
                        dmc.Text(id="query-detail-meta", c="dimmed", size="sm"),
                        dmc.Title("Generated Code", order=5, mt="sm"),
                        html.Pre(
                            id="query-detail-code",
                            className="code-preview",
                        ),
                    ],
                ),
            ),
        ],
    )


@callback(
    Output("query-detail-panel", "style"),
    Output("query-detail-name", "children"),
    Output("query-detail-meta", "children"),
    Output("query-detail-code", "children"),
    Input("queries-grid", "selectedRows"),
    prevent_initial_call=True,
)
def show_query_details(selected_rows):
    """Show details for the selected query."""
    if not selected_rows:
        return {"display": "none"}, "", "", ""

    query_id = selected_rows[0].get("id", "")
    query = _qm.get_query(query_id)
    if not query:
        return {"display": "none"}, "", "", ""

    gen = CodeGenerator.from_dict({"actions": query.code_actions})
    code = gen.generate_script() if gen.actions else "# No actions recorded"

    meta = f"Sport: {query.sport.upper()} | Season: {query.season or 'latest'} | Saved: {query.updated_at[:10]}"
    return {"display": "block"}, query.name, meta, code


@callback(
    Output("queries-grid", "rowData"),
    Output("queries-alert", "children"),
    Input("delete-query-btn", "n_clicks"),
    State("queries-grid", "selectedRows"),
    prevent_initial_call=True,
)
def delete_selected_query(n_clicks, selected_rows):
    """Delete the selected query and refresh the grid."""
    if not selected_rows:
        return no_update, dmc.Alert("Select a query to delete.", color="yellow")

    query_id = selected_rows[0].get("id", "")
    deleted = _qm.delete_query(query_id)
    queries = _qm.load_queries()
    rows = _queries_to_rows(queries)
    if deleted:
        return rows, dmc.Alert("Query deleted.", color="green")
    return rows, dmc.Alert("Query not found.", color="red")


@callback(
    Output("queries-alert", "children", allow_duplicate=True),
    Input("load-query-btn", "n_clicks"),
    State("queries-grid", "selectedRows"),
    prevent_initial_call=True,
)
def load_selected_query(n_clicks, selected_rows):
    """Redirect to explorer with the selected query loaded."""
    if not selected_rows:
        return dmc.Alert("Select a query to load.", color="yellow")
    return dmc.Alert("Use the Explorer page to run queries interactively.", color="blue")
