"""AgentRx prompt commands - Work with prompt files."""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from agentrx.render import build_context, read_stdin_if_available, render_file

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
              help="Path to JSON/YAML data file for context")
@click.option("-D", "--data-json", "data_json",
              help="Inline JSON string for context (merged with --data; highest priority)")
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
    data_json: Optional[str],
    history: bool,
    output_file: Optional[str],
    dry_run: bool,
    verbose: bool,
):
    """Execute a prompt with optional data context.

    If PROMPT_FILE is not specified, uses the most recent .md file
    in the ARX_PROMPTS directory.

    Data can be provided via --data file, --data-json inline string,
    or piped through stdin.  When multiple sources are given they are
    merged: file < --data-json < stdin (stdin wins).

    Examples:

        # Execute most recent prompt
        arx prompt do

        # Execute specific prompt with data file
        arx prompt do my_prompt.md --data context.json

        # Execute with inline JSON context
        arx prompt do my_prompt.md --data-json '{"name": "Alice"}'

        # Pipe data from another command
        cat data.json | arx prompt do my_prompt.md

        # Execute and log to history
        arx prompt do my_prompt.md --history
    """
    try:
        _do_prompt_impl(
            prompt_file=prompt_file,
            data_file=data_file,
            data_json=data_json,
            history=history,
            output_file=output_file,
            dry_run=dry_run,
            verbose=verbose,
        )
    except PromptError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


def _resolve_prompt_path(prompt_file: Optional[str], prompts_dir: Path) -> Path:
    """Resolve prompt_file arg to an existing Path."""
    if prompt_file:
        p = Path(prompt_file)
        if not p.is_absolute() and not p.exists():
            candidate = prompts_dir / prompt_file
            if candidate.exists():
                return candidate
        return p
    if not prompts_dir.exists():
        raise PromptError(
            f"Prompts directory not found: {prompts_dir}\n"
            "Set ARX_PROMPTS environment variable or specify a prompt file."
        )
    p = find_most_recent_prompt(prompts_dir)
    if not p:
        raise PromptError(f"No prompt files found in {prompts_dir}")
    return p


def _build_data_source_label(data_file: Optional[str], data_json: Optional[str], stdin: Optional[str]) -> Optional[str]:
    """Human-readable label for where data came from."""
    parts = []
    if data_file:
        parts.append(data_file)
    if data_json:
        parts.append("--data-json")
    if stdin:
        parts.append("stdin")
    return " + ".join(parts) if parts else None


def _do_prompt_impl(
    prompt_file: Optional[str],
    data_file: Optional[str],
    data_json: Optional[str],
    history: bool,
    output_file: Optional[str],
    dry_run: bool,
    verbose: bool,
) -> None:
    """Implementation of prompt do command."""
    prompts_dir = get_prompts_dir()
    prompt_path = _resolve_prompt_path(prompt_file, prompts_dir)

    if not prompt_path.exists():
        raise PromptError(f"Prompt file not found: {prompt_path}")

    # Build data context via render.build_context (file < --data-json < stdin)
    stdin_data = read_stdin_if_available()
    try:
        data = build_context(data_json=data_json, data_file=data_file, stdin_json=stdin_data)
    except ValueError as exc:
        raise PromptError(str(exc)) from exc

    data_source = _build_data_source_label(data_file, data_json, stdin_data)

    # Dry run
    if dry_run:
        _print_dry_run(prompt_path, data_source, data, output_file, history)
        return

    if verbose:
        click.secho(f"Executing prompt: {prompt_path}", fg="cyan")
        if data_source:
            click.secho(f"With data from: {data_source}", fg="cyan")

    # Render template at the "do" phase
    try:
        _fm, rendered = render_file(prompt_path, data, phase="do")
    except Exception as exc:
        raise PromptError(f"Render error: {exc}") from exc

    output_content = rendered

    # Write output
    _write_output(output_content, output_file, verbose)

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


def _print_dry_run(
    prompt_path: Path,
    data_source: Optional[str],
    data: dict,
    output_file: Optional[str],
    history: bool,
) -> None:
    """Print dry-run summary."""
    prompt_content = prompt_path.read_text(encoding="utf-8")
    click.secho("=== Dry Run ===", fg="cyan", bold=True)
    click.echo(f"Prompt file: {prompt_path}")
    click.echo(f"Data source: {data_source or 'none'}")
    if data:
        click.echo(f"Data keys: {list(data.keys())}")
    click.echo(f"Output: {output_file or 'stdout'}")
    click.echo(f"History: {'enabled' if history else 'disabled'}")
    click.echo()
    click.secho("=== Prompt Content (first 500 chars) ===", fg="cyan")
    click.echo(prompt_content[:500] + ("..." if len(prompt_content) > 500 else ""))
    if data:
        click.echo()
        click.secho("=== Data Preview ===", fg="cyan")
        click.echo(json.dumps(data, indent=2)[:500])


