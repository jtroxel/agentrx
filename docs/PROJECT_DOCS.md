# AgentRx Project Documentation
## *Home for detailed documentation on the target project, including setup instructions, architecture overview.*

## Project Docs Structure

```
PROJECT_
└── Product.md      # High-level product vision, core value proposition, and feature overview
└── Architecture.md   # System architecture, component interactions, and design decisions
└── features/
    ├── bill_pay.md       # (Example) Detailed design and implementation notes for the bill payment feature
└── architecture/
    ├── system_diagram.png  # Visual representation of the system architecture
    └── component_descriptions.md  # Detailed descriptions of each 
    └── capabilities/
        ├── task_orchestration.md  # (Example)Core logic for managing task lifecycle, status transitions, and error handling
└── agentrx                         # AI-assisted development artifacts (note below). 
    ├── deltas
    ├── history
    └── vibes
Note `agentrx` allows the user to define the document root (${AGENTRX_DOC_ROOT}) for this content, it could be anywhere on the filesystem. --- IGNORE ---. Since this project is for development of agentrx itself, we are keeping the artifacts in a subdirectory here for easy access, but in a typical use case this could be outside the project repo.
```
The `agentrx` directory contains all files generated during an AI-assisted development process using AgentRX tooling. This includes saved prompts and specifications used during development. This allows for easy reference and traceability of the development process.