"""AgentRx prompt commands - Work with prompt files."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

# Default directories
DEFAULT_PROMPTS_DIR = "_project/docs/agentrx/vibes"
DEFAULT_HISTORY_SUBDIR = "history"


class PromptError(Exception):
    """Error during prompt operations."""
    pass


def get_prompts_dir() -> Path:
    """Get the prompts directory from env or default."""
    prompts_dir = os.environ.get("ARX_PROMPTS", DEFAULT_PROMPTS_DIR)
    return Path(prompts_dir)


def get_history_dir() -> Path:
    """Get the history directory from env or default."""
    history_dir = os.environ.get("ARX_HISTORY")
    if history_dir:
        return Path(history_dir)
    return get_prompts_dir() / DEFAULT_HISTORY_SUBDIR


def find_most_recent_prompt(prompts_dir: Path) -> Optional[Path]:
    """Find the most recently modified .md file in prompts directory."""
    if not prompts_dir.exists():
        return None

    md_files = list(prompts_dir.glob("*.md"))
    if not md_files:
        return None

    # Sort by modification time, most recent first
    md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return md_files[0]


def load_json_data(data_path: Optional[Path], stdin_data: Optional[str]) -> dict:
    """Load and merge JSON data from file and/or stdin."""
    result = {}

    # Load from file if specified
    if data_path:
        if not data_path.exists():
            raise PromptError(f"Data file not found: {data_path}")
        try:
            result = json.loads(data_path.read_text())
        except json.JSONDecodeError as e:
            raise PromptError(f"Invalid JSON in {data_path}: {e}")

    # Load from stdin if available
    if stdin_data:
        try:
            stdin_json = json.loads(stdin_data)
            # Merge stdin data (stdin takes precedence)
            if isinstance(stdin_json, dict) and isinstance(result, dict):
                result.update(stdin_json)
            else:
                result = stdin_json
        except json.JSONDecodeError as e:
            raise PromptError(f"Invalid JSON from stdin: {e}")

    return result


def read_stdin_if_available() -> Optional[str]:
    """Read stdin if data is being piped in."""
    if sys.stdin.isatty():
        return None
    try:
        return sys.stdin.read()
    except Exception:
        return None


def write_history_entry(
    history_dir: Path,
    prompt_file: Path,
    data_source: Optional[str],
    data: dict,
    output_file: Optional[Path],
) -> Path:
    """Write execution history entry."""
    now = datetime.now()
    date_dir = history_dir / now.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)

    prompt_name = prompt_file.stem
    timestamp = now.strftime("%H-%M-%S")
    history_file = date_dir / f"{prompt_name}_{timestamp}.json"

    entry = {
        "timestamp": now.isoformat(),
        "prompt_file": str(prompt_file),
        "data_source": data_source,
        "data": data,
        "output_file": str(output_file) if output_file else None,
    }

    history_file.write_text(json.dumps(entry, indent=2))
    return history_file


@click.group()
def prompt():
    """Work with prompt files.

    Commands for creating, executing, and managing prompt files.
    """
    pass


@prompt.command("do")
@click.argument("prompt_file", required=False, type=click.Path())
@click.option("-d", "--data", "data_file", type=click.Path(exists=True),
              help="Path to JSON data file for context")
@click.option("-H", "--history", is_flag=True,
              help="Append execution to history log")
@click.option("-o", "--output", "output_file", type=click.Path(),
              help="Output file path (default: stdout)")
@click.option("--dry-run", is_flag=True,
              help="Show what would be executed without running")
@click.option("-v", "--verbose", is_flag=True,
              help="Show detailed output")
def do_prompt(
    prompt_file: Optional[str],
    data_file: Optional[str],
    history: bool,
    output_file: Optional[str],
    dry_run: bool,
    verbose: bool,
):
    """Execute a prompt with optional data context.

    If PROMPT_FILE is not specified, uses the most recent .md file
    in the ARX_PROMPTS directory.

    Data can be provided via --data file or piped through stdin.
    When both are provided, they are merged (stdin takes precedence).

    Examples:

        # Execute most recent prompt
        arx prompt do

        # Execute specific prompt with data
        arx prompt do my_prompt.md --data context.json

        # Pipe data from another command
        cat data.json | arx prompt do my_prompt.md

        # Execute and log to history
        arx prompt do my_prompt.md --history
    """
    try:
        _do_prompt_impl(
            prompt_file=prompt_file,
            data_file=data_file,
            history=history,
            output_file=output_file,
            dry_run=dry_run,
            verbose=verbose,
        )
    except PromptError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


def _do_prompt_impl(
    prompt_file: Optional[str],
    data_file: Optional[str],
    history: bool,
    output_file: Optional[str],
    dry_run: bool,
    verbose: bool,
) -> None:
    """Implementation of prompt do command."""
    prompts_dir = get_prompts_dir()

    # Resolve prompt file
    if prompt_file:
        prompt_path = Path(prompt_file)
        # If not absolute, check relative to prompts_dir first
        if not prompt_path.is_absolute() and not prompt_path.exists():
            candidate = prompts_dir / prompt_file
            if candidate.exists():
                prompt_path = candidate
    else:
        # Find most recent prompt
        if not prompts_dir.exists():
            raise PromptError(
                f"Prompts directory not found: {prompts_dir}\n"
                f"Set ARX_PROMPTS environment variable or specify a prompt file."
            )
        prompt_path = find_most_recent_prompt(prompts_dir)
        if not prompt_path:
            raise PromptError(f"No prompt files found in {prompts_dir}")

    if not prompt_path.exists():
        raise PromptError(f"Prompt file not found: {prompt_path}")

    # Load data
    stdin_data = read_stdin_if_available()
    data_path = Path(data_file) if data_file else None
    data = load_json_data(data_path, stdin_data)

    # Determine data source for history
    data_source = None
    if data_file and stdin_data:
        data_source = f"{data_file} + stdin"
    elif data_file:
        data_source = data_file
    elif stdin_data:
        data_source = "stdin"

    # Read prompt content
    prompt_content = prompt_path.read_text()

    # Dry run - just show what would happen
    if dry_run:
        click.secho("=== Dry Run ===", fg="cyan", bold=True)
        click.echo(f"Prompt file: {prompt_path}")
        click.echo(f"Data source: {data_source or 'none'}")
        if data:
            click.echo(f"Data keys: {list(data.keys())}")
        click.echo(f"Output: {output_file or 'stdout'}")
        click.echo(f"History: {'enabled' if history else 'disabled'}")
        click.echo()
        click.secho("=== Prompt Content ===", fg="cyan")
        click.echo(prompt_content[:500] + ("..." if len(prompt_content) > 500 else ""))
        if data:
            click.echo()
            click.secho("=== Data Preview ===", fg="cyan")
            click.echo(json.dumps(data, indent=2)[:500])
        return

    if verbose:
        click.secho(f"Executing prompt: {prompt_path}", fg="cyan")
        if data_source:
            click.secho(f"With data from: {data_source}", fg="cyan")

    # Build output content
    # For now, just output the prompt content with data summary
    # In full implementation, this would render ARX templates
    output_lines = [
        f"# Prompt: {prompt_path.name}",
        "",
        prompt_content,
    ]

    if data:
        output_lines.extend([
            "",
            "---",
            "## Context Data",
            "```json",
            json.dumps(data, indent=2),
            "```",
        ])

    output_content = "\n".join(output_lines)

    # Write output
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_content)
        if verbose:
            click.secho(f"Output written to: {output_path}", fg="green")
    else:
        click.echo(output_content)

    # Write history if requested
    if history:
        history_dir = get_history_dir()
        output_path_obj = Path(output_file) if output_file else None
        history_file = write_history_entry(
            history_dir=history_dir,
            prompt_file=prompt_path,
            data_source=data_source,
            data=data,
            output_file=output_path_obj,
        )
        if verbose:
            click.secho(f"History logged to: {history_file}", fg="green")


@prompt.command("new")
@click.argument("content")
@click.argument("short_name", required=False)
@click.option("--dir", "out_dir", type=click.Path(),
              help="Output directory (default: ARX_PROMPTS or current dir)")
@click.option("-v", "--verbose", is_flag=True,
              help="Show detailed output")
def new_prompt(content: str, short_name: Optional[str], out_dir: Optional[str], verbose: bool):
    """Create a new prompt file with automatic naming.

    CONTENT is the prompt text to save.

    SHORT_NAME is optional; if not provided, it's derived from the first
    3 words of the content.

    Examples:

        # Create with auto-generated name
        arx prompt new "Implement user authentication"

        # Create with specific name
        arx prompt new "Implement user authentication" auth_feature

        # Create in specific directory
        arx prompt new "Fix the bug" --dir ./prompts
    """
    # Determine output directory
    if out_dir:
        target_dir = Path(out_dir)
    else:
        target_dir = get_prompts_dir()

    target_dir.mkdir(parents=True, exist_ok=True)

    # Generate short name if not provided
    if not short_name:
        words = content.split()[:3]
        short_name = "_".join(
            "".join(c for c in w.lower() if c.isalnum())
            for w in words
        )

    # Generate timestamp
    now = datetime.now()
    timestamp = now.strftime("%y-%m-%d-%H")
    filename = f"{short_name}_{timestamp}.md"

    # Create file
    file_path = target_dir / filename
    file_content = f"""# Prompt: {short_name}

