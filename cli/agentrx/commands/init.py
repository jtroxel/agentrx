"""``arx init`` — initialize an AgentRx workspace.

Non-interactive counterpart to ``init-arx.sh``.  Creates the workspace
directory structure, copies/symlinks template assets, writes ``.env`` and
``arx.config.yaml``.

Template subdirectory mapping (from ``$AGENTRX_SOURCE/_arx_templates/``):

| Subdir                       | Destination            | Behaviour                              |
|------------------------------|------------------------|----------------------------------------|
| ``_arx_workspace_root.arx/`` | ``$ARX_ROOT``          | Copied as-is; only if absent           |
| ``_arx_agent_tools.arx/``    | ``$ARX_AGENT_FILES``   | Copied (or symlinked with --link-arx)  |
| ``_arx_work_docs.arx/``      | ``$ARX_WORKING``       | Always copied                          |
| ``_arx_proj_docs.arx/``      | ``$ARX_PROJ_DOCS``     | Optional (--docs / --no-docs)          |

Files/dirs with ``.arx.`` in the name (or ending in ``.arx``) are source-only
and are **skipped** during copy.  Everything else is copied verbatim.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import click
import yaml

from ..render import render_file

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _template_source() -> Path:
    """Resolve the ``_arx_templates`` directory inside ``$AGENTRX_SOURCE``."""
    src = os.environ.get("AGENTRX_SOURCE")
    if not src:
        raise click.ClickException(
            "AGENTRX_SOURCE is not set. "
            "Export it to point at your AgentRx source checkout."
        )
    p = Path(src) / "_arx_templates"
    if not p.is_dir():
        raise click.ClickException(f"Template directory not found: {p}")
    return p


def _is_source_only(name: str) -> bool:
    """Return True if *name* is a source-only file/dir (has ``.arx.`` or ends with ``.arx``).

    Source-only items are skipped during copy.  Everything else is copied as-is.
    """
    return ".arx." in name or name.endswith(".arx")


def _copy_tree(src: Path, dst: Path, *, only_if_absent: bool = False, link: bool = False):
    """Recursively copy *src* into *dst*, skipping source-only (``.arx``) items."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if _is_source_only(item.name):
            continue
        target = dst / item.name
        if item.is_dir():
            _copy_tree(item, target, only_if_absent=only_if_absent, link=link)
        else:
            if only_if_absent and target.exists():
                continue
            if link:
                target.unlink(missing_ok=True)
                target.symlink_to(item.resolve())
            else:
                shutil.copy2(item, target)


def _write_env(root: Path, env_vars: dict[str, str]):
    """Write or overwrite the ``.env`` file with ``ARX_*`` variables."""
    lines = [f'{k}="{v}"\n' for k, v in sorted(env_vars.items())]
    (root / ".env").write_text("".join(lines), encoding="utf-8")