def _write_output(content: str, output_file: Optional[str], verbose: bool) -> None:
    """Write rendered content to file or stdout."""
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        if verbose:
            click.secho(f"Output written to: {output_path}", fg="green")
    else:
        click.echo(content)


@prompt.command("new")
@click.argument("template", required=False)
@click.argument("prompt_text", required=False)
@click.option("-D", "--data", "data_json",
              help="Inline JSON context merged with template data")
@click.option("-n", "--name", "short_name",
              help="Base name for the output file (default: derived from PROMPT_TEXT)")
@click.option("--subdir",
              help="Subdirectory under ARX_WORK_DOCS for output (overrides template front-matter)")
@click.option("--dry-run", is_flag=True,
              help="Show what would be written without creating any file")
@click.option("-v", "--verbose", is_flag=True,
              help="Show detailed output")
def new_prompt(
    template: Optional[str],
    prompt_text: Optional[str],
    data_json: Optional[str],
    short_name: Optional[str],
    subdir: Optional[str],
    dry_run: bool,
    verbose: bool,
):
    """Create a new prompt file, optionally from a template.

    TEMPLATE is a template name (looked up in \b$ARX_AGENT_TOOLS/templates/ and
    \b$AGENTRX_SOURCE/templates/) or a direct file path.  When omitted the
    command falls back to writing PROMPT_TEXT as a plain file.

    PROMPT_TEXT is the user's command/intent text.  It is always available
    inside the template as \b[[prompt]] and sets the output file's short name.

    Template front-matter fields recognised by this command:

    \b
      subdir:      Output subdirectory under ARX_WORK_DOCS (default: vibes)
      short_name:  Base filename (default: derived from prompt text)
      script:      Path to a script that augments context — receives current
                   JSON on stdin, must emit a JSON object on stdout.

    Examples:

    \b
        # Plain prompt file (no template)
        arx prompt new "Implement user auth"

    \b
        # From template by name
        arx prompt new vibes "Refactor the payment module"

    \b
        # From template file with inline data
        arx prompt new ./templates/delta.md "Fix the cache bug" --data '{"ticket":"ENG-42"}'

    \b
        # Preview without writing
        arx prompt new vibes "Debug login" --dry-run
    """
    try:
        _new_prompt_impl(
            template=template,
            prompt_text=prompt_text,
            data_json=data_json,
            short_name=short_name,
            subdir_override=subdir,
            dry_run=dry_run,
            verbose=verbose,
        )
    except PromptError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# prompt new — helpers
# ---------------------------------------------------------------------------

_DEFAULT_SUBDIR = "vibes"
_DEFAULT_TEMPLATES_SUBDIR = "templates"


def _template_search_dirs() -> List[Path]:
    """Ordered list of directories to search for named templates."""
    dirs: List[Path] = []
    agent_tools = os.environ.get("ARX_AGENT_TOOLS")
    if agent_tools:
        dirs.append(Path(agent_tools) / _DEFAULT_TEMPLATES_SUBDIR)
    agentrx_src = os.environ.get("AGENTRX_SOURCE")
    if agentrx_src:
        dirs.append(Path(agentrx_src) / "templates")
    return dirs


def _find_template(name_or_path: str) -> Optional[Path]:
    """Resolve a template name or path to an existing file.

    Resolution order:
      1. Direct path (as-is, then with .md suffix)
      2. $ARX_AGENT_TOOLS/templates/{name}[.md]
      3. $AGENTRX_SOURCE/templates/{name}[.md]
    """
    p = Path(name_or_path)
    if p.exists():
        return p
    if p.suffix == "" and p.with_suffix(".md").exists():
        return p.with_suffix(".md")

    for search_dir in _template_search_dirs():
        if not search_dir.exists():
            continue
        for candidate in (search_dir / name_or_path, search_dir / f"{name_or_path}.md"):
            if candidate.exists():
                return candidate
    return None