{content}

---
*Created: {now.strftime("%Y-%m-%d %H:%M:%S")}*
"""

    file_path.write_text(file_content)

    if verbose:
        click.secho(f"Created: {file_path}", fg="green")
    else:
        click.echo(str(file_path))


@prompt.command("list")
@click.option("-n", "--limit", default=10, help="Number of prompts to show")
@click.option("--dir", "prompts_dir", type=click.Path(exists=True),
              help="Prompts directory (default: ARX_PROMPTS)")
def list_prompts(limit: int, prompts_dir: Optional[str]):
    """List recent prompt files.

    Shows the most recent prompt files in the prompts directory,
    sorted by modification time.
    """
    if prompts_dir:
        target_dir = Path(prompts_dir)
    else:
        target_dir = get_prompts_dir()

    if not target_dir.exists():
        click.secho(f"Prompts directory not found: {target_dir}", fg="red", err=True)
        sys.exit(1)

    md_files = list(target_dir.glob("*.md"))
    if not md_files:
        click.echo(f"No prompt files in {target_dir}")
        return

    # Sort by modification time
    md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    click.secho(f"Recent prompts in {target_dir}:", fg="cyan")
    for i, f in enumerate(md_files[:limit]):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        age = datetime.now() - mtime
        if age.days > 0:
            age_str = f"{age.days}d ago"
        elif age.seconds > 3600:
            age_str = f"{age.seconds // 3600}h ago"
        else:
            age_str = f"{age.seconds // 60}m ago"

        marker = "*" if i == 0 else " "
        click.echo(f"  {marker} {f.name} ({age_str})")

    if len(md_files) > limit:
        click.echo(f"  ... and {len(md_files) - limit} more")
