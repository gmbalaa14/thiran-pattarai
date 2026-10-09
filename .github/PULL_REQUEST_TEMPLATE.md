## Description

<!-- Briefly describe what this PR adds or changes, and why -->

## Type of change

<!-- Keep the lines that apply -->
- [ ] New skill in an existing plugin
- [ ] New plugin
- [ ] Change to an existing skill or plugin
- [ ] Docs site or documentation only
- [ ] CI, scripts or repository housekeeping

## PR Checklist

### Skills
- [ ] Skill folder name is lowercase-hyphenated and matches `name` in `SKILL.md`
- [ ] `SKILL.md` has frontmatter with `name` and `description`
- [ ] `SKILL.md` and bundled scripts are saved with LF line endings (no CRLF)
- [ ] No hard-coded `~/.claude/skills/...` paths; scripts are referenced with `${CLAUDE_SKILL_DIR}`
- [ ] Helper files live in the skill's `references/` or `scripts/` folder

### Plugins and versioning
- [ ] New plugin: added to the `plugins` array in `.claude-plugin/marketplace.json` with the same `name` and `version` as its `plugin.json`
- [ ] New plugin: name is kebab-case (`thiran` or `thiran-<domain>`)
- [ ] Changed plugin: `version` bumped in both `plugin.json` and `marketplace.json`

### Documentation
- [ ] Optional richer skill page added in `docs/src/data/skill-docs.ts` (if the skill needs one)
- [ ] New hand-written docs page has an entry in `docs/src/data/nav.ts`
- [ ] `CONTRIBUTING.md` and `docs/src/pages/contributing.md` updated together (if either changed)
- [ ] `CODE_OF_CONDUCT.md` and `docs/src/pages/code-of-conduct.md` updated together (if either changed)
- [ ] Root `README.md` plugin table updated (if commands were added or renamed)

### Testing
- [ ] `python3 scripts/validate.py` passes
- [ ] `cd docs && npm run build` completes without errors
- [ ] Skill tried in Claude Code (`/plugin install <plugin>@pattarai`, then run `/<plugin>:<skill>`)
