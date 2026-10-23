#!/usr/bin/env bash
# Summarise git state for the commit-msg skill.
#   git-summary.sh commit   -> staged / unstaged / untracked file counts and lists
#   git-summary.sh pr       -> detected base branch, commits ahead, files changed
# Read-only: never modifies the repository.
set -u

mode="${1:-commit}"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "ERROR: not inside a git repository"; exit 1; }

branch="$(git branch --show-current)"
[ -z "$branch" ] && branch="(detached HEAD)"

if [ "$mode" = "commit" ]; then
  staged="$(git diff --cached --name-status)"
  unstaged="$(git diff --name-status)"
  untracked="$(git ls-files --others --exclude-standard)"
  count() { [ -z "$1" ] && echo 0 || printf '%s\n' "$1" | wc -l | tr -d ' '; }
  echo "branch: $branch"
  echo "staged files: $(count "$staged")"
  echo "unstaged (modified, uncommitted) files: $(count "$unstaged")"
  echo "untracked files: $(count "$untracked")"
  echo "--- staged ---";    [ -n "$staged" ]    && printf '%s\n' "$staged"
  echo "--- unstaged ---";  [ -n "$unstaged" ]  && printf '%s\n' "$unstaged"
  echo "--- untracked ---"; [ -n "$untracked" ] && printf '%s\n' "$untracked"
  exit 0
fi

# ---- PR mode: find the branch this one was most likely cut from ----
# Candidates: the branch's configured upstream base, the remote default branch,
# and common long-lived branches. The base is the candidate with the fewest
# commits between it and HEAD, because that is the nearest ancestor branch.
candidates=""
cfg="$(git config --get "branch.$branch.gh-merge-base" 2>/dev/null || true)"
[ -n "$cfg" ] && candidates="$candidates $cfg"
def="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
[ -n "$def" ] && candidates="$candidates $def"
for b in main master develop development dev; do
  for ref in "origin/$b" "$b"; do
    git rev-parse --verify --quiet "$ref" >/dev/null && candidates="$candidates $ref"
  done
done
for r in $(git for-each-ref --format='%(refname:short)' 'refs/remotes/origin/release/*' 'refs/heads/release/*' 2>/dev/null); do
  candidates="$candidates $r"
done

best=""; best_n=999999; ranked=""
for c in $(printf '%s\n' $candidates | awk '!seen[$0]++'); do
  [ "$c" = "$branch" ] && continue
  [ "$c" = "origin/$branch" ] && continue
  git merge-base "$c" HEAD >/dev/null 2>&1 || continue
  n="$(git rev-list --count "$c..HEAD")"
  ranked="$ranked\n  $c ($n commits ahead)"
  if [ "$n" -lt "$best_n" ]; then best="$c"; best_n="$n"; fi
done

echo "branch: $branch"
if [ -z "$best" ]; then echo "ERROR: no base branch candidate found"; exit 2; fi
echo "base branch: $best"
echo "commits ahead of base: $best_n"
printf 'candidates considered:%b\n' "$ranked"
echo "--- commits ($best..HEAD) ---"
git log --format='%h %s' "$best..HEAD"
echo "--- files changed ($best...HEAD) ---"
git diff --stat "$best...HEAD" | tail -n 25
