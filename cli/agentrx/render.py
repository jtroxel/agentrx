"""ARX template renderer.

Implements the ARX templating syntax described in arx_templating.md.

Processing order
----------------
1. Strip YAML front matter (``---`` block) — returned separately.
2. Expand ``$ENV_VAR`` and ``${ENV_VAR}`` using ``os.environ``.
3. Resolve ``<ARX [[expr]] />`` variable tags from the *data* dict.
4. Any tag whose expression cannot be resolved is left **unchanged** in the
   output so downstream agents can still see and act on it.

Only variable substitution (``[[var]]``, ``[[obj.key]]``, defaults via
``[[var | "default"]]``) is performed here.  Block/loop/include directives
are preserved verbatim — full evaluation is agent-side.

Public API
----------
``render(text, data)``  → rendered string
``render_file(path, data)``  → (front_matter_dict, rendered_string)
``build_context(data_json, data_file, stdin_json)`` → merged dict
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Front-matter helpers
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\r?\n(.+?)\r?\n---\r?\n?", re.DOTALL)


def strip_front_matter(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Return ``(front_matter_dict_or_None, body)``."""
    m = _FM_RE.match(text)
    if not m:
        return None, text
    try:
        import yaml  # type: ignore[import]
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, text[m.end():]


# ---------------------------------------------------------------------------
# Environment variable expansion
# ---------------------------------------------------------------------------

_ENV_BRACED_RE = re.compile(r"\$\{([A-Za-z_]\w*)\}")
_ENV_BARE_RE = re.compile(r"\$([A-Za-z_]\w*)")


def _expand_env(text: str) -> str:
    """Expand ``$VAR`` and ``${VAR}`` from ``os.environ`` (leave unknown as-is)."""

    def _sub(m: re.Match) -> str:
        return os.environ.get(m.group(1), m.group(0))

    text = _ENV_BRACED_RE.sub(_sub, text)
    text = _ENV_BARE_RE.sub(_sub, text)
    return text


# ---------------------------------------------------------------------------
# ARX variable tag resolution
# ---------------------------------------------------------------------------

# Matches only simple variable tags — NOT block openers/closers/loops/includes.
# Pattern: <ARX [[ expr ]] />
#   where expr is NOT starting with #, ^, *, @, /  (those are structural tags)
_VAR_TAG_RE = re.compile(
    r"<ARX\s+\[\[\s*(?![#^*@/])(.*?)\s*\]\]\s*/>",
    re.DOTALL,
)

_DEFAULT_RE = re.compile(r'^(.*?)\s*\|\s*(.+)$')


def _resolve_path(key: str, data: Dict[str, Any]) -> Any:
    """Dot-notation lookup: ``user.profile.name``.  Returns ``None`` if missing."""
    parts = key.split(".")
    node: Any = data
    for part in parts:
        if isinstance(node, dict):
            if part not in node:
                return None
            node = node[part]
        elif isinstance(node, (list, tuple)):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return node


def _resolve_expr(expr: str, data: Dict[str, Any]) -> Optional[str]:
    """Resolve ``expr`` (possibly with ``| default``) from data + env.

    Returns ``None`` when unresolvable (tag should be preserved).
    """
    # Handle default: [[key | "default"]] or [[key | 42]]
    dm = _DEFAULT_RE.match(expr)
    if dm:
        key_part = dm.group(1).strip()
        default_raw = dm.group(2).strip().strip('"\'')
    else:
        key_part = expr.strip()
        default_raw = None

    # [[env.VAR_NAME]]
    if key_part.startswith("env."):
        env_key = key_part[4:]
        val = os.environ.get(env_key)
        if val is not None:
            return val
        return default_raw  # may be None → tag preserved

    val = _resolve_path(key_part, data)
    if val is not None:
        return str(val)
    return default_raw  # may be None → tag preserved


def _render_var_tags(text: str, data: Dict[str, Any]) -> str:
    """Replace resolvable ``<ARX [[expr]] />`` tags; leave unresolvable ones."""

    def _sub(m: re.Match) -> str:
        expr = m.group(1)
        resolved = _resolve_expr(expr, data)
        if resolved is None:
            return m.group(0)  # preserve
        return resolved

    return _VAR_TAG_RE.sub(_sub, text)


# ---------------------------------------------------------------------------
# Public render functions
# ---------------------------------------------------------------------------

def render(text: str, data: Optional[Dict[str, Any]] = None) -> str:
    """Render *text* (no front-matter stripping) against *data* + env.

    Steps:
      1. Env-var expansion (``$VAR`` / ``${VAR}``)
      2. ARX variable tag substitution

    Unresolvable tags are left unchanged.
    """
    data = data or {}
    text = _expand_env(text)
    text = _render_var_tags(text, data)
    return text


def render_file(
    path: Path,
    data: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Dict[str, Any]], str]:
    """Read *path*, strip front matter, render body.

    Returns ``(front_matter_dict_or_None, rendered_body)``.
    """
    raw = path.read_text(encoding="utf-8")
    fm, body = strip_front_matter(raw)
    rendered = render(body, data)
    return fm, rendered


# ---------------------------------------------------------------------------
# Context builder (CLI helper)
# ---------------------------------------------------------------------------

def _load_data_file(data_file: str) -> Dict[str, Any]:
    """Load a JSON or YAML file into a dict."""
    p = Path(data_file)
    if not p.exists():
        raise ValueError(f"Data file not found: {data_file}")
    raw = p.read_text(encoding="utf-8")
    if p.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore[import]
            return dict(yaml.safe_load(raw) or {})
        except Exception as exc:
            raise ValueError(f"Invalid YAML in {data_file}: {exc}") from exc
    try:
        return dict(json.loads(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {data_file}: {exc}") from exc


def _parse_json_arg(label: str, raw: str) -> Dict[str, Any]:
    """Parse a raw JSON string; raise ValueError with a clear message."""
    try:
        return dict(json.loads(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON from {label}: {exc}") from exc


def build_context(
    data_json: Optional[str] = None,
    data_file: Optional[str] = None,
    stdin_json: Optional[str] = None,
) -> Dict[str, Any]:
    """Merge data from multiple sources into a single dict.

    Priority (highest wins): stdin > ``--data`` JSON string > ``--data-file``.

    Args:
        data_json:  Inline JSON string (from ``--data '{...}'``).
        data_file:  Path to a JSON or YAML file.
        stdin_json: Raw text read from stdin.
    """
    result: Dict[str, Any] = {}
    if data_file:
        result.update(_load_data_file(data_file))
    if data_json:
        result.update(_parse_json_arg("--data", data_json))
    if stdin_json and stdin_json.strip():
        result.update(_parse_json_arg("stdin", stdin_json))
    return result


def read_stdin_if_available() -> Optional[str]:
    """Return stdin content when data is being piped; else None."""
    if sys.stdin.isatty():
        return None
    try:
        return sys.stdin.read()
    except Exception:
        return None
