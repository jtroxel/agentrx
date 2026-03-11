"""ARX Template Engine.

Three-step processing pipeline:
1. Strip YAML front matter (``---`` blocks) — returned separately.
2. Expand env vars: ``$VAR`` and ``${VAR}`` from ``os.environ``.
3. Resolve ARX tags:
   - ``<ARX [[expr]] />``  (variable substitution)
   - ``<ARX:IF [[expr]]>``...``</ARX:IF>``
   - ``<ARX:REPLACE agent: name, "prompt">``...``</ARX:REPLACE>``

Phase annotations (``:new``, ``:do``) control *when* expressions resolve.
Mustache ``{{...}}`` blocks are passed through unchanged.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

# ---------------------------------------------------------------------------
# Front-matter helpers
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def strip_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML front matter from *text*.

    Returns ``(front_matter_dict, body)`` where *body* is everything after the
    closing ``---``.  If no front matter is present, returns ``({}, text)``.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, text[m.end() :]


# ---------------------------------------------------------------------------
# Environment-variable expansion
# ---------------------------------------------------------------------------

_ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def _expand_env(text: str) -> str:
    """Replace ``$VAR`` and ``${VAR}`` with values from ``os.environ``.

    Unset variables are left as-is.
    """

    def _repl(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        return os.environ.get(name, m.group(0))

    return _ENV_RE.sub(_repl, text)


# ---------------------------------------------------------------------------
# ARX tag resolution
# ---------------------------------------------------------------------------

# Matches: <ARX [[expr]] />  or  <ARX [[expr]] :phase />
_VAR_TAG_RE = re.compile(
    r"<ARX\s+\[\[(.+?)\]\]"       # [[expression]]
    r"(?:\s+:(\w+))?"              # optional :phase
    r"\s*/>"                       # self-closing
)

# Matches: <ARX:IF [[expr]]> ... </ARX:IF>
_IF_TAG_RE = re.compile(
    r"<ARX:IF\s+\[\[(.+?)\]\]>"   # opening tag with expression
    r"(.*?)"                       # body
    r"</ARX:IF>",                  # closing tag
    re.DOTALL,
)

# Matches: <ARX:REPLACE agent: name, "prompt"> ... </ARX:REPLACE>
_REPLACE_TAG_RE = re.compile(
    r'<ARX:REPLACE\s+agent:\s*(\S+),\s*"([^"]*)">'  # agent + prompt
    r"(.*?)"                                          # body
    r"</ARX:REPLACE>",                                # closing tag
    re.DOTALL,
)


def _resolve_expr(expr: str, data: Dict[str, Any]) -> Any:
    """Evaluate a ``[[...]]`` expression against *data*.

    Supported forms:
    - ``key``                  — simple lookup
    - ``obj.nested.key``       — dot-notation traversal
    - ``array.0``              — integer index
    - ``env.VAR_NAME``         — environment variable
    - ``key | "default"``      — default value fallback
    """
    expr = expr.strip()

    # Handle default: [[key | "default"]]
    default = None
    if "|" in expr:
        expr, default_part = expr.split("|", 1)
        expr = expr.strip()
        default_part = default_part.strip().strip('"').strip("'")
        default = default_part

    # env.VAR_NAME shorthand
    if expr.startswith("env."):
        val = os.environ.get(expr[4:])
        if val is not None:
            return val
        return default if default is not None else None

    # Dot-notation traversal
    parts = expr.split(".")
    cur: Any = data
    for part in parts:
        if cur is None:
            break
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, (list, tuple)):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                cur = None
        else:
            cur = None

    if cur is not None:
        return cur
    return default if default is not None else None


def _resolve_var_tags(text: str, data: Dict[str, Any], phase: Optional[str]) -> str:
    """Replace ``<ARX [[...]] />`` tags whose phase matches."""

    def _repl(m: re.Match) -> str:
        expr = m.group(1)
        tag_phase = m.group(2)  # None when no :phase annotation

        # If tag has a phase and it doesn't match current phase, leave as-is
        if tag_phase and tag_phase != phase:
            return m.group(0)

        val = _resolve_expr(expr, data)
        if val is None:
            # Unresolved — leave the tag for a later phase
            return m.group(0)
        return str(val)

    return _VAR_TAG_RE.sub(_repl, text)


def _resolve_if_tags(text: str, data: Dict[str, Any]) -> str:
    """Evaluate ``<ARX:IF [[expr]]>...`` blocks."""

    def _repl(m: re.Match) -> str:
        val = _resolve_expr(m.group(1), data)
        if val:
            return m.group(2)
        return ""

    return _IF_TAG_RE.sub(_repl, text)


def _resolve_replace_tags(text: str, data: Dict[str, Any]) -> str:
    """Evaluate ``<ARX:REPLACE ...>`` blocks.

    Currently returns the body unchanged — replacement logic is agent-side.
    The tag is stripped, leaving the body content.
    """

    def _repl(m: re.Match) -> str:
        return m.group(3)

    return _REPLACE_TAG_RE.sub(_repl, text)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render(text: str, data: Optional[Dict[str, Any]] = None, phase: Optional[str] = None) -> str:
    """Render a template string.

    Processing order:
    1. Expand ``$VAR`` / ``${VAR}`` environment variables.
    2. Resolve ``<ARX:IF>`` conditional blocks.
    3. Resolve ``<ARX:REPLACE>`` blocks (strip tags, keep body).
    4. Resolve ``<ARX [[...]] />`` variable tags (phase-aware).

    Mustache ``{{...}}`` directives are left untouched.
    """
    data = data or {}
    text = _expand_env(text)
    text = _resolve_if_tags(text, data)
    text = _resolve_replace_tags(text, data)
    text = _resolve_var_tags(text, data, phase)
    return text


def render_file(
    path: str | Path,
    data: Optional[Dict[str, Any]] = None,
    phase: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Read a file, strip front matter, and render the body.

    Returns ``(front_matter_dict, rendered_body)``.
    """
    text = Path(path).read_text(encoding="utf-8")
    fm, body = strip_front_matter(text)
    rendered = render(body, data, phase)
    return fm, rendered


def build_context(
    data_json: Optional[str] = None,
    data_file: Optional[str] = None,
    stdin_json: bool = False,
) -> Dict[str, Any]:
    """Merge multiple data sources into a single context dict.

    Merge order (later wins): *data_file* < *data_json* < *stdin*.
    """
    ctx: Dict[str, Any] = {}

    if data_file:
        p = Path(data_file)
        if p.exists():
            raw = p.read_text(encoding="utf-8")
            if p.suffix in (".yaml", ".yml"):
                ctx.update(yaml.safe_load(raw) or {})
            else:
                ctx.update(json.loads(raw))

    if data_json:
        ctx.update(json.loads(data_json))

    if stdin_json and not sys.stdin.isatty():
        raw = sys.stdin.read()
        if raw.strip():
            ctx.update(json.loads(raw))

    return ctx
