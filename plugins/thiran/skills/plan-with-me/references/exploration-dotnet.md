# Exploration Agents — .NET / C#

Launch 2–3 **Explore** agents in parallel (subagent_type: `Explore`).

## Agent 1 — Impact Analysis

Identify:

* API entry points (Controllers, MinimalAPI endpoints)
* Services and their interfaces
* Domain models and entities (`Contracts/Entities/`)
* Persistence layer (repositories, ORM/DbContext or equivalent — identify the actual persistence technology in use, e.g. EF Core + SQLite, rather than assuming one)
* DI registrations (`Program.cs`, extension methods)
* Configuration keys (`appsettings.json`, `IOptions<T>` bindings)
* Authorization policies and permission keys

## Agent 2 — Pattern Discovery

Identify existing implementations that can be reused:

* Similar features or services already implemented
* Base classes and shared abstractions (e.g., `CloudServiceControllerBase`)
* Error handling patterns (`AppException`, `Codes.cs`, `GlobalExceptionHandler`)
* Logging patterns and structured log conventions — note when a "commonly used" pattern actually violates this repo's own logging rules (e.g. `.claude/rules/backend-logging.md`); flag it rather than proposing to copy it
* Validation patterns
* Migration mechanism actually in use (e.g. EF Core `Migrations/` folder + `dotnet ef migrations`, Flyway/Liquibase scripts, or none) — name the real one found, don't assume
* Background service patterns

## Agent 3 — Testing & Infrastructure

Identify:

* Unit and integration test projects and their structure
* Test fixtures and shared test helpers
* Migration test coverage
* CI/CD pipeline dependencies
* Infrastructure impacts (schema/index changes, encryption or connection-string handling if applicable, configuration changes) — precise to what's found in this repo
