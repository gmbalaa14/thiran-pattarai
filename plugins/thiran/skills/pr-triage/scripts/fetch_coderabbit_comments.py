#!/usr/bin/env python3
"""
Fetch unsolved CodeRabbit comments from an Azure DevOps PR.
Returns JSON with comment details: id, file, line, severity, description, prompt_for_ai_agents (if available)
"""

import sys
import json
import os
from typing import Optional
import base64
from urllib.request import Request, urlopen
from urllib.error import URLError


def get_ado_pat() -> str:
    """Get Azure DevOps PAT from environment or config."""
    # Try environment variable first
    pat = os.getenv("ADO_PAT")
    if pat:
        return pat

    # Try user-scoped config file (~/.claude/config.json)
    user_config_path = os.path.expanduser("~/.claude/config.json")
    if os.path.exists(user_config_path):
        try:
            with open(user_config_path) as f:
                config = json.load(f)
                pat = config.get("ado_pat")
                if pat:
                    return pat
        except Exception as e:
            print(f"Error reading {user_config_path}: {e}", file=sys.stderr)

    # Try repo-scoped config file (./.claude/config.json)
    config_path = os.path.join(os.getcwd(), ".claude", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                pat = config.get("ado_pat")
                if pat:
                    return pat
        except Exception as e:
            print(f"Error reading config.json: {e}", file=sys.stderr)

    # Not found
    return None


def parse_pr_url(pr_input: str) -> tuple:
    """
    Parse PR number or full URL.
    Returns (org, project, repo, pr_number) or raises error.

    Supports:
    - Just PR number: "1234" (requires org/project/repo in ~/.claude/config.json)
    - Full URL: "https://dev.azure.com/org/project/_git/repo/pullrequest/1234"
    """
    if pr_input.startswith("http"):
        # Parse URL
        # Format: https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{pr_number}
        parts = pr_input.strip("/").split("/")
        try:
            org = parts[3]
            project = parts[4]
            repo = parts[6]
            pr_number = parts[8]
            return org, project, repo, pr_number
        except (IndexError, ValueError):
            raise ValueError(f"Invalid Azure DevOps URL format: {pr_input}")
    else:
        # Just PR number - try to get org/project/repo from config
        config_path = os.path.expanduser("~/.claude/config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    org = config.get("ado_org")
                    project = config.get("ado_project")
                    repo = config.get("ado_repo")

                    if org and project and repo:
                        return org, project, repo, pr_input
            except Exception:
                pass

        raise ValueError(
            "PR number alone requires org/project/repo in ~/.claude/config.json\n"
            "Add this to ~/.claude/config.json:\n"
            '{\n'
            '  "ado_org": "YourOrg",\n'
            '  "ado_project": "YourProject",\n'
            '  "ado_repo": "YourRepo",\n'
            '  "ado_pat": "your-pat-token"\n'
            '}\n\n'
            "Or provide the full PR URL: https://dev.azure.com/org/project/_git/repo/pullrequest/pr_number"
        )


def fetch_comments(org: str, project: str, repo: str, pr_number: str, pat: str) -> list:
    """
    Fetch unsolved CodeRabbit comments from Azure DevOps PR.
    """
    base_url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullrequests/{pr_number}"

    # Fetch PR threads (comments)
    threads_url = f"{base_url}/threads?api-version=7.0"

    # Basic auth with PAT
    credentials = base64.b64encode(f":{pat}".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}"}

    try:
        req = Request(threads_url, headers=headers)
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
    except URLError as e:
        raise RuntimeError(f"Failed to fetch PR threads: {e}")

    comments = []

    for thread in data.get("value", []):
        # Skip resolved/fixed/closed threads (ADO CommentThreadStatus:
        # Unknown=0, Active=1, Fixed=2, WontFix=3, Closed=4, ByDesign=5, Pending=6)
        thread_status = thread.get("status")
        if thread_status in (2, 3, 4, 5, "fixed", "wontFix", "closed", "byDesign"):
            continue

        thread_context = thread.get("threadContext", {})
        comments_list = thread.get("comments", [])

        if not comments_list:
            continue

        # Check if ANY comment in the thread is from CodeRabbit
        # CodeRabbit can be in any nested reply, not just the top comment
        has_coderabbit = False
        coderabbit_comment = None

        for comment in comments_list:
            content = comment.get("content", "")
            author = comment.get("author", {}).get("displayName", "")

            # Check if this comment is from CodeRabbit
            if author == "CodeRabbit" or "CodeRabbit" in content:
                has_coderabbit = True
                coderabbit_comment = comment
                break

        # Use the first comment for context; if CodeRabbit replied, use that content
        first_comment = comments_list[0]

        if coderabbit_comment:
            content = coderabbit_comment.get("content", "")
            author = coderabbit_comment.get("author", {}).get("displayName", "") if coderabbit_comment.get("author") else "CodeRabbit"
        else:
            # Non-CodeRabbit comment (manual reviewer)
            content = first_comment.get("content", "")
            author = first_comment.get("author", {}).get("displayName", "")

        # Skip system authors (Azure DevOps system messages)
        if author == "Microsoft.VisualStudio.Services.TFS":
            continue

        if not content:
            continue

        # Extract comment info
        try:
            right_start = thread_context.get("rightFileStart") if thread_context else None
            left_start = thread_context.get("leftFileStart") if thread_context else None

            line_number = None
            if right_start and isinstance(right_start, dict):
                line_number = right_start.get("line")
            if not line_number and left_start and isinstance(left_start, dict):
                line_number = left_start.get("line")

            comment_info = {
                "id": thread.get("id"),
                "file": thread_context.get("filePath", "Unknown") if thread_context else "Unknown",
                "line": line_number,
                "content": content,
                "status": "Pending",
                "author": author,
                "created_date": thread.get("publishedDate") or coderabbit_comment.get("publishedDate") if coderabbit_comment else None,
                "updated_date": thread.get("lastUpdatedDate"),
                "description": extract_description(content),
            }

            # Severity: CodeRabbit gets parsed, non-CodeRabbit forced to Critical
            if has_coderabbit:
                severity = extract_severity(content) if content else None
                comment_info["severity"] = severity or "Unknown"
            else:
                comment_info["severity"] = "Critical"

            # Try to extract "Prompt for AI Agents" section or fallback to description
            prompt_for_ai = extract_prompt_for_ai(content) if content else None
            also_applies_to = extract_also_applies_to(content) if content else None

            # Append "Also applies to" to the prompt if present
            if prompt_for_ai and also_applies_to:
                prompt_for_ai = f"{prompt_for_ai}\n\n{also_applies_to}"
            elif also_applies_to:
                prompt_for_ai = also_applies_to

            comment_info["prompt_for_ai_agents"] = prompt_for_ai

            comments.append(comment_info)
        except Exception as e:
            # Skip this comment if there's an error processing it
            continue

    # Sort by creation date (earliest first)
    comments.sort(key=lambda c: c.get("created_date") or "", reverse=False)

    return comments


def extract_also_applies_to(content: str) -> Optional[str]:
    """Extract the 'Also applies to' line if present."""
    if not content:
        return None

    import re

    # Look for "Also applies to" line before first <details> tag
    match = re.search(r'\*\*Also applies to:\s*([^*\n<]+)\*\*', content)
    if match:
        return f"Also applies to: {match.group(1).strip()}"

    # Alternative format without bold
    match = re.search(r'Also applies to:\s*([^<\n]+)', content)
    if match:
        return f"Also applies to: {match.group(1).strip()}"

    return None


def extract_description(content: str) -> Optional[str]:
    """Extract full description: all text before first <details> tag, cleaned."""
    if not content:
        return None

    import re

    # Extract text before first <details> tag (entire main description section)
    match = re.search(r'^(.*?)(?=<details|$)', content, re.DOTALL)
    if match:
        section = match.group(1).strip()
    else:
        section = content.strip()

    # Split into lines
    lines = section.split('\n')

    # Collect all non-empty lines, skip "Also applies to" section
    description_lines = []
    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines
        if not line_stripped:
            continue

        # Skip "Also applies to" lines
        if line_stripped.startswith("Also applies to"):
            continue

        # Skip pure formatting lines
        if line_stripped.startswith("**") and not any(c.isalnum() for c in line_stripped):
            continue

        description_lines.append(line_stripped)

    result = ' '.join(description_lines).strip()

    # Clean up markdown formatting
    result = re.sub(r'\*\*(.+?)\*\*', r'\1', result)  # Remove **bold**
    result = re.sub(r'_(.+?)_', r'\1', result)  # Remove _italic_
    result = re.sub(r'\s+', ' ', result)  # Normalize whitespace

    return result if result else None


def extract_severity(content: str) -> Optional[str]:
    """Extract severity from Azure DevOps CodeRabbit comment.

    Looks for severity text in the first line (where CodeRabbit badge appears).
    Checks for: Critical, Major, Minor, Trivial, Info (case-insensitive).
    """
    if not content:
        return None

    # Check first line only (where severity badge appears)
    first_line = content.split("\n")[0].lower()

    # Check in order: Critical, Major, Minor, Trivial, Info
    # (return first match to avoid misclassification)
    if "critical" in first_line:
        return "Critical"
    elif "major" in first_line:
        return "Major"
    elif "minor" in first_line:
        return "Minor"
    elif "trivial" in first_line:
        return "Trivial"
    elif "info" in first_line:
        return "Info"

    return None


def extract_prompt_for_ai(content: str) -> Optional[str]:
    """Extract the EXACT prompt text from the 'Prompt for AI Agents' details section.

    In Azure DevOps, CodeRabbit comments have a collapsible "Prompt for AI Agents" section
    containing the exact prompt wrapped in a code block (```).
    """
    import re

    if not content:
        return None

    # Look for the prompt between <details> and </details>, inside code blocks
    # Pattern: <details>...Prompt for AI Agents...</summary>\n```\n(prompt text)\n```\n</details>
    match = re.search(r'<details>.*?Prompt for AI Agents.*?</summary>\s*\n\s*```\n(.*?)\n```\s*</details>', content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: look for markdown code block after "Prompt for AI Agents" (for non-HTML format)
    match = re.search(r'Prompt for AI Agents[^`]*```\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def merge_existing_statuses(comments: list, existing_report_path: str) -> tuple:
    """
    Merge statuses from existing report into fresh comments by ID, and preserve old comments.

    Returns: (merged_comments, merge_warning_or_None, generated_at_or_None)

    Behavior:
    - Fresh comments get matched by ID and update severity/description from fresh fetch
    - Existing status/verdict is preserved
    - Old comments NOT in fresh fetch are appended to preserve prior triage work
    - The original report's generation timestamp is preserved (not reset on refresh)
    """
    if not existing_report_path or not os.path.exists(existing_report_path):
        return comments, f"Report path not found: {existing_report_path}", None

    try:
        # Import extract_report_data to reuse its logic
        sys.path.insert(0, os.path.dirname(__file__))
        from extract_report_data import extract_report_data

        extracted = extract_report_data(existing_report_path)
        if not extracted.get("success"):
            return comments, f"Failed to extract report: {extracted.get('error')}", None

        # Build a map of existing comments by ID with their full data + status/verdict
        existing_by_id = {}
        for comment in extracted.get("all_comments", []):
            comment_id = comment.get("id")
            if comment_id:
                existing_by_id[comment_id] = comment

        # Set to track which IDs appear in fresh comments
        fresh_ids = set()

        # Merge existing statuses into fresh comments
        for comment in comments:
            comment_id = comment.get("id")
            fresh_ids.add(comment_id)

            if comment_id in existing_by_id:
                existing = existing_by_id[comment_id]
                # Update status/verdict from existing report
                comment["status"] = existing.get("status", "Pending")
                comment["pr_judge_assessment"] = existing.get("pr_judge_assessment")
                comment["user_decision"] = existing.get("user_decision")
                comment["fix_summary"] = existing.get("fix_summary", "")
            else:
                # New comment, keep Pending status and empty fix_summary
                if "status" not in comment:
                    comment["status"] = "Pending"
                if "fix_summary" not in comment:
                    comment["fix_summary"] = ""

        # Append old comments that aren't in fresh fetch (resolved/archived comments)
        old_not_in_fresh = []
        for comment_id, old_comment in existing_by_id.items():
            if comment_id not in fresh_ids:
                # Preserve the old comment with all its data and status
                old_not_in_fresh.append(old_comment)

        # Merge old comments at the end
        comments.extend(old_not_in_fresh)

        return comments, None, extracted.get("generated_at")

    except Exception as e:
        return comments, f"Merge failed: {str(e)}", None


if __name__ == "__main__":
    # Usage: python fetch_coderabbit_comments.py <pr_url_or_number> [existing_report_path]
    if len(sys.argv) < 2:
        print("Usage: fetch_coderabbit_comments.py <pr_url_or_number> [existing_report_path]", file=sys.stderr)
        sys.exit(1)

    pr_input = sys.argv[1]
    existing_report_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Get PAT
    pat = get_ado_pat()
    if not pat:
        print(json.dumps({"error": "ADO_PAT not found. Set ADO_PAT env var or .claude/config.json"}), file=sys.stderr)
        sys.exit(1)

    try:
        org, project, repo, pr_number = parse_pr_url(pr_input)
        comments = fetch_comments(org, project, repo, pr_number, pat)
        pr_url = f"https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{pr_number}"

        # Merge existing statuses if report path provided (Refresh mode)
        merge_warning = None
        generated_at = None
        if existing_report_path:
            comments, merge_warning, generated_at = merge_existing_statuses(comments, existing_report_path)

        result = {
            "success": True,
            "pr_number": pr_number,
            "pr_url": pr_url,
            "all_comments": comments
        }

        if merge_warning:
            result["merge_warning"] = merge_warning

        if generated_at:
            result["generated_at"] = generated_at

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)
