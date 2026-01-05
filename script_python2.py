#!/usr/bin/env python3
# Python 3.6 compatible
# Enrich ALL CSV files using Fusion Compiler man pages
# Clean FC headers/footers/prompts
# Regenerate HTML from enriched CSV
# EXECUTION-PATH BASED, NO .bak FILES

import csv
import subprocess
import re
import sys
from pathlib import Path
import html

# ------------------------------------------------------------
# PATH CONFIG (MATCH SCRIPT 1)
# ------------------------------------------------------------
BASE_DIR = Path.cwd()
CSV_DIR  = BASE_DIR / "logs_report"
CSV_DIR.mkdir(parents=True, exist_ok=True)

print("Reading CSVs from:", CSV_DIR)

# ------------------------------------------------------------
# Clean MAN text: keep only NAME / DESCRIPTION / WHAT NEXT
# ------------------------------------------------------------
def clean_man_text(text):
    lines = text.splitlines()
    cleaned = []
    recording = False

    for line in lines:
        line = line.rstrip()

        if line.strip().startswith("fc_shell>"):
            continue
        if line.strip() == "NAME":
            recording = True
        if line.strip().startswith("Version "):
            break
        if recording:
            cleaned.append(line)

    return "\n".join(cleaned).strip()


def run_fc_man(codes):
    tcl_lines = []
    for c in codes:
        tcl_lines.append(f'puts "<<<CODE:{c}>>>"')
        tcl_lines.append(f'man {c}')
        tcl_lines.append('puts "<<<END>>>"')

    tcl_script = "\n".join(tcl_lines) + "\nexit\n"

    try:
        cmd = "echo '{}' | fc_shell -no_init -no_local_init".format(
            tcl_script.replace("'", "'\\''")
        )
        output = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        print("ERROR: Fusion Compiler failed")
        print(e.output)
        return {}

    man_db = {}
    for code, body in re.findall(r'<<<CODE:(.*?)>>>(.*?)<<<END>>>', output, re.S):
        man_db[code.strip()] = clean_man_text(body)

    return man_db


def write_html(csv_path, fieldnames, rows):
    html_path = csv_path.with_suffix(".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='UTF-8'>\n")
        f.write(f"<title>{csv_path.name}</title>\n")
        f.write("<style>\n")
        f.write("body { font-family: Arial, sans-serif; }\n")
        f.write("table { border-collapse: collapse; width: 100%; }\n")
        f.write("th, td { border: 1px solid #888; padding: 6px; vertical-align: top; }\n")
        f.write("th { background-color: #f0f0f0; }\n")
        f.write("pre { white-space: pre-wrap; max-height: 320px; overflow-y: auto; }\n")
        f.write("</style></head><body>\n")

        f.write(f"<h2>{html.escape(csv_path.name)}</h2>\n")
        f.write("<table>\n<tr>")
        for h in fieldnames:
            f.write(f"<th>{html.escape(h)}</th>")
        f.write("</tr>\n")

        for row in rows:
            f.write("<tr>")
            for h in fieldnames:
                val = row.get(h, "")
                if h == "Description":
                    f.write(f"<td><pre>{html.escape(val)}</pre></td>")
                else:
                    f.write(f"<td>{html.escape(val)}</td>")
            f.write("</tr>\n")

        f.write("</table>\n</body></html>")

    print("  → HTML written:", html_path)


# ------------------------------------------------------------
# MAIN FLOW
# ------------------------------------------------------------
csv_files = list(CSV_DIR.glob("*.csv"))

if not csv_files:
    print("No CSV files found in logs_report — nothing to enrich.")
    sys.exit(0)

for csv_path in csv_files:
    print("\nProcessing:", csv_path.name)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        if not fieldnames:
            print("  → SKIPPED (empty CSV)")
            continue
        if "Code" not in fieldnames or "Description" not in fieldnames:
            print("  → SKIPPED (missing Code / Description)")
            continue

        rows = list(reader)

    codes = sorted({
        r["Code"].strip()
        for r in rows
        if r.get("Code") and r["Code"].strip()
    })

    if not codes:
        print("  → No codes found")
        continue

    print(f"  → Running fc_shell for {len(codes)} codes")
    man_db = run_fc_man(codes)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        for row in rows:
            code = row["Code"].strip()
            if code in man_db:
                row["Description"] = man_db[code]
            writer.writerow(row)

    print("  → CSV updated:", csv_path.name)
    write_html(csv_path, fieldnames, rows)

print("\n✔ DONE: Script 2 enrichment complete")

