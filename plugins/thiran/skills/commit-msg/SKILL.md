---
name: commit-msg
description: "Writes a conventional commit message or a PR title and description from real git changes, text only, never runs git commit. Use when: about to commit staged changes; user says commit message, write the commit, PR title, PR description or summarize my branch; a messy diff needs splitting into commits; user pastes a diff to describe. Asks first which one to generate."
compatibility: Requires a git repository and bash. Commit messages need staged or uncommitted changes; PR text needs commits on the current branch.
license: "MIT"
metadata:
  author: "Balagurunathan Marimuthu"
  version: "1.1.0"
---

# Commit Message Generator

Turn a git diff into a commit message or PR text a reviewer can skim in ten seconds. Read the real changes first: a message written from the user's description alone tends to state intent rather than what the code does.

## Step 1: Ask what to generate

Call `AskUserQuestion` with one question, header "Generate", and these options:

- **Commit message**: for the staged (or uncommitted) changes in the working tree
- **PR title and description**: for the commits on the current branch against its base branch

Skip the question only when the user already said which one ("commit message pls", "PR description for this branch"). Then run only the matching flow below.

## Flow A: Commit message

1. **Summarise the working tree.** Run `bash ${CLAUDE_SKILL_DIR}/scripts/git-summary.sh commit` (if bash is unavailable, use `git status --porcelain` and `git diff --cached --name-status`). Show the user a one-line summary before the message, for example: `Staged: 3 files, unstaged: 2 files, untracked: 1 file`.
2. **Choose what to describe.**
   - Staged files exist: describe `git diff --cached`. Mention if unstaged files were left out.
   - Nothing staged but unstaged or untracked files exist: say so, list them, and ask whether to describe those instead. Do not guess silently.
   - Nothing at all: say the working tree is clean and stop.
3. **Read the diff.** Start with `git diff --cached --stat`, then the full diff. On a large diff, open only the files that carry the meaning and skip lockfiles, generated code and snapshots. Run `git log -5 --format=%s` to reuse the repo's scope names and tone.
4. **Check the shape.** If the diff mixes unrelated concerns (a feature, a drive-by fix, a formatting sweep), propose a split into separate commits with a message for each. Focused commits are what make history useful.
5. **Write the message** using the rules below.
6. **Humanize** with `${CLAUDE_SKILL_DIR}/references/humanizer-rules.md` (see Step 3).

### Message rules (Conventional Commits)

- **Type**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`. Choose by what changes for users or the system, not by which files were touched. A fix that also adds a test is `fix`.
- **Scope**: the module or folder most affected, reusing names seen in `git log`. Omit it when the change is cross-cutting.
- **Subject**: `type(scope): description`. Imperative mood, starts with a lowercase letter, no trailing period, about 50 characters and never over 72.
- **Body** (only when the subject is not enough): explain why the change was needed and what behaviour changes, since the diff already shows what. Wrap at about 72 characters. Separate from the subject with a blank line.
- **Breaking change**: when a public API, config key, schema, CLI flag or file format changes incompatibly, add `!` after the type or scope and a `BREAKING CHANGE:` footer saying how to adapt. The token must be exactly that, because release tooling reads it.
- **Footer**: issue references such as `Fixes #123`. Take them from the branch name (`git branch --show-current`) or the diff. If none is found, leave the footer out rather than inventing one.

```
type(scope): subject in imperative mood

Why the change was needed and what it affects. Mention migration steps
if anything downstream must change.

BREAKING CHANGE: what changed and how to adapt.
Fixes #123
```

## Flow B: PR title and description

1. **Find the real base branch.** Run `bash ${CLAUDE_SKILL_DIR}/scripts/git-summary.sh pr`. It picks the nearest ancestor among the remote default branch, `main`, `master`, `develop` and `release/*`, meaning the candidate with the fewest commits between it and HEAD, so a branch cut from `develop` is compared to `develop` and not to `main`. If the top two candidates are close, or the result looks wrong, tell the user which base you used and ask them to confirm before writing.
2. **Run git log against that base**: `git log --format='%h %s' <base>..HEAD` and `git diff <base>...HEAD`. The script prints the commit list and file stat; open the diff for the files that matter. If there are zero commits ahead, say so and stop.
3. **Show a short summary first**: base branch, number of commits, number of files changed.
4. **Title**: one line under 100 characters naming the outcome of the whole PR. For a single-commit PR, reuse its subject.
5. **Description**:
   - `## Summary`: 2 to 5 bullets, each under 100 characters, on what the PR achieves.
   - `## Details`: only when a reviewer needs context such as a design decision, a risky area or a migration step. Use backticks for identifiers and fenced blocks for snippets.
   - `## Breaking changes`: only when there are some.
   - Closing references (`Fixes #234`) at the end, only for issues found in commits or the branch name. If the repo uses Azure DevOps work item links (`AB#123`) in its history, follow that.
6. **Humanize** (Step 3).

```markdown
## Summary
- Add JWT login with automatic token refresh
- Validate tokens in the auth middleware on all protected routes

## Details
Refresh runs 60 seconds before expiry, see `TokenRefresher`.

Fixes #234
```

## Step 3: Humanize before showing

Read `${CLAUDE_SKILL_DIR}/references/humanizer-rules.md` and apply it to the draft. It lists the punctuation tells (em dashes), buzzwords, structural tells and compulsive summaries that make text read as machine-written. If a separate humanizer skill is installed, you may also run the draft through it, but the bundled rules are the standard and nothing depends on that skill.

## Output

Show the summary line, then the message in one code block so it can be copied, then one line on anything the user should decide (a suggested split, a guessed scope, a base-branch confirmation, a missing issue number). Never run `git commit`, `git push` or create a PR unless the user explicitly asks; the text is the deliverable.
