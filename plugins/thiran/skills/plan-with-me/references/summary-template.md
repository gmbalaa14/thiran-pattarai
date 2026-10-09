> **Document Template — everything below this line defines what to write in the output file.**

> **See also:** [Implementation Plan](./<slug>-plan.md) · [Flow Diagrams](./<slug>-flow-diagrams.md)

**Writing rules for every section below:**

* Precise and high-level — state the conclusion, not the reasoning trail that led to it.
* Stay within what Phase 1–2.6 exploration actually surfaced. Do not restate plan-doc detail (code, file paths, line numbers, test/verification commands) — link there instead of duplicating it.
* A few sentences or a short bullet list per section. If a section has nothing substantive to say, write one line saying so (e.g. `None identified`) rather than padding it.
* This document must stay short enough for an SA to read end-to-end in a few minutes — if a section is growing past that, cut it down to the decision-relevant points and move detail to `<slug>-plan.md`.

---

# Context

2–3 sentences an SA can read first to orient: what this change is, why it's happening now, and what's being asked of them (FYI vs. approval). Not a repeat of Findings — this is the one-paragraph version someone skims before deciding whether to read further.

---

# Findings

What exists today, and what's missing or broken that motivates this change. Plain language — no code, no file paths beyond naming the affected component or service.

---

# Proposed Changes

High-level description of what will change, by component. Describe outcomes, not implementation.

---

# Approach & Alternatives Considered

One short paragraph: why this approach, and what else was weighed and rejected. Enough for an SA to judge the direction without re-deriving it — not a repeat of the plan doc's detailed Design Decisions section.

---

# Impact

What this touches — systems, teams, data, user-facing behavior. Call out anything with downstream effects (other teams, other services, migrations, external integrations).

---

# Dependencies

What this change is blocked by, and what it blocks — other teams, other in-flight work, external systems/vendors, or sequencing constraints. State `None identified` if there are none.

---

# Risks & Mitigations

Technical, security, or operational risks worth an SA's attention, each with a one-line mitigation. Focus on risks that would change the SA's decision — not routine engineering concerns already handled in the plan doc. State `None identified beyond standard practice` if that's genuinely the case.

---

# Rollback / Contingency

One line: can this be safely reverted, and how, at a high level (no commands — that detail belongs in `<slug>-plan.md`).

---

# Benefits

Why this is worth doing.

---

# Verification Required

What needs to be confirmed before this is considered done, in business/operational terms (e.g. "confirm the reporting team doesn't rely on the old field name"). Not test-command syntax — that detail belongs in `<slug>-plan.md`.

---

# Decisions Requested

The specific things the SA is being asked to approve or weigh in on — a curated subset of the plan doc's `Validation Required` list, limited to items that need architectural or business judgment rather than an engineer-level assumption. State `None — informational only` if this doc is for awareness rather than approval.

---

# Timeline & Effort

One line combining the estimate with anything from Dependencies that affects it, e.g. `Medium (1–3 days), contingent on the platform team's API being available`.

* Small (<1 day)
* Medium (1–3 days)
* Large (3–5 days)
* Epic (>5 days)
