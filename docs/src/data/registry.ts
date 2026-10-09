// Build-time registry. Reads the real manifests and SKILL.md files so the site
// updates itself when a plugin or skill is added: no navigation to hand-edit.
import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import { skillDocs, type SkillDoc } from './skill-docs';

const ROOT = path.resolve(process.cwd(), '..');

export interface Skill {
  plugin: string;
  slug: string;
  command: string;
  title: string;
  stage: string;
  tagline: string;
  whenToUse: string[];
  howItWorks: string[];
  example: string;
  needs: string[];
  notes?: string[];
  documented: boolean;
  fm: { description: string; version?: string; author?: string; compatibility?: string; license?: string };
  sourcePath: string;
}
export interface Plugin {
  name: string;
  description: string;
  version: string;
  category?: string;
  skills: Skill[];
}

const titleCase = (s: string) => s.split('-').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ');
const readJson = (p: string) => JSON.parse(fs.readFileSync(p, 'utf8'));

function readSkill(plugin: string, dir: string): Skill {
  const file = path.join(ROOT, 'plugins', plugin, 'skills', dir, 'SKILL.md');
  const raw = fs.readFileSync(file, 'utf8');
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) throw new Error(`${file}: missing frontmatter`);
  const fm = YAML.parse(m[1]);
  if (fm.name !== dir) throw new Error(`${file}: name "${fm.name}" must equal folder "${dir}"`);
  const doc: SkillDoc | undefined = skillDocs.find((d) => d.plugin === plugin && d.slug === dir);
  const description = String(fm.description ?? '').replace(/^Usage:[^.]*\.\s*/, '');
  return {
    plugin,
    slug: dir,
    command: `/${plugin}:${dir}`,
    title: doc?.title ?? titleCase(dir),
    stage: doc?.stage ?? 'Skill',
    tagline: doc?.tagline ?? description,
    whenToUse: doc?.whenToUse ?? [],
    howItWorks: doc?.howItWorks ?? [],
    example: doc?.example ?? `/${plugin}:${dir}`,
    needs: doc?.needs ?? (fm.compatibility ? [String(fm.compatibility)] : []),
    notes: doc?.notes,
    documented: !!doc,
    fm: {
      description: String(fm.description ?? ''),
      version: fm.metadata?.version,
      author: fm.metadata?.author,
      compatibility: fm.compatibility,
      license: fm.license,
    },
    sourcePath: `plugins/${plugin}/skills/${dir}/SKILL.md`,
  };
}

export function loadPlugins(): Plugin[] {
  const market = readJson(path.join(ROOT, '.claude-plugin', 'marketplace.json'));
  return market.plugins.map((entry: any) => {
    const name: string = entry.name;
    const skillsDir = path.join(ROOT, 'plugins', name, 'skills');
    const dirs = fs.existsSync(skillsDir)
      ? fs.readdirSync(skillsDir).filter((d) => fs.existsSync(path.join(skillsDir, d, 'SKILL.md')))
      : [];
    // Documented skills keep their authored order; new ones follow alphabetically.
    const order = skillDocs.filter((d) => d.plugin === name).map((d) => d.slug);
    dirs.sort((a, b) => {
      const ia = order.indexOf(a), ib = order.indexOf(b);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib) || a.localeCompare(b);
    });
    return {
      name,
      description: entry.description,
      version: entry.version,
      category: entry.category,
      skills: dirs.map((d) => readSkill(name, d)),
    } as Plugin;
  });
}

export const plugins = loadPlugins();
export const getPlugin = (name: string) => plugins.find((p) => p.name === name)!;
