#!/usr/bin/env python3
"""
Update a specific comment's status in the report and regenerate.
Usage: python update_comment_status.py <report_path> <comment_id> <status> <verdict> <decision> [<fix_summary>]

Args:
  <status>: "Resolved" | "Pending" | "Unresolved" | "Skipped"
  <verdict>: "valid" | "false_positive" | "partially_valid" | "uncertain" | "" (empty string if no pr-judge)
  <decision>: "accept_fix" | "write_rebuttal" | "ignore"
  <fix_summary>: Fix summary text (optional)
"""

import sys
import json
import re
import os
from datetime import datetime


def update_report(report_path: str, comment_id: int, status: str, verdict: str, decision: str, fix_summary: str = ""):
    """Update a specific comment by ID and regenerate report."""

    # Read current report
    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract technical info JSON - handle multiline JSON
    match = re.search(r'id="pr-triage-technical-info">\s*({.*?})\s*</script>', html_content, re.DOTALL)
    if not match:
        print(json.dumps({"success": False, "error": "Could not find technical info in report"}))
        sys.exit(1)

    try:
        json_str = match.group(1).strip()
        technical_info = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"Invalid JSON in report: {e}"}))
        sys.exit(1)

    # Ensure "comments" field exists
    if "comments" not in technical_info:
        technical_info["comments"] = []

    # Find and update the comment by ID
    updated = False
    for comment in technical_info.get("all_comments", []):
        if comment.get("id") == comment_id:
            comment["status"] = status
            comment["pr_judge_assessment"] = verdict  # Changed from pr_judge_verdict to match generate_report_react.py
            comment["user_decision"] = decision
            if fix_summary:
                comment["fix_summary"] = fix_summary
            updated = True

            # If not deferred, add to processed list (always keep in sync on every update)
            if status != "Deferred":
                # Remove any existing entry for this comment_id, then add the freshly-updated one
                technical_info["comments"] = [
                    c for c in technical_info.get("comments", []) if c.get("id") != comment_id
                ]
                technical_info["comments"].append(comment)
            break

    if not updated:
        print(json.dumps({"success": False, "error": f"Comment ID {comment_id} not found"}))
        sys.exit(1)

    # Regenerate report with updated data
    sys.path.insert(0, os.path.dirname(__file__))
    from generate_report_react import generate_react_report

    pr_number = technical_info.get("pr_number", "")

    html = generate_react_report(pr_number, technical_info, report_path)

    # Write back to same file
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Calculate updated counts
    status_counts = {}
    for comment in technical_info.get("all_comments", []):
        stat = comment.get("status", "Pending")
        status_counts[stat] = status_counts.get(stat, 0) + 1

    print(json.dumps({
        "success": True,
        "report_path": report_path,
        "updated_comment_id": comment_id,
        "counts": {
            "total": len(technical_info.get("all_comments", [])),
            "pending": status_counts.get("Pending", 0),
            "resolved": status_counts.get("Resolved", 0),
            "skipped": status_counts.get("Skipped", 0),
            "deferred": status_counts.get("Deferred", 0),
        }
    }))


if __name__ == "__main__":
    if len(sys.argv) < 6 or len(sys.argv) > 7:
        print(json.dumps({
            "success": False,
            "error": "Usage: python update_comment_status.py <report_path> <comment_id> <status> <verdict> <decision> [<fix_summary>]"
        }), file=sys.stderr)
        sys.exit(1)

    report_path = sys.argv[1]
    comment_id = int(sys.argv[2])
    status = sys.argv[3]  # "Resolved" | "Skipped" | "Deferred" | "Pending"
    verdict = sys.argv[4]  # "valid" | "false_positive" | "partially_valid" | "uncertain" | "" (empty if no pr-judge)
    decision = sys.argv[5]  # Usually same as status
    fix_summary = sys.argv[6] if len(sys.argv) > 6 else ""  # Optional fix_summary

    if not os.path.exists(report_path):
        print(json.dumps({"success": False, "error": f"Report file not found: {report_path}"}), file=sys.stderr)
        sys.exit(1)

    update_report(report_path, comment_id, status, verdict, decision, fix_summary)
