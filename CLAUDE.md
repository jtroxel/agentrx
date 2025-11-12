# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentRX is a toolkit that provides templates and tools for authentic coding practices that can coexist with files in any project repository. It's designed to enhance development workflows by providing a standardized set of prompts, commands, and utilities for working with AI agents like Claude.

## Architecture

This is a simple documentation and tooling project with the following structure:

- `agents/prompts/` - Collection of reusable prompt templates for AI agents
  - `agentrx_dev/` - Development-specific prompts including git integration patterns
  - Various markdown prompt files with variable substitution support
- `.claude/commands/` - Claude-specific commands and utilities
  - `prompt-file.md` - Command for executing markdown files as prompts with variable substitution
- `docs/` - Project documentation including host project setup guides

## Key Commands

### Prompt File Execution
```bash
/prompt-file {filename} {variables_json}
```

This is the primary command for executing markdown files as prompts. The command supports:
- Variable substitution using `{{variable_name}}` syntax
- Default variables defined in HTML comment blocks: `<!-- variable_name: default_value -->`
- JSON string for passing variables as second argument

Examples:
```bash
/prompt-file agents/prompts/agentrx_dev/agentrx_readme01.md
/prompt-file agents/prompts/test_prompt_1.md '{"project_name": "my-app"}'
```

## Development Workflow

No build, test, or lint commands are present as this is primarily a documentation and template project. Development involves:

1. Creating new prompt templates in `agents/prompts/`
2. Adding new Claude commands in `.claude/commands/`
3. Testing prompt execution via the `/prompt-file` command

## Integration Pattern

This project is designed to be integrated into host projects as a git submodule placed in `.agentrx/` directory. The integration allows:
- Clean separation between host project and AgentRX files
- Version control over AgentRX updates
- Project-specific customizations via `.agentrx-local/` (gitignored)
- Consistent agent workflows across development teams

## Variable Substitution System

Prompt files support variable substitution using:
- Default values: `<!-- variable_name: default_value -->` in HTML comments
- Runtime values: Pass JSON object as second argument to `/prompt-file`
- Template syntax: `{{variable_name}}` in prompt content

This allows for reusable, parameterizable prompt templates across different projects and contexts.