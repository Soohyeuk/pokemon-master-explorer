"""Build the three Plotly figures. These functions do not change dashboard state."""

from statistics import mean
import plotly.graph_objects as go
from data import TYPES, COLORS

CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "autoScale2d"],
}
AXIS = dict(gridcolor="#edf0eb", zeroline=False, tickfont=dict(size=10))


def figure(traces, **kwargs):
    fig = go.Figure(traces)
    fig.update_layout(
        font=dict(family="Arial", size=11, color="#596c62"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=52, r=18, t=12, b=45),
        **kwargs,
    )
    return fig


def build_scatter(scatter_rows, selected, selected_ids):
    """Attack vs. Defense: type controls color, and HP controls point area."""
    scatter = []
    for type_name in TYPES:
        subset = [row for row in scatter_rows if row["Type 1"] == type_name]
        selection_style = {}
        if selected and selected["origin"] == "scatter":
            selection_style.update(
                selectedpoints=[
                    i for i, row in enumerate(subset) if row["id"] in selected_ids
                ],
                selected=dict(marker=dict(opacity=1)),
                unselected=dict(marker=dict(opacity=0.12)),
            )
        scatter.append(
            go.Scatter(
                x=[row["Attack"] for row in subset],
                y=[row["Defense"] for row in subset],
                mode="markers",
                name=type_name,
                customdata=[
                    [
                        row["id"],
                        row["Name"],
                        type_name,
                        row["HP"],
                        row["Speed"],
                        row["Total"],
                        row["Generation"],
                    ]
                    for row in subset
                ],
                marker=dict(
                    size=[row["HP"] for row in subset],
                    sizemode="area",
                    sizeref=2 * 255 / (28 * 28),
                    color=COLORS[type_name],
                    opacity=0.72,
                    line=dict(color="white", width=0.7),
                ),
                hovertemplate="<b>%{customdata[1]}</b><br>%{customdata[2]} · Generation %{customdata[6]}<br>Attack %{x} · Defense %{y}<br>HP %{customdata[3]} · Speed %{customdata[4]}<br>Total %{customdata[5]}<extra></extra>",
                **selection_style,
            )
        )
    scatter_fig = figure(
        scatter,
        dragmode="select",
        clickmode="event",
        xaxis={**AXIS, "title": "Attack", "range": [0, 200], "dtick": 50},
        yaxis={**AXIS, "title": "Defense", "range": [0, 200], "dtick": 50},
    )
    return scatter_fig


def build_speed(speed_rows, selected, selected_ids):
    """Sort types by mean Speed and return the figure plus groups for its caption."""
    groups = [
        (type_name, [row for row in speed_rows if row["Type 1"] == type_name])
        for type_name in TYPES
    ]
    groups = sorted(
        [(type_name, type_rows) for type_name, type_rows in groups if type_rows],
        key=lambda item: mean(row["Speed"] for row in item[1]),
    )
    bars = go.Bar(
        x=[mean(row["Speed"] for row in type_rows) for type_name, type_rows in groups],
        y=[type_name for type_name, type_rows in groups],
        orientation="h",
        marker=dict(
            color=[COLORS[type_name] for type_name, type_rows in groups],
            opacity=[
                0.23
                if selected
                and selected["origin"] == "speed"
                and not any(row["id"] in selected_ids for row in type_rows)
                else 1
                for type_name, type_rows in groups
            ],
        ),
        text=[
            f"{mean(row['Speed'] for row in type_rows):.1f} · n={len(type_rows)}"
            for type_name, type_rows in groups
        ],
        textposition="outside",
        cliponaxis=False,
        customdata=[len(type_rows) for type_name, type_rows in groups],
        hovertemplate="<b>%{y}</b><br>Mean Speed %{x:.2f}<br>Entries %{customdata}<extra></extra>",
    )
    speed_fig = figure(
        [bars],
        bargap=0.36,
        xaxis={
            **AXIS,
            "title": "Average Speed",
            "range": [
                0,
                max(
                    [135]
                    + [
                        mean(row["Speed"] for row in type_rows) * 1.28
                        for _, type_rows in groups
                    ]
                ),
            ],
            "dtick": 25,
        },
        yaxis={
            **AXIS,
            "categoryorder": "array",
            "categoryarray": [type_name for type_name, type_rows in groups],
        },
    )
    speed_fig.update_layout(margin=dict(l=68, r=55, t=6, b=39))
    return speed_fig, groups


def build_total(total_rows, selected, selected_ids):
    """Compare Total distributions in generation order, retaining selection context."""
    boxes = []
    for generation_number in range(1, 7):
        subset = [row for row in total_rows if row["Generation"] == generation_number]
        boxes.append(
            go.Box(
                x=[generation_number] * len(subset),
                y=[row["Total"] for row in subset],
                name=str(generation_number),
                quartilemethod="linear",
                boxpoints="outliers",
                width=0.48,
                text=[f"{row['Name']} · {row['Type 1']}" for row in subset],
                fillcolor="#b7cbbb",
                line=dict(color="#3e6c51", width=1.5),
                marker=dict(color="#3e6c51", size=4),
                opacity=0.2
                if selected
                and selected["origin"] == "total"
                and not any(row["id"] in selected_ids for row in subset)
                else 1,
            )
        )
    total_fig = figure(
        boxes,
        xaxis={
            **AXIS,
            "title": "Generation",
            "range": [0.5, 6.5],
            "tickvals": list(range(1, 7)),
        },
        yaxis={**AXIS, "title": "Total base stats", "range": [150, 800], "dtick": 200},
    )
    return total_fig
