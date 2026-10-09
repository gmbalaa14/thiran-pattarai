import { plugins } from './registry';

// Plugins can add extra hand-written pages here (shown under that plugin).
const extraPages: Record<string, { label: string; href: string }[]> = {
  thiran: [{ label: 'The workflow', href: '/plugins/thiran/workflow/' }],
};

export const nav = [
  {
    label: 'Start here',
    items: [
      { label: 'Introduction', href: '/' },
      { label: 'Getting started', href: '/getting-started/' },
    ],
  },
  ...plugins.map((p) => ({
    label: `Plugin · ${p.name}`,
    items: [
      { label: 'Overview', href: `/plugins/${p.name}/` },
      ...(extraPages[p.name] ?? []),
      ...p.skills.map((s) => ({ label: s.title, href: `/plugins/${p.name}/${s.slug}/` })),
    ],
  })),
  {
    label: 'Project',
    items: [
      { label: 'Contributing', href: '/contributing/' },
      { label: 'Code of Conduct', href: '/code-of-conduct/' },
    ],
  },
];
