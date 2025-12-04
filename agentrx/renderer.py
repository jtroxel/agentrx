"""Template renderer for agentrx using Jinja2."""
from __future__ import annotations

from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_template(template_path: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template file with the given context.

    Args:
        template_path: Path to the template file.
        context: Mapping of values used in the template.

    Returns:
        Rendered text.
    """

    loader = FileSystemLoader(searchpath="./")
    env = Environment(loader=loader, autoescape=select_autoescape(["html", "xml"]))
    template = env.get_template(template_path)
    return template.render(**context)
