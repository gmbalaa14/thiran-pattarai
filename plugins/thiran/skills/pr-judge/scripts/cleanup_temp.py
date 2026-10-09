#!/usr/bin/env python3
"""
Delete pr-judge's own scratch temp files — and only those.

Usage:
  python cleanup_temp.py <path> [<path> ...]

Each argument is deleted ONLY if its filename (basename) starts with
"pr_judge_". Anything else is skipped and reported, never deleted. This
script exists so a Bash permission allowlist can safely target a fixed,
never-changing command prefix (this script's own path) instead of a raw
`rm -f`, which would have to be scoped by the scratchpad directory's
per-session path — something a permission rule's prefix match can't express
safely. The real safety boundary is the basename check below, not the
permission rule; the rule just avoids prompting for a call that was always
going to be refused deletion of anything outside this prefix anyway.
"""

import sys
import os

PREFIX = "pr_judge_"


def main():
    if len(sys.argv) < 2:
        print("Usage: cleanup_temp.py <path> [<path> ...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        basename = os.path.basename(path)
        if not basename.startswith(PREFIX):
            print(f"skip (not a pr_judge_* file): {path}")
            continue
        try:
            os.remove(path)
            print(f"deleted: {path}")
        except FileNotFoundError:
            print(f"already gone: {path}")
        except OSError as e:
            print(f"failed to delete {path}: {e}")


if __name__ == "__main__":
    main()
