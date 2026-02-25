# [Component / Subsystem] — Deep Dive

> *Detailed architecture notes for a specific component or cross-cutting concern.*

## Scope

*What aspect of the system does this document cover?*

## Background

*Context needed to understand the design — why it exists, history of decisions, etc.*

## Design

### Approach

*Explain the chosen design and why alternatives were rejected.*

### Key Abstractions

| Abstraction | Responsibility |
|-------------|---------------|
| [Class / module / service] | [What it owns] |
| [Class / module / service] | [What it owns] |

### Sequence / Interaction Diagram

```
[Caller]          [Component A]         [Component B]
    │                   │                     │
    │── request ────────►                     │
    │                   │── sub-call ─────────►
    │                   │◄── response ─────────
    │◄── result ─────────                     │
```

## Trade-offs & Constraints

- **[Trade-off]**: [Why this was accepted]

## Future Work

- [ ] [Known limitation or planned improvement]

---
*Parent: `Architecture.md`*
