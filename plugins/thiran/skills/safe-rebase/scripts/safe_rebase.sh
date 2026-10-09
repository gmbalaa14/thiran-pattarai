#!/usr/bin/env bash
# Helper for the safe-rebase skill. Never force-pushes or rewrites the real
# branch without the caller explicitly invoking `apply` / `push` — `trial`
# is always non-destructive (it cleans up after itself no matter what).
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  safe_rebase.sh trial   <working-branch> <new-base> [old-base]
  safe_rebase.sh apply   <working-branch> <new-base> [old-base]
  safe_rebase.sh push    <working-branch> [remote]
  safe_rebase.sh tracks  <working-branch>
  safe_rebase.sh undo    <working-branch> <pre-rebase-tip>

trial  - Rebases a disposable copy of <working-branch> onto <new-base> to check
         for conflicts, then discards the copy and restores the original
         checkout. Prints OLD_BASE, STATUS (clean|conflict), the commits that
         would move, and (on conflict) the conflicting files.
apply  - Performs the real `git rebase --onto <new-base> <old-base>
         <working-branch>` on the actual branch. Only call this after a
         clean `trial` and explicit user confirmation. Prints PRE_REBASE_TIP
         (the branch's commit before this rebase touches it) FIRST, before
         attempting the rebase — capture this value regardless of whether the
         rebase then conflicts, so there is always a way back to this exact
         point with `undo`, including mid-conflict (`git rebase --abort`
         handles that case instead — see SKILL.md).
push   - `git push --force-with-lease <remote> <working-branch>`
         (remote defaults to origin). Only call after explicit user
         confirmation that the branch is pushed / has an open PR.
tracks - Reports whether <working-branch> has an upstream remote-tracking
         branch, so the skill knows whether it's worth asking about push.
undo   - Resets <working-branch> back to <pre-rebase-tip> with a hard reset.
         Only valid once the rebase has *finished* (no conflict in progress —
         use `git rebase --abort` for that) and only before anything has been
         pushed. Refuses to run if a rebase is currently in progress, or if
         <pre-rebase-tip> isn't a commit that actually exists in this repo.
EOF
  exit 1
}

resolve_old_base() {
  local working_branch=$1 new_base=$2 old_base=${3:-}
  if [ -z "$old_base" ]; then
    git merge-base "$working_branch" "$new_base"
  else
    echo "$old_base"
  fi
}

cmd_trial() {
  local working_branch=$1 new_base=$2 old_base
  old_base=$(resolve_old_base "$working_branch" "$new_base" "${3:-}")

  local current_branch
  current_branch=$(git branch --show-current)
  local trial_branch="_saferebase_trial_$$"

  git branch -f "$trial_branch" "$working_branch" >/dev/null
  git checkout -q "$trial_branch"

  echo "OLD_BASE=$old_base"
  echo "NEW_BASE_TIP=$(git rev-parse --short "$new_base")"
  echo "COMMITS_TO_REPLAY:"
  git log --oneline "$old_base..$working_branch"

  local status="clean"
  local rebase_log
  rebase_log=$(mktemp)
  if ! git rebase --onto "$new_base" "$old_base" "$trial_branch" >"$rebase_log" 2>&1; then
    status="conflict"
    echo "CONFLICTING_FILES:"
    git diff --name-only --diff-filter=U
    echo "REBASE_OUTPUT:"
    cat "$rebase_log"
    git rebase --abort >/dev/null 2>&1 || true
  fi
  rm -f "$rebase_log"

  git checkout -q "$current_branch"
  git branch -D "$trial_branch" >/dev/null 2>&1 || true

  echo "STATUS=$status"
  [ "$status" = "clean" ]
}

cmd_apply() {
  local working_branch=$1 new_base=$2 old_base
  old_base=$(resolve_old_base "$working_branch" "$new_base" "${3:-}")
  git checkout -q "$working_branch"
  echo "PRE_REBASE_TIP=$(git rev-parse "$working_branch")"
  git rebase --onto "$new_base" "$old_base" "$working_branch"
}

cmd_push() {
  local working_branch=$1 remote=${2:-origin}
  git push --force-with-lease "$remote" "$working_branch"
}

cmd_tracks() {
  local working_branch=$1 upstream
  if upstream=$(git rev-parse --abbrev-ref --symbolic-full-name "$working_branch@{u}" 2>/dev/null); then
    echo "TRACKS=yes"
    echo "UPSTREAM=$upstream"
  else
    echo "TRACKS=no"
  fi
}

cmd_undo() {
  local working_branch=$1 pre_rebase_tip=$2

  if [ -d "$(git rev-parse --git-path rebase-merge)" ] || [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
    echo "ERROR: a rebase is currently in progress — use 'git rebase --abort' instead, not undo." >&2
    exit 1
  fi

  if ! git cat-file -e "${pre_rebase_tip}^{commit}" 2>/dev/null; then
    echo "ERROR: '$pre_rebase_tip' is not a commit that exists in this repo — refusing to reset." >&2
    exit 1
  fi

  git checkout -q "$working_branch"
  git reset --hard "$pre_rebase_tip"
  echo "RESTORED $working_branch TO $pre_rebase_tip"
}

[ $# -ge 1 ] || usage
sub=$1; shift
case "$sub" in
  trial)  [ $# -ge 2 ] || usage; cmd_trial "$@" ;;
  apply)  [ $# -ge 2 ] || usage; cmd_apply "$@" ;;
  push)   [ $# -ge 1 ] || usage; cmd_push "$@" ;;
  tracks) [ $# -ge 1 ] || usage; cmd_tracks "$@" ;;
  undo)   [ $# -ge 2 ] || usage; cmd_undo "$@" ;;
  *) usage ;;
esac
