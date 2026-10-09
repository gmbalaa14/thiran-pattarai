---
layout: ../layouts/Doc.astro
title: Contributing
description: How to add a skill or a plugin to Thiran Pattarai, and get your change merged.
---

# Contributing

<p class="lede">Adding a skill is a folder and a file. Adding a plugin is one more folder and one catalogue entry. The docs site discovers both on its own.</p>

Everyone taking part is expected to follow the [Code of Conduct](/code-of-conduct/).

## How the repository is organised

```text
.claude-plugin/marketplace.json   marketplace catalogue (name: pattarai)
plugins/<plugin>/                 one folder per plugin
  .claude-plugin/plugin.json
  skills/<skill>/SKILL.md
docs/                             Astro documentation site
scripts/validate.py               manifest and skill checks used in CI
brand/                            logos, favicon and banners
```

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
4. Save files with LF line endings. CI rejects CRLF in `SKILL.md`.
5. Open a pull request.

That is enough for the skill to appear on the site, with its name, description, version and requirements read straight from `SKILL.md`. For a richer page (when to use it, how it works, an example), add an entry in `docs/src/data/skill-docs.ts`.

## Add a new plugin

1. Create `plugins/<new-plugin>/.claude-plugin/plugin.json` and a `skills/` folder with at least one skill.
2. Add the plugin to the `plugins` array in `.claude-plugin/marketplace.json`, with the same name and version as in its `plugin.json`.
3. Run `python3 scripts/validate.py`.

Naming: the core plugin is `thiran`. Domain plugins use `thiran-<domain>`, such as `thiran-devops`. Names must be kebab-case. The plugin name is also the command prefix, so keep it short.

## Refer to bundled scripts safely

A plugin is copied into a cache folder when installed, so never hard-code `~/.claude/skills/...`. Use `${CLAUDE_SKILL_DIR}` instead:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/render_diff.py "$FILE"
```

To call a script in a sibling skill of the same plugin, use `${CLAUDE_SKILL_DIR}/../<other-skill>/scripts/...`.

## Documentation site

The site builds with Astro and deploys to GitHub Pages from `main`.

- Skill and plugin pages are generated from the manifests and `SKILL.md` files.
- Hand-written pages live in `docs/src/pages/`.
- Sidebar entries are defined in `docs/src/data/nav.ts`. A new hand-written page needs an entry there.
- Root-relative links inside Markdown, such as `/contributing/`, are prefixed with the site base path automatically.

`CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` in the repository root have matching pages here. If you change one, update the other in the same pull request.

To run the site locally:

```bash
cd docs
npm install
npm run dev
```

## Validate your change

```bash
python3 scripts/validate.py          # manifests and skills
cd docs && npm ci && npm run build   # docs site builds without errors
```

CI runs both on every pull request.

## Releasing a change

Bump `version` for the plugin in both its `plugin.json` and the marketplace entry. Installed copies update only when the version changes. Plugins are versioned independently.

## Submitting a PR

1. Fork the repository.
2. Create a branch: `git checkout -b add-<skill-or-plugin-name>`.
3. Make your change, following the sections above.
4. Run the checks in [Validate your change](#validate-your-change).
5. Open a pull request against `main`. The pull request template fills in automatically; tick every item that applies and delete the ones that do not.

## PR checklist

The pull request template covers four groups of checks:

- **Skills:** folder name matches `name` in `SKILL.md`, frontmatter is present, LF line endings, and no hard-coded `~/.claude/skills` paths.
- **Plugins and versioning:** new plugins are in `marketplace.json` with matching name and version, and changed plugins have their version bumped in both manifests.
- **Documentation:** new hand-written pages are in `nav.ts`, and the repo and docs-site copies of `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` change together.
- **Testing:** `python3 scripts/validate.py` and the docs build pass, and the skill has been tried in Claude Code.

## Reporting issues

Use the [issue templates](https://github.com/gmbalaa14/thiran-pattarai/issues/new/choose):

- **Bug report:** a skill misbehaves, a plugin fails to install, or the site is broken.
- **Skill or plugin request:** a new skill, a new plugin, or an improvement to an existing skill.
- **Documentation issue:** something on the site or in a README is unclear, wrong or missing.

Blank issues are turned off so every report has the details needed to act on it. Report Code of Conduct concerns privately, as described in the [Code of Conduct](/code-of-conduct/#enforcement).

## License

By contributing, you agree your contribution is licensed under MIT.
