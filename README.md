# Open Home Cleaning Checklists

Free, reusable residential cleaning checklists in CSV, JSON, Markdown, and printable PDF formats.

This repository is designed for homeowners, cleaners, property managers, and software teams that need a practical starting point for defining cleaning scope. Adapt it to your service model, local requirements, home condition, and safety policies.

## What's included

- Routine or recurring cleaning checklist
- Deep cleaning checklist
- Move-in or move-out cleaning checklist
- Room-by-room task library
- Optional add-ons and exclusions
- Blank CSV template
- Printable one-page scope checklist
- Dirt Code 1-10 home-condition guide
- Machine-readable CSV and JSON data

## Quick downloads

- [Printable one-page cleaning checklist](printables/shiny-go-clean-one-page-checklist.pdf)
- [Printable Dirt Code condition guide](printables/dirt-code-condition-guide.pdf)
- [Complete checklist CSV](data/cleaning-checklists.csv)
- [Complete checklist JSON](data/cleaning-checklists.json)
- [Blank checklist template](templates/blank-cleaning-checklist.csv)

## Status values

| Value | Meaning |
| --- | --- |
| `included` | Included in the selected cleaning scope |
| `optional` | Optional add-on or custom-scope item |
| `not_included` | Not included in the selected cleaning scope |

## Dirt Code guidance

The Dirt Code is a simple 1-10 condition scale:

- Scores 1-4: maintained or light condition
- Score 5: review whether a deep clean is a better fit
- Scores 6-9: request photos before confirming scope
- Score 10: use an appropriately qualified specialist

It is a conversation aid, not an industry standard, safety assessment, or substitute for an onsite evaluation.

## Use the data

```python
import json

with open("data/cleaning-checklists.json") as file:
    checklist = json.load(file)

included_in_deep_clean = [
    task for task in checklist["tasks"]
    if task["deep"] == "included"
]
```

## Customize it

1. Copy the CSV, JSON, or Markdown file closest to your use case.
2. Confirm which tasks are included, optional, or excluded.
3. Add your own access, safety, supply, and quality-control rules.
4. Review the scope with the customer before work begins.
5. Keep pricing and service promises separate unless your business has approved them.

## Source and attribution

Created and maintained by [Shiny Go Clean](https://www.shinygoclean.com/), a residential cleaning company serving Madison and Dane County, Wisconsin.

The public checklist is informed by Shiny Go Clean's field-tested [residential cleaning checklist](https://www.shinygoclean.com/checklist).

## License

The checklist content, data, and printables are licensed under [Creative Commons Attribution 4.0 International](LICENSE). You may copy and adapt them, including commercially, with appropriate attribution.

## Disclaimer

This repository provides editable examples, not legal, safety, insurance, employment, or pricing advice. Users are responsible for verifying their own scope, claims, worker practices, chemical handling, access rules, and local requirements.
