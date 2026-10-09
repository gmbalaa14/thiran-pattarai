# Exploration Agents — Angular / TypeScript

Launch 2–3 **Explore** agents in parallel (subagent_type: `Explore`).

## Agent 1 — Impact Analysis

Identify:

* Entry points (routed components, lazy-loaded modules, standalone routes)
* Services and their injection scope (`providedIn: 'root'` vs feature-level)
* State management (NgRx store slices, signals, or BehaviorSubjects)
* HTTP interceptors and API service patterns
* Route guards and resolvers
* TypeScript interfaces and models
* Angular module or standalone component imports affected

## Agent 2 — Pattern Discovery

Identify existing implementations that can be reused:

* Similar features or flows already built
* Component communication patterns (Input/Output, signals, services)
* Error handling patterns (global error handler, HTTP error interceptor)
* Reactive patterns (async pipe, `takeUntilDestroyed`, effect())
* Form patterns (Reactive Forms vs Template-driven)
* Shared UI components and design system primitives

## Agent 3 — Testing & Infrastructure

Identify:

* Unit and component test files (`.spec.ts`) and their structure
* TestBed configuration patterns and shared test utilities
* E2E test coverage (Playwright, Cypress)
* CI/CD pipeline dependencies (build steps, lint, type-check)
* Infrastructure impacts (environment configs, API base URL changes, lazy chunk boundaries)
