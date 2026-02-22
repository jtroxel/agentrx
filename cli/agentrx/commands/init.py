"""AgentRx init command - Initialize project structure.

Implements `arx init` per the CLI README specification.

Environment variables (written to .env, read as defaults):
  ARX_PROJECT_ROOT   Root directory of the host project (always = CWD / target_dir).
  ARX_AGENT_TOOLS    Agent assets directory (default: $ARX_PROJECT_ROOT/_agents/).
  ARX_TARGET_PROJ    Target project directory (default: $ARX_PROJECT_ROOT/_project/).
  ARX_PROJ_DOCS      Project documentation directory (default: $ARX_TARGET_PROJ/docs).
  ARX_WORK_DOCS      Working docs directory — vibes, deltas, history (default: $ARX_PROJ_DOCS/agentrx).
  AGENTRX_SOURCE     Source of AgentRx assets used with --link-arx or copy.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import click

from agentrx.render import render as _arx_render


# ---------------------------------------------------------------------------
# Inline bootstrap file templates
# ---------------------------------------------------------------------------

AGENTS_MD_TEMPLATE = """\
# AGENTS Guidance

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## IMPORTANT: Coding Agents
> Follow the instructions precisely. If it wasn't specified, don't do it.

## Startup Context
When starting a chat conversation or session for this project, read all the files indicated below.
Do NOT read anything else until directed in prompts.

