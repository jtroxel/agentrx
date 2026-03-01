# System Architecture

## Overview

> *Describe the high-level shape of the system — what it is and how it fits together.*

## Component Diagram

```
┌─────────────────────────────────────────────┐
│                                             │
│   [Top-level component / entry point]       │
│                                             │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
┌───────▼──────┐  ...  ┌──────▼──────┐
│ [Component A]│       │ [Component B]│
└──────────────┘       └─────────────┘
```

## Core Components

### 1. [Component Name]
- **Responsibility**: *What it owns*
- **Key Functions**:
  - [Function / behaviour]
  - [Function / behaviour]
- **Dependencies**: [list]

### 2. [Component Name]
- **Responsibility**: *What it owns*
- **Key Functions**:
  - [Function / behaviour]

## Data Flow

1. [Step — e.g. "Request enters via API Gateway"]
2. [Step]
3. [Step — e.g. "Response returned to caller"]

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| [Layer] | [Tech] | [Why] |
| [Layer] | [Tech] | [Why] |

## Key Design Decisions

- **[Decision]**: [Rationale and trade-offs]
- **[Decision]**: [Rationale and trade-offs]

## Scalability & Performance Notes

*Document known bottlenecks, scaling strategies, and SLA targets here.*

---
*See `features/` for per-feature design docs; `architecture/` for diagrams and deep-dives.*
