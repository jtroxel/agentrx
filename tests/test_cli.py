import os
from pathlib import Path
from typer.testing import CliRunner

from agentrx.cli import app


def test_generate_basic(tmp_path, monkeypatch):
    runner = CliRunner()
    out_file = tmp_path / "out.md"
    result = runner.invoke(app, [
        "generate",
        "--title",
        "Test",
        "--description",
        "desc",
        "--output",
        str(out_file),
    ])
    assert result.exit_code == 0
    assert out_file.exists()


def test_new_capability(tmp_path, monkeypatch):
    """Test creating a new capability specification."""
    # Set up environment
    project_dir = tmp_path / "project"
    monkeypatch.setenv("AGENTX_PROJECT_DIR", str(project_dir))
    
    runner = CliRunner()
    result = runner.invoke(app, [
        "new",
        "capability",
        "a service to manage user-defined, persistent tags for photos"
    ])
    
    assert result.exit_code == 0
    assert "Created new capability specification:" in result.stdout
    
    # Check that file was created
    created_files = list(project_dir.glob("*.md"))
    assert len(created_files) == 1
    
    # Check file content
    content = created_files[0].read_text()
    assert "Capability: a service to manage user-defined, persistent tags for photos" in content
    assert "Type: Capability" in content


def test_new_feature(tmp_path, monkeypatch):
    """Test creating a new feature specification."""
    # Set up environment
    project_dir = tmp_path / "project"
    monkeypatch.setenv("AGENTX_PROJECT_DIR", str(project_dir))
    
    runner = CliRunner()
    result = runner.invoke(app, [
        "new",
        "feature",
        "user authentication with OAuth2"
    ])
    
    assert result.exit_code == 0
    assert "Created new feature specification:" in result.stdout
    
    # Check that file was created
    created_files = list(project_dir.glob("*.md"))
    assert len(created_files) == 1
    
    # Check file content
    content = created_files[0].read_text()
    assert "Feature: user authentication with OAuth2" in content
    assert "Type: Feature" in content


def test_new_invalid_spec_type(tmp_path, monkeypatch):
    """Test that invalid spec types are rejected."""
    project_dir = tmp_path / "project"
    monkeypatch.setenv("AGENTX_PROJECT_DIR", str(project_dir))
    
    runner = CliRunner()
    result = runner.invoke(app, [
        "new",
        "invalid_type",
        "some description"
    ])
    
    assert result.exit_code == 1
    assert "spec_type must be either 'feature' or 'capability'" in result.stdout


def test_new_filename_generation(tmp_path, monkeypatch):
    """Test that filenames are generated correctly."""
    project_dir = tmp_path / "project"
    monkeypatch.setenv("AGENTX_PROJECT_DIR", str(project_dir))
    
    runner = CliRunner()
    result = runner.invoke(app, [
        "new",
        "capability",
        "a service to manage user tags"
    ])
    
    assert result.exit_code == 0
    
    # Check filename pattern (should be YY-MMDD-W_astmt.md)
    created_files = list(project_dir.glob("*.md"))
    assert len(created_files) == 1
    
    filename = created_files[0].name
    # Should match pattern: digits-digits-digit_letters.md
    import re
    pattern = r'^\d{2}-\d{4}-\d_[a-z]+\.md$'
    assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"
    
    # Check that abbreviation is correct (first letters: a, s, t, m, u -> astmu or astm due to 5 word limit)
    assert "_astm" in filename or "_astmu" in filename


def test_new_creates_directory(tmp_path, monkeypatch):
    """Test that the project directory is created if it doesn't exist."""
    project_dir = tmp_path / "nonexistent" / "project"
    monkeypatch.setenv("AGENTX_PROJECT_DIR", str(project_dir))
    
    runner = CliRunner()
    result = runner.invoke(app, [
        "new",
        "feature",
        "test feature"
    ])
    
    assert result.exit_code == 0
    assert project_dir.exists()
    assert len(list(project_dir.glob("*.md"))) == 1
