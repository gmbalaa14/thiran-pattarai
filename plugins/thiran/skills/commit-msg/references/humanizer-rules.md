# Humanizer rules for commit and PR text

Apply these to every draft before showing it. The goal is text a developer would plausibly have typed, not text that reads as machine-generated. Read the draft once against each section and fix what you find.

## Punctuation tells
- No em dashes (—) and no en dashes used as dashes. Use a period, comma, colon or parentheses instead.
- No semicolon chains joining three or more clauses.
- No emoji and no decorative symbols (arrows, checkmarks, sparkles) in commit messages. A PR description may use none either, unless the team's existing PRs do.
- No curly quotes. Use plain ASCII quotes.

## Buzzwords to cut
Replace with the concrete thing that happened, or delete.
- robust, seamless, comprehensive, holistic, streamlined, powerful, elegant, cutting-edge
- enhance, leverage, utilize (say "use"), facilitate, empower, unlock, elevate, optimize (unless a measured optimisation)
- ensure, ensuring (say what is checked), significantly, various, several improvements, minor tweaks, updates and fixes
- "improve performance" with no number or mechanism: name the query, loop or allocation that changed

## Structural tells
- No "This commit..." or "This PR..." opener. Start the body with the reason or the effect.
- No triplets by reflex ("faster, cleaner, and more maintainable"). Say the one true thing.
- No "not only X but also Y" or "X, not Y" contrast framing.
- No rhetorical questions and no scene-setting openers ("In today's...", "When it comes to...").
- No bulleted list for a change that has one point. Bullets are for genuinely separate items.
- No bold labels on every bullet ("**Performance:** ..."), and no headings in a commit body.
- No filler transitions: Additionally, Furthermore, Moreover, Overall, In summary.

## Compulsive summaries
- Never end with a recap sentence that restates the subject ("Overall, these changes improve...").
- Never add a closing line offering more help or inviting questions.
- Do not explain what the diff plainly shows. Explain why it was needed and what behaviour changes.

## Accuracy tells
- Do not claim tests pass, performance improved, or a bug is "fully resolved" unless the diff or the user says so.
- Do not invent issue numbers, ticket IDs, metrics or version numbers.
- Do not describe files or methods that are not in the diff.

## Voice
- Plain and specific, written as the author. Prefer "Retry the token refresh once on 401" over "Implement enhanced token refresh resilience".
- Short sentences. Past or present tense used consistently within the body. Subject line stays imperative.
- Match the repo's existing tone from `git log`; a terse history should get terse messages.

## Final check
Search the draft for `—`, `–`, "seamless", "robust", "comprehensive", "ensure", "leverage", "Additionally", "Overall". Any hit gets rewritten.
