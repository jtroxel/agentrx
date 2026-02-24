"""AgentRx setup command - Configure AI coding agent integration."""

import json
import os
import click
from pathlib import Path
from typing import Optional, List

VALID_PROVIDERS = ["claude", "cursor", "opencode", "all"]


def find_workspace_root(start_path: Path) -> Optional[Path]:
    """Find project root by looking for _agents or .claude directory."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / "_agents").exists() or (current / ".claude").exists():
            return current
        current = current.parent
    return None


def create_symlink(link_path: Path, target_path: Path) -> bool:
    """Create symbolic link with relative path."""
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()

    try:
        rel_target = os.path.relpath(target_path, link_path.parent)
    except ValueError:
        rel_target = str(target_path)

    link_path.symlink_to(rel_target)
    return True


def is_doc_file(name: str) -> bool:
    """Check if a filename is a documentation file (not a command/skill)."""
    doc_patterns = ["README", "SUMMARY", "GETTING-STARTED", "QUICKREF"]
    return (name in doc_patterns or
            name.startswith("COMMAND_") or
            "USAGE" in name or
            "INDEX" in name)


def setup_claude(root: Path, agents_dir: Path, clean: bool, verbose: bool):
    """Set up Claude Code integration with symlinks."""
    claude_dir = root / ".claude"

    click.secho("Setting up Claude Code integration...", fg="cyan")
    click.echo()

    # Create .claude directories
    (claude_dir / "commands").mkdir(parents=True, exist_ok=True)
    (claude_dir / "skills").mkdir(parents=True, exist_ok=True)

    # Clean existing links if requested
    if clean:
        click.secho("Cleaning existing Claude links...", fg="cyan")
        for item in claude_dir.rglob("*"):
            if item.is_symlink():
                item.unlink()

    # Link commands
    click.secho("Setting up command links...", fg="cyan")
    commands_dir = agents_dir / "commands"
    if commands_dir.exists():
        for namespace_dir in commands_dir.iterdir():
            if namespace_dir.is_dir():
                namespace = namespace_dir.name
                link_path = claude_dir / "commands" / namespace
                create_symlink(link_path, namespace_dir)
                click.secho(f"  [OK] commands/{namespace}", fg="green")

                if verbose:
                    for cmd_file in namespace_dir.glob("*.md"):
                        if not is_doc_file(cmd_file.stem):
                            click.echo(f"       /{namespace}:{cmd_file.stem}")

    # Link skills
    click.secho("Setting up skill links...", fg="cyan")
    skills_dir = agents_dir / "skills"
    if skills_dir.exists():
        for namespace_dir in skills_dir.iterdir():
            if namespace_dir.is_dir():
                namespace = namespace_dir.name
                link_path = claude_dir / "skills" / namespace
                create_symlink(link_path, namespace_dir)
                click.secho(f"  [OK] skills/{namespace}", fg="green")

                if verbose:
                    for skill_file in namespace_dir.glob("*.md"):
                        click.echo(f"       {namespace}:{skill_file.stem}")

    # Link hooks
    hooks_dir = agents_dir / "hooks"
    if hooks_dir.exists():
        click.secho("Setting up hooks link...", fg="cyan")
        link_path = claude_dir / "hooks"
        create_symlink(link_path, hooks_dir)
        click.secho("  [OK] hooks", fg="green")

    # Link settings
    settings_file = agents_dir / "settings.local.json"
    if settings_file.exists():
        click.secho("Setting up settings link...", fg="cyan")
        link_path = claude_dir / "settings.local.json"
        create_symlink(link_path, settings_file)
        click.secho("  [OK] settings.local.json", fg="green")

    click.secho("Claude Code setup complete!", fg="green")


def setup_cursor(root: Path, agents_dir: Path, clean: bool, verbose: bool):
    """Set up Cursor IDE integration with wrapper files."""
    cursor_dir = root / ".cursor"
    cursor_rules_dir = cursor_dir / "rules"

    click.secho("Setting up Cursor IDE integration...", fg="cyan")
    click.echo()

    # Clean existing files if requested
    if clean:
        click.secho("Cleaning existing Cursor files...", fg="cyan")
        cursorrules = root / ".cursorrules"
        if cursorrules.exists():
            cursorrules.unlink()
        if cursor_rules_dir.exists():
            import shutil
            shutil.rmtree(cursor_rules_dir)

    # Create .cursor/rules directory
    cursor_rules_dir.mkdir(parents=True, exist_ok=True)

    # Create .cursorrules wrapper file (legacy support)
    click.secho("Creating .cursorrules wrapper file...", fg="cyan")
    cursorrules_content = """\