def _run_context_script(script: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Run *script*, pass *context* as JSON on stdin, merge JSON stdout into context.

    The script must:
      - Accept current context JSON on stdin
      - Print a JSON object on stdout (merged with highest priority)
      - Exit 0 on success

    Raises PromptError on non-zero exit or non-JSON output.
    """
    try:
        proc = subprocess.run(
            [script],
            input=json.dumps(context),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        raise PromptError(f"Context script not found: {script}")
    except subprocess.TimeoutExpired:
        raise PromptError(f"Context script timed out (30 s): {script}")

    if proc.returncode != 0:
        raise PromptError(
            f"Context script exited {proc.returncode}: {proc.stderr.strip()}"
        )
    try:
        return dict(json.loads(proc.stdout))
    except json.JSONDecodeError as exc:
        raise PromptError(
            f"Context script returned non-JSON output: {exc}"
        ) from exc


def _derive_short_name(text: str) -> str:
    """Derive a short name from the first three words of *text*."""
    words = text.split()[:3]
    return "_".join(
        "".join(c for c in w.lower() if c.isalnum())
        for w in words
    ) or "prompt"


def _build_output_path(work_docs: Path, subdir: str, short_name: str) -> Path:
    """Return the full output path (does not create dirs)."""
    ts = datetime.now().strftime("%y-%m-%d-%H")
    return work_docs / subdir / f"{short_name}_{ts}.md"


def _resolve_template_arg(
    template: Optional[str],
    prompt_text: Optional[str],
) -> tuple:
    """Return ``(template_path_or_None, prompt_text_or_None)``.

    If *template* doesn't resolve to a file and *prompt_text* is None,
    the first arg is treated as prompt text (backward-compat).
    Raises PromptError when *template* is given, doesn't resolve, and
    *prompt_text* is also given (ambiguous).
    """
    if not template:
        return None, prompt_text

    template_path = _find_template(template)
    if template_path is not None:
        return template_path, prompt_text

    # Didn't resolve — fall back or error
    if prompt_text is None:
        return None, template  # treat as plain prompt text
    raise PromptError(
        f"Template not found: '{template}'\n"
        f"Searched: {[str(d) for d in _template_search_dirs()]}"
    )


def _render_template_stage(
    template_path: Path,
    context: Dict[str, Any],
    verbose: bool,
) -> tuple:
    """Load + render template at the "new" phase, run optional context script.

    Returns ``(front_matter_dict_or_None, rendered_body)``.
    """
    from agentrx.render import render as _arx_render

    try:
        fm, body = render_file(template_path, context, phase="new")
    except Exception as exc:
        raise PromptError(f"Failed to read template {template_path}: {exc}") from exc

    script = (fm or {}).get("script")
    if script:
        if verbose:
            click.secho(f"Running context script: {script}", fg="cyan")
        script_out = _run_context_script(script, context)
        context.update(script_out)
        body = _arx_render(body, context, phase="new")

    return fm, body


def _new_prompt_impl(
    template: Optional[str],
    prompt_text: Optional[str],
    data_json: Optional[str],
    short_name: Optional[str],
    subdir_override: Optional[str],
    dry_run: bool,
    verbose: bool,
) -> None:
    """Implementation of ``arx prompt new``."""

    # Stage 1: resolve template / plain-text mode
    template_path, prompt_text = _resolve_template_arg(template, prompt_text)

    if not template_path and not prompt_text:
        raise PromptError("Provide a TEMPLATE and/or PROMPT_TEXT.")

    # Build initial context (--data JSON + stdin; prompt text added separately)
    stdin_data = read_stdin_if_available()
    try:
        context: Dict[str, Any] = build_context(data_json=data_json, stdin_json=stdin_data)
    except ValueError as exc:
        raise PromptError(str(exc)) from exc
    if prompt_text:
        context.setdefault("prompt", prompt_text)

    # Stage 2/3: template rendering + optional context script
    fm: Optional[Dict[str, Any]] = None
    if template_path:
        fm, body = _render_template_stage(template_path, context, verbose)
    else:
        body = prompt_text or ""

    # Resolve output metadata
    out_subdir = subdir_override or (fm or {}).get("subdir", _DEFAULT_SUBDIR)
    out_name = (
        short_name
        or (fm or {}).get("short_name")
        or _derive_short_name(
            prompt_text or (template_path.stem if template_path else "prompt")
        )
    )
    work_docs = Path(os.environ.get("ARX_WORK_DOCS", get_prompts_dir()))
    out_path = _build_output_path(work_docs, out_subdir, out_name)

    # Stage 4: dry-run preview
    if dry_run:
        _print_new_dry_run(template_path, out_path, out_subdir, out_name, context, body)
        return

    # Stage 5: write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    click.secho(f"Created: {out_path}", fg="green") if verbose else click.echo(str(out_path))


def _print_new_dry_run(
    template_path: Optional[Path],
    out_path: Path,
    out_subdir: str,
    out_name: str,
    context: Dict[str, Any],
    body: str,
) -> None:
    """Print dry-run summary for prompt new."""
    click.secho("=== Dry Run ===", fg="cyan", bold=True)
    click.echo(f"Template:  {template_path or '(none)'}")
    click.echo(f"Output:    {out_path}")
    click.echo(f"Subdir:    {out_subdir}")
    click.echo(f"Name:      {out_name}")
    if context:
        click.echo(f"Context keys: {sorted(context.keys())}")
    click.echo()
    click.secho("=== Rendered body (first 600 chars) ===", fg="cyan")
    click.echo(body[:600] + ("..." if len(body) > 600 else ""))


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
