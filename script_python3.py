#!/usr/bin/env python3
# Python 3.6 compatible
# Generate WARNING / ERROR summary CSV + HTML (exclude INFO)
# EXECUTION-PATH BASED
# FORCE-FILL User Severity and solution placeholders

import csv
from pathlib import Path
import html
import sys

# ==================================================
# PATH CONFIG (MATCH SCRIPT 1 & 2)
# ==================================================
BASE_DIR = Path.cwd()
CSV_DIR  = BASE_DIR / "logs_report"
CSV_DIR.mkdir(parents=True, exist_ok=True)

KEEP_SEVERITY = {"WARNING", "ERROR"}

USER_SEVERITY_PLACEHOLDER = "[fill severity]"
SOLUTION_PLACEHOLDER      = "[fill solution]"

print("Reading CSVs from:", CSV_DIR)

# ==================================================
# HTML WRITER
# ==================================================
def write_summary_html(html_path, fieldnames, rows):
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='UTF-8'>\n")
        f.write(f"<title>{html.escape(html_path.name)}</title>\n")
        f.write("<style>\n")
        f.write("body { font-family: Arial, sans-serif; }\n")
        f.write("table { border-collapse: collapse; width: 100%; }\n")
        f.write("th, td { border: 1px solid #888; padding: 6px; vertical-align: top; }\n")
        f.write("th { background-color: #f0f0f0; }\n")
        f.write(".WARNING { background-color: #fff6cc; }\n")
        f.write(".ERROR { background-color: #ffd6d6; }\n")
        f.write("pre { white-space: pre-wrap; max-height: 320px; overflow-y: auto; }\n")
        f.write("</style></head><body>\n")

        f.write(f"<h2>{html.escape(html_path.name)}</h2>\n")
        f.write("<table>\n<tr>")

        for h in fieldnames:
            f.write(f"<th>{html.escape(h)}</th>")
        f.write("</tr>\n")

        for row in rows:
            sev = row.get("Severity", "").upper()
            f.write(f"<tr class='{sev}'>")

            for h in fieldnames:
                val = row.get(h, "")
                if h == "Description":
                    f.write(f"<td><pre>{html.escape(val)}</pre></td>")
                else:
                    f.write(f"<td>{html.escape(val)}</td>")

            f.write("</tr>\n")

        f.write("</table></body></html>")

# ==================================================
# MAIN
# ==================================================
csv_files = sorted(CSV_DIR.glob("*.csv"))

if not csv_files:
    print("No CSV files found in logs_report")
    sys.exit(0)

for csv_path in csv_files:
    if csv_path.name.endswith("_summary.csv"):
        continue

    print("\nProcessing:", csv_path.name)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        if not fieldnames or "Severity" not in fieldnames:
            print("  → SKIPPED (no Severity column)")
            continue

        rows = [
            r for r in reader
            if r.get("Severity", "").upper() in KEEP_SEVERITY
        ]

    if not rows:
        print("  → No WARNING / ERROR found")
        continue

    # --------------------------------------------------
    # Ensure columns exist + FORCE placeholders
    # --------------------------------------------------
    if "User Severity" not in fieldnames:
        fieldnames.append("User Severity")
    if "solution" not in fieldnames:
        fieldnames.append("solution")

    for r in rows:
        r["User Severity"] = USER_SEVERITY_PLACEHOLDER
        r["solution"]     = SOLUTION_PLACEHOLDER

    # --------------------------------------------------
    # Write summary CSV
    # --------------------------------------------------
    summary_csv = csv_path.with_name(csv_path.stem + "_summary.csv")
    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("  → Summary CSV written:", summary_csv.name)

    # --------------------------------------------------
    # Write summary HTML
    # --------------------------------------------------
    summary_html = csv_path.with_name(csv_path.stem + "_summary.html")
    write_summary_html(summary_html, fieldnames, rows)

    print("  → Summary HTML written:", summary_html.name)

print("\n✔ DONE: Script 3 summary generation complete")