# Cursor Rules - AgentRx Integration
# This file wraps the AgentRx agent configuration.
# For full agent instructions, see: _agents/AGENTS.md

## Important Files
Read the following files at the start of each session:
1. `_agents/AGENTS.md` - Main agent instructions
2. `_agents/CLAUDE.md` - Additional guidance (if exists)

## Quick Reference
- Commands are in `_agents/commands/`
- Skills are in `_agents/skills/`
- Hooks are in `_agents/hooks/`

## Instructions
Follow all guidance in `_agents/AGENTS.md`. That file contains the primary
instructions for AI agents working with this codebase.
"""
    (root / ".cursorrules").write_text(cursorrules_content)
    click.secho("  [OK] .cursorrules", fg="green")

    # Create .cursor/rules/agents.mdc (new format)
    click.secho("Creating .cursor/rules/agents.mdc...", fg="cyan")
    mdc_content = """\
---
description: "AgentRx Agent Configuration"
globs: ["**/*"]
alwaysApply: true
---

# AgentRx Agent Configuration

This project uses AgentRx for AI agent configuration.

## Required Reading

At the start of each session, read:
1. `_agents/AGENTS.md` - Primary agent instructions
2. `_agents/CLAUDE.md` - Additional Claude-specific guidance

## Project Structure

- `_agents/commands/` - Slash commands (e.g., /agentrx:init)
- `_agents/skills/` - Reusable skills and templates
- `_agents/hooks/` - Event hooks for agent actions
- `_agents/scripts/` - Shell scripts for automation

## Key Principles

Follow all guidance in `_agents/AGENTS.md`. The instructions there take
precedence for this project.
"""
    (cursor_rules_dir / "agents.mdc").write_text(mdc_content)
    click.secho("  [OK] .cursor/rules/agents.mdc", fg="green")

    click.secho("Cursor setup complete!", fg="green")


def setup_opencode(root: Path, agents_dir: Path, clean: bool, verbose: bool):
    """Set up OpenCode integration with wrapper files."""
    click.secho("Setting up OpenCode integration...", fg="cyan")
    click.echo()

    agents_md = root / "AGENTS.md"
    opencode_config = root / "opencode.json"

    # Clean existing files if requested
    if clean:
        click.secho("Cleaning existing OpenCode files...", fg="cyan")
        # Only remove if it's a wrapper file
        if agents_md.exists():
            content = agents_md.read_text()
            if "AgentRx Wrapper" in content:
                agents_md.unlink()

    # Create AGENTS.md wrapper in project root
    output_file = agents_md
    if agents_md.exists():
        content = agents_md.read_text()
        if "AgentRx Wrapper" in content:
            click.secho("AGENTS.md wrapper already exists, updating...", fg="cyan")
        else:
            click.secho("AGENTS.md already exists. Creating AGENTS.md.agentrx instead.", fg="yellow")
            click.secho("You may want to manually merge or replace.", fg="yellow")
            output_file = root / "AGENTS.md.agentrx"

    click.secho("Creating AGENTS.md wrapper file...", fg="cyan")
    agents_content = """\
<!-- AgentRx Wrapper - Auto-generated by arx setup -->
# Agent Instructions

This project uses AgentRx for AI agent configuration.

## Required Reading

**IMPORTANT**: Read the full agent instructions from the following file:

→ **`_agents/AGENTS.md`** - Primary agent instructions and project context

Additional context files:
- `_agents/CLAUDE.md` - Claude-specific guidance
- `_agents/workspace_root_files/CONTEXT_DOCUMENTS_INDEX.md` - Context document index

## Quick Reference

| Resource | Location |
|----------|----------|
| Commands | `_agents/commands/` |
| Skills | `_agents/skills/` |
| Hooks | `_agents/hooks/` |
| Scripts | `_agents/scripts/` |

## Instructions

