from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict
from typing import Iterable

from .matcher import MatchResult
from .utils import ensure_directory


class ReportGenerator:
    def __init__(self, output_dir: str = "output/reports") -> None:
        self.output_dir = output_dir
        ensure_directory(self.output_dir)

    def to_json(self, results: Iterable[MatchResult], file_name: str = "report.json") -> str:
        path = os.path.join(self.output_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        return path

    def to_csv(self, results: Iterable[MatchResult], file_name: str = "report.csv") -> str:
        path = os.path.join(self.output_dir, file_name)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "is_vuln",
                    "reason",
                    "target_url",
                    "method",
                    "param",
                    "payload",
                    "status_base",
                    "status_new",
                    "len_base",
                    "len_new",
                ],
            )
            writer.writeheader()
            for r in results:
                writer.writerow(asdict(r))
        return path

    def to_html(self, results: Iterable[MatchResult], file_name: str = "report.html") -> str:
        path = os.path.join(self.output_dir, file_name)
        rows = []
        for r in results:
            rows.append(
                f"<tr><td>{r.is_vuln}</td><td>{r.reason}</td><td>{r.method}</td><td>{r.target_url}</td><td>{r.param}</td><td>{r.payload}</td><td>{r.status_base}</td><td>{r.status_new}</td><td>{r.len_base}</td><td>{r.len_new}</td></tr>"
            )
        html = f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>IDOR Finder Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; font-size: 13px; }}
    th {{ background: #f7f7f7; text-align: left; }}
    tr:nth-child(even) {{ background: #fafafa; }}
  </style>
  </head>
  <body>
    <h1>IDOR Finder Report</h1>
    <table>
      <thead>
        <tr><th>Vuln</th><th>Reason</th><th>Method</th><th>URL</th><th>Param</th><th>Payload</th><th>Base</th><th>New</th><th>Len Base</th><th>Len New</th></tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path


