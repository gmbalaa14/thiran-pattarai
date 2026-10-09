import { defineConfig } from 'astro/config';

const SITE_BASE = '/thiran-pattarai';

// Astro's `base` only prefixes routes/assets it generates itself. Root-relative
// links written inside Markdown (e.g. `[Skills](/skills/)`) are not rewritten,
// so they would 404 under the GitHub Pages sub-path. This plugin prefixes them.
function remarkBasePrefixInternalLinks() {
  return (tree) => {
    const visit = (node) => {
      if (node.type === 'link' && typeof node.url === 'string') {
        const rootRelative = node.url.startsWith('/') && !node.url.startsWith('//');
        const prefixed = node.url === SITE_BASE || node.url.startsWith(SITE_BASE + '/');
        if (rootRelative && !prefixed) node.url = SITE_BASE + node.url;
      }
      if (Array.isArray(node.children)) node.children.forEach(visit);
    };
    visit(tree);
  };
}

export default defineConfig({
  site: 'https://gmbalaa14.github.io',
  base: SITE_BASE,
  trailingSlash: 'always',
  markdown: {
    remarkPlugins: [remarkBasePrefixInternalLinks],
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
      defaultColor: false,
    },
  },
});
