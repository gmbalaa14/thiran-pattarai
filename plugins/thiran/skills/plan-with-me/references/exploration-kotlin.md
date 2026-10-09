# Exploration Agents — Kotlin

Launch 2–3 **Explore** agents in parallel (subagent_type: `Explore`).

## Agent 1 — Impact Analysis

Identify:

* Entry points (Activities, Fragments, Composables, NavGraph destinations)
* ViewModels and their state holders
* Repositories and data sources (local Room, remote Retrofit)
* Domain models and data classes
* Hilt modules and DI bindings
* Room entities, DAOs, and database version
* API interfaces and DTOs

## Agent 2 — Pattern Discovery

Identify existing implementations that can be reused:

* Similar features already implemented
* Coroutine scope and dispatcher patterns (`viewModelScope`, `Dispatchers.IO`)
* Flow / StateFlow / SharedFlow usage patterns
* Error handling and result-wrapping patterns (`Result<T>`, sealed classes)
* Repository patterns and caching strategies
* Extension functions and utility helpers

## Agent 3 — Testing & Infrastructure

Identify:

* Unit test structure (`src/test/`) and instrumented test structure (`src/androidTest/`)
* ViewModel test patterns (Turbine, `runTest`)
* Mock and fake conventions (MockK, Fakes)
* CI/CD dependencies (Gradle tasks, build variants)
* Infrastructure impacts (Room migrations, API versioning)
