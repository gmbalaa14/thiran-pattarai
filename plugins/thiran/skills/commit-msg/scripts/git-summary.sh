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
  # Usage: git-summary.sh commit [staged|staged+modified|modified]
  # The optional scope picks which file set gets classified (default: staged).
  scope="${2:-staged}"
  g() { git -c core.quotepath=off "$@"; }
  staged="$(g diff --cached --name-status)"
  unstaged="$(g diff --name-status)"
  untracked="$(g ls-files --others --exclude-standard)"
  staged_names="$(g diff --cached --name-only | sort -u)"
  unstaged_names="$(g diff --name-only | sort -u)"
  partly="$(comm -12 <(printf '%s\n' "$staged_names") <(printf '%s\n' "$unstaged_names") | sed '/^$/d')"
  count() { [ -z "$1" ] && echo 0 || printf '%s\n' "$1" | wc -l | tr -d ' '; }

  # Classify a path as companion (generated/lock/snapshot), tests, docs or code.
  # Companions are produced by a change rather than authored, so they never
  # count toward totals or trigger a split. Markdown under skills/ is the
  # product of this kind of repo, so it counts as code, not docs.
  classify() {
    case "$1" in
      package-lock.json|*/package-lock.json|yarn.lock|*/yarn.lock|pnpm-lock.yaml|*/pnpm-lock.yaml|*.lock|go.sum|*/go.sum|packages.lock.json|*/packages.lock.json|*.g.cs|*.Designer.cs|*ModelSnapshot.cs|*.generated.*|*.snap|*__snapshots__/*) echo companion; return;;
      tests/*|*/tests/*|test/*|*/test/*|__tests__/*|*/__tests__/*|*Tests.cs|*Test.cs|*.spec.*|*.test.*|*_test.go|test_*.py|*/test_*.py) echo tests; return;;
      skills/*.md|*/skills/*.md) echo code; return;;
      *.md|*.rst|docs/*|*/docs/*|README*|*/README*|CHANGELOG*|*/CHANGELOG*|LICENSE*|*/LICENSE*) echo docs; return;;
      *) echo code;;
    esac
  }

  case "$scope" in
    staged)           scope_names="$staged_names" ;;
    modified)         scope_names="$unstaged_names" ;;
    staged+modified)  scope_names="$(printf '%s\n%s\n' "$staged_names" "$unstaged_names" | sort -u | sed '/^$/d')" ;;
    *) echo "ERROR: unknown scope '$scope'"; exit 1 ;;
  esac

  n_code=0; n_docs=0; n_tests=0; n_comp=0; listing=""
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    c="$(classify "$f")"
    case "$c" in code) n_code=$((n_code+1));; docs) n_docs=$((n_docs+1));; tests) n_tests=$((n_tests+1));; companion) n_comp=$((n_comp+1));; esac
    listing="$listing\n  [$c] $f"
  done <<< "$scope_names"

  echo "branch: $branch"
  echo "staged files: $(count "$staged")"
  echo "unstaged (modified, uncommitted) files: $(count "$unstaged")"
  echo "untracked files: $(count "$untracked") (excluded from every scope)"
  echo "partly staged files: $(count "$partly")"
  [ -n "$partly" ] && printf '%s\n' "$partly" | sed 's/^/  /'
  echo "--- scope: $scope ---"
  echo "code: $n_code, docs: $n_docs, tests: $n_tests, companions: $n_comp"
  printf '%b\n' "$listing" | sed '/^$/d'
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
