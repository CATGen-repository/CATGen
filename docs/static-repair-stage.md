# Static Repair Stage

## Overview

The static repair stage in CATGen applies eight deterministic repair strategies to generated tests. These strategies correspond to the repair design described in the paper and are derived from recurring failure patterns observed in LLM-generated test code.

The purpose of this stage is to improve:

- compilability
- framework consistency
- structural correctness

All repairs are guided by project-aware static analysis, which provides contextual information such as valid types, method signatures, dependency structures, and framework configuration.

## Relationship to Static Analysis

The repair rules are driven by static analysis results, including:

- valid class and method definitions
- dependency relationships
- framework usage signals

This keeps the repair stage context-aware and deterministic instead of relying on additional LLM calls.

## Key Characteristics

- Deterministic: no additional LLM interaction is required.
- Pattern-driven: the rules target real failure cases seen in generated tests.
- Context-aware: repairs are grounded in the actual project structure.

## Repair Strategies

### 1. Package Declaration Completion

#### Problem

- missing package declarations
- incorrect package paths

#### Repair

Align the generated test package with the focal class source location.

#### Example

**Before**

```java
class FixMethodTest {
```

**After**

```java
package org.utbot.postprocess;

class FixMethodTest {
```

### 2. Import Statement Supplementation

#### Problem

- missing required imports
- incorrect or incomplete import statements

#### Repair

- detect unresolved types through static analysis
- resolve their fully qualified names
- insert or correct import statements

#### Example

**Before**

```java
User user = new User("alice");
assertEquals("alice", user.getName());
```

**After**

```java
import com.example.domain.User;
import static org.junit.jupiter.api.Assertions.assertEquals;

User user = new User("alice");
assertEquals("alice", user.getName());
```

### 3. Class Annotation Rectification

#### Problem

Generated tests may omit or misuse framework annotations.

#### Repair

- normalize test framework annotations such as JUnit configuration
- normalize mocking framework configuration such as Mockito extensions

#### Example

**Before**

```java
class PaymentServiceTest {

    @Mock
    private PaymentGateway gateway;
}
```

**After**

```java
@ExtendWith(MockitoExtension.class)
class PaymentServiceTest {

    @Mock
    private PaymentGateway gateway;
}
```

### 4. Invalid Reference Resolution

#### Problem

- references to non-existent classes
- undefined variables
- invalid method calls

#### Repair

- remove invalid references
- replace them with valid alternatives when resolution is possible
- eliminate statements involving undefined symbols

#### Example

**Before**

```java
@Mock
private Auto auto; // non-existent class

map = new HashMap<>(); // undefined variable
```

**After**

```java
@Mock
private AutoService autoService;
```

### 5. Private Member Access Adaptation

#### Problem

Generated tests may access private members directly.

#### Repair

Introduce reflection-based access when direct access is invalid.

#### Example

**Before**

```java
service.internalState = null;
```

**After**

```java
Field field = UserService.class.getDeclaredField("internalState");
field.setAccessible(true);
field.set(service, null);
```

### 6. Method Signature Alignment

#### Problem

- incorrect method names
- wrong parameter types
- mismatched return-value expectations

#### Repair

- align method calls with actual signatures
- correct parameter types and values

#### Example

**Before**

```java
dao.setFlag("true"); // string instead of boolean
dao.setRes(1);       // int instead of string
```

**After**

```java
dao.setFlag(true);
dao.setRes("1");
```

### 7. Exception Specification Enhancement

#### Problem

- missing exception declarations or assertions
- exceptions are not handled in a framework-consistent way

#### Repair

- add explicit exception assertions or declarations when required
- normalize exception handling patterns

#### Example

**Before**

```java
@Test
void testProcess() {
    service.process(null);
}
```

**After**

```java
@Test
void testProcess() {
    assertThrows(IllegalArgumentException.class, () -> service.process(null));
}
```

### 8. Fallback Assertion Mechanism

#### Problem

- missing assertions
- tests execute code but do not validate behavior

#### Repair

Insert default assertions so that generated tests retain at least minimal validation value.

#### Example

**Before**

```java
@Test
void shouldCreateUser() {
    User user = service.createUser("alice");
}
```

**After**

```java
@Test
void shouldCreateUser() {
    User user = service.createUser("alice");
    assertNotNull(user);
}
```

## Workflow Position

The static repair stage runs after initial test generation and before final compilation or execution. In practice, it acts as a rule-based correction layer between LLM output and downstream validation.

Its responsibilities are to:

- resolve deterministic structural defects
- align generated code with project conventions
- reduce avoidable compile-time failures before execution

## Summary

The static repair stage gives CATGen a deterministic post-processing layer for fixing common structural and framework-related failures in generated tests. By pairing repair rules with project-aware static analysis, CATGen improves the usability and compilability of LLM-generated tests without depending on additional model calls.
