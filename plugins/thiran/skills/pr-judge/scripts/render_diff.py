#!/usr/bin/env python3
"""
Render a deterministic unified diff with dual-column line numbers and accurate added/removed counts.
Addresses: correct line numbering for changed lines, accurate hunk boundaries with line-count
separators, exact added/removed counts that match the displayed diff, and multiple hunks within
the same file.

Usage (single hunk — one changed region in the file):
  python render_diff.py "<file_path>" <start_line> <old_file> <new_file>

Usage (multiple hunks — several changed regions in the SAME file, e.g. an added
using-directive near the top plus a method body change hundreds of lines later):
  python render_diff.py "<file_path>" --hunks <hunks_json_file>

  <hunks_json_file> contains a JSON array, one entry per changed region, each with
  its own real start line and its own old/new snippet — the regions do not need to
  be adjacent or share any content, so there's no need to paste the unchanged code
  between them:
  [
    {"start_line": 5,   "old_file": "/tmp/h1_old.txt", "new_file": "/tmp/h1_new.txt"},
    {"start_line": 179, "old_file": "/tmp/h2_old.txt", "new_file": "/tmp/h2_new.txt"}
  ]

  Output is ONE combined diff for the file: one added/removed count, hunks in
  file order separated by a "⋯ N lines unchanged ⋯" divider stating the real
  skipped-line count — the way a real diff tool (git, Rider, Visual Studio)
  renders one file's diff as multiple hunks instead of one block per changed
  region, and keeps line numbers consistent across the whole file.

Args:
  file_path: Display name for the file (e.g., "Services/AuthService.cs")
  start_line: Real line number of the first line in the old snippet
  old_file: Path to file containing original code snippet
  new_file: Path to file containing proposed fixed code snippet

Output:
  JSON on stdout: {"diff_text": "...", "added": N, "removed": M}
"""

import sys
import json
import difflib

# How much unchanged context to show around each change. Matches what other diff
# tools (git, Rider, Visual Studio) typically show, rather than a tight 3-line clip.
CONTEXT_LINES = 7
# Two changes closer than this (in old-file lines) render as one hunk with the
# unchanged lines between them shown as context, instead of a "..." divider.
MERGE_GAP = CONTEXT_LINES * 2


# Every line type (context/delete/insert) renders through this one helper so the
# code column always starts at the same character position, the way a real diff
# viewer (git, Rider) keeps code aligned regardless of +/-/context markers.
# marker is always padded to 2 chars, and either number column is blanked to 4
# spaces when not applicable, so the total prefix width is constant: 2 + 4 + 1 + 4 + 3 = 14.
def fmt_line(marker, old_num, new_num, content):
    old_str = f"{old_num:>4}" if old_num is not None else "    "
    new_str = f"{new_num:>4}" if new_num is not None else "    "
    return f"{marker:<2}{old_str} {new_str}   {content}"


def compute_hunks(old_lines, new_lines):
    """Group opcodes from difflib into hunks with CONTEXT_LINES of context,
    merging changes closer than MERGE_GAP and marking farther ones with a separator."""
    sm = difflib.SequenceMatcher(None, old_lines, new_lines)
    opcodes = sm.get_opcodes()

    hunks = []
    i = 0
    while i < len(opcodes):
        tag, i1, i2, j1, j2 = opcodes[i]

        if tag == 'equal':
            i += 1
            continue

        context_start_i = max(0, i1 - CONTEXT_LINES)
        context_start_j = max(0, j1 - CONTEXT_LINES)

        change_i2 = i2
        change_j2 = j2
        ii = i + 1
        while ii < len(opcodes):
            next_tag, next_i1, next_i2, next_j1, next_j2 = opcodes[ii]
            if next_tag == 'equal':
                # The size of the unchanged span itself — NOT next_i1 - change_i2,
                # which is always 0 since difflib's opcodes tile the sequence with
                # no gaps between them. That off-by-definition bug used to make
                # every change in a file merge into one giant hunk no matter how
                # far apart, since 0 <= MERGE_GAP was always true.
                gap = next_i2 - next_i1
                if gap <= MERGE_GAP:
                    change_i2 = next_i2
                    change_j2 = next_j2
                    ii += 1
                    continue
                else:
                    break
            else:
                change_i2 = next_i2
                change_j2 = next_j2
                ii += 1

        context_end_i = min(len(old_lines), change_i2 + CONTEXT_LINES)
        context_end_j = min(len(new_lines), change_j2 + CONTEXT_LINES)

        need_separator = context_start_i > 0 and (not hunks or hunks[-1]['end_i'] < context_start_i - 1)

        hunks.append({
            'separator': need_separator,
            'start_i': context_start_i,
            'end_i': context_end_i,
            'start_j': context_start_j,
            'end_j': context_end_j,
            'opcodes': opcodes[i:ii],
        })

        i = ii

    return hunks


