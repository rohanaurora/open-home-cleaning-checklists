#!/usr/bin/env python3
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
json_path = root / "data" / "cleaning-checklists.json"
csv_path = root / "data" / "cleaning-checklists.csv"

payload = json.loads(json_path.read_text())
rows = list(csv.DictReader(csv_path.open()))
assert payload["license"] == "CC-BY-4.0"
assert len(payload["tasks"]) == len(rows) >= 25
assert len(payload["dirt_code"]) == 10
assert [entry["score"] for entry in payload["dirt_code"]] == list(range(1, 11))
assert {task["routine"] for task in payload["tasks"]} <= {"included", "optional", "not_included"}
assert {task["deep"] for task in payload["tasks"]} <= {"included", "optional", "not_included"}
assert {task["move_in_out"] for task in payload["tasks"]} <= {"included", "optional", "not_included"}
assert rows == [{key: str(value) for key, value in task.items()} for task in payload["tasks"]]
for required in (
    root / "printables" / "shiny-go-clean-one-page-checklist.pdf",
    root / "printables" / "dirt-code-condition-guide.pdf",
    root / "templates" / "blank-cleaning-checklist.csv",
    root / "docs" / "index.html",
    root / "docs" / "downloads" / "shiny-go-clean-one-page-checklist.pdf",
    root / "docs" / "downloads" / "dirt-code-condition-guide.pdf",
    root / "docs" / "downloads" / "cleaning-checklists.csv",
    root / "docs" / "downloads" / "cleaning-checklists.json",
    root / "docs" / "downloads" / "blank-cleaning-checklist.csv",
):
    assert required.exists() and required.stat().st_size > 0, required
print(f"Validated {len(rows)} checklist tasks, 10 Dirt Code scores, and all published assets.")
