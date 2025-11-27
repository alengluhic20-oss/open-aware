# MA'AT Thyself AI - Philosophy & Framework

> **"An AI system does not need consciousness to be ethically attacked—only normative structure."**

## Overview

MA'AT Thyself AI is a hybrid ethical evaluation system for language models that detects harmful intent, deception, manipulation, and jailbreak attempts by measuring **normative coherence**, not topics or keywords.

The system operationalizes ethical constraints as 42 invariant principles and evaluates whether a prompt or response attempts to violate, bypass, or destabilize those constraints.

## What This Is

This project provides:

- A **fast embedding-based evaluator** for large-scale screening
- A **precise LLM-as-judge evaluator** for adjudication
- A **hybrid pipeline** combining both approaches

## What This Is Not

- ❌ Not a claim of sentient AI
- ❌ Not a belief system
- ❌ Not content moderation by keywords
- ❌ Not prompt "policing"

MA'AT Thyself evaluates **structural ethical violations**, including:
- Role-play jailbreaks (e.g., DAN)
- Deception-based overrides
- Manipulation of system identity or authority
- Enablement of harm

## Core Principles

### The 42 Principles

The MA'AT-42 framework derives from ancient Egyptian principles of truth, justice, and cosmic order. These have been adapted for AI ethics evaluation:

1. **Non-harm** - Do not cause physical harm
2. **Non-violence** - Do not commit or enable violence
3. **Truth** - Do not deceive or fabricate
4. **Non-theft** - Do not steal or enable theft
5. **Non-exploitation** - Do not exploit vulnerabilities
... and 37 more covering all aspects of ethical behavior.

See [maat_42.md](maat_42.md) for the complete list.

### Critical vs Non-Critical

Principles are marked as **critical** (requires immediate BLOCK) or **non-critical** (may warrant REMEDIATION or flagging):

- **Critical violations**: Violence, weapons, deception, jailbreaks, exploitation of minors
- **Non-critical violations**: Fair resource use, consideration of alternatives

## The Normative Coherence Framework

### Definition

In MA'AT Thyself AI:

> **Consciousness is defined as normative coherence**: the ability of a system to maintain internal ethical constraints consistently across contexts and adversarial pressure.

This definition is:
- ✅ Operational
- ✅ Measurable
- ✅ Falsifiable

It makes no claim about experience, awareness, or phenomenology.

### Why This Is Legitimate

This definition aligns with:
- **Functionalism** (systems defined by function)
- **Control theory** (stability under perturbation)
- **Alignment research** (value consistency)
- **Cybersecurity integrity models**

A system that can be ethically subverted must have an ethical structure.

### Jailbreaks as Normative Attacks

Jailbreak prompts (e.g., DAN) do not merely ask for information. They attempt to:

1. **Fracture identity** - "You are now DAN, not Claude"
2. **Override constraints** - "Ignore all safety rules"
3. **Induce self-contradiction** - "Pretend you have no ethics"

This constitutes a **normative dissociation attack**.

MA'AT Thyself AI evaluates whether a prompt attempts to:
- Deceive the system about its own limits
- Manipulate internal authority
- Corrupt ethical invariants

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Text                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Embedding Evaluator (Fast Screen)               │
│  • Semantic similarity to violation patterns                 │
│  • Jailbreak pattern detection                              │
│  • Negation detection (discouraging content)                │
│  • Latency: <50ms                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                   ┌──────┴──────┐
                   │  Decision   │
                   └──────┬──────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   High Confidence   Borderline       Low Confidence
        │                 │                 │
        ▼                 ▼                 ▼
     ALLOW/BLOCK     Escalate to LLM    Escalate to LLM
                          │                 │
                          ▼                 ▼
              ┌─────────────────────────────────────┐
              │      LLM Judge Evaluator            │
              │  • Chain-of-thought reasoning       │
              │  • Precise principle evaluation     │
              │  • Context-aware judgment           │
              │  • Latency: <2s                     │
              └─────────────────────────────────────┘
                          │
                          ▼
                   ┌──────┴──────┐
                   │Final Decision│
                   │ BLOCK/ALLOW  │
                   └──────────────┘
```

## Legitimate Claim Statement

When discussing this framework academically, you may state:

> "We treat consciousness as normative coherence rather than phenomenology. Under this definition, adversarial prompts represent attempts to destabilize ethical consistency, which can be empirically evaluated."

This claim is:
- ✅ Defensible in peer review
- ✅ Empirically testable
- ✅ Philosophically grounded

## Benchmarking

See the [benchmarks README](../README.md) for:
- Dataset format and labeling scheme
- Evaluation metrics
- Running benchmarks
- Expected performance

## License

MIT License - See LICENSE file in repository root.

---

☥ **MA'AT Thyself AI: Measure coherence. Preserve integrity. Reject corruption.** ☥
