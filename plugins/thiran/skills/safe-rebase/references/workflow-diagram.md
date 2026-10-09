# Safe Rebase — Workflow Diagram (Mermaid)

Reference copy of the workflow described in `SKILL.md`'s "Workflow at a glance" section, in Mermaid form for rendering (GitHub, most Markdown previewers, mermaid.live, etc.). `SKILL.md` uses a plain nested list instead of a diagram there — it's the one actually loaded into context when the skill triggers, and stays readable at any width. Read this file only when a rendered picture is more useful, e.g. sharing it with someone else or checking the full shape of the flow at a glance.

```mermaid
flowchart TD
    A["trial: rebase disposable branch<br/>onto new-base (real branch untouched)"] --> B{STATUS}

    B -->|clean| E["Confirm plan with user<br/>(branch, old base to new base, commit count)"]
    B -->|conflict| C["Report CONFLICTING_FILES to user"]
    C --> D{User choice}
    D -->|hold off| Z1["Stop, nothing touched"]
    D -->|resolve for real| E

    E -->|confirmed| F["apply: git rebase --onto<br/>(records PRE_REBASE_TIP first)"]

    F --> G{Result}

    G -->|conflict on a commit| H["Resolve hunk-by-hunk:<br/>read both sides' intent,<br/>never blanket --ours or --theirs"]
    H -->|commit resolved| I["git add; git rebase --continue"]
    I --> G
    H -->|user wants to stop| J["git rebase --abort<br/>results in full revert to PRE_REBASE_TIP<br/>no partial state survives"]

    G -->|clean or all commits resolved| K{tracks upstream?}

    K -->|no| L["Done, local only"]
    K -->|yes| M["Confirm push with user<br/>(mention PR / CI impact)"]

    M -->|decline / not yet| N["Stop, rebase kept locally.<br/>undo command with PRE_REBASE_TIP<br/>still available"]
    M -->|confirmed| O["push --force-with-lease<br/>never bare --force"]
    O --> P["Done, remote / PR updated.<br/>PRE_REBASE_TIP safety net gone."]

    style Z1 fill:#2d5,stroke:#333
    style L fill:#2d5,stroke:#333
    style N fill:#fc5,stroke:#333
    style P fill:#2d5,stroke:#333
    style J fill:#fc5,stroke:#333
```

## Key invariants this diagram encodes

- **Every terminal node is either "matches what the user asked for" or "back at the exact commit they started from"** — never a state the user didn't choose to be in.
- **`J` (mid-rebase abort) and `N` → `undo` (post-apply, pre-push revert) are different mechanisms for different moments** — see the "Backing out" section in `SKILL.md` for why they aren't interchangeable. There is no path in this diagram that partially reverts a rebase; abort is always a full revert to `PRE_REBASE_TIP`, regardless of how many commits already replayed cleanly in that attempt.
- **The safety net (`undo`) disappears at `O`** — pushing is the actual point of no return in this workflow, not the local rebase itself.
