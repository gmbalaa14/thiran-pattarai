# Kotlin Evaluation Criteria

## Framework Awareness
Infer the framework from the code before evaluating:
- `@Composable`, `remember`, `LaunchedEffect` → Jetpack Compose
- `Flow`, `suspend`, `coroutineScope` → Kotlin Coroutines
- `ViewModel`, `LiveData` → Android Architecture Components
- `@RestController`, `@Service`, `@Repository` → Spring Boot

## Evaluation Standards

### Null Safety
- Avoid non-null assertions (`!!`) — prefer safe calls (`?.`), Elvis operator (`?:`), or `requireNotNull()`
- Use nullable types explicitly (`String?`) rather than relying on platform types
- Prefer `let`, `also`, `run` for null-safe chains over repeated null checks

### Coroutines & Async
- Use `suspend` functions instead of callbacks or `Future`
- Prefer `Flow` over `LiveData` for new code
- Structured concurrency: always use a proper scope (`viewModelScope`, `lifecycleScope`) — never `GlobalScope`
- Avoid `runBlocking` outside of tests

### Idiomatic Kotlin
- Prefer `data class` for value holders
- Use `sealed class` / `sealed interface` for exhaustive `when` expressions
- Use scope functions appropriately: `let` (nullable transform), `apply` (object init), `run` (grouped operations), `also` (side effects)
- Prefer extension functions over utility classes

### Naming Conventions
- camelCase for functions, properties, and local variables
- PascalCase for classes, interfaces, and objects
- SCREAMING_SNAKE_CASE for constants (`const val`)
- Backing properties prefixed with `_` (e.g., `_uiState` backed by public `uiState`)

## Test vs Production Code Detection
Code is test code if any of the following apply:
- File path contains `test/`, `androidTest/`, or filename ends in `Test.kt` or `Spec.kt`
- Contains `@Test`, `@DisplayName`, `@BeforeEach`, or `@AfterEach` (JUnit)
- Imports from `io.mockk`, `org.mockito`, or `kotlin.test`

For test code: apply the same correctness standards, but `runBlocking` in test functions and verbose mock setup are acceptable.

## Build & Test Commands

**Build:**
```
./gradlew build
```

**Test — changed-scoped** (substitute `{ClassName}` with the actual class name from the fix):
```
./gradlew test --tests "*.{ClassName}"
```

**Test — full suite:**
```
./gradlew test
```
