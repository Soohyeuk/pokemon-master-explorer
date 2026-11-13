"""Load the local CSV, convert numeric fields, and select the six proposed types."""

import csv
from pathlib import Path

ROOT = Path(__file__).parent
TYPES = ["Water", "Fire", "Grass", "Electric", "Normal", "Psychic"]
COLORS = dict(
    zip(TYPES, ["#327ca5", "#ce6537", "#43845a", "#a78a16", "#7a7372", "#a15d97"])
)
NUMERIC = [
    "#",
    "Total",
    "HP",
    "Attack",
    "Defense",
    "Sp. Atk",
    "Sp. Def",
    "Speed",
    "Generation",
]
with (ROOT / "data" / "Pokemon.csv").open(encoding="utf-8-sig", newline="") as f:
    ALL = list(csv.DictReader(f))
for i, row in enumerate(ALL):
    row["id"] = i
    for key in NUMERIC:
        row[key] = int(row[key])
    assert row["Total"] == sum(
        row[k] for k in ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    )
ROWS = [r for r in ALL if r["Type 1"] in TYPES]
assert len(ALL) == 800 and len(ROWS) == 433
assert len({r["#"] for r in ALL}) == 721