All agent behavior should follow the guidance in `_agents/AGENTS.md`.
That file contains the authoritative instructions for this project.
"""
    output_file.write_text(agents_content)
    click.secho(f"  [OK] {output_file.name}", fg="green")

    # Create opencode.json if it doesn't exist
    if not opencode_config.exists():
        click.secho("Creating opencode.json configuration...", fg="cyan")
        config = {
            "$schema": "https://opencode.ai/config.json",
            "instructions": [
                "_agents/AGENTS.md",
                "_agents/CLAUDE.md"
            ]
        }
        opencode_config.write_text(json.dumps(config, indent=2) + "\n")
        click.secho("  [OK] opencode.json", fg="green")
    else:
        click.secho("opencode.json already exists, skipping...", fg="cyan")

    click.secho("OpenCode setup complete!", fg="green")


@click.command()
@click.option("--provider", type=click.Choice(VALID_PROVIDERS, case_sensitive=False),
              default="all", help="Provider to set up: claude, cursor, opencode, or all")
@click.option("--workspace-root", type=click.Path(exists=True),
              help="Set workspace root directory")
@click.option("--clean", is_flag=True, help="Remove existing files before creating new ones")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output")
def setup(provider: str, workspace_root: Optional[str], clean: bool, verbose: bool):
    """Set up AI coding agent integration.

    Creates integration files for Claude Code, Cursor, and OpenCode.

    \b
    Supported providers:
      claude    - .claude/ directory with symlinks
      cursor    - .cursorrules and .cursor/rules/
      opencode  - AGENTS.md wrapper and opencode.json
      all       - All of the above (default)
    """
    # Find project root
    if workspace_root:
        root = Path(workspace_root).resolve()
    else:
        root = find_workspace_root(Path.cwd())
        if not root:
            root = Path.cwd()

    agents_dir = root / "_agents"

    click.echo()
    click.secho("AgentRx Agent Setup", fg="blue", bold=True)
    click.echo("=" * 40)
    click.echo(f"Project root: {root}")
    click.echo(f"Agents dir:   {agents_dir}")
    click.echo(f"Provider:     {provider}")
    click.echo()

    # Verify _agents exists
    if not agents_dir.exists():
        click.secho(f"Error: _agents directory not found at {agents_dir}", fg="red")
        click.echo("Run 'arx init' first to create the project structure.")
        raise SystemExit(1)

    # Run setup based on provider
    if provider in ("claude", "all"):
        setup_claude(root, agents_dir, clean, verbose)
        click.echo()

    if provider in ("cursor", "all"):
        setup_cursor(root, agents_dir, clean, verbose)
        click.echo()

    if provider in ("opencode", "all"):
        setup_opencode(root, agents_dir, clean, verbose)
        click.echo()

    # Summary
    click.echo("=" * 40)
    click.secho(f"Setup complete for: {provider}", fg="green", bold=True)
    click.echo()

    # List available commands (only if Claude was set up)
    if provider in ("claude", "all"):
        claude_dir = root / ".claude"
        click.echo("Available commands:")
        commands_link = claude_dir / "commands"
        if commands_link.exists():
            for namespace_dir in commands_link.iterdir():
                if namespace_dir.is_dir():
                    namespace = namespace_dir.name
                    for cmd_file in namespace_dir.glob("*.md"):
                        if not is_doc_file(cmd_file.stem):
                            click.echo(f"  /{namespace}:{cmd_file.stem}")

        click.echo()
        click.echo("Available skills:")
        skills_link = claude_dir / "skills"
        if skills_link.exists():
            for namespace_dir in skills_link.iterdir():
                if namespace_dir.is_dir():
                    namespace = namespace_dir.name
                    for skill_file in namespace_dir.glob("*.md"):
                        click.echo(f"  {namespace}:{skill_file.stem}")
        click.echo()

    # Show created files
    click.echo("Provider-specific files created:")
    if provider in ("claude", "all"):
        click.echo("  - .claude/ directory with symlinks")
    if provider in ("cursor", "all"):
        click.echo("  - .cursorrules (legacy format)")
        click.echo("  - .cursor/rules/agents.mdc (new format)")
    if provider in ("opencode", "all"):
        click.echo("  - AGENTS.md wrapper file")
        click.echo("  - opencode.json configuration")

    click.echo()
    click.echo("To verify:")
    if provider in ("claude", "all"):
        click.echo(f"  ls -la {root / '.claude'}/")
    if provider in ("cursor", "all"):
        click.echo(f"  cat {root / '.cursorrules'}")
    if provider in ("opencode", "all"):
        click.echo(f"  cat {root / 'AGENTS.md'}")
    click.echo()
