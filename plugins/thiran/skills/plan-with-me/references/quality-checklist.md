# Quality Checklist

Before presenting the plan verify:

* [ ] Architecture understood
* [ ] Every file discovered through exploration
* [ ] No hallucinated paths
* [ ] Required/Potential/Reference files classified
* [ ] Design decisions documented
* [ ] Risks documented
* [ ] Integration test scope confirmed with user (flows/use cases and layers explicitly specified)
* [ ] Testing strategy documented
* [ ] Dependency impact documented
* [ ] Verification commands executable
* [ ] Confidence level declared
* [ ] Scope estimated
* [ ] No implementation code produced
* [ ] Output folder is `<base_dir>/<slug>/`
* [ ] `<slug>-plan.md`, `<slug>-flow-diagrams.md`, and `<slug>-summary.md` all exist in the folder
* [ ] Plan doc opens with `See also` links to `<slug>-flow-diagrams.md` and `<slug>-summary.md`
* [ ] Flow diagrams doc opens with `See also` links to `<slug>-plan.md` and `<slug>-summary.md`
* [ ] Summary doc opens with `See also` links to `<slug>-plan.md` and `<slug>-flow-diagrams.md`, and contains no code or line numbers
* [ ] No unresolved items remain in `Validation Required` (Phase 4.5 cleared)
* [ ] `<slug>-plan.md` and `<slug>-summary.md` are in sync — no section was edited in one without the corresponding update in the other
* [ ] If refine mode was used, the existing docs were loaded and edited rather than regenerated from scratch
