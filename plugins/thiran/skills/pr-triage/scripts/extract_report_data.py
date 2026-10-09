#!/usr/bin/env python3
"""
Extract technical information from pr-triage HTML report.
Usage: python extract_report_data.py <html_file_path>

Returns JSON with:
{
  "success": true,
  "pr_number": "...",
  "pr_url": "...",
  "all_comments": [...],
  "comments": [...]
}
"""

import sys
import json
import re
import os


def extract_report_data(html_path: str) -> dict:
    """Extract technical info from HTML report."""

    if not os.path.exists(html_path):
        return {
            "success": False,
            "error": f"Report not found: {html_path}"
        }

    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read file: {str(e)}"
        }

    # Extract JSON from <script type="application/json" id="pr-triage-technical-info">
    # Pattern: <script ...id="pr-triage-technical-info">...JSON...</script>
    pattern = r'<script[^>]*id="pr-triage-technical-info"[^>]*>(.*?)</script>'
    match = re.search(pattern, html_content, re.DOTALL)

    if not match:
        return {
            "success": False,
            "error": "Technical information section not found in HTML. Report may be corrupted or outdated."
        }

    try:
        json_str = match.group(1).strip()
        technical_info = json.loads(json_str)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse technical information JSON: {str(e)}"
        }

    # Validate structure
    if not isinstance(technical_info, dict):
        return {
            "success": False,
            "error": "Technical information is not a valid object"
        }

    required_fields = ["pr_number", "all_comments"]
    missing_fields = [f for f in required_fields if f not in technical_info]

    if missing_fields:
        return {
            "success": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }

    # Extract processing status for each comment
    all_comments = technical_info.get("all_comments", [])
    processed_comments = technical_info.get("comments", [])

    # Build status map from processed comments
    processed_ids = {c.get("id"): c for c in processed_comments}

    # Categorize comments
    # Resolved/Skipped are final; Deferred goes back to pending
    pending_comments = []
    completed_comments = []

    for comment in all_comments:
        comment_id = comment.get("id")
        processed_item = processed_ids.get(comment_id)

        # `comment["status"]` on all_comments is the single source of truth — the
        # processed list only enriches pr_judge_assessment/user_decision when this
        # ID was explicitly triaged. Never let processed-list membership override
        # (or reset) a status the comment already carries: that's what silently
        # flipped long-standing Resolved comments back to Pending on refresh,
        # because a comment can be marked Resolved in all_comments without being
        # in the processed list (e.g. by tooling predating update_comment_status.py,
        # the only script that keeps both lists in sync).
        if processed_item:
            comment["pr_judge_assessment"] = processed_item.get("pr_judge_assessment")
            comment["user_decision"] = processed_item.get("user_decision")
            status = comment.get("status") or processed_item.get("status", "Unknown")
        else:
            status = comment.get("status") or "Pending"

        comment["status"] = status

        # Only Resolved and Skipped are truly complete
        # Pending, Deferred, and Unresolved all go back to pending on resume
        if status in ("Resolved", "Skipped"):
            completed_comments.append(comment)
        else:  # Pending, Deferred, Unresolved
            pending_comments.append(comment)

    return {
        "success": True,
        "pr_number": technical_info.get("pr_number"),
        "pr_url": technical_info.get("pr_url"),
        "timestamp": technical_info.get("timestamp"),
        "generated_at": technical_info.get("generated_at"),
        "all_comments_count": len(all_comments),
        "completed_count": len(completed_comments),
        "pending_count": len(pending_comments),
        "all_comments": all_comments,
        "pending_comments": pending_comments,
        "completed_comments": completed_comments,
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python extract_report_data.py <html_file_path>"
        }))
        sys.exit(1)

    html_path = sys.argv[1]
    result = extract_report_data(html_path)
    print(json.dumps(result))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
