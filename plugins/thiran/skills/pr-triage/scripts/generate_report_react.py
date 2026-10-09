#!/usr/bin/env python3
"""
Generate React-based HTML report for CodeRabbit triage results.
Uses React from CDN for interactive expandable table with filters.
"""

import sys
import json
import os
from datetime import datetime


def generate_react_report(pr_number: str, results: dict, report_path: str = "") -> str:
    """Generate interactive React-based HTML report."""

    # Prepare data
    all_comments = results.get("all_comments", results.get("comments", []))

    # `comments` (the processed list) must reflect every comment whose status has
    # moved past Pending — refresh (fetch_coderabbit_comments.py) only ever
    # updates all_comments[].status and never maintains this list itself, so
    # deriving it here keeps status as the single source of truth. Without this,
    # extract_report_data.py (which treats `comments` membership as ground truth)
    # resets such comments back to Pending on the next read.
    explicit_processed = {c.get("id"): c for c in results.get("comments", [])}
    processed_comments = [
        explicit_processed.get(c.get("id"), c)
        for c in all_comments
        if c.get("status") not in (None, "Pending")
    ]
    pr_url = results.get("pr_url", "")

    # Create status map for processed comments
    processed_map = {c.get("id"): c for c in processed_comments}

    # Enrich all comments with status and fix_summary
    for comment in all_comments:
        comment_id = comment.get("id")
        if comment_id in processed_map:
            processed = processed_map[comment_id]
            comment["status"] = processed.get("status", "Pending")
            comment["pr_judge_assessment"] = processed.get("pr_judge_assessment")
            comment["user_decision"] = processed.get("user_decision")
            comment["fix_summary"] = processed.get("fix_summary", "")
        elif not comment.get("status"):
            comment["status"] = "Pending"

        # Ensure fix_summary exists (initialize if missing)
        if "fix_summary" not in comment:
            comment["fix_summary"] = ""

    # Count by severity and status
    severity_counts = {}
    status_counts = {}
    for c in all_comments:
        sev = c.get("severity", "Unknown")
        stat = c.get("status", "Pending")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        status_counts[stat] = status_counts.get(stat, 0) + 1

    # Prepare summary stats
    resolved_count = status_counts.get("Resolved", 0)
    skipped_count = status_counts.get("Skipped", 0)
    pending_count = status_counts.get("Pending", 0)
    unresolved_count = status_counts.get("Unresolved", 0)

    # Create technical info JSON for resume
    # Keep original generated_at if updating an existing report, otherwise set new one
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    generated_at = results.get("generated_at", current_time)  # Preserve original generation time on refresh

    summary_stats = {
        "total": len(all_comments),
        "processed": len(processed_comments),
        "pending": pending_count,
        "resolved": resolved_count,
        "skipped": skipped_count,
        "unresolved": unresolved_count,
        "severity": severity_counts,
        "status": status_counts,
        "generated_at": generated_at,
        "updated_at": current_time,
    }

    technical_info = {
        "pr_number": pr_number,
        "pr_url": pr_url,
        "generated_at": generated_at,
        "updated_at": current_time,
        "timestamp": current_time,
        "all_comments": all_comments,
        "comments": processed_comments,  # Changed from processed_comments to comments for consistency
    }

    # Escape JSON for embedding in HTML
    comments_json = json.dumps(all_comments)
    technical_json = json.dumps(technical_info)
    summary_json = json.dumps(summary_stats)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeRabbit Triage Report - PR {pr_number}</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        /* SweetAlert Toast Notification styling */
        .swal2-container {{
            z-index: 10000;
            padding: 0 !important;
        }}
        .swal2-toast {{
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            background: white;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            padding: 12px 16px;
            min-width: 280px;
        }}
        .swal2-toast.swal2-show {{
            animation: slideInRight 0.3s ease-out;
        }}
        @keyframes slideInRight {{
            from {{
                transform: translateX(400px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        .swal2-toast .swal2-icon {{
            width: 24px;
            height: 24px;
            margin: 0 12px 0 0;
        }}
        .swal2-toast .swal2-icon.swal2-success {{
            border: none;
            background-color: #28a745;
            color: white;
        }}
        .swal2-toast .swal2-icon.swal2-success .swal2-success-ring {{
            display: none;
        }}
        .swal2-toast .swal2-icon.swal2-success [class*='swal2-success-'] {{
            background-color: transparent;
        }}
        .swal2-toast .swal2-icon.swal2-error {{
            border: none;
            background-color: #dc3545;
            color: white;
        }}
        .swal2-toast .swal2-title {{
            color: #333;
            font-size: 14px;
            font-weight: 600;
            margin: 0;
        }}
        .swal2-toast .swal2-html-container {{
            color: #666;
            font-size: 13px;
            margin: 4px 0 0 0;
        }}
        .swal2-toast .swal2-close {{
            color: #999;
            font-size: 20px;
            top: 8px;
            right: 8px;
        }}
        .swal2-toast .swal2-close:hover {{
            color: #333;
        }}
        .swal2-timer-progress {{
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            height: 3px;
            border-radius: 0 0 8px 8px;
        }}
        .swal2-toast.swal2-icon-error .swal2-timer-progress {{
            background: linear-gradient(90deg, #dc3545 0%, #e74c3c 100%);
        }}
    </style>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef7 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .pr-info {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px 20px;
            margin-top: 15px;
            border-radius: 4px;
            font-size: 14px;
        }}

        .content {{
            padding: 40px;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .summary-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .summary-item strong {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .summary-item span {{
            font-size: 12px;
            color: #666;
        }}

        .card {{
            background: white;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            padding: 30px;
            margin-bottom: 20px;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .card-header h2 {{
            font-size: 20px;
            color: #333;
            margin: 0;
        }}

        .controls {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}

        .button:hover {{
            background: #5568d3;
        }}

        .button.secondary {{
            background: #6c757d;
        }}

        .button.secondary:hover {{
            background: #5a6268;
        }}

        .filters {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: flex-start;
        }}

        .filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex: 1;
            min-width: 250px;
        }}

        .filter-group label {{
            font-size: 13px;
            font-weight: 600;
            color: #333;
        }}

        .multiselect-container {{
            position: relative;
        }}

        .multiselect-input {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
            padding: 8px 12px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            min-height: 38px;
            transition: all 0.2s ease;
        }}

        .multiselect-input:hover {{
            border-color: #667eea;
        }}

        .multiselect-input.focused {{
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .multiselect-tag {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: #e7e5ff;
            color: #667eea;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .multiselect-tag:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
        }}

        .multiselect-tag.severity-critical {{
            background: #ffe7e7;
            color: #dc3545;
        }}

        .multiselect-tag.severity-critical:hover {{
            box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
        }}

        .multiselect-tag.severity-major {{
            background: #ffe7d1;
            color: #fd7e14;
        }}

        .multiselect-tag.severity-major:hover {{
            box-shadow: 0 2px 8px rgba(253, 126, 20, 0.2);
        }}

        .multiselect-tag.severity-minor {{
            background: #e7f5ff;
            color: #0dcaf0;
        }}

        .multiselect-tag.severity-minor:hover {{
            box-shadow: 0 2px 8px rgba(13, 202, 240, 0.2);
        }}

        .multiselect-tag.severity-trivial {{
            background: #f0f0f0;
            color: #666;
        }}

        .multiselect-tag.severity-trivial:hover {{
            box-shadow: 0 2px 8px rgba(102, 102, 102, 0.2);
        }}

        .multiselect-tag-remove {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            cursor: pointer;
            font-weight: bold;
            opacity: 0.7;
            transition: opacity 0.3s;
            border-radius: 50%;
            line-height: 1;
        }}

        .multiselect-tag-remove:hover {{
            opacity: 1;
            background: rgba(0, 0, 0, 0.1);
        }}

        .multiselect-placeholder {{
            color: #999;
            font-size: 13px;
        }}

        .multiselect-dropdown {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 4px 4px;
            max-height: 250px;
            overflow-y: auto;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .multiselect-option {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            cursor: pointer;
            transition: background 0.2s;
            border-bottom: 1px solid #f0f0f0;
        }}

        .multiselect-option:hover {{
            background: #f8f9fa;
        }}

        .multiselect-option.selected {{
            background: #f0f3ff;
        }}

        .multiselect-option input {{
            cursor: pointer;
            margin: 0;
            width: 16px;
            height: 16px;
            accent-color: #667eea;
        }}

        .multiselect-option-label {{
            font-size: 13px;
            color: #333;
        }}

        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}

        .table-header {{
            display: grid;
            grid-template-columns: 35px 55px 1fr 50px 100px 120px 110px 100px;
            gap: 12px;
            background: #667eea;
            color: white;
            padding: 12px 15px;
            border-radius: 4px 4px 0 0;
            font-weight: 600;
            font-size: 13px;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .table-header .sortable-header {{
            cursor: pointer;
            user-select: none;
        }}

        .table-header .sortable-header:hover {{
            color: #dbe4ff;
        }}

        .table-row {{
            display: grid;
            grid-template-columns: 35px 55px 1fr 50px 100px 120px 110px 100px;
            gap: 12px;
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
            align-items: center;
            transition: background 0.2s;
            cursor: pointer;
        }}

        .col-extra {{
            /* These columns hide on smaller screens */
        }}

        .table-row:hover {{
            background: #f8f9fa;
        }}

        .expand-icon {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            background: #667eea;
            color: white;
            border-radius: 4px;
            font-size: 18px;
            cursor: pointer;
            transition: transform 0.2s;
        }}

        .expand-icon.expanded {{
            transform: rotate(90deg);
        }}

        .cell-id {{
            font-weight: 600;
            color: #333;
        }}

        .cell-file {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #555;
            word-break: break-word;
        }}

        .cell-line {{
            text-align: center;
            color: #666;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            min-width: 80px;
        }}

        .severity-critical {{
            background: #f8d7da;
            color: #721c24;
        }}

        .severity-major {{
            background: #ffe7d1;
            color: #fd7e14;
        }}

        .severity-minor {{
            background: #d1ecf1;
            color: #0c5460;
        }}

        .severity-trivial {{
            background: #e2e3e5;
            color: #383d41;
        }}

        .severity-unknown {{
            background: #f0f0f0;
            color: #666;
        }}

        .verdict-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            min-width: 90px;
        }}

        .verdict-valid {{
            background: #d4edda;
            color: #155724;
        }}

        .verdict-false-positive {{
            background: #f8d7da;
            color: #721c24;
        }}

        .verdict-partially-valid {{
            background: #fff3cd;
            color: #856404;
        }}

        .verdict-uncertain {{
            background: #e2e3e5;
            color: #383d41;
        }}

        .verdict-empty {{
            color: #999;
            font-size: 12px;
            font-style: italic;
        }}

        .status-pending {{
            background: #cfe2ff;
            color: #084298;
        }}

        .status-resolved {{
            background: #d1e7dd;
            color: #0f5132;
        }}

        .status-unresolved {{
            background: #f8d7da;
            color: #842029;
        }}

        .status-skipped {{
            background: #e2e3e5;
            color: #383d41;
        }}

        .expanded-row {{
            grid-column: 1 / -1;
            padding: 20px 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}

        .expanded-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .expanded-section {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: -8px;
        }}

        .expanded-section-title {{
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }}

        .expanded-section-content {{
            background: white;
            padding: 12px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
            font-size: 13px;
            line-height: 1.5;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #555;
        }}

        .no-data {{
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }}

        .pagination-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .pagination-info {{
            font-size: 13px;
            color: #666;
        }}

        .pagination-controls {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .entries-selector {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #666;
        }}

        .entries-selector select {{
            padding: 6px 10px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            font-size: 13px;
        }}

        .pagination-button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border: 1px solid #dee2e6;
            background: white;
            color: #666;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .pagination-button:hover:not(:disabled) {{
            border-color: #667eea;
            color: #667eea;
            background: #f8f9fa;
        }}

        .pagination-button.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}

        .pagination-button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .pagination-page-list {{
            display: flex;
            gap: 4px;
            align-items: center;
        }}

        .pagination-ellipsis {{
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-size: 13px;
        }}

        .no-data {{
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }}

        @media (max-width: 1200px) {{
            .table-header,
            .table-row {{
                grid-template-columns: 35px 50px 1fr 50px 90px 110px 100px;
            }}

            .expanded-content {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 1024px) {{
            .table-header,
            .table-row {{
                grid-template-columns: 35px 45px 1fr 45px 85px 100px 80px;
                font-size: 12px;
                gap: 10px;
            }}

            .cell-file {{
                font-size: 12px;
            }}

            .filters {{
                gap: 15px;
            }}

            .col-extra {{
                font-size: 11px;
            }}
        }}

        @media (max-width: 768px) {{
            .content {{
                padding: 20px;
            }}

            .card {{
                padding: 15px;
            }}

            .card-header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .controls {{
                width: 100%;
            }}

            .button {{
                width: 100%;
            }}

            .filters {{
                flex-direction: column;
                gap: 15px;
            }}

            .filter-group {{
                width: 100%;
            }}

            .table-header,
            .table-row {{
                grid-template-columns: 30px 40px 1fr 40px 75px 90px;
                font-size: 11px;
                gap: 8px;
            }}

            .col-extra {{
                display: none;
            }}

            .cell-file {{
                font-size: 11px;
                min-width: 100px;
            }}

            .expand-icon {{
                width: 25px;
                height: 25px;
                font-size: 16px;
            }}

            .badge {{
                font-size: 11px;
                padding: 3px 8px;
            }}

            .expanded-content {{
                grid-template-columns: 1fr;
                gap: 15px;
                font-size: 12px;
            }}

            .expanded-section-content {{
                max-height: 200px;
                font-size: 11px;
            }}
        }}

        @media (max-width: 768px) {{
            .pagination-container {{
                flex-direction: column;
                align-items: stretch;
                gap: 12px;
            }}

            .pagination-info {{
                text-align: center;
            }}

            .pagination-controls {{
                justify-content: center;
            }}

            .entries-selector {{
                justify-content: center;
            }}

            .pagination-page-list {{
                flex-wrap: wrap;
                justify-content: center;
            }}
        }}

        @media (max-width: 480px) {{
            .table-header,
            .table-row {{
                grid-template-columns: 30px 35px 1fr 35px 65px 75px;
                font-size: 10px;
                gap: 6px;
                padding: 10px 8px;
            }}

            .col-extra {{
                display: none;
            }}

            .cell-id {{
                font-size: 10px;
            }}

            .cell-file {{
                font-size: 10px;
            }}

            .cell-line {{
                font-size: 10px;
            }}

            .badge {{
                font-size: 10px;
                padding: 2px 6px;
            }}

            .filter-tag {{
                font-size: 12px;
                padding: 6px 10px;
            }}

            .summary {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}

            .summary-item {{
                padding: 15px;
                border-left-width: 3px;
            }}

            .pagination-button {{
                width: 28px;
                height: 28px;
                font-size: 12px;
            }}

            .pagination-info {{
                font-size: 12px;
            }}

            .entries-selector {{
                font-size: 12px;
            }}

            .entries-selector select {{
                font-size: 12px;
                padding: 4px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const {{useState, useMemo}} = React;

        const commentsData = {comments_json};
        const summaryStats = {summary_json};
        const PR_URL = {json.dumps(pr_url)};
        const REPORT_URL = {json.dumps(report_path)};

        function SeverityBadge({{severity}}) {{
            const className = `badge severity-${{severity.toLowerCase()}}`;
            return <span className={{className}}>{{severity}}</span>;
        }}

        function StatusBadge({{status}}) {{
            const className = `badge status-${{status.toLowerCase()}}`;
            return <span className={{className}}>{{status}}</span>;
        }}

        function TableRow({{comment, expanded, onToggle}}) {{
            const getVerdictClass = (verdict) => {{
                if (!verdict) return 'verdict-empty';
                const verdictMap = {{
                    'valid': 'verdict-valid',
                    'false-positive': 'verdict-false-positive',
                    'false_positive': 'verdict-false-positive',
                    'partially-valid': 'verdict-partially-valid',
                    'partially_valid': 'verdict-partially-valid',
                    'uncertain': 'verdict-uncertain',
                }};
                return verdictMap[verdict.toLowerCase()] || 'verdict-uncertain';
            }};

            const getVerdictText = (verdict) => {{
                if (!verdict) return '—';
                const textMap = {{
                    'valid': 'Valid',
                    'false-positive': 'False +',
                    'false_positive': 'False +',
                    'partially-valid': 'Partial',
                    'partially_valid': 'Partial',
                    'uncertain': 'Uncertain',
                }};
                return textMap[verdict.toLowerCase()] || verdict;
            }};

            const formatDate = (dateStr) => {{
                if (!dateStr) return '—';
                try {{
                    return new Date(dateStr).toLocaleDateString('en-US', {{year: '2-digit', month: '2-digit', day: '2-digit'}})
                }} catch {{
                    return '—';
                }}
            }};

            return (
                <>
                    <div
                        className="table-row"
                        onClick={{onToggle}}
                    >
                        <div>
                            <div
                                className={{'expand-icon ' + (expanded ? 'expanded' : '')}}
                            >
                                +
                            </div>
                        </div>
                        <div className="cell-id">
                            <a
                                href={{`${{PR_URL}}?discussionId=${{comment.id}}`}}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={{(e) => e.stopPropagation()}}
                                style={{{{color: '#667eea', textDecoration: 'none', fontWeight: '600', cursor: 'pointer', whiteSpace: 'nowrap'}}}}
                                title="Open this comment thread in Azure DevOps"
                            >
                                {{comment.id}}↗
                            </a>
                        </div>
                        <div className="cell-file">{{comment.file}}</div>
                        <div className="cell-line">{{comment.line || 'N/A'}}</div>
                        <div>
                            <SeverityBadge severity={{comment.severity}} />
                        </div>
                        <div>
                            <StatusBadge status={{comment.status}} />
                        </div>
                        <div>
                            <span className={{`verdict-badge ${{getVerdictClass(comment.pr_judge_assessment)}}`}}>
                                {{getVerdictText(comment.pr_judge_assessment)}}
                            </span>
                        </div>
                        <div className="col-extra">{{comment.author || '—'}}</div>
                    </div>
                    {{expanded && (
                        <div className="expanded-row">
                            <div className="expanded-content">
                                <div className="expanded-section">
                                    <div style={{{{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}}}>
                                        <div className="expanded-section-title" style={{{{margin: '0'}}}}>Description</div>
                                        <button onClick={{() => {{const description = comment.description || comment.content.substring(0, 200) || 'No description available'; const text = `Comment ID: ${{comment.id}}\nReport URL: ${{REPORT_URL}}\n\nContext: ${{description}}`; navigator.clipboard.writeText(text).then(() => Swal.fire({{position: 'top-end', icon: 'success', title: 'Copied!', text: 'Description copied to clipboard', timer: 2000, timerProgressBar: true, showConfirmButton: false, toast: true}})).catch(() => Swal.fire({{position: 'top-end', icon: 'error', title: 'Error', text: 'Failed to copy', timer: 2000, timerProgressBar: true, showConfirmButton: false, toast: true}}));}}}} style={{{{padding: '4px 8px', fontSize: '12px', cursor: 'pointer', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', gap: '4px'}}}}>📋 Copy</button>
                                    </div>
                                    <div className="expanded-section-content">
                                        {{comment.description || comment.content.substring(0, 200) || 'No description available'}}
                                    </div>
                                </div>
                                <div className="expanded-section">
                                    <div style={{{{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}}}>
                                        <div className="expanded-section-title" style={{{{margin: '0'}}}}>Prompt for AI Agents</div>
                                        <button onClick={{() => {{const prompt = comment.prompt_for_ai_agents || 'No prompt available'; const text = `Comment ID: ${{comment.id}}\nReport URL: ${{REPORT_URL}}\n\nContext: ${{prompt}}`; navigator.clipboard.writeText(text).then(() => Swal.fire({{position: 'top-end', icon: 'success', title: 'Copied!', text: 'Prompt copied to clipboard', timer: 2000, timerProgressBar: true, showConfirmButton: false, toast: true}})).catch(() => Swal.fire({{position: 'top-end', icon: 'error', title: 'Error', text: 'Failed to copy', timer: 2000, timerProgressBar: true, showConfirmButton: false, toast: true}}));}}}} style={{{{padding: '4px 8px', fontSize: '12px', cursor: 'pointer', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', gap: '4px'}}}}>📋 Copy</button>
                                    </div>
                                    <div className="expanded-section-content">
                                        {{comment.prompt_for_ai_agents || 'No prompt available'}}
                                    </div>
                                </div>
                                {{comment.fix_summary && (
                                    <div className="expanded-section">
                                        <div className="expanded-section-title" style={{{{margin: '0', marginTop: '16px'}}}}>🔧 Fix Summary & Considerations</div>
                                        <div className="expanded-section-content" style={{{{whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '13px'}}}}>
                                            {{comment.fix_summary}}
                                        </div>
                                    </div>
                                )}}
                            </div>
                        </div>
                    )}}
                </>
            );
        }}

        function MultiSelect({{options, selectedValues, onChange, tagType = 'primary'}}) {{
            const [isOpen, setIsOpen] = useState(false);

            const handleToggle = (value) => {{
                const newSet = new Set(selectedValues);
                if (newSet.has(value)) {{
                    newSet.delete(value);
                }} else {{
                    newSet.add(value);
                }}
                onChange(newSet);
            }};

            const handleRemoveTag = (e, value) => {{
                e.stopPropagation();
                const newSet = new Set(selectedValues);
                newSet.delete(value);
                onChange(newSet);
            }};

            const getTagClass = (value) => {{
                if (tagType === 'severity') {{
                    const severityClass = `severity-${{value.toLowerCase()}}`;
                    return `multiselect-tag ${{severityClass}}`;
                }}
                return 'multiselect-tag';
            }};

            return (
                <div className="multiselect-container" onBlur={{() => setIsOpen(false)}}>
                    <div
                        className={{'multiselect-input ' + (isOpen ? 'focused' : '')}}
                        onClick={{() => setIsOpen(!isOpen)}}
                    >
                        {{selectedValues.size > 0 ? (
                            Array.from(selectedValues).map(value => (
                                <div key={{value}} className={{getTagClass(value)}}>
                                    <span>{{value}}</span>
                                    <span
                                        className="multiselect-tag-remove"
                                        onClick={{(e) => handleRemoveTag(e, value)}}
                                    >
                                        ×
                                    </span>
                                </div>
                            ))
                        ) : (
                            <span className="multiselect-placeholder">Select options...</span>
                        )}}
                    </div>
                    {{isOpen && (
                        <div className="multiselect-dropdown">
                            {{options.map(option => (
                                <div
                                    key={{option}}
                                    className={{'multiselect-option ' + (selectedValues.has(option) ? 'selected' : '')}}
                                    onClick={{() => handleToggle(option)}}
                                >
                                    <input
                                        type="checkbox"
                                        checked={{selectedValues.has(option)}}
                                        onChange={{() => {{}}}}
                                    />
                                    <span className="multiselect-option-label">{{option}}</span>
                                </div>
                            ))}}
                        </div>
                    )}}
                </div>
            );
        }}

        function TechnicalInfoTable() {{
            // Load saved filter state from localStorage or use defaults
            const savedFilterState = JSON.parse(localStorage.getItem('prTriageFilterState') || '{{}}');

            const [expandedIds, setExpandedIds] = useState(new Set());
            const [selectedStatuses, setSelectedStatuses] = useState(new Set(savedFilterState.selectedStatuses || []));
            const [selectedSeverities, setSelectedSeverities] = useState(new Set(savedFilterState.selectedSeverities || []));
            const [showAll, setShowAll] = useState(savedFilterState.showAll !== undefined ? savedFilterState.showAll : false);
            const [currentPage, setCurrentPage] = useState(savedFilterState.currentPage || 1);
            const [entriesPerPage, setEntriesPerPage] = useState(savedFilterState.entriesPerPage || 10);
            const [sortColumn, setSortColumn] = useState(savedFilterState.sortColumn || 'id');
            const [sortDirection, setSortDirection] = useState(savedFilterState.sortDirection || 'asc');

            // Save filter state to localStorage whenever it changes
            React.useEffect(() => {{
                localStorage.setItem('prTriageFilterState', JSON.stringify({{
                    selectedStatuses: Array.from(selectedStatuses),
                    selectedSeverities: Array.from(selectedSeverities),
                    showAll: showAll,
                    currentPage: currentPage,
                    entriesPerPage: entriesPerPage,
                    sortColumn: sortColumn,
                    sortDirection: sortDirection
                }}));
            }}, [selectedStatuses, selectedSeverities, showAll, currentPage, entriesPerPage, sortColumn, sortDirection]);

            const severities = ['Critical', 'Major', 'Minor', 'Trivial', 'Unknown'];
            const statuses = ['Pending', 'Resolved', 'Unresolved', 'Skipped'];

            const filteredComments = useMemo(() => {{
                return commentsData.filter(c => {{
                    const statusMatch = selectedStatuses.size === 0 || selectedStatuses.has(c.status);
                    const severityMatch = selectedSeverities.size === 0 || selectedSeverities.has(c.severity);
                    return statusMatch && severityMatch;
                }});
            }}, [selectedStatuses, selectedSeverities]);

            const sortedComments = useMemo(() => {{
                const columnGetters = {{
                    id: c => c.id,
                    file: c => (c.file || '').toLowerCase(),
                    line: c => c.line ?? -1,
                    severity: c => c.severity || '',
                    status: c => c.status || '',
                    pr_judge_assessment: c => c.pr_judge_assessment || '',
                    author: c => (c.author || '').toLowerCase()
                }};
                const getValue = columnGetters[sortColumn] || columnGetters.id;
                const sorted = [...filteredComments].sort((a, b) => {{
                    const va = getValue(a), vb = getValue(b);
                    if (va < vb) return -1;
                    if (va > vb) return 1;
                    return 0;
                }});
                return sortDirection === 'asc' ? sorted : sorted.reverse();
            }}, [filteredComments, sortColumn, sortDirection]);

            const handleSort = (column) => {{
                if (sortColumn === column) {{
                    setSortDirection(d => d === 'asc' ? 'desc' : 'asc');
                }} else {{
                    setSortColumn(column);
                    setSortDirection('asc');
                }}
            }};

            const sortIndicator = (column) => sortColumn === column ? (sortDirection === 'asc' ? ' ▲' : ' ▼') : '';

            // Reset page when filters or sort change
            React.useEffect(() => {{
                setCurrentPage(1);
            }}, [selectedStatuses, selectedSeverities, sortColumn, sortDirection]);

            // Calculate pagination
            const itemsPerPage = showAll ? entriesPerPage : 20;
            const totalItems = filteredComments.length;
            const totalPages = showAll ? Math.ceil(totalItems / itemsPerPage) : 1;

            // Ensure currentPage is valid
            const validCurrentPage = Math.min(Math.max(1, currentPage), totalPages || 1);

            const startIndex = (validCurrentPage - 1) * itemsPerPage;
            const endIndex = Math.min(startIndex + itemsPerPage, totalItems);
            const displayedComments = sortedComments.slice(startIndex, endIndex);

            // Generate page numbers
            const getPageNumbers = () => {{
                const pages = [];
                const maxPagesToShow = 5;

                if (totalPages <= maxPagesToShow) {{
                    for (let i = 1; i <= totalPages; i++) {{
                        pages.push(i);
                    }}
                }} else {{
                    pages.push(1);
                    if (validCurrentPage > 3) pages.push('...');

                    const start = Math.max(2, validCurrentPage - 1);
                    const end = Math.min(totalPages - 1, validCurrentPage + 1);
                    for (let i = start; i <= end; i++) {{
                        if (!pages.includes(i)) pages.push(i);
                    }}

                    if (validCurrentPage < totalPages - 2) pages.push('...');
                    pages.push(totalPages);
                }}
                return pages;
            }};

            const pageNumbers = showAll ? getPageNumbers() : [];


            const toggleExpand = (id) => {{
                const newSet = new Set(expandedIds);
                if (newSet.has(id)) {{
                    newSet.delete(id);
                }} else {{
                    newSet.add(id);
                }}
                setExpandedIds(newSet);
            }};

            const toggleAll = () => {{
                setShowAll(!showAll);
                setCurrentPage(1);
            }};

            return (
                <div className="card">
                    <div className="card-header">
                        <h2>Technical Information</h2>
                        <div className="controls">
                            <button
                                className="button"
                                onClick={{toggleAll}}
                            >
                                {{showAll ? 'Hide All Comments' : 'Show All Comments (' + filteredComments.length + ')'}}
                            </button>
                        </div>
                    </div>

                    <div className="filters">
                        <div className="filter-group">
                            <label>Status</label>
                            <MultiSelect
                                options={{statuses}}
                                selectedValues={{selectedStatuses}}
                                onChange={{setSelectedStatuses}}
                                tagType="primary"
                            />
                        </div>
                        <div className="filter-group">
                            <label>Severity</label>
                            <MultiSelect
                                options={{severities}}
                                selectedValues={{selectedSeverities}}
                                onChange={{setSelectedSeverities}}
                                tagType="severity"
                            />
                        </div>
                    </div>

                    <div className="table">
                        <div className="table-header">
                            <div></div>
                            <div className="sortable-header" onClick={{() => handleSort('id')}}>ID{{sortIndicator('id')}}</div>
                            <div className="sortable-header" onClick={{() => handleSort('file')}}>File{{sortIndicator('file')}}</div>
                            <div className="sortable-header" onClick={{() => handleSort('line')}}>Line{{sortIndicator('line')}}</div>
                            <div className="sortable-header" onClick={{() => handleSort('severity')}}>Severity{{sortIndicator('severity')}}</div>
                            <div className="sortable-header" onClick={{() => handleSort('status')}}>Status{{sortIndicator('status')}}</div>
                            <div className="sortable-header" onClick={{() => handleSort('pr_judge_assessment')}}>pr-judge Verdict{{sortIndicator('pr_judge_assessment')}}</div>
                            <div className="col-extra sortable-header" onClick={{() => handleSort('author')}}>Author{{sortIndicator('author')}}</div>
                        </div>
                        {{displayedComments.length > 0 ? (
                            displayedComments.map(comment => (
                                <TableRow
                                    key={{comment.id}}
                                    comment={{comment}}
                                    expanded={{expandedIds.has(comment.id)}}
                                    onToggle={{() => toggleExpand(comment.id)}}
                                />
                            ))
                        ) : (
                            <div className="no-data">No comments match the selected filters</div>
                        )}}
                    </div>

                    {{showAll && (
                        <div className="pagination-container">
                            <div className="entries-selector">
                                <span>Show</span>
                                <select
                                    value={{entriesPerPage}}
                                    onChange={{(e) => {{
                                        setEntriesPerPage(parseInt(e.target.value));
                                        setCurrentPage(1);
                                    }}}}
                                >
                                    <option value={{10}}>10</option>
                                    <option value={{25}}>25</option>
                                    <option value={{50}}>50</option>
                                    <option value={{100}}>100</option>
                                </select>
                                <span>entries</span>
                            </div>

                            <div className="pagination-info">
                                Showing {{startIndex + 1}} to {{endIndex}} of {{totalItems}} entries
                            </div>

                            <div className="pagination-controls">
                                <button
                                    className="pagination-button"
                                    onClick={{() => setCurrentPage(validCurrentPage - 1)}}
                                    disabled={{validCurrentPage === 1}}
                                >
                                    Prev
                                </button>

                                <div className="pagination-page-list">
                                    {{pageNumbers.map((page, idx) => (
                                        page === '...' ? (
                                            <div key={{`ellipsis-${{idx}}`}} className="pagination-ellipsis">...</div>
                                        ) : (
                                            <button
                                                key={{page}}
                                                className={{'pagination-button ' + (validCurrentPage === page ? 'active' : '')}}
                                                onClick={{() => setCurrentPage(page)}}
                                            >
                                                {{page}}
                                            </button>
                                        )
                                    ))}}
                                </div>

                                <button
                                    className="pagination-button"
                                    onClick={{() => setCurrentPage(validCurrentPage + 1)}}
                                    disabled={{validCurrentPage === totalPages}}
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    )}}

                    {{!showAll && (
                        <div className="pagination-container">
                            <div className="pagination-info">
                                Showing 1 to {{displayedComments.length}} of {{filteredComments.length}} entries (first 20 shown)
                            </div>
                        </div>
                    )}}
                </div>
            );
        }}

        function App() {{
            return (
                <div className="container">
                    <div className="header">
                        <h1>CodeRabbit Triage Report</h1>
                        <p>Automated validation and resolution tracking</p>
                        <div className="pr-info">
                            <strong>PR Number:</strong> {pr_number}<br/>
                            <strong>PR URL:</strong> {pr_url}<br/>
                            <strong>Generated:</strong> {{summaryStats.generated_at || '{generated_at}'}}<br/>
                            <strong>Updated:</strong> {{summaryStats.updated_at || '{current_time}'}}
                        </div>
                    </div>

                    <div className="content">
                        <h2 style={{{{marginBottom: '20px'}}}}>Summary</h2>
                        <div className="summary">
                            <div style={{{{fontSize: '12px', fontWeight: '600', color: '#333', marginBottom: '10px', gridColumn: '1 / -1'}}}}>Status Breakdown</div>

                            <div className="summary-item">
                                <strong>{{summaryStats.total}}</strong>
                                <span>Total Comments</span>
                            </div>
                            <div className="summary-item">
                                <strong>{{summaryStats.pending}}</strong>
                                <span>Pending</span>
                            </div>
                            <div className="summary-item">
                                <strong>{{summaryStats.resolved}}</strong>
                                <span>Resolved</span>
                            </div>
                            <div className="summary-item">
                                <strong>{{summaryStats.skipped}}</strong>
                                <span>Skipped</span>
                            </div>

                            <div style={{{{marginTop: '15px', borderTop: '2px solid #e0e0e0', paddingTop: '15px', gridColumn: '1 / -1'}}}}>
                                <div style={{{{fontSize: '12px', fontWeight: '600', color: '#333', marginBottom: '10px'}}}}>Severity Breakdown</div>
                            </div>

                            <div className="summary-item">
                                <strong style={{{{color: '#dc3545'}}}}>{{summaryStats.severity ? summaryStats.severity['Critical'] || 0 : 0}}</strong>
                                <span>🔴 Critical</span>
                            </div>
                            <div className="summary-item">
                                <strong style={{{{color: '#ff9800'}}}}>{{summaryStats.severity ? summaryStats.severity['Major'] || 0 : 0}}</strong>
                                <span>🟠 Major</span>
                            </div>
                            <div className="summary-item">
                                <strong style={{{{color: '#ffc107'}}}}>{{summaryStats.severity ? summaryStats.severity['Minor'] || 0 : 0}}</strong>
                                <span>🟡 Minor</span>
                            </div>
                            <div className="summary-item">
                                <strong style={{{{color: '#6c757d'}}}}>{{summaryStats.severity ? summaryStats.severity['Trivial'] || 0 : 0}}</strong>
                                <span>🔵 Trivial</span>
                            </div>
                        </div>

                        <div style={{{{marginTop: '30px', padding: '25px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #e0e0e0'}}}}>
                            <h3 style={{{{marginBottom: '15px', fontSize: '14px', fontWeight: '600'}}}}>Status Legend</h3>
                            <div style={{{{display: 'grid', gridTemplateColumns: '1fr', gap: '12px', fontSize: '13px', marginBottom: '12px'}}}} >
                                <div><strong style={{{{color: '#ffc107'}}}}>● Pending:</strong> Not yet processed during triage</div>
                                <div><strong style={{{{color: '#28a745'}}}}>● Resolved:</strong> Processed via pr-judge, decision made and will be fixed</div>
                                <div><strong style={{{{color: '#6c757d'}}}}>● Skipped:</strong> Intentionally skipped during triage, no further action</div>
                                <div><strong style={{{{color: '#dc3545'}}}}>● Unresolved:</strong> Processed but marked as unresolved after analysis</div>
                            </div>
                            <div style={{{{fontSize: '12px', color: '#555', paddingTop: '10px', borderTop: '1px solid #ddd', fontStyle: 'italic'}}}}>
                                💡 <strong>On Refresh:</strong> Existing statuses/verdicts are preserved by comment ID. New comments start at Pending. Resolved and Skipped are considered complete.
                            </div>
                        </div>

                        <TechnicalInfoTable />
                    </div>
                </div>
            );
        }}

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>

    <!-- Technical Information JSON for Resume Capability -->
    <script type="application/json" id="pr-triage-technical-info">
    {technical_json}
    </script>
</body>
</html>
"""

    return html


def main():
    """Main entry point — supports both file path and inline JSON."""
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python generate_report_react.py <pr_number> <results_json_or_file> [report_dir]"
        }))
        sys.exit(1)

    pr_number = sys.argv[1]
    json_arg = sys.argv[2]

    # IMPROVEMENT: Detect if json_arg is a file path or inline JSON
    results = None
    try:
        if os.path.isfile(json_arg) and json_arg.endswith('.json'):
            # Load from file (NEW BEHAVIOR - FIXES WINDOWS CLI LIMIT ISSUE)
            with open(json_arg, 'r') as f:
                results = json.load(f)
        else:
            # Parse as inline JSON (LEGACY SUPPORT)
            results = json.loads(json_arg)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON: {str(e)}"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Failed to load results: {str(e)}"
        }))
        sys.exit(1)

    try:
        # Get report path or directory from argument
        if len(sys.argv) >= 4 and sys.argv[3]:
            output_arg = sys.argv[3]
            # If it ends with .html, treat as file path (finalization mode - overwrite)
            if output_arg.endswith('.html'):
                report_path = output_arg
                report_dir = os.path.dirname(report_path)
            else:
                # Treat as directory (initial mode - generate new timestamped file)
                report_dir = output_arg
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                report_path = os.path.join(report_dir, f"{pr_number}-pr-triage-{timestamp}.html")
        else:
            # Default mode
            report_dir = r"C:\Repos\docs\reports\pr-triage"
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            report_path = os.path.join(report_dir, f"{pr_number}-pr-triage-{timestamp}.html")

        html = generate_react_report(pr_number, results, report_path)

        # Ensure report directory exists
        os.makedirs(report_dir, exist_ok=True)

        # Write report (will overwrite if path is specified)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(json.dumps({
            "success": True,
            "report_path": report_path,
            "size_kb": len(html) / 1024,
            "comments_count": len(results.get("all_comments", []))
        }))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