def _write_config(root: Path, config: dict):
    """Write ``arx.config.yaml``."""
    (root / "arx.config.yaml").write_text(
        yaml.dump(config, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


@click.command("init")
@click.argument("workspace", default=".", type=click.Path())
@click.option("--agent-files", default="_agents", help="Agent tools directory (default: _agents).")
@click.option("--templates-dir", default=None, help="Local templates copy destination. Omit to use from $AGENTRX_SOURCE.")
@click.option("--projects-dir", default="_projects", help="Root directory for target projects.")
@click.option("--working-dir", default=None, help="Working docs directory. Default: <projects-dir>/arx_docs.")
@click.option("--link-arx", is_flag=True, default=False, help="Symlink agent tools instead of copying.")
@click.option("--docs/--no-docs", default=True, help="Install project-doc templates (default: yes).")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be done without writing.")
def init(workspace, agent_files, templates_dir, projects_dir, working_dir, link_arx, docs, dry_run):
    """Initialize an AgentRx workspace.

    WORKSPACE is the target directory (default: current directory).
    """
    root = Path(workspace).resolve()
    root.mkdir(parents=True, exist_ok=True)

    tmpl_src = _template_source()

    # Resolve key paths
    agent_files_path = root / agent_files
    projects_path = root / projects_dir
    working_path = Path(working_dir) if working_dir else projects_path / "arx_docs"
    if not working_path.is_absolute():
        working_path = root / working_path

    if templates_dir:
        local_tmpl = root / templates_dir
    else:
        local_tmpl = None  # use from source

    # Resolve effective template source (local copy or $AGENTRX_SOURCE)
    effective_tmpl = local_tmpl if local_tmpl else tmpl_src

    # Build environment variables
    env_vars = {
        "AGENTRX_SOURCE": os.environ.get("AGENTRX_SOURCE", ""),
        "ARX_ROOT": str(root),
        "ARX_AGENT_FILES": str(agent_files_path),
        "ARX_TEMPLATES": str(effective_tmpl),
        "ARX_WORKING": str(working_path),
    }

    # Build config
    config = {
        "arx_root": str(root),
        "agent_files": str(agent_files_path),
        "templates": str(effective_tmpl),
        "projects_dir": str(projects_path),
        "working_dir": str(working_path),
        "projects": {},
    }

    # Auto-detect existing project subdirectories
    if projects_path.is_dir():
        for child in sorted(projects_path.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                abbr = child.name.replace("-", "_").upper()
                config["projects"][child.name] = {
                    "path": str(child),
                    "abbr": abbr,
                }
                env_vars[f"ARX_{abbr}"] = str(child)

    if dry_run:
        click.echo("Dry run — the following actions would be taken:\n")
        click.echo(f"  Workspace root : {root}")
        click.echo(f"  Agent files    : {agent_files_path}")
        click.echo(f"  Templates      : {effective_tmpl}")
        click.echo(f"  Projects       : {projects_path}")
        click.echo(f"  Working docs   : {working_path}")
        click.echo(f"  Link mode      : {link_arx}")
        click.echo(f"  Install docs   : {docs}")
        click.echo(f"\n  .env variables:")
        for k, v in sorted(env_vars.items()):
            click.echo(f"    {k}={v}")
        return

    # 1. Copy local templates if requested
    if local_tmpl:
        click.echo(f"Copying templates → {local_tmpl}")
        _copy_tree(tmpl_src, local_tmpl)

    # 2. Workspace root files (copied as-is, only if absent)
    ws_root_tmpl = effective_tmpl / "_arx_workspace_root.arx"
    if ws_root_tmpl.is_dir():
        click.echo(f"Installing workspace root files → {root}")
        _copy_tree(ws_root_tmpl, root, only_if_absent=True)

    # 3. Agent tools (copy or symlink)
    agent_tmpl = effective_tmpl / "_arx_agent_tools.arx"
    if agent_tmpl.is_dir():
        click.echo(f"Installing agent tools → {agent_files_path}")
        _copy_tree(agent_tmpl, agent_files_path, link=link_arx)

    # 4. Working docs (always copied)
    work_tmpl = effective_tmpl / "_arx_work_docs.arx"
    if work_tmpl.is_dir():
        click.echo(f"Installing working docs → {working_path}")
        _copy_tree(work_tmpl, working_path)

    # 5. Project docs (optional)
    if docs:
        proj_tmpl = effective_tmpl / "_arx_proj_docs.arx"
        if proj_tmpl.is_dir():
            # Install into each known project, or into projects_path if none
            targets = [Path(p["path"]) for p in config["projects"].values()] or [projects_path]
            for proj_path in targets:
                dest = proj_path / "docs"
                click.echo(f"Installing project docs → {dest}")
                _copy_tree(proj_tmpl, dest)

    # 6. Create directory structure
    for d in [agent_files_path, projects_path, working_path]:
        d.mkdir(parents=True, exist_ok=True)

    for subdir in ["vibes", "deltas", "sessions", "tasks"]:
        (working_path / subdir).mkdir(parents=True, exist_ok=True)

    # 7. Write .env and config
    _write_env(root, env_vars)
    click.echo(f"Wrote {root / '.env'}")

    _write_config(root, config)
    click.echo(f"Wrote {root / 'arx.config.yaml'}")

    click.echo(f"\nWorkspace initialized at {root}")
