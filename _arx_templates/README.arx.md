---
title: "AgentRx Templates"
description: "Template files for AgentRx projects. Each subdirectory maps to one ARX_* destination variable."
arx: template
---

# AgentRx Templates

This directory contains all template files installed by `arx init`. Each `_arx_<name>` subdirectory maps **1-to-1** to an `ARX_*` environment variable (destination path).

## Subdirectory → Destination Mapping

| Subdirectory | Destination | Behaviour |
|---|---|---|
| `_arx_workspace_root/` | `$ARX_WORKSPACE_ROOT` | Contains workspace root files. Files with `.ARX.` marker are ignored; bare files are installed as-is. |
| `_arx_agent_tools/` | `$ARX_AGENT_TOOLS` | All files copied as-is (files with `.ARX.` are ignored). |
| `_arx_work_docs/` | `$ARX_WORK_DOCS` | Always copied (files with `.ARX.` are ignored). |
| `_arx_proj_docs/` | `$ARX_PROJ_DOCS` | Optional; user is prompted interactively (or `--docs`/`--no-docs`). Files with `.ARX.` are ignored. |

## `.ARX.` Naming Convention

Files whose names contain `.ARX.` (or `.arx.`) are **excluded** from installation (treated as template documentation or metadata).

Files **without** the marker (bare files) are installed **as-is** to the destination.

- `AGENTS.md` → `AGENTS.md` (installed)
- `README.arx.md` → (ignored/not installed)

This allows you to keep documentation or metadata alongside your templates without polluting the generated project.

## `_arx_workspace_root/`

Templates for the workspace root (`$ARX_WORKSPACE_ROOT`). Installed as-is (ignoring `.ARX.` files):
- `AGENTS.md` → startup instructions for coding agents
- `AGENT_TOOLS.md` → context documents index
- `CLAUDE.md` → Claude Code guidance
- `.cursorrules` → Cursor IDE rules (delegates to AGENTS.md)

## `_arx_agent_tools/`

Agent assets installed into `$ARX_AGENT_TOOLS` (default: `_agents/`):
- `commands/agentrx/` — slash command definitions
- `skills/agentrx/` — agent skill documents
- `scripts/agentrx/` — utility shell scripts
- `hooks/agentrx/` — event hooks
- `agents/` — agent configurations

In `--link-arx` mode each `agentrx/` leaf is symlinked back to this source tree instead of copied.

## `_arx_proj_docs/`

Optional project documentation skeleton installed into `$ARX_PROJ_DOCS` (default: `_project/docs/`). Prompted interactively unless `--docs` or `--no-docs` is passed:
- `README.md` → `README.md` — docs index
- `Architecture.md` → `Architecture.md`
- `Product.md` → `Product.md`
- `features/feature.md` → per-feature design template
- `architecture/` — deep-dive architecture templates

## `_arx_work_docs/`

Working docs scaffolding installed into `$ARX_WORK_DOCS` (default: `_project/docs/agentrx/`). Always copied. Subdirs contain `.gitkeep` files so git tracks the empty directories:
- `deltas/` — change specs and delta documents
- `sessions/` — session context and notes
- `tasks_tracking/` — active task lists
- `vibes/` — prompt files (`arx prompt new` output)
