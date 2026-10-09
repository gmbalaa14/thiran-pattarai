# .NET / C# Evaluation Criteria

## Language Version Awareness
Infer the C# version from the existing code style before recommending features:
- Primary constructors, collection expressions → C# 12+
- Required members, file-scoped types → C# 11+
- Records, pattern matching enhancements, global using → C# 10+
- Range/index operators, switch expressions → C# 8+

Do not suggest features from a version higher than what the code already demonstrates.

## Evaluation Standards

### Performance
- Proper use of `ReadOnlySpan<T>` and `Memory<T>` for buffer manipulation
- Minimizing heap allocations (avoid boxing, prefer struct where appropriate)
- Efficient LINQ queries (avoid multiple enumeration, prefer `Any()` over `Count() > 0`)
- Avoid `async void` except for event handlers

### Resource Management
- Correct implementation of `IDisposable` / `IAsyncDisposable`: use `IDisposable` for synchronous cleanup, `IAsyncDisposable` for async cleanup operations
- Prefer `using` declarations over `using` statements for simple cases
- Object lifetime and cleanup responsibility are separate from the async-cleanup decision: an object spanning multiple methods should follow the ownership model where the consumer is responsible for disposal, but implements `IDisposable` or `IAsyncDisposable` based on cleanup needs, not method boundaries

### Idiomatic C#
- Modern language features: pattern matching, primary constructors, records, switch expressions
- Null handling: null-coalescing (`??`), null-conditional (`?.`), not-null checks (`is not null`)
- Prefer `var` when the type is obvious from the right-hand side

### Naming Conventions
- PascalCase for methods, properties, classes, and interfaces
- camelCase for local variables and parameters
- `_camelCase` for private fields
- `Async` suffix for all asynchronous methods

## Test vs Production Code Detection
Code is test code if any of the following apply:
- File path contains `Tests/`, `Test/`, `.Tests.`, or `.Specs.`
- Contains `[Fact]`, `[Theory]`, `[Test]`, or `[TestMethod]` attributes
- References `Moq`, `NSubstitute`, `FluentAssertions`, `xunit`, `NUnit`, or `MSTest`

For test code: apply the same correctness standards, but note that test-only helpers may prefer simpler solutions (e.g., a plain `lock`) over production-grade ones (e.g., `ConcurrentDictionary`).

## Build & Test Commands

**Build:**
```
dotnet build
```

**Test — changed-scoped** (substitute `{ClassName}` with the actual class name from the fix):
```
dotnet test --filter "FullyQualifiedName~{ClassName}"
```

**Test — full suite:**
```
dotnet test
```
