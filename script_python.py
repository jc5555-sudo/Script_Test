#!/usr/bin/env python3

import os
import csv
import re
import glob
import sys

# ==================================================
# CONFIGURATION (GLOBAL BEHAVIOR)
# ==================================================

# Execution directory (where user runs the script)
BASE_DIR = os.getcwd()

# Default: read logs from ./logs_fc relative to execution path
DEFAULT_LOG_PATTERN = os.path.join(BASE_DIR, 'logs_fc', '*.log')

# Allow user to override input pattern
LOG_PATTERN = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG_PATTERN

# Output always goes to ./logs_report relative to execution path
OUTPUT_DIR = os.path.join(BASE_DIR, 'logs_report')

HEADER = ['Code', 'Severity', 'Description', 'User Severity', 'rpt msg', 'solution']

# ==================================================
# SETUP
# ==================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

log_files = sorted(glob.glob(LOG_PATTERN))

if not log_files:
    print("ERROR: No .log files found")
    print("Looked for pattern:")
    print(f"  {LOG_PATTERN}")
    sys.exit(1)

print(f"Found {len(log_files)} log file(s)")
print(f"Input pattern : {LOG_PATTERN}")
print(f"Output dir    : {OUTPUT_DIR}")

# ==================================================
# PARSER
# ==================================================
def parse_log_file(log_file):
    rows = []

    try:
        with open(log_file, 'r', errors='ignore') as f:
            for line in f:
                line = line.strip()

                if line.startswith("Information:"):
                    m = re.search(
                        r'(\w+-\d+)\s+(INFO|WARNING|ERROR)\s+(.*)',
                        line
                    )
                    if m:
                        rows.append([
                            m.group(1),                 # Code
                            m.group(2).capitalize(),   # Severity
                            '',                         # Description (to be filled later)
                            '',                         # User Severity
                            m.group(3).strip(),         # rpt msg
                            ''                          # solution
                        ])
    except IOError as e:
        print(f"WARNING: Failed to read {log_file}: {e}")

    return rows

# ==================================================
# WRITERS
# ==================================================
def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

def write_html(path, rows, title):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('<html><head><meta charset="UTF-8">')
        f.write(f'<title>{title}</title>')
        f.write('</head><body>')
        f.write(f'<h2>{title}</h2>')
        f.write('<table border="1" cellpadding="4" cellspacing="0">')
        f.write('<tr>' + ''.join(f'<th>{h}</th>' for h in HEADER) + '</tr>')

        for row in rows:
            f.write('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>')

        f.write('</table></body></html>')

# ==================================================
# MAIN
# ==================================================
for log_path in log_files:
    filename = os.path.basename(log_path)
    base = os.path.splitext(filename)[0]

    print(f"\nProcessing: {log_path}")

    rows = parse_log_file(log_path)

    csv_path = os.path.join(OUTPUT_DIR, base + '.csv')
    html_path = os.path.join(OUTPUT_DIR, base + '.html')

    write_csv(csv_path, rows)
    write_html(html_path, rows, title=f"Log Report - {filename}")

    print(f"  → {base}.csv  ({len(rows)} rows)")
    print(f"  → {base}.html")

print("\n✔ All log files processed successfully")