### PARALLEL READ the following ONLY:
#### AgentRx Instructions
- README.md # to understand the basics of the project and directory structure
- _agents/commands/agentrx/*.md # agentrx commands
- _agents/skills/agentrx/*.md  # agentrx skills

#### Project Context
Project-specific commands, skills, and context documents follow similar naming conventions.
Add those context documents into your context when prompted by the user.

## IMPORTANT: List What Files You've Read on Startup
At startup, after reading the files indicated above, print a list of the files read into the chat terminal.
"""

CLAUDE_MD_TEMPLATE = """\
# Claude Code Guidance

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. IMPORTANT: Start with AGENTS.md
When loading memory, prioritize reading AGENTS.md first.

## 2. Please Summarize What You've Read
At startup provide a list of the files read in the chat history.

## Context Documents
For comprehensive project context, see [CONTEXT_DOCUMENTS_INDEX.md](./CONTEXT_DOCUMENTS_INDEX.md).
"""

CHAT_START_TEMPLATE = """\
---
arx: config
name: chat-start
description: Bootstrap instructions for coding agents starting new sessions
version: 1
---

# AgentRx Bootstrap Instructions

> **For Coding Agents**: Follow these instructions precisely at session start.

## Step 1: Load Core Context

Read these files **in parallel** to establish AgentRx capabilities:

### Commands (treat as native slash commands)
```
_agents/commands/agentrx/*.md
```

### Skills
```
_agents/skills/agentrx/*.md
```

## Step 2: Confirm Bootstrap

After loading, output a confirmation listing available commands and skills.

## Important Notes

1. **Commands as native** - Treat `_agents/commands/` items as native CLI slash commands
2. **Project context** - Load project-specific files when user references them
3. **ARX templates** - Files with `arx: template` front matter are renderable templates
4. **Follow precisely** - If something wasn't specified, don't do it
"""

# ---------------------------------------------------------------------------
# Environment variable names (per README)
# ---------------------------------------------------------------------------

ENV_PROJECT_ROOT = "ARX_PROJECT_ROOT"
ENV_AGENT_TOOLS  = "ARX_AGENT_TOOLS"
ENV_TARGET_PROJ  = "ARX_TARGET_PROJ"
ENV_PROJ_DOCS    = "ARX_PROJ_DOCS"
ENV_WORK_DOCS    = "ARX_WORK_DOCS"

# Default relative paths (relative to project root)
DEFAULT_AGENTS_DIR  = "_agents"
DEFAULT_PROJECT_DIR = "_project"
DEFAULT_PROJ_DOCS   = "_project/docs"
DEFAULT_WORK_DOCS   = "_project/docs/agentrx"

# Sub-category names under the agent-tools directory
AGENT_SUBDIRS = ["commands", "skills", "scripts", "hooks", "agents"]

# Name of the agents-tools template subdir inside templates/
# This subtree is routed to ARX_AGENT_TOOLS instead of the project root.
AGENTS_TEMPLATE_SUBDIR = "_arx_agent_tools.arx"


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class InitError(Exception):
    """Raised on unrecoverable init errors."""


# ---------------------------------------------------------------------------
# Low-level helpers (pure FS, no dry-run logic here)
# ---------------------------------------------------------------------------

def _mkdir(path: Path, verbose: bool = False) -> bool:
    """Create *path* (and parents) if it does not already exist."""
    if path.exists():
        return False
    path.mkdir(parents=True, exist_ok=True)
    if verbose:
        click.echo(f"    mkdir  {path}")
    return True


def _write_file(path: Path, content: str, skip_existing: bool = True,
                verbose: bool = False) -> bool:
    """Write *content* to *path*; skip if exists and skip_existing=True."""
    if skip_existing and path.exists():
        if verbose:
            click.secho(f"    [--]   {path.name} (exists, skipped)", fg="yellow")
        return False
    path.write_text(content, encoding="utf-8")
    if verbose:
        click.echo(f"    [OK]   {path.name}")
    return True


def _make_symlink(link: Path, target: Path, verbose: bool = False) -> None:
    """Create *link* -> *target* symlink, removing a prior entry if needed."""
    if link.exists() and link.is_dir() and not link.is_symlink():
        shutil.rmtree(link)
    elif link.exists() or link.is_symlink():
        link.unlink()
    try:
        rel = os.path.relpath(target, link.parent)
    except ValueError:
        rel = str(target)
    link.symlink_to(rel)
    if verbose:
        click.echo(f"    [OK]   symlink {link.name} -> {rel}")


def _copy_tree_safe(src: Path, dst: Path, verbose: bool = False) -> tuple[int, int]:
    """Copy *src* tree into *dst*, skipping files that already exist.
    Returns (files_copied, files_skipped).
    """
    copied = skipped = 0
    for item in sorted(src.rglob("*")):
        if not item.is_file():
            continue
        rel = item.relative_to(src)
        dst_file = dst / rel
        if dst_file.exists():
            skipped += 1
            if verbose:
                click.secho(f"    [--]   {rel} (skipped)", fg="yellow")
        else:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst_file)
            copied += 1
            if verbose:
                click.echo(f"    [OK]   {rel}")
    return copied, skipped


def _parse_env_lines(lines: list[str]) -> dict[str, int]:
    """Return mapping of env key -> line index for non-comment KEY=VAL lines."""
    result: dict[str, int] = {}
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            result[stripped.split("=", 1)[0].strip()] = idx
    return result


def _update_env_file(env_path: Path, values: Dict[str, str],
                     verbose: bool = False) -> None:
    """Merge *values* into *env_path* in-place.
    Existing keys are updated; new keys are appended; unrelated lines preserved.
    """
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    key_to_line = _parse_env_lines(lines)
    updated = list(lines)
    to_append: list[str] = []

    for k, v in values.items():
        if k in key_to_line:
            updated[key_to_line[k]] = f"{k}={v}"
        else:
            to_append.append(f"{k}={v}")

    if to_append:
        if updated and updated[-1].strip():
            updated.append("")
        updated.extend(to_append)

    env_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
    if verbose:
        click.secho(f"  [OK] .env  {env_path}", fg="green")


def _load_yaml(path: Optional[str]) -> Dict[str, Any]:
    """Load YAML from *path* (or '-' for stdin).  Returns {} if nothing provided."""
    if not path:
        return {}
    try:
        import yaml  # type: ignore[import]
    except ModuleNotFoundError as exc:
        raise InitError(
            "PyYAML is required for --data.  Install: pip install PyYAML"
        ) from exc
    if path == "-":
        raw = sys.stdin.read()
    else:
        p = Path(path)
        if not p.exists():
            raise InitError(f"--data file not found: {path}")
        raw = p.read_text(encoding="utf-8")
    return dict(yaml.safe_load(raw) or {})


def _safe_mustache_render(text: str, context: Dict[str, Any]) -> str:
    """Render ARX variable tags and env-var expansions in *text*."""
    return _arx_render(text, context)


def _find_templates_dir(agentrx_source: Optional[str]) -> Optional[Path]:
    """Locate the templates/ directory (prefer from AGENTRX_SOURCE, then walk up)."""
    if agentrx_source:
        cand = Path(agentrx_source) / "templates"
        if cand.is_dir():
            return cand
    for parent in Path(__file__).resolve().parents:
        cand = parent / "templates"
        if cand.is_dir():
            return cand
    return None


# ---------------------------------------------------------------------------
# Dry-run–aware runner
# ---------------------------------------------------------------------------

_JUNK_FILES = frozenset({".DS_Store", "Thumbs.db", ".AppleDouble"})
_JUNK_SUFFIXES = frozenset({".pyc", ".pyo"})
_JUNK_DIRS = frozenset({".git", "__pycache__", ".mypy_cache", ".ruff_cache"})


def _is_junk(rel: Path) -> bool:
    """Return True for OS/tool artefacts that should never be copied."""
    return (
        rel.name in _JUNK_FILES
        or rel.suffix in _JUNK_SUFFIXES
        or any(p in _JUNK_DIRS for p in rel.parts)
    )


def _strip_arx_marker(name: str) -> str:
    """Strip the ``.ARX.`` or ``.arx.`` marker from a template filename.

    e.g. ``AGENTS.ARX.md`` → ``AGENTS.md``
         ``context.arx.yaml`` → ``context.yaml``
    """
    return name.replace(".ARX.", ".").replace(".arx.", ".")


class _Runner:
    """Wraps FS actions; in dry-run mode prints concise planned actions."""

    def __init__(self, dry_run: bool, verbose: bool) -> None:
        self.dry_run = dry_run
        self.verbose = verbose
        self._seen_dirs: set[Path] = set()   # dedup mkdir announcements

    def mkdir(self, path: Path) -> None:
        if self.dry_run:
            resolved = path.resolve()
            if resolved in self._seen_dirs:
                return
            self._seen_dirs.add(resolved)
            # Show path relative to CWD when possible, else absolute
            try:
                display = path.relative_to(Path.cwd())
            except ValueError:
                display = path
            if path.exists():
                click.secho(f"  [skip] {display}/  (exists)", fg="yellow")
            else:
                click.echo(f"  [make] {display}/")
        else:
            _mkdir(path, self.verbose)

    def _write_copy_line(self, filename: str, from_dir: str, to_dir: str) -> None:
        """Print the [copy] dry-run line in 'from … to …' format.

        Keeps output to one line when it fits; wraps from/to onto a second
        indented line when the combined text would exceed 80 columns.
        """
        from_triv = from_dir in (".", "")
        to_triv = to_dir in (".", "")
        if from_triv and to_triv:
            click.echo(f"  [copy] {filename}")
            return
        if from_triv:
            suffix = f"  to {to_dir}/"
        elif to_triv:
            suffix = f"  from {from_dir}/"
        else:
            suffix = f"  from {from_dir}/  to {to_dir}/"
        line = f"  [copy] {filename}{suffix}"
        if len(line) <= 120:
            click.echo(line)
        else:
            click.echo(f"  [copy] {filename}")
            if not from_triv:
                click.echo(f"         from {from_dir}/")
            if not to_triv:
                click.echo(f"           to {to_dir}/")

    def write(self, path: Path, content: str, skip_existing: bool = True,
              label: Optional[str] = None, src: Optional[Path] = None) -> None:
        if self.dry_run:
            name = label or path.name
            if skip_existing and path.exists():
                click.secho(f"  [skip] {name}  (exists)", fg="yellow")
            elif src is not None:
                from_dir = str(Path(src).parent)
                try:
                    to_dir = str(path.parent.relative_to(Path.cwd()))
                except ValueError:
                    to_dir = str(path.parent)
                self._write_copy_line(Path(src).name, from_dir, to_dir)
            else:
                click.echo(f"  [write] {name}")
        else:
            _write_file(path, content, skip_existing=skip_existing, verbose=self.verbose)

    def symlink(self, link: Path, target: Path) -> None:
        if self.dry_run:
            try:
                link_disp = link.relative_to(Path.cwd())
            except ValueError:
                link_disp = link
            # Show target as AGENTRX_SOURCE-relative when possible
            agentrx_src = os.environ.get("AGENTRX_SOURCE", "")
            if agentrx_src:
                try:
                    target_disp: Path | str = Path("AGENTRX_SOURCE") / target.relative_to(agentrx_src)
                except ValueError:
                    target_disp = target
            else:
                target_disp = target
            line = f"  [link]  {target_disp}  ->  {link_disp}"
            if len(line) <= 120:
                click.echo(line)
            else:
                click.echo(f"  [link]  {target_disp}")
                click.echo(f"       ->  {link_disp}")
        else:
            _make_symlink(link, target, self.verbose)

    def copy_tree(self, src: Path, dst: Path) -> tuple[int, int]:
        if self.dry_run:
            cnt = sum(1 for f in src.rglob("*") if f.is_file() and not _is_junk(f.relative_to(src)))
            try:
                dst_disp = dst.relative_to(Path.cwd())
            except ValueError:
                dst_disp = dst
            click.echo(f"  [copy]  {src}/  ->  {dst_disp}/  ({cnt} files)")
            return cnt, 0
        return _copy_tree_safe(src, dst, self.verbose)

    def update_env(self, env_path: Path, values: Dict[str, str]) -> None:
        if self.dry_run:
            click.echo(f"  {env_path}")
            for k, v in values.items():
                click.echo(f"    {k}={v}")
        else:
            _update_env_file(env_path, values, self.verbose)


# ---------------------------------------------------------------------------
# Directory-setup helpers
# ---------------------------------------------------------------------------

def _link_one_subdir(sub: str, agents_path: Path, src_agents: Path,
                     runner: _Runner) -> None:
    """Create the parent subdir and symlink its agentrx/ leaf."""
    runner.mkdir(agents_path / sub)
    src_leaf = src_agents / sub / "agentrx"
    dst_leaf = agents_path / sub / "agentrx"
    if not src_leaf.exists():
        click.secho(f"    [skip] source {src_leaf} not found", fg="yellow")
        return
    if dst_leaf.exists() and not dst_leaf.is_symlink():
        raise InitError(f"Cannot symlink: {dst_leaf} already exists as a real path.")
    runner.symlink(dst_leaf, src_leaf)


def _copy_one_subdir(sub: str, agents_path: Path, src_agents: Path,
                     runner: _Runner) -> None:
    """Copy agentrx/ assets for one category subdir."""
    runner.mkdir(agents_path / sub / "agentrx")
    src_leaf = src_agents / sub / "agentrx"
    dst_leaf = agents_path / sub / "agentrx"
    if not src_leaf.is_dir():
        return
    copied, skipped = runner.copy_tree(src_leaf, dst_leaf)
    if runner.dry_run:
        return
    if copied:
        click.secho(f"    [OK] {sub}/agentrx: {copied} files", fg="green")
    if skipped:
        click.secho(f"    [--] {sub}/agentrx: {skipped} skipped", fg="yellow")


def _setup_agent_tools_link(agents_path: Path, agentrx_source: str,
                            runner: _Runner) -> None:
    """Link mode: create parent subdirs + symlink each agentrx/ leaf.

    Per README: symlinks target templates/AGENTS_TEMPLATE_SUBDIR/**/agentrx/,
    not the live _agents/ tree.
    """
    templates_dir = _find_templates_dir(agentrx_source)
    if not templates_dir:
        raise InitError(f"Cannot find templates/ dir in AGENTRX_SOURCE: {agentrx_source}")
    src_agents = templates_dir / AGENTS_TEMPLATE_SUBDIR
    if not src_agents.is_dir():
        raise InitError(
            f"AGENTRX_SOURCE templates has no {AGENTS_TEMPLATE_SUBDIR}/ dir: {templates_dir}"
        )
    click.secho("  Creating deep symlinks to AgentRx assets...", fg="cyan")
    for sub in AGENT_SUBDIRS:
        _link_one_subdir(sub, agents_path, src_agents, runner)


def _setup_agent_tools_copy(agents_path: Path, runner: _Runner) -> None:
    """Copy mode: create standard category skeleton under agents_path.

    Per README: file contents come from templates/AGENTS_TEMPLATE_SUBDIR/ via
    _copy_templates routing.  Here we only ensure the skeleton dirs exist.
    """
    for sub in AGENT_SUBDIRS:
        runner.mkdir(agents_path / sub)


def _setup_agent_tools(agents_path: Path, link_arx: bool,
                       agentrx_source: Optional[str], runner: _Runner) -> None:
    """Create or leave the agent-tools directory tree.

    EXISTS   -> leave untouched (per README spec).
    MISSING + link mode  -> parent subdirs only; symlink each agentrx/ leaf.
    MISSING + copy mode  -> full skeleton; copy agentrx/ files from source.
    """
    already_exists = agents_path.exists()
    runner.mkdir(agents_path)
    if already_exists:
        return
    if link_arx:
        if not agentrx_source:
            raise InitError("--link-arx requires --agentrx-source or the AGENTRX_SOURCE env var.")
        _setup_agent_tools_link(agents_path, agentrx_source, runner)
    else:
        _setup_agent_tools_copy(agents_path, runner)


def _setup_project_dir(proj_path: Path, runner: _Runner) -> None:
    """Create target project directory (and src/) if absent; leave alone if exists."""
    already_exists = proj_path.exists()
    runner.mkdir(proj_path)
    if not already_exists:
        runner.mkdir(proj_path / "src")


def _setup_docs_dir(docs_path: Path, runner: _Runner) -> None:
    """Create docs output directory (with artifact subdirs) if absent."""
    already_exists = docs_path.exists()
    runner.mkdir(docs_path)
    if not already_exists:
        for sub in ("deltas", "vibes", "history"):
            runner.mkdir(docs_path / sub)


def _write_template_item(item: Path, dst: Path, context: Dict[str, Any],
                         runner: _Runner, label: Optional[str] = None,
                         src_display: Optional[Path] = None) -> None:
    """Write a single template file (text or binary) to *dst*."""
    try:
        text = _safe_mustache_render(item.read_text(encoding="utf-8"), context)
        runner.write(dst, text, skip_existing=True, label=label, src=src_display or item)
    except UnicodeDecodeError:
        src = src_display or item
        if runner.dry_run:
            from_dir = str(Path(src).parent)
            try:
                to_dir = str(dst.parent.relative_to(Path.cwd()))
            except ValueError:
                to_dir = str(dst.parent)
            runner._write_copy_line(Path(src).name + "  (binary)", from_dir, to_dir)
        else:
            shutil.copy2(item, dst)
            if runner.verbose:
                click.echo(f"    [OK] binary {dst}")


def _route_template(rel: Path, root: Path, agents_path: Path,
                    agents_subdir: str) -> tuple[Path, Path]:
    """Return (dst_base, rel_in_dst) for a template file."""
    if rel.parts[0] == agents_subdir:
        return agents_path, rel.relative_to(agents_subdir)
    return root, rel


def _templates_display(templates_dir: Path, agentrx_source: Optional[str]) -> Path:
    """Return a short display path for the templates directory header."""
    if agentrx_source:
        try:
            return templates_dir.relative_to(Path(agentrx_source))
        except ValueError:
            pass
    try:
        return templates_dir.relative_to(Path.cwd())
    except ValueError:
        return templates_dir


def _copy_templates(root: Path, agents_path: Path,
                    agentrx_source: Optional[str],
                    context: Dict[str, Any], runner: _Runner,
                    link_arx: bool = False) -> None:
    """Process templates/ and route results to the correct destination.

    Templates under AGENTS_TEMPLATE_SUBDIR/ are routed to *agents_path*
    (populating ARX_AGENT_TOOLS per README spec).  In link mode that subtree
    is skipped because _setup_agent_tools_link already created symlinks for it.
    All other templates are routed to *root*.
    .git and OS junk paths are skipped unconditionally.
    """
    templates_dir = _find_templates_dir(agentrx_source)
    if not templates_dir:
        return

    tmpl_disp = _templates_display(templates_dir, agentrx_source)

    click.echo()
    click.secho(f"Templates  ({tmpl_disp}):", fg="cyan")
    for item in sorted(templates_dir.rglob("*")):
        if item.is_dir():
            continue
        rel = item.relative_to(templates_dir)
        if _is_junk(rel):
            continue
        in_agents_subdir = rel.parts[0] == AGENTS_TEMPLATE_SUBDIR
        # In link mode, skip the agents subtree — it is already symlinked
        if link_arx and in_agents_subdir:
            continue
        # Root-level files must carry the .ARX. / .arx. marker to be installed;
        # bare files (e.g. README.md) are templates-dir documentation only.
        if not in_agents_subdir and ".ARX." not in rel.name and ".arx." not in rel.name:
            continue
        dst_base, rel_in_dst = _route_template(rel, root, agents_path, AGENTS_TEMPLATE_SUBDIR)
        # Strip .ARX. / .arx. marker from root-level template destination filenames
        if not in_agents_subdir:
            stripped_name = _strip_arx_marker(rel_in_dst.name)
            if stripped_name != rel_in_dst.name:
                rel_in_dst = rel_in_dst.parent / stripped_name
        dst = dst_base / rel_in_dst
        if dst.parent != dst_base and not dst.parent.exists():
            runner.mkdir(dst.parent)
        # src_display uses templates/<rel> so dry-run shows "from templates/..."
        _write_template_item(item, dst, context, runner,
                             label=str(rel_in_dst),
                             src_display=Path("templates") / rel)


# ---------------------------------------------------------------------------
# Click command
# ---------------------------------------------------------------------------

@click.command()
@click.argument("target_dir", default=".", type=click.Path())
@click.option("-l", "--link-arx", "link_arx", is_flag=True,
              help="Symlink agentrx/ assets from AGENTRX_SOURCE instead of copying.")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed output.")
@click.option("--dry-run", "dry_run", is_flag=True,
              help="Print planned actions without making any changes.")
@click.option("--agentrx-source", envvar="AGENTRX_SOURCE",
              type=click.Path(exists=True),
              help="AgentRx source directory (required with --link-arx; optional for copy).")
@click.option("--agents-dir", "agents_dir", envvar=ENV_AGENT_TOOLS, type=str,
              help=f"Agent-tools dir.  Env: {ENV_AGENT_TOOLS}  [default: {DEFAULT_AGENTS_DIR}]")
@click.option("--target-proj", "target_proj", envvar=ENV_TARGET_PROJ, type=str,
              help=f"Target project dir.  Env: {ENV_TARGET_PROJ}  [default: {DEFAULT_PROJECT_DIR}]")
@click.option("--proj-docs", "proj_docs", envvar=ENV_PROJ_DOCS, type=str,
              help=f"Project docs dir.  Env: {ENV_PROJ_DOCS}  [default: {DEFAULT_PROJ_DOCS}]")
@click.option("--work-docs", "work_docs", envvar=ENV_WORK_DOCS, type=str,
              help=f"Working docs dir (vibes/deltas/history).  Env: {ENV_WORK_DOCS}  [default: {DEFAULT_WORK_DOCS}]")
@click.option("--data", "data_path", type=str,
              help="YAML file with template variables, or '-' for stdin.")
def init(
    target_dir: str,
    link_arx: bool,
    verbose: bool,
    dry_run: bool,
    agentrx_source: Optional[str],
    agents_dir: Optional[str],
    target_proj: Optional[str],
    proj_docs: Optional[str],
    work_docs: Optional[str],
    data_path: Optional[str],
) -> None:
    """Initialize an AgentRx project structure.

    \b
    TARGET_DIR  Project root to initialise (default: current directory).
                ARX_PROJECT_ROOT is always set to this path.

    \b
    Directory rules (per README):
      ARX_AGENT_TOOLS  exists -> left untouched.
      ARX_AGENT_TOOLS  missing, copy mode -> created with full agentrx/ skeleton.
                                             Files copied from AGENTRX_SOURCE if set.
      ARX_AGENT_TOOLS  missing, --link-arx -> parent subdirs created (no agentrx/ leaf).
                                             Each agentrx/ subdir symlinked to source.
      ARX_TARGET_PROJ  exists -> left untouched.
      ARX_TARGET_PROJ  missing -> created (with src/ inside).
      ARX_PROJ_DOCS    exists -> left untouched.
      ARX_PROJ_DOCS    missing -> created.
      ARX_WORK_DOCS    exists -> left untouched.
      ARX_WORK_DOCS    missing -> created (with deltas/, vibes/, history/).

    \b
    A .env is always written/updated in TARGET_DIR with the five ARX_* variables.
    Root-level *.ARX.* templates are installed (with .ARX. stripped) only if absent.
    CLAUDE.md and CHAT_START.md are written from built-in defaults only if absent.

    \b
    Examples:
      arx init
      arx init /path/to/project
      arx init --link-arx --agentrx-source ~/dev/agentrx-src
      arx init --agents-dir ~/dev/agentrx-src --target-proj ~/dev/myproj --dry-run
    """
    try:
        _run_init(
            target_dir=target_dir,
            link_arx=link_arx,
            verbose=verbose,
            dry_run=dry_run,
            agentrx_source=agentrx_source,
            agents_dir=agents_dir,
            target_proj=target_proj,
            proj_docs=proj_docs,
            work_docs=work_docs,
            data_path=data_path,
        )
    except InitError as exc:
        click.secho(f"\nError: {exc}", fg="red", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Resolve dirs (may be interactive)
# ---------------------------------------------------------------------------

def _resolve_dirs(
    root: Path,
    agents_dir: Optional[str],
    target_proj: Optional[str],
    proj_docs: Optional[str],
    work_docs: Optional[str],
    interactive: bool,
) -> tuple[Path, Path, Path, Path]:
    def _env(name: str, default: str) -> str:
        return os.environ.get(name, default)

    if interactive and sys.stdin.isatty():
        click.secho("Directory configuration (Enter to accept defaults)", fg="cyan")
        a = click.prompt(
            f"  {ENV_AGENT_TOOLS}",
            default=agents_dir or _env(ENV_AGENT_TOOLS, DEFAULT_AGENTS_DIR),
        )
        p = click.prompt(
            f"  {ENV_TARGET_PROJ}",
            default=target_proj or _env(ENV_TARGET_PROJ, DEFAULT_PROJECT_DIR),
        )
        pd_default = proj_docs or _env(ENV_PROJ_DOCS, f"{p}/docs")
        pd = click.prompt(f"  {ENV_PROJ_DOCS}", default=pd_default)
        wd_default = work_docs or _env(ENV_WORK_DOCS, f"{pd}/agentrx")
        wd = click.prompt(f"  {ENV_WORK_DOCS}", default=wd_default)
        click.echo()
    else:
        a  = agents_dir  or _env(ENV_AGENT_TOOLS, DEFAULT_AGENTS_DIR)
        p  = target_proj or _env(ENV_TARGET_PROJ,  DEFAULT_PROJECT_DIR)
        pd = proj_docs   or _env(ENV_PROJ_DOCS,    DEFAULT_PROJ_DOCS)
        wd = work_docs   or _env(ENV_WORK_DOCS,    DEFAULT_WORK_DOCS)

    def _abs(val: str, base: Path) -> Path:
        v = Path(val)
        return v if v.is_absolute() else base / v

    return _abs(a, root), _abs(p, root), _abs(pd, root), _abs(wd, root)


# ---------------------------------------------------------------------------
# Main implementation
# ---------------------------------------------------------------------------

def _run_init(
    target_dir: str,
    link_arx: bool,
    verbose: bool,
    dry_run: bool,
    agentrx_source: Optional[str],
    agents_dir: Optional[str],
    target_proj: Optional[str],
    proj_docs: Optional[str],
    work_docs: Optional[str],
    data_path: Optional[str],
) -> None:
    root = Path(target_dir).resolve()
    runner = _Runner(dry_run=dry_run, verbose=verbose)

    # ── header ────────────────────────────────────────────────────────────────
    click.echo()
    click.secho("AgentRx Project Initialization", fg="blue", bold=True)
    click.echo("=" * 44)
    click.echo(f"  {ENV_PROJECT_ROOT:20s} = {root}")
    click.echo(f"  Mode                 = {'link (--link-arx)' if link_arx else 'copy (default)'}")
    if agentrx_source:
        click.echo(f"  AGENTRX_SOURCE       = {agentrx_source}")
    if dry_run:
        click.secho("  ** DRY RUN – no changes will be made **", fg="yellow", bold=True)
    click.echo()

    # ── ensure root exists ────────────────────────────────────────────────────
    if not root.exists():
        runner.mkdir(root)

    # ── resolve directory paths (may prompt interactively) ────────────────────
    interactive = (agents_dir is None and target_proj is None
                   and proj_docs is None and work_docs is None)
    agents_path, proj_path, proj_docs_path, work_docs_path = _resolve_dirs(
        root, agents_dir, target_proj, proj_docs, work_docs, interactive
    )

    click.secho("Resolved paths:", fg="cyan")
    click.echo(f"  {ENV_AGENT_TOOLS:20s} = {agents_path}")
    click.echo(f"  {ENV_TARGET_PROJ:20s} = {proj_path}")
    click.echo(f"  {ENV_PROJ_DOCS:20s} = {proj_docs_path}")
    click.echo(f"  {ENV_WORK_DOCS:20s} = {work_docs_path}")
    click.echo()

    # ── load YAML template context ────────────────────────────────────────────
    context: Dict[str, Any] = _load_yaml(data_path)

    # ── set up directories ────────────────────────────────────────────────────
    click.secho("Directories:", fg="cyan")
    _setup_agent_tools(agents_path, link_arx, agentrx_source, runner)
    _setup_project_dir(proj_path, runner)
    runner.mkdir(proj_docs_path)
    _setup_docs_dir(work_docs_path, runner)

    # ── copy / process templates ──────────────────────────────────────────────
    _copy_templates(root, agents_path, agentrx_source, context, runner, link_arx=link_arx)

    # ── root bootstrap files ──────────────────────────────────────────────────
    # AGENTS.md is installed by _copy_templates (from templates/AGENTS.ARX.md).
    # CLAUDE.md and CHAT_START.md have no .ARX. template counterpart yet; write
    # from inline defaults only if absent.
    click.echo()
    click.secho("Bootstrap files:", fg="cyan")
    for fname, content in [
        ("CLAUDE.md", CLAUDE_MD_TEMPLATE),
        ("CHAT_START.md", CHAT_START_TEMPLATE),
    ]:
        runner.write(root / fname, content, skip_existing=True, label=fname)

    # ── .env (always written / updated) ──────────────────────────────────────
    click.echo()
    click.secho(".env:", fg="cyan")
    runner.update_env(root / ".env", {
        ENV_PROJECT_ROOT: str(root),
        ENV_AGENT_TOOLS:  str(agents_path),
        ENV_TARGET_PROJ:  str(proj_path),
        ENV_PROJ_DOCS:    str(proj_docs_path),
        ENV_WORK_DOCS:    str(work_docs_path),
    })

    # ── summary ───────────────────────────────────────────────────────────────
    click.echo()
    click.echo("=" * 44)
    if dry_run:
        click.secho("Dry run complete – no changes made.", fg="yellow", bold=True)
    else:
        click.secho("AgentRx initialized successfully!", fg="green", bold=True)
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Review AGENTS.md and CLAUDE.md")
    click.echo(f"  2. Add your project code under {proj_path}/")
    click.echo("  3. Use /agentrx:prompt-new to create prompts")
    click.echo()
