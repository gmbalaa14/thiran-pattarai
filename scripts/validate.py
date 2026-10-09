#!/usr/bin/env python3
"""Validate manifests and skills. Exit 1 on any problem."""
import json, re, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
errors = []

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"{p.relative_to(root)}: invalid JSON ({e})")

RESERVED = {"claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
            "anthropic-marketplace", "anthropic-plugins", "agent-skills", "life-sciences"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

mp = load(root / ".claude-plugin" / "marketplace.json")
if mp:
    if mp.get("name") in RESERVED or not KEBAB.match(mp.get("name", "")):
        errors.append(f"marketplace name '{mp.get('name')}' is reserved or not kebab-case")
    names = [e["name"] for e in mp.get("plugins", [])]
    if len(names) != len(set(names)):
        errors.append("duplicate plugin names in marketplace.json")
for entry in (mp or {}).get("plugins", []):
    src = root / entry["source"]
    if not KEBAB.match(entry["name"]):
        errors.append(f"plugin name '{entry['name']}' must be kebab-case")
    if not src.is_dir():
        errors.append(f"{entry['name']}: source folder {entry['source']} not found"); continue
    pj = load(src / ".claude-plugin" / "plugin.json")
    if pj and pj.get("name") != entry["name"]:
        errors.append(f"plugin name mismatch: {entry['name']} vs {pj.get('name')}")
    if pj and pj.get("version") != entry.get("version"):
        errors.append(f"{entry['name']}: version differs between marketplace.json and plugin.json")
    skills = sorted((src / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append(f"{entry['name']}: no skills found")
    for f in skills:
        raw = f.read_bytes()
        if b"\r\n" in raw:
            errors.append(f"{f.relative_to(root)}: CRLF line endings; save as LF")
        text = raw.decode("utf-8")
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not m:
            errors.append(f"{f.relative_to(root)}: missing frontmatter"); continue
        fm = m.group(1)
        name = re.search(r"^name:\s*(.+)$", fm, re.M)
        desc = re.search(r"^description:\s*(.+)$", fm, re.M)
        if not name or name.group(1).strip().strip('"') != f.parent.name:
            errors.append(f"{f.relative_to(root)}: name must equal folder '{f.parent.name}'")
        if not desc:
            errors.append(f"{f.relative_to(root)}: missing description")
        if ".claude/skills/" in text:
            errors.append(f"{f.relative_to(root)}: hard-coded ~/.claude/skills path; use ${{CLAUDE_SKILL_DIR}}")
    print(f"{entry['name']}: {len(skills)} skills checked")

if errors:
    print("\n".join("ERROR " + e for e in errors)); sys.exit(1)
print("OK")
