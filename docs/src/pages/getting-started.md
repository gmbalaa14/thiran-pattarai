---
layout: ../layouts/Doc.astro
title: Getting started
description: Install the thiran plugin from the pattarai marketplace.
---

# Getting started

<p class="lede">Add the marketplace once, install a plugin, and its skills are ready to use. The marketplace is called `pattarai` and the first plugin is `thiran`.</p>

## Install

Run these inside Claude Code:

```text
/plugin marketplace add gmbalaa14/thiran-pattarai
/plugin install thiran@pattarai
```

Restart or reload Claude Code if the skills do not show up straight away. Run `/plugin` to confirm that **thiran** is enabled.

The `@pattarai` in the install command names the marketplace. Future plugins install the same way, for example `/plugin install thiran-devops@pattarai`.

## Use a skill

Plugin skills are namespaced by the plugin name, so they run as `/thiran:<skill>`:

| Skill | Command |
| --- | --- |
| Plan With Me | `/thiran:plan-with-me` |
| Commit Message | `/thiran:commit-msg` |
| Safe Rebase | `/thiran:safe-rebase` |
| PR Triage | `/thiran:pr-triage` |
| PR Judge | `/thiran:pr-judge` |

Claude can also pick a skill by itself when your request matches its description. Asking to "rebase this branch onto the updated develop" will bring in Safe Rebase.

## Share it with your team

The fastest route is to commit this to a project's `.claude/settings.json`, so everyone is prompted to install it when they trust the folder:

```json
{
  "extraKnownMarketplaces": {
    "pattarai": {
      "source": { "source": "github", "repo": "gmbalaa14/thiran-pattarai" }
    }
  },
  "enabledPlugins": {
    "thiran@pattarai": true
  }
}
```

## Update

```text
/plugin marketplace update pattarai
```

## Requirements by skill

| Skill | Needs |
| --- | --- |
| Plan With Me | Read access to the codebase. OpusPlan mode is recommended. |
| Commit Message | A git repository with staged changes. |
| Safe Rebase | `git` and `bash` (Git Bash on Windows). |
| PR Triage | Python 3.7+, and an Azure DevOps personal access token. |
| PR Judge | Python 3 for the diff renderer. A pr-triage report is optional. |

## Set up the Azure DevOps token

PR Triage looks for the token in this order:

1. The `ADO_PAT` environment variable
2. `ado_pat` in `~/.claude/config.json`
3. `ado_pat` in `./.claude/config.json` at the repo root

```json
{ "ado_pat": "your-token-here" }
```

Never commit a file that contains a real token.
