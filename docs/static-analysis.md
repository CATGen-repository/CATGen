# Static Analysis

## Overview

The static analysis component in CATGen extracts structured project context before test generation. Its goal is to make project-specific information explicit so that later stages do not need to rely on the language model to infer missing dependencies, framework conventions, or program structure.

This analysis supports three practical objectives:

- provide stable contextual input for test generation
- support deterministic construction of the test skeleton
- enable rule-based post-processing and repair

Rather than performing heavyweight whole-program reasoning, CATGen uses a lightweight, context-oriented analysis focused on the code elements that matter most for unit test synthesis.

## Analysis Scope

Given a focal method, the analysis collects context from four sources.

### 1. Focal-Method Context

The analysis extracts the focal method's signature, parameters, return type, modifiers, and body-level structural information. This forms the direct target description for downstream generation.

### 2. Source-Class Context

The analysis gathers the surrounding class information needed to understand how the focal method is embedded in its local environment, including:

- field declarations
- constructor information
- related methods in the same class
- class-level imports and declarations

This context supports object initialization, state setup, and reasoning about whether dependencies come from fields, constructors, or helper methods.

### 3. Dependency Context

The analysis identifies directly relevant dependencies connected to the focal method, such as invoked methods, referenced classes, static callees, private callees, and return-type-related structures. The goal is not to reconstruct the entire project dependency graph, but to retain the dependency information most likely to affect test generation, mocking, and compilability.

### 4. Test and Framework Context

The analysis also extracts the project's testing environment, including existing test-class information, test-related imports, and framework-level signals. These signals are later used to align generated tests with project conventions instead of synthesizing framework scaffolding from scratch.

## Design Characteristics

The static analysis stage has four main characteristics.

### 1. Lightweight

The analysis focuses on structural extraction rather than expensive semantic reasoning. It does not attempt whole-program verification or exhaustive behavioral modeling; instead, it captures the subset of information that is most useful for reliable test generation in practice.

### 2. Modular

The pipeline is decomposed into focused processing stages, each responsible for a particular category of context, such as naming information, field information, callee relationships, branch structures, or test-class context. This makes the pipeline easier to extend and maintain.

### 3. Deterministic

Whenever possible, contextual information is extracted directly from the project structure rather than inferred by the model. This is especially important for package names, imports, framework signals, method metadata, and dependency-related context.

### 4. Context-Oriented

The analysis is optimized for downstream usefulness rather than completeness. The objective is not to summarize all program properties, but to surface the information that most directly influences compilability, scaffold correctness, mocking setup, and branch coverage.

## Extracted Information

The analysis outputs a structured context representation that includes the following categories.

### 1. Naming and Declaration Information

This includes package names, source-class names, source-method names, and other declaration-level information required to place generated tests in the correct structural location.

### 2. Method Interface Information

This includes parameter lists, return types, visibility, and other method-level metadata needed to construct valid invocations and assertions.

### 3. Class Structure Information

This includes source-class fields, constructors, and related class-level structures that influence test setup and object construction.

### 4. Invocation and Dependency Information

This includes direct callees and specialized subsets of callees, such as static or private calls. It is used to identify helper logic, potential mocking targets, and dependencies that cannot be left implicit.

### 5. Branch-Related Information

This includes structural information about decision points and control-flow constructs in the focal method. It is later used to guide test generation and identify conditions that may require additional test cases.

### 6. Test-Environment Information

This includes test-class context, test-related fields, and import-level information from the testing environment. It helps CATGen align generated tests with existing project conventions.

## Role in the CATGen Pipeline

The static analysis stage provides the structured foundation for several later stages.

### 1. Prompt Construction

The extracted context is used to build structured inputs for the language model. This reduces reliance on implicit reasoning and improves the consistency of generated tests.

### 2. Skeleton Construction

Framework-aware scaffolding requires accurate information about packages, fields, constructors, and test conventions. Static analysis supplies these inputs deterministically.

### 3. Import Construction

Import-related information derived from source structure and dependency context is used to construct or supplement imports without relying solely on model inference.

### 4. Static Repair

The repair stage uses statically extracted context to correct mismatches between generated code and the actual project structure, such as invalid references, missing context, or structural misalignment.

### 5. Coverage Enhancement

Branch-related context is used to detect important but uncovered conditions and to support the synthesis of additional tests for those cases.

## Why It Is Called Lightweight Static Analysis

In the paper, this component is described as lightweight static analysis because it deliberately avoids heavyweight analysis objectives and instead focuses on practical context extraction for test generation. More specifically:

- it is centered on the focal method and its immediately relevant context
- it emphasizes structural extraction over exhaustive semantic reasoning
- it is designed for scalability and engineering robustness in large codebases

## Limitations

The static analysis component has several limitations.

- It is primarily structural and does not fully capture runtime behavior.
- Its dependency view is selective rather than exhaustive, so some deeper behavioral relationships may remain implicit.
- Language- and framework-specific runtime semantics may only be partially visible through static structure.

These limitations are acceptable for CATGen because the analysis is intended to provide reliable engineering context, not full behavioral verification.

## Summary

The static analysis component gives CATGen a deterministic and structured representation of the focal method's relevant project context. By making dependencies, class structure, branch-related cues, and testing conventions explicit before generation, it improves the stability, compilability, and practical reliability of generated unit tests.
