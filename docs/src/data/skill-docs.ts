export interface SkillDoc {
  slug: string;
  plugin: string;
  title: string;
  stage: string;
  tagline: string;
  whenToUse: string[];
  howItWorks: string[];
  example: string;
  needs: string[];
  notes?: string[];
}


/** Hand-written extras for skills. Key: `<plugin>/<skill>`. Skills without an entry still get a page built from SKILL.md. */
export const skillDocs: SkillDoc[] = [
  {
    plugin: 'thiran',
    slug: 'plan-with-me',
    title: 'Plan With Me',
    stage: 'Plan',
    tagline:
      'Turn a feature idea into a reviewed plan, flow diagrams and a summary, before any code is written.',
    whenToUse: [
      'You are starting a feature and want a plan grounded in the real codebase.',
      'You want a plan folder you can hand to the team, or come back to and refine later.',
      'The stack is C#/.NET, Kotlin or Angular/TypeScript (other stacks work too).',
    ],
    howItWorks: [
      'Choose a fresh plan or refine an existing plan folder.',
      'Give a feature description, a base directory and a slug. Planning starts only when all three are provided.',
      'Claude enters plan mode, detects the tech stack and explores the codebase with stack-specific guidance.',
      'It summarises the current architecture and reusable patterns, then interviews you about integration tests.',
      'It writes <slug>-plan.md, <slug>-flow-diagrams.md and <slug>-summary.md, cross-referenced, into <base_dir>/<slug>/.',
      'A refinement loop and a validation gate on open assumptions come next. Plan mode is exited only after you explicitly choose to proceed.',
    ],
    example: '/thiran:plan-with-me add rate limiting to the public orders API',
    needs: ['Read access to the codebase being planned', 'OpusPlan mode is recommended'],
  },
  {
    plugin: 'thiran',
    slug: 'commit-msg',
    title: 'Commit Message',
    stage: 'Commit',
    tagline:
      'Conventional Commit messages and pull request titles and descriptions, written from your staged or modified changes.',
    whenToUse: [
      'You are about to commit and want a clean, standards-compliant message.',
      'Your working tree mixes several kinds of change and you want to know whether to split it.',
      'You are preparing a pull request and need a title plus a readable description.',
    ],
    howItWorks: [
      'Asks whether you want a commit message or a PR description.',
      'For a commit, counts staged, modified and untracked files, and asks which set to describe when there is a real choice. Retry is available if you restage.',
      'Sorts the files into code, docs, tests and generated companions such as lockfiles.',
      'Picks the commit type. Docs, tests and companions ride along with another type. Different primary types, such as feat and fix, get a proposed split.',
      'Writes a lowercase imperative subject, a body that explains the why, and a BREAKING CHANGE footer when needed.',
      'For a pull request, finds the real base branch, reads git log against it, and writes a title and short bullet summary.',
      'Removes machine-written tells such as em dashes and filler summaries before showing the text.',
    ],
    example: '/thiran:commit-msg commit message',
    needs: ['A git repository', 'git and bash (Git Bash on Windows)'],
    notes: [
      'The skill writes text only. It never runs git commit, git push or opens a pull request unless you ask.',
      'Untracked files are always left out. Run git add on one and choose Retry to include it.',
      'The file patterns for docs, tests and companions are in references/file-classification.md and can be edited.',
    ],
  },
  {
    plugin: 'thiran',
    slug: 'safe-rebase',
    title: 'Safe Rebase',
    stage: 'Rebase',
    tagline:
      'Rehearse a rebase on a disposable branch first, so conflicts show up before real history is touched.',
    whenToUse: [
      'Any rebase, rebase --onto, or "move this branch onto the updated base" request.',
      'The branch has an open pull request and you are nervous about force-pushing.',
      'You want a guaranteed way back if something goes wrong.',
    ],
    howItWorks: [
      'Trial: the rebase runs on a throwaway branch. Your real branch is untouched. A clean trial means the real rebase will be clean.',
      'Confirm: if the trial conflicts, Claude lists the conflicting files and lets you hold off or continue.',
      'Apply: the real rebase runs after the current tip is recorded as PRE_REBASE_TIP. Conflicts are resolved hunk by hunk.',
      'Push: if the branch tracks an upstream, Claude asks first and pushes only with --force-with-lease after your confirmation.',
    ],
    example: 'Rebase feature/orders onto the updated develop branch',
    needs: ['git', 'bash (Git Bash on Windows)'],
    notes: [
      'Mid-rebase, git rebase --abort fully restores the starting state.',
      'After a finished, unpushed rebase, the bundled undo command restores PRE_REBASE_TIP. This safety net ends once you push.',
    ],
  },
  {
    plugin: 'thiran',
    slug: 'pr-triage',
    title: 'PR Triage',
    stage: 'Review',
    tagline:
      'Pull CodeRabbit and reviewer comments from an Azure DevOps PR into one interactive HTML report.',
    whenToUse: [
      'A pull request has accumulated many review comments and you need to see them at a glance.',
      'You want severity and status breakdowns and a record of what has been dealt with.',
    ],
    howItWorks: [
      'Choose New Report or Refresh Existing.',
      'Give the Azure DevOps pull request URL. Comments from CodeRabbit and human reviewers are fetched.',
      'An interactive HTML report is generated with severity and status breakdowns and sortable columns.',
      'Refresh merges fresh comments into an earlier report, keeps statuses already set, and writes a new timestamped file instead of overwriting.',
      'Triage itself happens in /pr-judge, which can write its verdict back to the report by comment ID.',
    ],
    example: '/thiran:pr-triage',
    needs: [
      'Python 3.7 or newer',
      'An Azure DevOps personal access token (ADO_PAT environment variable, or ado_pat in ~/.claude/config.json or ./.claude/config.json)',
    ],
  },
  {
    plugin: 'thiran',
    slug: 'pr-judge',
    title: 'PR Judge',
    stage: 'Review',
    tagline:
      'Decide whether a CodeRabbit comment is right, then get a fix, a rebuttal, or both.',
    whenToUse: [
      'You have one review comment and want an honest verdict, not automatic agreement.',
      'You want a ready-to-post reply when the comment is a false positive.',
    ],
    howItWorks: [
      'Detects the language and loads the matching review criteria (.NET, Kotlin or Angular/TypeScript).',
      'Checks whether the comment conflicts with a documented architecture decision in your CLAUDE.md.',
      'Classifies the comment as valid, a false positive, or partially valid.',
      'Valid comments get a proposed fix shown as an annotated diff. False positives get a rebuttal reply. Partially valid ones get a corrected fix plus a rebuttal.',
      'Nothing is applied until you confirm. After a fix, the change is verified.',
      'Optionally syncs the verdict and status back to a pr-triage report by comment ID.',
    ],
    example: '/thiran:pr-judge Consider disposing the HttpClient after use…',
    needs: [
      'The code snippet the comment refers to',
      'Python 3 for the diff renderer',
      'Optional: a pr-triage report for status sync',
    ],
    notes: ['Paste from the pr-triage report’s Copy buttons and the comment ID and report path are picked up automatically.'],
  },
];

