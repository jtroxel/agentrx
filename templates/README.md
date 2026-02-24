---
title: "AgenTrx Templates"
description: "Template files for AgentRx projects, including documentation templates, prompt templates, and example artifacts."
arx: template
---

# AgenTrx Templates
## Top-Level Folder
This folder contains template files for AgentRx projects, including documentation templates, prompt templates, and example artifacts.

The (top-level) directory (here) contains templates for AgentRx files that instruct Coding Agents on how use AgentRx tools on a project. These files contain core context information for agentic development. This level corresponds to the workspace root directory, `$ARX_WORKSPACE_ROOT`.

During init/install, all files at this (top-level) directory, matching the following patterns are copied or linked into `$ARX_WORKSPACE_ROOT/`.
 - `*.ARX.*`
 - `*.arx.*`

## ./_arx_agent_tools.arx
This directory contains template files for AgentRx tools that are used by Coding Agents. The directory targets `$ARX_AGENT_TOOLS`, which corresponds to the location where these tools are installed or linked during initialization.