def render_hunks(start_line, old_lines, new_lines, hunks, prev_old_end=None):
    """Render a list of hunks (from compute_hunks) into diff lines.

    prev_old_end, if given, is the real old-file line number the previous hunk
    (possibly from a different region/spec) ended on — used to print a divider
    with the actual skipped line count before this call's first hunk. Pass None
    when this is the very first hunk of the whole diff (nothing to divide from).

    Returns (lines, added, removed, last_old_end) — last_old_end lets the caller
    chain this into the next render_hunks() call for a subsequent region.
    """
    lines = []
    added_count = 0
    removed_count = 0
    last_old_end = prev_old_end

    for idx, hunk in enumerate(hunks):
        show_separator = (idx > 0 and hunk['separator']) or (idx == 0 and prev_old_end is not None)
        if show_separator:
            hunk_first_old = start_line + hunk['start_i']
            gap = hunk_first_old - last_old_end - 1 if last_old_end is not None else None
            if gap and gap > 0:
                label = "line" if gap == 1 else "lines"
                lines.append(f"⋯ {gap} {label} unchanged ⋯")
            else:
                lines.append("⋯⋯⋯")

        for tag, i1, i2, j1, j2 in hunk['opcodes']:
            if tag == 'equal':
                for off in range(i2 - i1):
                    old_idx = i1 + off
                    new_idx = j1 + off
                    if hunk['start_i'] <= old_idx < hunk['end_i'] and hunk['start_j'] <= new_idx < hunk['end_j']:
                        lines.append(fmt_line('', start_line + old_idx, start_line + new_idx, old_lines[old_idx]))
            elif tag == 'delete':
                for idx2 in range(i1, i2):
                    if hunk['start_i'] <= idx2 < hunk['end_i']:
                        lines.append(fmt_line('-', start_line + idx2, None, old_lines[idx2]))
                        removed_count += 1
            elif tag == 'insert':
                for idx2 in range(j1, j2):
                    if hunk['start_j'] <= idx2 < hunk['end_j']:
                        lines.append(fmt_line('+', None, start_line + idx2, new_lines[idx2]))
                        added_count += 1
            elif tag == 'replace':
                for idx2 in range(i1, i2):
                    if hunk['start_i'] <= idx2 < hunk['end_i']:
                        lines.append(fmt_line('-', start_line + idx2, None, old_lines[idx2]))
                        removed_count += 1
                for idx2 in range(j1, j2):
                    if hunk['start_j'] <= idx2 < hunk['end_j']:
                        lines.append(fmt_line('+', None, start_line + idx2, new_lines[idx2]))
                        added_count += 1

        last_old_end = start_line + hunk['end_i'] - 1

    return lines, added_count, removed_count, last_old_end


def render_diff(file_path, start_line, old_file, new_file):
    """Render a unified diff with dual-column line numbers for a single changed region."""
    with open(old_file, 'r') as f:
        old_lines = f.read().splitlines(keepends=False)
    with open(new_file, 'r') as f:
        new_lines = f.read().splitlines(keepends=False)

    hunks = compute_hunks(old_lines, new_lines)
    lines, added_count, removed_count, _ = render_hunks(start_line, old_lines, new_lines, hunks)

    return {
        'diff_text': '\n'.join(lines),
        'added': added_count,
        'removed': removed_count,
    }


def render_diff_multi_hunk(file_path, hunk_specs):
    """Render ONE combined diff for a file that changed in multiple, possibly
    far-apart regions. Each spec is diffed independently (no need to supply the
    unchanged code between regions), then joined in file order with a divider
    between every pair of hunks stating how many lines were skipped — the same
    divider a single-region diff uses for an internal gap, so multi-region and
    single-region output look identical to the reader regardless of how many
    render_diff.py calls it took."""
    all_lines = []
    total_added = 0
    total_removed = 0
    last_old_end = None

    for spec in hunk_specs:
        start_line = spec['start_line']
        with open(spec['old_file'], 'r') as f:
            old_lines = f.read().splitlines(keepends=False)
        with open(spec['new_file'], 'r') as f:
            new_lines = f.read().splitlines(keepends=False)

        hunks = compute_hunks(old_lines, new_lines)
        lines, added_count, removed_count, last_old_end = render_hunks(
            start_line, old_lines, new_lines, hunks,
            prev_old_end=last_old_end,
        )
        all_lines.extend(lines)
        total_added += added_count
        total_removed += removed_count

    return {
        'diff_text': '\n'.join(all_lines),
        'added': total_added,
        'removed': total_removed,
    }


def main():
    if len(sys.argv) >= 4 and sys.argv[2] == '--hunks':
        file_path = sys.argv[1]
        hunks_json_file = sys.argv[3]
        try:
            with open(hunks_json_file, 'r') as f:
                hunk_specs = json.load(f)
            result = render_diff_multi_hunk(file_path, hunk_specs)
            print(json.dumps(result))
        except Exception as e:
            print(json.dumps({'error': str(e)}))
            sys.exit(1)
        return

    if len(sys.argv) < 5:
        print(json.dumps({
            'error': 'Usage: render_diff.py "<file_path>" <start_line> <old_file> <new_file>'
                     '   OR: render_diff.py "<file_path>" --hunks <hunks_json_file>'
        }))
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        start_line = int(sys.argv[2])
    except ValueError:
        print(json.dumps({'error': f'Invalid start_line: {sys.argv[2]}'}))
        sys.exit(1)

    old_file = sys.argv[3]
    new_file = sys.argv[4]

    try:
        result = render_diff(file_path, start_line, old_file, new_file)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
