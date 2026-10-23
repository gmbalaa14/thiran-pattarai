---
name: commit-msg
description: "Writes a conventional commit message or a PR title and description from real git changes, text only, never runs git commit. Use when: about to commit staged or modified changes; user says commit message, write the commit, PR title, PR description or summarize my branch; a mixed diff may need splitting into commits; user pastes a diff to describe. Asks first which one to generate."
compatibility: Requires a git repository and bash. Commit messages need staged or modified changes; PR text needs commits on the current branch.
license: "MIT"
metadata:
  author: "Balagurunathan Marimuthu"
  version: "1.1.0"
---

# Commit Message Generator

Turn a git diff into a commit message or PR text a reviewer can skim in ten seconds. Read the real changes first: a message written from the user's description alone tends to state intent rather than what the code does.

## Step 1: Ask what to generate

Call `AskUserQuestion` with one question, header "Generate", and these options:

- **Commit message**: for the staged or modified changes in the working tree
- **PR title and description**: for the commits on the current branch against its base branch

Skip the question only when the user already said which ("commit message pls", "PR description for this branch"). Then run only the matching flow below.

## Flow A: Commit message

### A1. Summarise the working tree

Run `bash ${CLAUDE_SKILL_DIR}/scripts/git-summary.sh commit` (if bash is unavailable, use `git status --porcelain` and `git diff --cached --name-status`). Show one line before anything else, for example: `Staged: 3 files, modified: 2, untracked: 1 (excluded)`. If the script lists partly staged files, name them: the staged-only message will not cover their unstaged part.

### A2. Choose the scope

Untracked files are always excluded: they are often scratch or build output, and `git diff` does not show them. Mention them in the summary line and leave them out. If the user wants one included, they run `git add` and pick Retry.

| Situation | What to do |
|---|---|
| Only staged files | No question. Describe `git diff --cached`. |
| Staged and modified both exist | Ask: **Staged only (N files) (Recommended)**, **Staged + modified (N files)**, **Retry after I restage** |
| Nothing staged, modified files exist | Ask: **Modified files (N files)**, **Retry after I stage**, **Cancel** |
| Only untracked files | Say so, list them, and stop. |
| Nothing at all | Say the working tree is clean and stop. |

Put the real file count in each label. **Retry** means the user is rearranging files: re-run the summary, show the new counts, and continue from the top of this table. If the state did not change, say so and ask again.

Re-run `git-summary.sh commit <scope>` with the chosen scope (`staged`, `modified` or `staged+modified`) so the classification counts match what you will describe. The diff to read is:

- Staged only: `git diff --cached`
- Staged + modified: `git diff HEAD`, which shows the net result even for partly staged files
- Modified files: `git diff`

If the message covers files that are not staged, end the output with a reminder to `git add` them first so the commit matches the message. If `AskUserQuestion` is not available (an unattended run), default to staged only and say so.

### A3. Read the diff

Start with the `--stat` form of the chosen diff, then the full diff. On a large diff, open only the files that carry the meaning. Run `git log -5 --format=%s` to reuse the repo's scope names and tone.

### A4. Decide the type and whether to split

Read `${CLAUDE_SKILL_DIR}/references/file-classification.md` and apply it with the counts from the script. In short:

- `docs`, `test` and companion files (lockfiles, generated code, snapshots) ride along with any other type and never trigger a split.
- Two or more different primary types (`feat`, `fix`, `refactor`, `perf`, `build`, `ci`, `chore`, `style`) mean a proposed split: one message per type, with the files for each, and a note that `git add -p` is needed if one file holds two concerns.
- The same primary type across several folders is one message with combined scopes, such as `fix(encryption,utils)`.
- Docs and tests only: the type with more changed files wins, `test` wins a tie. Flag the choice with the override line described under Output.

### A5. Write the message

- **Type**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`. Choose by what changes for users or the system, not by which files were touched. A fix that also adds a test is `fix`.
- **Scope**: the module or folder most affected, reusing names from `git log`. Several scopes are comma-separated with no space and capped at 3. Leave the docs scope out when docs ride along.
- **Subject**: `type(scope): description`. Imperative mood, starts with a lowercase letter, no trailing period, about 50 characters and never over 72.
- **Body**: add one when the subject cannot carry the reason. Explain why the change was needed and what behaviour changes, since the diff already shows what. Wrap at about 72 characters, separated from the subject by a blank line. When docs, tests or a dependency ride along with another type, add one combined sentence such as `Also adds tests and updates the README.` A docs-only commit gets a body when it describes a behaviour change, a command or a requirement, or spans several files or sections; a typo fix or wording tweak gets none.
- **Breaking change**: when a public API, config key, schema, CLI flag or file format changes incompatibly, add `!` after the type or scope and a `BREAKING CHANGE:` footer saying how to adapt. The token must be exactly that, because release tooling reads it.
- **Footer**: issue references such as `Fixes #123`. Take them from the branch name (`git branch --show-current`) or the diff. If none is found, leave the footer out rather than inventing one.

```
type(scope): subject in imperative mood

Why the change was needed and what it affects. Mention migration steps
if anything downstream must change.

BREAKING CHANGE: what changed and how to adapt.
Fixes #123
```

Then humanize the draft (Step 3).

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
6. Humanize (Step 3).

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

Show the summary line, then the message in one code block so it can be copied, then short notes on anything the user should decide: a suggested split, a guessed scope, a base-branch confirmation, a missing issue number, or the staging reminder.

When the type was a judgment call between docs and tests, add one plain line instead of a question, for example: `Typed as test (3 test files vs 2 docs). Say "use docs" to switch.`

Never run `git commit`, `git push` or create a PR unless the user explicitly asks. The text is the deliverable. Do not add any Claude attribution, co-author trailer or "generated with" line to a commit message or PR description: the user is the author of everything this skill writes.
