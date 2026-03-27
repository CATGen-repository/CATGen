# Test Skeleton Construction

## Overview

The test skeleton construction stage in CATGen provides a deterministic and framework-consistent structural foundation for LLM-based test generation. Instead of asking the LLM to synthesize an entire test class from scratch, CATGen constructs the reusable scaffolding of the test class from project context, framework configuration, and static analysis results, and then lets the model focus on completing the test logic.

This design addresses a recurring failure mode in practice: generated test logic may look plausible, but the test class still fails to compile because of missing annotations, incorrect imports, invalid initialization, or inconsistent framework usage.

## Design Principles

The skeleton construction stage follows three principles:

- Deterministic: structural elements are constructed without relying on LLM inference.
- Framework-aware: the skeleton is aligned with the testing and mocking frameworks detected from the project.
- Minimal but sufficient: CATGen provides the scaffolding needed for compilation and execution while leaving test-specific logic, values, and assertions to the LLM.

## Skeleton Components

The generated skeleton contains the following elements.

### 1. Package Declaration

The test class is placed in a package consistent with the focal class. This keeps the generated test aligned with the project structure and avoids package-related compilation issues.

**Example**

```java
package com.example.service;
```

### 2. Import Statements

Import statements are constructed deterministically using three complementary sources instead of being inferred entirely by the LLM.

#### 2.1 Framework Imports

Imports required by the detected testing and mocking frameworks are added unconditionally based on project configuration.

**Example (JUnit 5 + Mockito)**

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
```

These imports are fully deterministic and independent of model output.

#### 2.2 Common Testing Utilities

Frequently used testing utilities and assertions are included as a predefined set to support typical test behaviors.

**Example**

```java
import static org.junit.jupiter.api.Assertions.*;
```

This ensures that common assertions such as `assertEquals`, `assertNotNull`, and `assertThrows` are always available.

#### 2.3 Dependency-Based Imports

Imports related to the focal method and its dependencies are constructed from static analysis and project context. This includes:

- types appearing in the focal method signature
- types referenced in focal-class fields and constructors
- types required by detected dependencies, including collaborators that need to be mocked or initialized

The resolution process is:

```text
1. Extract type references from the focal method and focal class.
2. Map simple type names to fully qualified names using project context and classpath information.
3. Filter to project-local and dependency-relevant types.
4. Generate the corresponding import statements.
```

**Example**

```java
import com.example.domain.User;
import com.example.repository.UserRepository;
```

### 3. Class Declaration

The test class name is derived deterministically from the focal class name, typically by appending the suffix `Test`.

**Example**

```java
class UserServiceTest {
```

### 4. Framework Initialization

CATGen detects the testing and mocking frameworks used in the project and constructs the corresponding class-level configuration, including required extensions, runners, or other setup annotations.

**Example (JUnit 5 + Mockito)**

```java
@ExtendWith(MockitoExtension.class)
```

### 5. Dependency Fields and Mock Injection

Dependencies of the focal class are identified through static analysis of fields, constructors, and related context. CATGen then inserts the fields needed to initialize the focal object consistently with the project setup.

In common Mockito-based settings:

- external collaborators are declared as `@Mock`
- the focal object is declared as `@InjectMocks`

**Example**

```java
@Mock
private UserRepository userRepository;

@InjectMocks
private UserService userService;
```

### 6. Test Method Templates

The skeleton also provides placeholder test methods with a consistent structure. These templates anchor generation and reduce structural drift.

**Example**

```java
@Test
void shouldReturnUser() {
    // Given

    // When

    // Then
}
```

## Construction Workflow

The overall process is:

```text
Input: focal method + focal class context + project configuration

1. Detect testing and mocking frameworks from project configuration.
2. Extract focal-class dependencies from fields, constructors, and method context.
3. Generate the package declaration.
4. Construct imports from framework imports, common testing utilities, and dependency-based imports.
5. Build the test class declaration.
6. Insert framework configuration annotations.
7. Add dependency fields and focal-object initialization fields.
8. Create test method templates for LLM completion.

Output: deterministic test skeleton
```

## Example Comparison

### Without a Deterministic Skeleton

```java
@Test
void testUser() {
    UserService service = new UserService();
    User user = service.getUser("alice");
    assertEquals("alice", user.getName());
}
```

Typical issues in this setting include:

- missing or incorrect imports
- missing framework initialization
- incorrect object construction
- omitted mock injection

### With a CATGen Skeleton

```java
package com.example.service;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void shouldReturnUser() {
        // Given

        // When
        User user = userService.getUser("alice");

        // Then
        assertEquals("alice", user.getName());
    }
}
```

In this version, CATGen has already provided the package declaration, deterministic imports, framework configuration, and dependency fields, allowing the LLM to focus on test behavior rather than structural scaffolding.

## Interaction with the LLM

The skeleton acts as a grounding structure for generation:

- CATGen constructs the reusable structural part of the test class deterministically.
- The LLM completes the open parts of the skeleton, including setup details, input values, mock behavior, and assertions.

This division of responsibility reduces structural errors while still allowing the model to generate diverse test logic.

## Scope and Limitations

The skeleton construction stage improves structural validity and framework consistency, but it does not by itself guarantee semantic correctness or fault-detection ability. In addition, while the framework-to-template mapping is extensible, supporting a new or highly customized testing framework may require additional template rules.

## Summary

The test skeleton construction stage ensures that generated tests start from a project-consistent, framework-correct, and dependency-aware structure. By separating structural scaffolding from LLM-driven test logic generation, CATGen improves the reliability and compilability of generated tests, especially in projects with non-trivial framework and dependency requirements.
