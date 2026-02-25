# AgentRx Project Documentation
## *Home for detailed documentation on the target project, including setup instructions, architecture overview.*

## Project Docs Structure
### AgentRx Project Docs
```
$ARX_TARGET_DOCS/
└── Product.md                     # High-level product vision, core value proposition, and feature overview
└── Architecture.md                # System architecture, component interactions, and design decisions
└── features/
    ├── STATUS.md                 # Concise, up-to-date status of all features
    ├── user-bill-pay.md          # (Example) Detailed design and implementation notes for the bill payment feature
    ├── <another-feature>.md      
└── architecture/
    ├── STATUS.md                 # Concise, up-to-date status of all architecturural facets
    ├── system_diagram.png  # Visual representation of the system architecture
    └── component_descriptions.md  # Detailed descriptions of each 
    └── facets/
        ├── task_orchestration.md  # (Example)Core logic for managing task lifecycle, status transitions, and error handling
        ├── <another-facet>.md  
        
```
Note: the init process allows the user to define the document root ($ARX_PROJ_DOCS) for project documentation... The could be a directory in the 

### AgentRx Work[ing] Docs
```
$ARX_WORK_DOCS/
└── agentrx                         # AI-assisted development artifacts (note below). 
    ├── deltas
    ├── history
    └── vibes
```

The `agentrx` directory contains all files generated during an AI-assisted development process using AgentRX tooling. This includes saved prompts and specifications used during development. This allows for easy reference and traceability of the development process.