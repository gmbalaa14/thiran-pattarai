# Contributing to Thiran Pattarai

Thank you for contributing! This guide covers how to add a skill, add a plugin, and get a change merged. The same guide is published on the [documentation site](https://gmbalaa14.github.io/thiran-pattarai/contributing/).

## Table of Contents

- [How the repository is organised](#how-the-repository-is-organised)
- [Add a skill to an existing plugin](#add-a-skill-to-an-existing-plugin)
- [Add a new plugin](#add-a-new-plugin)
- [Refer to bundled scripts safely](#refer-to-bundled-scripts-safely)
- [Documentation site](#documentation-site)
- [Validate your change](#validate-your-change)
- [Releasing a change](#releasing-a-change)
- [Submitting a PR](#submitting-a-pr)
- [PR checklist](#pr-checklist)
- [Code of Conduct](#code-of-conduct)

---

## How the repository is organised

```
.claude-plugin/marketplace.json   marketplace catalogue (name: pattarai)
plugins/<plugin>/                 one folder per plugin
  .claude-plugin/plugin.json
  skills/<skill>/SKILL.md
docs/                             Astro documentation site
scripts/validate.py               manifest and skill checks used in CI
brand/                            logos, favicon and banners
```

The docs site discovers plugins and skills from the manifests and `SKILL.md` files, so adding either needs no navigation edits.

---

## Add a skill to an existing plugin

1. Create `plugins/<plugin>/skills/<your-skill>/SKILL.md`.
2. Start it with frontmatter. The `name` must match the folder name:

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

---

## Add a new plugin

1. Create `plugins/<new-plugin>/.claude-plugin/plugin.json` and a `skills/` folder with at least one skill.
2. Add the plugin to the `plugins` array in `.claude-plugin/marketplace.json`, with the same `name` and `version` as in its `plugin.json`.
3. Run `python3 scripts/validate.py`.

**Naming:** the core plugin is `thiran`. Domain plugins use `thiran-<domain>`, such as `thiran-devops`. Names must be kebab-case. The plugin name is also the command prefix (`/<plugin>:<skill>`), so keep it short.

---

## Refer to bundled scripts safely

A plugin is copied into a cache folder when installed, so never hard-code `~/.claude/skills/...`. Use `${CLAUDE_SKILL_DIR}` instead:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/render_diff.py "$FILE"
```

To call a script in a sibling skill of the same plugin, use `${CLAUDE_SKILL_DIR}/../<other-skill>/scripts/...`.

---

## Documentation site

The site lives in `docs/`, is built with [Astro](https://astro.build/), and deploys to GitHub Pages from `main`.

- Skill and plugin pages are generated from the manifests and `SKILL.md` files.
- Hand-written pages live in `docs/src/pages/` (for example `contributing.md` and `code-of-conduct.md`).
- Sidebar entries are defined in `docs/src/data/nav.ts`. A new hand-written page needs an entry there.
- Root-relative links inside Markdown (such as `/contributing/`) are prefixed with the site base path automatically.

If you change `CONTRIBUTING.md` or `CODE_OF_CONDUCT.md`, update the matching page under `docs/src/pages/` in the same pull request so the site and the repository stay in step.

To run the site locally:

```bash
cd docs
npm install
npm run dev
```

---

## Validate your change

```bash
python3 scripts/validate.py          # manifests and skills
cd docs && npm ci && npm run build   # docs site builds without errors
```

CI runs both on every pull request.

---

## Releasing a change

Bump `version` for the plugin in both its `plugin.json` and its marketplace entry. Installed copies update only when the version changes. Plugins are versioned independently.

---

## Submitting a PR

1. Fork the repository.
2. Create a branch: `git checkout -b add-<skill-or-plugin-name>`
3. Make your change, following the sections above.
4. Run the checks in [Validate your change](#validate-your-change).
5. Open a pull request against `main` and copy in the checklist below.

---

## PR checklist

```
- [ ] Skill folder name is lowercase-hyphenated and matches `name` in SKILL.md
- [ ] SKILL.md has frontmatter with name and description
- [ ] SKILL.md is saved with LF line endings
- [ ] No hard-coded ~/.claude/skills paths (use ${CLAUDE_SKILL_DIR})
- [ ] New plugin: added to .claude-plugin/marketplace.json with matching name and version
- [ ] Changed plugin: version bumped in plugin.json and marketplace.json
- [ ] python3 scripts/validate.py passes
- [ ] Docs build passes (cd docs && npm run build)
- [ ] Docs pages updated if CONTRIBUTING.md or CODE_OF_CONDUCT.md changed
```

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). By participating you agree to abide by its terms.
