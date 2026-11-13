"""Run `python app.py`, then open http://127.0.0.1:8050.

Data loading lives in data.py, chart builders in charts.py, and HTML in layout.py.
This file connects user interactions to those chart builders with Dash callbacks.
"""

from statistics import mean
from dash import Dash, Input, Output, State, ctx
from data import ROOT, ROWS
from charts import build_scatter, build_speed, build_total
from layout import layout

app = Dash(
    __name__, assets_folder=str(ROOT / "assets"), title="Pokémon Master Explorer"
)
app.layout = layout


def filter_rows(primary_type, generation):
    """Apply the two dropdown filters before applying a chart selection."""
    return [
        row
        for row in ROWS
        if (not primary_type or row["Type 1"] == primary_type)
        and (not generation or row["Generation"] == generation)
    ]


@app.callback(
    Output("type", "value"),
    Output("generation", "value"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    """Return both dropdowns to their initial values."""
    return "", ""


@app.callback(
    Output("selected", "data"),
    Input("scatter", "selectedData"),
    Input("scatter", "clickData"),
    Input("speed", "clickData"),
    Input("total", "clickData"),
    Input("type", "value"),
    Input("generation", "value"),
    Input("reset", "n_clicks"),
    State("selected", "data"),
    prevent_initial_call=True,
)
def select(
    scatter_selection,
    scatter_click,
    speed_click,
    total_click,
    primary_type,
    generation,
    _,
    previous,
):
    # Dropdown changes and Reset clear the chart selection.
    triggered = ctx.triggered_prop_ids
    if any(
        k in triggered for k in ["type.value", "generation.value", "reset.n_clicks"]
    ):
        return None
    filtered_rows = filter_rows(primary_type, generation)
    event = ctx.triggered[0]["prop_id"]
    if event == "scatter.selectedData":
        if not scatter_selection or not scatter_selection.get("points"):
            return previous
        selected_ids = [p["customdata"][0] for p in scatter_selection["points"]]
        return {"origin": "scatter", "ids": selected_ids, "label": "Scatter selection"}
    if event == "scatter.clickData" and scatter_click:
        point = scatter_click["points"][0]["customdata"]
        return {"origin": "scatter", "ids": [point[0]], "label": point[1]}
    if event == "speed.clickData" and speed_click:
        type_name = speed_click["points"][0]["y"]
        return {
            "origin": "speed",
            "ids": [row["id"] for row in filtered_rows if row["Type 1"] == type_name],
            "label": type_name,
        }
    if event == "total.clickData" and total_click:
        generation_number = int(total_click["points"][0]["x"])
        return {
            "origin": "total",
            "ids": [
                row["id"]
                for row in filtered_rows
                if row["Generation"] == generation_number
            ],
            "label": f"Generation {generation_number}",
        }
    return previous


@app.callback(
    Output("scatter", "figure"),
    Output("speed", "figure"),
    Output("total", "figure"),
    Output("count", "children"),
    Output("selection", "children"),
    Output("scatter-note", "children"),
    Output("speed-note", "children"),
    Output("total-note", "children"),
    Input("type", "value"),
    Input("generation", "value"),
    Input("selected", "data"),
)
def render(primary_type, generation, selected):
    filtered_rows = filter_rows(primary_type, generation)
    selected_ids = set(selected["ids"]) if selected else None
    selected_rows = [
        row
        for row in filtered_rows
        if selected_ids is None or row["id"] in selected_ids
    ]

    # Keep context in the chart that was clicked; filter the other two.
    def view(origin):
        return (
            filtered_rows
            if selected and selected["origin"] == origin
            else selected_rows
        )

    scatter_rows, speed_rows, total_rows = view("scatter"), view("speed"), view("total")
    scatter_fig = build_scatter(scatter_rows, selected, selected_ids)
    speed_fig, groups = build_speed(speed_rows, selected, selected_ids)
    total_fig = build_total(total_rows, selected, selected_ids)
    selection_text = (
        f"{selected['label']} · {len(selected_rows)} selected"
        if selected
        else f"{len(filtered_rows)} entries · {primary_type or 'all six types'} · {'generation ' + str(generation) if generation else 'all generations'}"
    )
    fastest = groups[-1] if groups else None
    speed_note = (
        f"{fastest[0]} has the highest mean Speed in this view: {mean(row['Speed'] for row in fastest[1]):.1f} (n={len(fastest[1])})."
        if fastest
        else "No entries in selection."
    )
    return (
        scatter_fig,
        speed_fig,
        total_fig,
        len(selected_rows),
        selection_text,
        f"{len(scatter_rows)} entries plotted."
        + (
            " Selection highlighted; other views show selected entries."
            if selected and selected["origin"] == "scatter"
            else ""
        ),
        speed_note,
        f"{len(total_rows)} entries · Box = middle 50%; line = median; dots = outliers.",
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
