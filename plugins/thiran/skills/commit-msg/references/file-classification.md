# File classification and commit-type rules

`scripts/git-summary.sh commit` classifies every file in the chosen scope and prints the counts. Use those counts with the rules below. The patterns are a starting point: if a file is clearly misclassified (a `README` that is really a generated report, a `tests/` folder holding fixtures for production code), use judgment and say so.

## Categories

| Category | Patterns | Role |
|---|---|---|
| companion | `*.lock`, `package-lock.json`, `pnpm-lock.yaml`, `go.sum`, `packages.lock.json`, `*.g.cs`, `*.Designer.cs`, `*ModelSnapshot.cs`, `*.generated.*`, `*.snap`, `__snapshots__/` | Produced by a change, not authored. Never counted, never triggers a split. |
| tests | `tests/`, `test/`, `__tests__/`, `*Tests.cs`, `*Test.cs`, `*.spec.*`, `*.test.*`, `*_test.go`, `test_*.py` | Rides along with another type. |
| docs | `*.md`, `*.rst`, `docs/`, `README*`, `CHANGELOG*`, `LICENSE*` | Rides along with another type. Markdown under `skills/` counts as code because the skill file is the product. |
| code | everything else | Decides the type. |

## Choosing the type

1. **Primary types** are `feat`, `fix`, `refactor`, `perf`, `build`, `ci`, `chore`, `style`. Each one decides a commit.
2. **One primary type present**: use it. Docs, tests and companions ride along.
3. **Two or more primary types present** (for example `feat` plus `fix`): propose a split, one commit per type, listing which files go in which commit. Say that a file holding two concerns needs `git add -p`. Do not split on `docs`, `test` or companions.
4. **Same primary type across several folders**: one message, scopes combined.
5. **Only docs and tests present** (no code, no primary type):
   - Only one of them: use that type (`docs` or `test`).
   - Both: the type with more changed files wins. On a tie, `test` wins and a body line covers the docs.
   - Add the override line from the skill output section.
   - Only companions (a lockfile refresh with no authored change): use `chore(deps)` for lockfiles, otherwise `chore` with the generator as scope, and say in the notes that nothing authored changed.
6. **`style` stays a split trigger.** Formatting sweeps bury the real change in review and blame history.
7. **Dependency manifests** (`.csproj`, `package.json`, `requirements.txt`): if the diff only adds or bumps the package the code change uses, it rides along and gets flagged in the body. Anything broader (a wholesale upgrade, a new build target) is a separate `build` commit.
8. **Docs go with the commit they document.** In a split, the README line about JWT login belongs with the `feat`, not with an unrelated `fix`.

## Scopes

- Take the module or folder most affected. Reuse names from `git log`.
- Several scopes: comma, no space: `fix(encryption,utils)`.
- Cap at 3. Beyond that, use the parent module name or drop the scope.
- Leave the docs scope out when docs ride along. Say it in the body instead.

## Body lines for riding-along files

Write one combined sentence, not one line per kind:

- docs only rides along: `Also updates the README.`
- tests only rides along: `Also adds tests for order totals.`
- both: `Also adds tests and updates the README.`
- docs-and-tests tie won by `test`: `Also updates the README.`
- docs win on count: `Also adds tests for X.`
- manifest rides along: `Also adds the Foo package.`

## Docs-only commits

No body when the subject says everything (a typo, a wording tweak, "add local run steps and .NET 8 requirement"). Add a body when the docs describe a behaviour change, a command or a requirement the reader needs explained, or when the commit spans several files or sections.
