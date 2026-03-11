"""``arx prompt`` — create, execute, and list prompt files.

Sub-commands:

- ``arx prompt new``  — create a prompt from a template or plain text.
- ``arx prompt do``   — execute (render) an existing prompt file.
- ``arx prompt list`` — show recent prompt files with relative age.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import click
import yaml

from ..render import build_context, render, render_file, strip_front_matter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _working_dir() -> Path:
    """Return the working-docs directory (``$ARX_WORKING``), falling back to cwd."""
    return Path(os.environ.get("ARX_WORKING", "."))


def _templates_dir() -> Path:
    """Return the templates directory (``$ARX_TEMPLATES``)."""
    d = os.environ.get("ARX_TEMPLATES")
    if not d:
        src = os.environ.get("AGENTRX_SOURCE")
        if src:
            d = str(Path(src) / "_arx_templates")
    if not d:
        raise click.ClickException(
            "Cannot locate templates. Set ARX_TEMPLATES or AGENTRX_SOURCE."
        )
    return Path(d)


def _resolve_template(name: str) -> Path:
    """Find a template by subdirectory name under ``$ARX_TEMPLATES``.

    Searches for ``<name>.md``, ``<name>.yaml``, or a directory ``<name>/``
    containing an index file.
    """
    base = _templates_dir()

    # Direct file matches
    for ext in (".md", ".yaml", ".yml"):
        candidate = base / f"{name}{ext}"
        if candidate.is_file():
            return candidate

    # Subdirectory with index
    subdir = base / name
    if subdir.is_dir():
        for idx in ("index.md", "index.yaml", f"{name}.md", f"{name}.yaml"):
            candidate = subdir / idx
            if candidate.is_file():
                return candidate

    raise click.ClickException(f"Template not found: {name} (searched {base})")


def _output_path(short_name: str, subdir: str = "vibes") -> Path:
    """Build the output path: ``$ARX_WORKING/<subdir>/<short_name>_<timestamp>.md``."""
    ts = datetime.now().strftime("%y%m%d_%H%M")
    working = _working_dir()
    dest = working / subdir
    dest.mkdir(parents=True, exist_ok=True)
    return dest / f"{short_name}_{ts}.md"


def _run_context_script(script: str, data: dict) -> dict:
    """Execute a front-matter ``script:`` enrichment command.

    The script receives the current context as JSON on stdin and is expected
    to emit augmented JSON on stdout.
    """
    import json

    try:
        result = subprocess.run(
            script,
            shell=True,
            input=json.dumps(data),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            data.update(json.loads(result.stdout))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        click.echo(f"Warning: context script failed: {exc}", err=True)
    return data


def _relative_age(ts: float) -> str:
    """Human-friendly relative age string."""
    delta = time.time() - ts
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{int(delta / 60)}m ago"
    if delta < 86400:
        return f"{int(delta / 3600)}h ago"
    return f"{int(delta / 86400)}d ago"


# ---------------------------------------------------------------------------
# Click group
# ---------------------------------------------------------------------------


@click.group("prompt")
def prompt():
    """Work with prompt files — create, execute, and list."""


# ---------------------------------------------------------------------------
# prompt new
# ---------------------------------------------------------------------------


@prompt.command("new")
@click.argument("template", required=False)
@click.argument("text", required=False)
@click.option("--data", "data_json", default=None, help="Inline JSON data context.")
@click.option("--data-file", default=None, type=click.Path(exists=True), help="YAML/JSON data file.")
@click.option("-o", "--output", "output_path", default=None, type=click.Path(), help="Output file path (overrides default).")
def prompt_new(template, text, data_json, data_file, output_path):
    """Create a new prompt file from a template or plain text.

    TEMPLATE is a template name resolved from $ARX_TEMPLATES (e.g. arch-facet).
    TEXT is optional plain text to use as the prompt body (instead of a template).
    """
    ctx = build_context(data_json=data_json, data_file=data_file, stdin_json=True)

    if template:
        # Resolve and render from template
        tmpl_path = _resolve_template(template)
        fm, body = render_file(tmpl_path, ctx, phase="new")

        # Run context script if declared in front matter
        script = fm.get("script")
        if script:
            ctx = _run_context_script(script, ctx)
            body = render(body, ctx, phase="new")

        short_name = fm.get("short_name", template)
        subdir = fm.get("subdir", "vibes")
    elif text:
        # Plain text prompt
        fm = {}
        body = text
        short_name = "prompt"
        subdir = "vibes"
    else:
        raise click.ClickException("Provide a TEMPLATE name or TEXT content.")

    # Determine output location
    if output_path:
        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
    else:
        dest = _output_path(short_name, subdir)

    # Write front matter + body
    out_parts = []
    if fm:
        # Rewrite front matter as a prompt (not template)
        out_fm = {k: v for k, v in fm.items() if k not in ("script",)}
        out_fm["arx"] = "prompt"
        out_parts.append("---\n")
        out_parts.append(yaml.dump(out_fm, default_flow_style=False, sort_keys=False))
        out_parts.append("---\n")
    out_parts.append(body)

    dest.write_text("".join(out_parts), encoding="utf-8")
    click.echo(f"Created {dest}")


# ---------------------------------------------------------------------------
# prompt do
# ---------------------------------------------------------------------------


@prompt.command("do")
@click.argument("prompt_file", type=click.Path(exists=True))
@click.option("--data", "data_json", default=None, help="Inline JSON data context.")
@click.option("--data-file", default=None, type=click.Path(exists=True), help="YAML/JSON data file.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview rendered output without side effects.")
@click.option("-o", "--output", "output_path", default=None, type=click.Path(), help="Write output to file instead of stdout.")
def prompt_do(prompt_file, data_json, data_file, dry_run, output_path):
    """Execute (render) an existing prompt file.

    Renders the prompt with the ``:do`` phase, merging data from
    data-file < --data JSON < stdin.
    """
    ctx = build_context(data_json=data_json, data_file=data_file, stdin_json=True)
    fm, body = render_file(prompt_file, ctx, phase="do")

    # Run context script if declared
    script = fm.get("script")
    if script:
        ctx = _run_context_script(script, ctx)
        body = render(body, ctx, phase="do")

    if dry_run:
        click.echo("--- DRY RUN ---")
        click.echo(body)
        return

    if output_path:
        Path(output_path).write_text(body, encoding="utf-8")
        click.echo(f"Wrote {output_path}")
    else:
        click.echo(body)


# ---------------------------------------------------------------------------
# prompt list
# ---------------------------------------------------------------------------


@prompt.command("list")
@click.option("-n", "--limit", default=20, help="Max number of files to show.")
@click.option("--dir", "search_dir", default=None, type=click.Path(exists=True), help="Directory to search (default: $ARX_WORKING/vibes).")
def prompt_list(limit, search_dir):
    """Show recent prompt files sorted by modification time."""
    if search_dir:
        base = Path(search_dir)
    else:
        base = _working_dir() / "vibes"

    if not base.is_dir():
        click.echo(f"No prompts directory found at {base}")
        return

    files = sorted(
        (f for f in base.iterdir() if f.is_file() and f.suffix in (".md", ".yaml", ".yml")),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    if not files:
        click.echo("No prompt files found.")
        return

    for f in files[:limit]:
        age = _relative_age(f.stat().st_mtime)
        click.echo(f"  {age:>10}  {f.name}")
