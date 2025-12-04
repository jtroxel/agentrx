"""Command-line interface for agentrx."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

import typer

from .models import TemplateData
from .renderer import render_template
from .agents import run_agent

app = typer.Typer()


@app.command()
def generate(
    title: str = typer.Option(..., help="Title for the markdown document"),
    description: Optional[str] = typer.Option(None, help="Short description"),
    tags: Optional[str] = typer.Option(None, help="Comma-separated tags"),
    output: Path = typer.Option(Path("output.md"), help="Output markdown file"),
    use_ai: bool = typer.Option(False, help="Use AI agent to expand fields"),
):
    """Generate a markdown file from a template.

    The CLI collects simple structured input (title, description, tags) and optionally
    delegates to a LangChain agent to expand or enrich the fields before rendering.
    """

    tags_list = [t.strip() for t in tags.split(",")] if tags else []
    data = TemplateData(title=title, description=description or "", tags=tags_list)

    if use_ai:
        typer.echo("Running AI agent to enrich content...")
        enriched = run_agent(data.dict())
        # merge enriched fields into data
        for k, v in enriched.items():
            if hasattr(data, k):
                setattr(data, k, v)

    template_text = Path(__file__).parent / "templates" / "default.md.j2"
    rendered = render_template(str(template_text), data.dict())

    output.write_text(rendered, encoding="utf-8")
    typer.echo(f"Wrote {output}")


@app.command()
def new(
    spec_type: str = typer.Argument(..., help="Type of specification: feature or capability"),
    user_text: str = typer.Argument(..., help="Description of the feature or capability"),
):
    """Create a new specification document from template.
    
    Example: agentrx new capability "a service to manage user-defined, persistent tags for photos"
    """
    
    # Validate spec_type
    if spec_type not in ["feature", "capability"]:
        typer.echo("Error: spec_type must be either 'feature' or 'capability'", err=True)
        raise typer.Exit(1)
    
    # Load environment variables
    project_dir = os.getenv("AGENTX_PROJECT_DIR", "dev/agentrx-sdd")
    
    # Generate filename with condensed date and abbreviated user text
    now = datetime.now()
    date_str = now.strftime("%y-%m%d-%w")  # YY-MMDD-W format
    
    # Create abbreviated version of user text (first letter of each word, max 5)
    text_words = user_text.lower().split()[:5]
    text_abbrev = "".join(word[0] for word in text_words if word.isalpha())
    filename = f"{date_str}_{text_abbrev}.md"
    
    # Create output path
    output_path = Path(project_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read template
    template_path = Path(__file__).parent / "dot-project" / "sdd" / "new" / "template.md"
    template_content = template_path.read_text(encoding="utf-8")
    
    # Replace template variables
    content = template_content.replace("{{spec_type}}", spec_type.title())
    content = content.replace("{{user_text}}", user_text)
    content = content.replace("{{goals}}", "")
    content = content.replace("{{technical_requirements}}", "")
    content = content.replace("{{implementation_notes}}", "")
    content = content.replace("{{success_criteria}}", "")
    content = content.replace("{{date}}", now.strftime("%Y-%m-%d"))
    content = content.replace("{{project_name}}", "agentrx")
    
    # Write the file
    output_path.write_text(content, encoding="utf-8")
    typer.echo(f"Created new {spec_type} specification: {output_path}")


def main():
    app()


if __name__ == "__main__":
    main()
