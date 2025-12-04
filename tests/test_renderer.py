from agentrx.renderer import render_template
from pathlib import Path


def test_render_simple(tmp_path):
    tpl = tmp_path / "tpl.md.j2"
    tpl.write_text("# {{ title }}\n\n{{ description }}\n")
    out = render_template(str(tpl), {"title": "T", "description": "D"})
    assert "# T" in out
    assert "D" in out
