> **Document Template — everything below this line defines what to write in the output file.**

> **See also:** [Flow Diagrams](./<slug>-flow-diagrams.md) · [Summary](./<slug>-summary.md) — the summary doc is a sibling file for a non-implementer audience; keep it cross-linked the same way.

---

# Context

3–5 concise sentences describing:

* Business need
* Technical motivation
* Intended outcome
* Scope of change

---

# Architecture Overview

Describe:

* Components involved
* Current flow
* Future flow
* Boundaries affected

Use diagrams when helpful.

---

# Design Decisions

For each major change explain:

## Decision

What is being changed.

## Reasoning

Why this approach was selected.

## Alternatives Considered

Other options explored.

## Rejected Because

Why alternatives were not selected.

---

# Dependency Impact

Identify:

### Packages / Dependencies

* Added
* Updated
* Removed

### Configuration

* config file changes (e.g. appsettings.json, application.yml, environment.ts)
* feature flags
* environment variables

### Infrastructure

* databases
* queues
* storage
* external services

---

# Changes

For every required file create a section:

## File Classification

Before listing changes classify discovered files:

### Required Change

Files that must be modified.

### Potential Change

Files that may require modification.

### Reference Only

Files used for guidance.

Only Required Change files receive dedicated sections.

---

## File 1:

Description of change.

Key snippets:

```
// Key signatures in the detected language
```

---

## File 2:

Description of change.

Key snippets:

```
// Key logic in the detected language
```

Repeat for every affected file.

Rules:

* Mark new files with `(NEW)`
* Use full paths
* Show critical logic only
* Avoid boilerplate
* Do not provide full implementations

---

# Testing Strategy

## Unit Tests

List:

* New tests
* Updated tests

## Integration Tests

### Layer 1 — Service/Data Layer

For each confirmed test case:

- **Test class**: `<ClassName>` in `<path found during Phase 2.6>` (`(NEW)` or existing)
- **Collection / Fixture**: the actual one this repo uses for this layer — found during Phase 2.6, never a placeholder or guessed name (e.g. state "no existing fixture — will need one added" if none exists)
- **Scenario**: what the test exercises
- **Assertions**: what it verifies
- **Seed data**: state required before the test runs, using the real persistence mechanism found for this repo

If not in scope: `Not required — <reason the user gave>.`

> **Cross-layer note**: If a flow also has a Layer 2 test, add after its entry: `Complements the Layer 2 test in <ClassName> — covers the service logic in isolation.`

### Layer 2 — HTTP/API Layer

For each confirmed test case:

- **Test class**: `<ClassName>` in `<path found during Phase 2.6>` (`(NEW)` or existing)
- **Collection / Fixture**: the actual one this repo uses for this layer — found during Phase 2.6, never a placeholder or guessed name
- **Scenario**: what the test exercises (endpoint, HTTP method, auth state)
- **Assertions**: HTTP status code, response body shape, side effects
- **Seed data**: users, roles, or records seeded via the real persistence mechanism found for this repo, before the test

If not in scope: `Not required — <reason the user gave>.`

> **Cross-layer note**: If a flow also has a Layer 1 test, add after its entry: `Complements the Layer 1 test in <ClassName> — covers the end-to-end HTTP pipeline for the same flow.`

## Edge Cases

List:

* Failure paths
* Boundary conditions
* Invalid inputs

---

# Risks

## Backward Compatibility Risks

Potential breaking changes.

## Performance Risks

Potential performance impacts.

## Deployment Risks

Operational concerns.

## Migration Risks

Data/configuration migration concerns.

## Rollback Strategy

How the feature can be safely reverted.

---

# Verification

Provide exact commands.

## Build Verification

```powershell
# e.g. dotnet build / ./gradlew build / npm run build
```

## Test Verification

```powershell
# e.g. dotnet test / ./gradlew test / npm test
```

## Functional Verification

Step-by-step commands.

```powershell
# Example commands
```

## Failure Path Verification

Commands proving error handling works.

```powershell
# Example commands
```

If the change has no real failure branch beyond a global/default handler (e.g. a trivial read-only endpoint), say so directly: `Not applicable — <reason>.` rather than fabricating a failure path.

## Logging Verification

Commands proving expected logs are emitted.

```powershell
# Example commands
```

---

# Estimated Scope

Provide one:

* Small (<1 day)
* Medium (1–3 days)
* Large (3–5 days)
* Epic (>5 days)

Include reasoning.

---

# Planning Confidence

## Confidence

* High
* Medium
* Low

## Assumptions

Explicit assumptions made.

## Validation Required

Items that must be confirmed during implementation.
