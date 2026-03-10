# AgentRx Project Documentation Templates

ARX templates for creating project documentation. These templates use the ARX templating syntax (see [`arx_templating.md`](../../_agents/skills/agentrx/arx_templating.md)).

## Quick Reference

| Template | Purpose | Example Output |
|----------|---------|----------------|
| [`Product.ARX.md`](./Product.ARX.md) | Product vision and value proposition | `Product.md` |
| [`Architecture.ARX.md`](./Architecture.ARX.md) | System architecture and capabilities | `Architecture.md` |
| [`README.ARX.md`](./README.ARX.md) | Documentation index | `docs/README.md` |
| [`features.arx/feature.ARX.md`](./features.arx/feature.ARX.md) | Feature specifications | `features/*.md` |
| [`facets.arx/facet.ARX.md`](./facets.arx/facet.ARX.md) | Architecture facets | `architecture/facets/*.md` |

## Usage

### Using ARX CLI

```bash
# Create Product.md from Product.ARX.md template
arx prompt new product-0 "User-Facing AI Documentation Tool"

# Create with structured data
arx prompt new architecture-0 "MyProject" --data '{
  "project_description": "AI-powered workflow automation",
  "capabilities": [
    {"name": "Recorder", "purpose": "Capture actions", "status": "Implemented"}
  ]
}'

# Create a feature spec
arx prompt new feature "User Authentication" --data '{
  "status": "In Design",
  "problem": "Users need secure access"
}'
```

### Using Shell Init Script

```bash
# Initialize project with placeholder docs
$AGENTRX_SOURCE/bin/init-arx.sh --init-docs .
```

This creates:
- `docs/Product.md` — placeholder with template instructions
- `docs/Architecture.md` — placeholder with template instructions
- `docs/features/STATUS.md`
- `docs/architecture/STATUS.md`

## Template Details

### Product.ARX.md

**Purpose:** Define product vision, goals, target users, and competitive landscape.

**Key Sections:**
- One-liner tagline
- Problem statement
- Solution vision
- Core product themes
- Target users
- Goals and non-goals
- Success metrics
- Competitive landscape
- Logical architecture

**Example Data:**
```json
{
  "project_name": "Flo",
  "tagline": "Local AI assistant for productivity",
  "problem_statement": "Knowledge workers waste hours on repetitive tasks",
  "solution_vision": "Local-first AI that automates with human approval",
  "target_users": [
    {"role": "Knowledge Worker", "description": "Uses multiple tools daily"}
  ],
  "key_features": [
    {"name": "Workflow Recording", "description": "Capture by demonstration"}
  ]
}
```

**See Example:** [`PRODUCT-0.EXAMPLE.md`](./PRODUCT-0.EXAMPLE.md) — Real product doc for "Flo Local Agent"

### Architecture.ARX.md

**Purpose:** Document system architecture, capabilities, and design decisions.

**Key Sections:**
- System overview (ASCII diagram)
- Capabilities (purpose, inputs, outputs, status)
- Cross-cutting concerns
- Development phases
- Technology stack
- Architecture Decision Records (ADRs)

**Example Data:**
```json
{
  "project_name": "Flo",
  "project_description": "Local AI assistant",
  "capabilities": [
    {
      "name": "Workflow Recorder",
      "purpose": "Capture human interactions as workflow steps",
      "inputs": ["Browser actions", "gate annotations"],
      "outputs": ["Workflow definition", "screenshots"],
      "behaviors": ["Launch recording mode", "Capture selectors"],
      "technical_approach": "Playwright tracing and CDP events",
      "status": "✅ Implemented"
    }
  ],
  "development_phases": [
    {"name": "Foundation", "items": ["Recorder", "Library", "Orchestrator"]}
  ]
}
```

**See Example:** [`ARCHITECTURE-0.EXAMPLE.md`](./ARCHITECTURE-0.EXAMPLE.md) — Real architecture doc for "Flo Local Agent"

### README.ARX.md

**Purpose:** Documentation index with navigation to all project docs.

**Uses:** Links to Product, Architecture, features, and facets.

## Template Structure

All templates follow ARX conventions:

1. **Front Matter** — `arx: template` identifies template type
2. **Inputs** — Declared parameters with types and defaults
3. **ARX Tags** — `[[variable]]`, `[[#condition]]:`, `[[*items]]:`, etc.
4. **Sections** — Conditionally rendered based on data presence

### Example: Conditional Sections

```markdown
<ARX [[#capabilities]]: />
## Capabilities
<ARX [[*capabilities as capability]]: />
### <ARX [[capability.name]] />
...
<ARX /: />
<ARX /: />

<ARX [[^capabilities]]: />
*Capabilities will be documented here.*
<ARX /: />
```

### Example: Default Values

```markdown
<ARX [[capability.status | "🔨 Not started"]] />
```

## Document Lifecycle

| Phase | Document | Template | Status |
|-------|----------|----------|--------|
| 0 | Product-0 | `Product.ARX.md` | Initial concept |
| 0 | Architecture-0 | `Architecture.ARX.md` | Initial design |
| Current | Product | Manual/ARX | Living document |
| Current | Architecture | Manual/ARX | Living document |
| Deep-dives | features/*.md | `feature.ARX.md` | Feature specs |
| Deep-dives | facets/*.md | `facet.ARX.md` | Component specs |

## Best Practices

1. **Start with Phase 0** — Use templates to create initial Product and Architecture docs
2. **Iterate** — Update the "Current" documents as your understanding evolves
3. **Use STATUS.md** — Track feature and facet status in dedicated files
4. **Link Documents** — Use relative links between docs
5. **ARX Rendering** — Use `arx prompt new` to generate from templates

## Directory Layout

After initialization with `--init-docs`:

```
docs/
├── Product.md              # Product.ARX.md rendered
├── Architecture.md         # Architecture.ARX.md rendered
├── README.md               # This index
├── features/
│   ├── STATUS.md          # Feature tracking
│   └── *.md               # Feature specs
└── architecture/
    ├── STATUS.md          # Facet tracking
    └── facets/
        └── *.md           # Component docs
```

## See Also

- [`arx_templating.md`](../../_agents/skills/agentrx/arx_templating.md) — ARX syntax reference
- [`PROJECT_DOCS.md`](../../docs/PROJECT_DOCS.md) — AgentRx documentation guide
- [`COMMAND_INDEX.md`](../../_agents/commands/agentrx/COMMAND_INDEX.md) — Available commands
