# AgenTrx Process Overview
## An overview of using AgentRx in an iterative, incremental software development process.

## Project Documentation
See: [Project Dev Files](../PROJECT_STRUCT.md) for an outline of the recommended documentation structure for an AgentRx project. In many ways, the process for AgentRx, iterative and incremental development entails creating & updating these documents as you work through the development process. 

## Prompt-Driven Primitives
The core primitives for using AgentRx in a development process are: 
- Prompt creation: Using `/agentrx:prompt-new` to create new prompt files for Agent-assisted development. (TODO:)Prompts can be a generic "vibe" prompt by default. Or the user can specify a template to use for the prompt file
either a custom template or referincing an artifact "type" as outlined in [Project Docs](../PROJECT_STRUCT.md).
- Prompt execution: Using `/agentrx:prompt-do` to execute prompt files and generate outputs (e.g. design documents, code snippets, test cases).

## Foundation: AgentRx Templated Prompt Commands
```mermaid
---
config:
  theme: redux
  look: handDrawn
  layout: dagre
---
flowchart LR
 subgraph s1["Coding Agent TUI"]
    direction LR
        n10["L L M"]
        sA("Sub-Agent")
        B["doCommand"]
  end
    n7(("user")) -- input --> A["**(start) /arx:command<br>- prompt_template<br>- command-args...**"]
    A ---> B
    n5["<br>Command<br>. Prompt Template .<br><br>"] -.-> B
    C["<br>. Commands .<br>(files)<br><br>"] -.-> B
    B --> sA
    sA <-.-> n10
    n11["<br>. Skills (files) .<br><br>"] -.-> D["CLIs,<br>APIs, MCP<br>"]

    n10 --> n8[". <br>. **(end)<br>. Generated Output** .<br><br>"]
    n12["<br>. Agents (files) .<br><br>"] -.-> sA
    n13["<br>. Skills (files) .<br><br>"] --> n9["2) {{}} processor"]
    n13 -.-> B
    sA <-.-> n11

    B@{ shape: rounded}
    n10@{ shape: dbl-circ}
    A@{ shape: rounded}
    n5@{ shape: card}
    C@{ shape: card}
    n11@{ shape: card}
    n9@{ shape: rounded}
    D@{ shape: rounded}
    n8@{ shape: card}
    n12@{ shape: card}
    n13@{ shape: card}
    style n11 stroke-width:2px,stroke-dasharray: 0
    style n8 stroke-width:4px,stroke-dasharray: 0
    style n12 stroke-width:2px,stroke-dasharray: 0
    style n13 stroke-width:2px,stroke-dasharray: 0
```

## Iterative Development Workflow
### Generic Flow for 1 Iteration
/prompt-new (User: summary and optional variables)
  -> System: creates a new, prompt file--
 New prompt file with summary and optional variables
  -> elaborate/review prompt & context docs -> prompt-do => (code or interim artifact) -> review output -> update docs/specs -> ... (repeat until done)