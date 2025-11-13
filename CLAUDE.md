# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

For general agent guidance and project overview, see [AGENTS.md](AGENTS.md).

## Claude-Specific Configuration

### Prompt File Execution
The primary Claude command for this repository:
```bash
/prompt-file {filename} {variables_json}
```

This command is available through `.claude/commands/prompt-file.md` and enables Claude to execute markdown files as prompts with variable substitution.

### Development Workflow for Claude

When working with this repository, Claude should:

Look for Claude Code files in .claude

### Claude Command Integration

Claude commands are stored in `.claude/commands/` and provide Claude-specific functionality for working with the AgentRX toolkit.