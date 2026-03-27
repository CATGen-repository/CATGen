# LLM Configuration and Local Deployment

## Overview

All large language models (LLMs) used in this study are open-source checkpoints deployed locally. CATGen does not rely on external APIs or third-party hosted inference services; all inference is executed in the local environment with vLLM.

This setup provides three practical benefits:

- Data privacy: proprietary or industrial code never leaves the local environment.
- Reproducibility: all experiments are based on publicly available checkpoints.
- Cost stability: there are no API charges, rate limits, or service-side fluctuations.

## Model Families

We evaluate three representative open-source model families: Llama, DeepSeek, and Qwen. Together, they cover several dimensions that are important for test-generation research:

- general-purpose versus code-specialized models
- smaller versus larger parameter scales
- standard instruction tuning versus reasoning-enhanced distillation

## Evaluated Models

### 1. Llama Family

#### Llama3.1-8B (Lla-8B)

- Type: general-purpose instruction-tuned model
- Role: small-to-medium general LLM baseline
- Purpose: evaluate how a mainstream general model performs on unit test generation

#### CodeLlama-7B (CL-7B)

- Type: code-specialized instruction-tuned model
- Role: code-focused Llama-family representative
- Purpose: compare code-specialized behavior against general Llama-family behavior

### 2. DeepSeek Family

#### DeepSeekCoder-6.7B-Instruct (DC-7B)

- Type: code-specialized instruction-tuned model
- Role: small-scale code model
- Purpose: measure the effectiveness of code-specialized models under limited parameter scale

#### DeepSeekCoder-33B-Instruct (DC-33B)

- Type: code-specialized instruction-tuned model
- Role: large-scale code model
- Purpose: evaluate the effect of larger parameter scale within the DeepSeekCoder line

#### DeepSeek-R1-Distill-Llama-8B (DRL-8B)

- Type: reasoning-enhanced distilled model
- Role: compact reasoning-oriented variant
- Purpose: study whether reasoning-enhanced distillation improves test generation and repair

#### DeepSeek-R1-Distill-Qwen-32B (DRQ-32B)

- Type: reasoning-enhanced distilled model
- Role: large reasoning-oriented variant
- Purpose: evaluate the effect of combining reasoning distillation with larger model capacity

### 3. Qwen Family

#### Qwen2.5-Coder-7B-Instruct (QC-7B)

- Type: code-specialized instruction-tuned model
- Role: compact Qwen code model
- Purpose: evaluate the performance of a smaller code-specialized Qwen variant

#### Qwen2.5-Coder-32B-Instruct (QC-32B)

- Type: code-specialized instruction-tuned model
- Role: primary large code-specialized Qwen model
- Purpose: serve as one of the strongest code-oriented open-source baselines in our evaluation

#### Qwen2.5-32B (Q-32B)

- Type: general-purpose instruction-tuned model
- Role: large general Qwen model
- Purpose: compare general-purpose and code-specialized behavior within the same model family

## Selection Rationale

The final model set was chosen to provide coverage along four axes:

1. General versus code-specialized models.
2. Small versus large parameter scales.
3. Standard instruction tuning versus reasoning-enhanced distillation.
4. Cross-family diversity across Llama, DeepSeek, and Qwen.

This diversity reduces the chance that the study's conclusions depend on a single architecture family or training style.

## Local Deployment Environment

All selected models are deployed locally with vLLM 0.8.4.

### Deployment Characteristics

- Inference framework: vLLM
- Deployment mode: fully local
- External APIs: none
- Remote hosted inference: none

### Hardware and Software

- GPU: 4 x NVIDIA A100-PCIE-40GB
- CPU: Intel Xeon Gold 6330
- CUDA: 12.2
- Python: 3.10.12
- vLLM: 0.8.4

## Inference Configuration

To ensure consistency and reproducibility, all models are evaluated under the same inference settings whenever possible:

- Temperature: 0
- Inference mode: deterministic generation
- Serving framework: vLLM

## Baseline Reconfiguration

Some baseline methods originally depend on commercial ChatGPT-style APIs for:

- unit test generation
- compilation repair
- iterative refinement

In our experiments, these API-based components are replaced with the locally deployed open-source models listed above. This keeps the comparison fairer across methods while preserving local privacy guarantees and avoiding dependence on proprietary hosted services.

## Summary

CATGen uses a fully local LLM deployment pipeline built on open-source checkpoints and vLLM. This configuration supports privacy-sensitive evaluation, improves reproducibility, and keeps model comparisons consistent across all experiments.
