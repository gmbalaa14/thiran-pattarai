---
layout: ../layouts/Doc.astro
title: Contributing
description: How to add a skill or a plugin to Thiran Pattarai.
---

# Contributing

<p class="lede">Adding a skill is a folder and a file. Adding a plugin is one more folder and one catalogue entry. The docs site discovers both on its own.</p>

## Add a skill to an existing plugin

1. Create `plugins/<plugin>/skills/<your-skill>/SKILL.md`.
2. Start it with frontmatter. The name must match the folder:

```markdown
---
name: your-skill
description: One or two sentences on what it does and when Claude should use it.
metadata:
  author: "Your Name"
  version: "1.0.0"
---
```

3. Put helper files next to it in `references/` or `scripts/`.
4. Open a pull request.

That is enough for the skill to appear on the site, with its name, description, version and requirements read straight from `SKILL.md`. For a richer page (when to use it, how it works, an example), add an entry in `docs/src/data/skill-docs.ts`.

## Add a new plugin

1. Create `plugins/<new-plugin>/.claude-plugin/plugin.json` and a `skills/` folder.
2. Add the plugin to the `plugins` array in `.claude-plugin/marketplace.json`, with the same name and version.
3. Run `python3 scripts/validate.py`.

Naming: the core plugin is `thiran`. Domain plugins use `thiran-<domain>`, such as `thiran-devops`. The plugin name is also the command prefix, so keep it short.

## Refer to bundled scripts safely

A plugin is copied into a cache folder when installed, so never hard-code `~/.claude/skills/...`. Use `${CLAUDE_SKILL_DIR}` instead:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/render_diff.py "$FILE"
```

To call a script in a sibling skill of the same plugin, use `${CLAUDE_SKILL_DIR}/../<other-skill>/scripts/...`.

## Run the docs site locally

```bash
cd docs
npm install
npm run dev
```

The site builds with Astro and deploys to GitHub Pages from `main`.

## Releasing a change

Bump `version` for the plugin in both its `plugin.json` and the marketplace entry. Installed copies update only when the version changes. Plugins are versioned independently.
