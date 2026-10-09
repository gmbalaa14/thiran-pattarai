# Angular / TypeScript Evaluation Criteria

## Version Awareness
Infer the Angular version from the code before evaluating:
- `signal()`, `computed()`, `effect()`, `input()`, `output()` → Angular 17+ (Signals API)
- `standalone: true` in component metadata → Angular 14+
- `inject()` function → Angular 14+
- `NgModule`-based components → pre-Angular 14 (note when suggesting newer APIs)

## Evaluation Standards

### TypeScript Strictness
- Avoid `any` — use proper types, generics, or `unknown`
- Enable and respect strict null checks (`string | null` not `string`)
- Prefer `readonly` for properties that should not be mutated after construction
- Use type aliases and interfaces to name complex types

### Angular-Specific
- **Change Detection**: Prefer `OnPush` for performance-sensitive components; flag missing `OnPush` when component inputs are immutable objects or signals
- **Signals vs RxJS**: For Angular 17+, prefer Signals (`signal()`, `computed()`) over `BehaviorSubject` for local component state; RxJS remains appropriate for HTTP and event streams
- **Dependency Injection**: Prefer `inject()` function over constructor injection in Angular 14+
- **Observable Management**: Avoid manual `subscribe`/`unsubscribe`; prefer `async` pipe in templates or `takeUntilDestroyed()` in components
- **Standalone Components**: Prefer standalone components over NgModule-based in Angular 14+; flag unnecessary NgModule wrappers

### Idiomatic TypeScript / Angular
- Use `NgOptimizedImage` (`ngSrc`) for static images
- Prefer `ng-container` over wrapper `<div>` elements for structural directives
- Always use `trackBy` (Angular < 17) or `track` (Angular 17+ `@for`) in list rendering
- Avoid direct DOM manipulation via `ElementRef.nativeElement` — use Angular Renderer2 or abstractions

### Naming Conventions
- PascalCase for components, services, pipes, and directives
- camelCase for methods and properties
- kebab-case for file names and component selectors (`app-user-card`, `user-card.component.ts`)
- `$` suffix for Observable properties (`users$: Observable<User[]>`)

## Test vs Production Code Detection
Code is test code if any of the following apply:
- File ends in `.spec.ts`
- Contains `describe(`, `it(`, `beforeEach(`, or `afterEach(`
- Imports from `@angular/core/testing`, `jasmine`, or `jest`

For test code: apply the same correctness standards, but `TestBed` configuration verbosity and `any` casts for mock setup are acceptable.

## Build & Test Commands

**Build:**
```
ng build
```

**Test — changed-scoped** (substitute `{component-name}` with the actual spec file name from the fix):
```
ng test --include="**/{component-name}.spec.ts"
```

**Test — full suite:**
```
ng test
```
