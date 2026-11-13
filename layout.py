"""Page structure: title, filters, three chart panels, and a short data guide."""

from dash import dcc, html
from data import TYPES, COLORS
from charts import CONFIG


def header(title):
    return html.Div(html.H2(title), className="panel-head")


def panel(title, hint, chart_id, note_id):
    return html.Section(
        [
            header(title),
            html.P(hint, className="hint"),
            dcc.Graph(id=chart_id, config=CONFIG, className="chart"),
            html.P(id=note_id, className="chart-note"),
        ],
        className="panel",
    )


layout = html.Main(
    [
        dcc.Store(id="selected"),
        html.Section(
            [
                html.Div(
                    [
                        html.P("Working prototype", className="eyebrow"),
                        html.H1("Pokémon Master Explorer"),
                        html.P(
                            "Compare base stats across six primary types and generations 1–6.",
                            className="subtitle",
                        ),
                    ]
                ),
                html.Div(
                    [html.Strong(id="count"), html.Span("of 433 entries")],
                    className="scope",
                ),
            ],
            className="intro",
        ),
        html.Section(
            [
                html.Label(
                    [
                        "Primary type",
                        dcc.Dropdown(
                            id="type",
                            options=[{"label": "All six types", "value": ""}]
                            + [{"label": t, "value": t} for t in TYPES],
                            value="",
                            clearable=False,
                        ),
                    ]
                ),
                html.Label(
                    [
                        "Generation",
                        dcc.Dropdown(
                            id="generation",
                            options=[{"label": "All generations", "value": ""}]
                            + [
                                {"label": f"Generation {g}", "value": g}
                                for g in range(1, 7)
                            ],
                            value="",
                            clearable=False,
                        ),
                    ]
                ),
                html.Div(id="selection", className="selection", role="status"),
                html.Button("Reset", id="reset", n_clicks=0),
            ],
            className="controls",
        ),
        html.Div(
            [
                html.Section(
                    [
                        header("Attack vs. defense"),
                        html.P(
                            "Drag a box to select Pokémon. Click a point for one entry. Hover for details.",
                            className="hint",
                        ),
                        html.Div(
                            [
                                html.Span([html.I(style={"background": COLORS[t]}), t])
                                for t in TYPES
                            ],
                            className="legend",
                        ),
                        dcc.Graph(id="scatter", config=CONFIG, className="chart"),
                        html.Div(
                            [
                                html.Span("Point area = HP"),
                                *[
                                    html.Span(
                                        [
                                            html.I(
                                                style={
                                                    "width": f"{s}px",
                                                    "height": f"{s}px",
                                                }
                                            ),
                                            f" {v}",
                                        ]
                                    )
                                    for s, v in [(9, 25), (18, 100), (27, 225)]
                                ],
                            ],
                            className="size-key",
                        ),
                        html.P(id="scatter-note", className="chart-note"),
                    ],
                    className="panel scatter-panel",
                ),
                html.Div(
                    [
                        panel(
                            "Average speed by type",
                            "Click a bar to select a type. Labels show mean and count.",
                            "speed",
                            "speed-note",
                        ),
                        panel(
                            "Total stats by generation",
                            "Click a box or outlier to select a generation.",
                            "total",
                            "total-note",
                        ),
                    ],
                    className="summaries",
                ),
            ],
            className="dashboard",
        ),
        html.Section(
            html.Details(
                [
                    html.Summary("Data & chart guide"),
                    html.Div(
                        [
                            html.P(
                                [
                                    "Source: Alberto Barradas, ",
                                    html.A(
                                        "Pokémon with stats",
                                        href="https://www.kaggle.com/datasets/abcsds/pokemon",
                                    ),
                                    ". Showing 433 entries across six primary types and generations 1–6. Alternate forms count separately.",
                                ]
                            ),
                            html.P(
                                "Color = primary type; point area = HP. Boxes show the middle 50% of Total stats, with a median line and outlier dots."
                            ),
                            html.P(
                                "Select points, a type bar, or a generation to update the other charts. A new selection replaces the previous one. Reset clears all filters."
                            ),
                        ],
                        className="about",
                    ),
                ]
            ),
            className="details",
        ),
        html.Footer(
            [
                html.Span("SOOHYEUK CHOI · CS-GY 6313 A"),
                html.Span("POKÉMON MASTER EXPLORER / MID SUBMISSION"),
            ]
        ),
    ]
)
