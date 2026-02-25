"""Tests for the setup command."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from agentrx.cli import cli
from agentrx.commands.setup import (
    find_workspace_root,
    create_symlink,
    is_doc_file,
    setup_claude,
    setup_cursor,
    setup_opencode,
)


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def mock_project(tmp_path):
    """Create a mock project with _agents structure."""
    project = tmp_path / "project"
    project.mkdir()

    # Create _agents structure
    agents = project / "_agents"
    agents.mkdir()

    # Commands
    commands = agents / "commands" / "agentrx"
    commands.mkdir(parents=True)
    (commands / "init.md").write_text("# Init Command")
    (commands / "prompt-new.md").write_text("# Prompt New Command")
    (commands / "README.md").write_text("# Commands README")

    # Skills
    skills = agents / "skills" / "agentrx"
    skills.mkdir(parents=True)
    (skills / "trial-init.md").write_text("# Trial Init Skill")
    (skills / "trial-status.md").write_text("# Trial Status Skill")

    # Hooks
    hooks = agents / "hooks"
    hooks.mkdir()
    (hooks / "pre-commit.sh").write_text("#!/bin/bash\necho 'pre-commit'")

    # Settings
    (agents / "settings.local.json").write_text('{"key": "value"}')

    # AGENTS.md and CLAUDE.md
    (agents / "AGENTS.md").write_text("# Agent Instructions")
    (agents / "CLAUDE.md").write_text("# Claude Guidance")

    return project


class TestFindProjectRoot:
    """Tests for find_workspace_root function."""

    def test_finds_root_with_agents_dir(self, temp_dir):
        """Should find project root with _agents directory."""
        project = temp_dir / "project"
        (project / "_agents").mkdir(parents=True)

        result = find_workspace_root(project / "subdir")
        assert result == project

    def test_finds_root_with_claude_dir(self, temp_dir):
        """Should find project root with .claude directory."""
        project = temp_dir / "project"
        (project / ".claude").mkdir(parents=True)

        result = find_workspace_root(project)
        assert result == project

    def test_returns_none_when_not_found(self, temp_dir):
        """Should return None when no project markers found."""
        result = find_workspace_root(temp_dir)
        assert result is None


class TestCreateSymlink:
    """Tests for create_symlink function."""

    def test_creates_symlink(self, temp_dir):
        """Should create symbolic link."""
        target = temp_dir / "target"
        target.mkdir()
        link = temp_dir / "link"

        result = create_symlink(link, target)
        assert result is True
        assert link.is_symlink()

    def test_replaces_existing_symlink(self, temp_dir):
        """Should replace existing symlink."""
        target1 = temp_dir / "target1"
        target2 = temp_dir / "target2"
        target1.mkdir()
        target2.mkdir()
        link = temp_dir / "link"

        link.symlink_to(target1)
        create_symlink(link, target2)
        assert link.resolve() == target2


class TestIsDocFile:
    """Tests for is_doc_file function."""

    def test_identifies_readme(self):
        """Should identify README as doc file."""
        assert is_doc_file("README") is True

    def test_identifies_summary(self):
        """Should identify SUMMARY as doc file."""
        assert is_doc_file("SUMMARY") is True

    def test_identifies_command_prefixed(self):
        """Should identify COMMAND_* as doc file."""
        assert is_doc_file("COMMAND_REFERENCE") is True

    def test_identifies_usage_containing(self):
        """Should identify *USAGE* as doc file."""
        assert is_doc_file("QUICK_USAGE") is True

    def test_identifies_index_containing(self):
        """Should identify *INDEX* as doc file."""
        assert is_doc_file("FILE_INDEX") is True

    def test_rejects_regular_command(self):
        """Should not identify regular command as doc file."""
        assert is_doc_file("init") is False
        assert is_doc_file("prompt-new") is False


class TestSetupClaude:
    """Tests for setup_claude function."""

    def test_creates_claude_directory(self, mock_project):
        """Should create .claude directory structure."""
        setup_claude(mock_project, mock_project / "_agents", False, False)

        assert (mock_project / ".claude").exists()
        assert (mock_project / ".claude" / "commands").exists()
        assert (mock_project / ".claude" / "skills").exists()

    def test_creates_command_symlinks(self, mock_project):
        """Should create symlinks for command namespaces."""
        setup_claude(mock_project, mock_project / "_agents", False, False)

        link = mock_project / ".claude" / "commands" / "agentrx"
        assert link.exists()
        assert link.is_symlink()

    def test_creates_skill_symlinks(self, mock_project):
        """Should create symlinks for skill namespaces."""
        setup_claude(mock_project, mock_project / "_agents", False, False)

        link = mock_project / ".claude" / "skills" / "agentrx"
        assert link.exists()
        assert link.is_symlink()

    def test_creates_hooks_symlink(self, mock_project):
        """Should create symlink for hooks directory."""
        setup_claude(mock_project, mock_project / "_agents", False, False)

        link = mock_project / ".claude" / "hooks"
        assert link.exists()
        assert link.is_symlink()

    def test_creates_settings_symlink(self, mock_project):
        """Should create symlink for settings.local.json."""
        setup_claude(mock_project, mock_project / "_agents", False, False)

        link = mock_project / ".claude" / "settings.local.json"
        assert link.exists()
        assert link.is_symlink()

    def test_clean_removes_existing_symlinks(self, mock_project):
        """--clean should remove existing symlinks before recreating."""
        # First setup
        setup_claude(mock_project, mock_project / "_agents", False, False)

        # Create an extra symlink that should be removed
        extra_link = mock_project / ".claude" / "extra"
        extra_link.symlink_to(mock_project)

        # Second setup with clean
        setup_claude(mock_project, mock_project / "_agents", True, False)

        assert not extra_link.exists()


class TestSetupCursor:
    """Tests for setup_cursor function."""

    def test_creates_cursorrules(self, mock_project):
        """Should create .cursorrules file."""
        setup_cursor(mock_project, mock_project / "_agents", False, False)

        cursorrules = mock_project / ".cursorrules"
        assert cursorrules.exists()
        content = cursorrules.read_text()
        assert "AgentRx" in content
        assert "_agents/AGENTS.md" in content

    def test_creates_cursor_rules_directory(self, mock_project):
        """Should create .cursor/rules directory."""
        setup_cursor(mock_project, mock_project / "_agents", False, False)

        assert (mock_project / ".cursor" / "rules").exists()

    def test_creates_agents_mdc(self, mock_project):
        """Should create agents.mdc file."""
        setup_cursor(mock_project, mock_project / "_agents", False, False)

        mdc_file = mock_project / ".cursor" / "rules" / "agents.mdc"
        assert mdc_file.exists()
        content = mdc_file.read_text()
        assert "alwaysApply: true" in content
        assert "_agents/AGENTS.md" in content

    def test_clean_removes_existing_files(self, mock_project):
        """--clean should remove existing files before recreating."""
        # Create old cursorrules
        old_cursorrules = mock_project / ".cursorrules"
        old_cursorrules.write_text("old content")

        setup_cursor(mock_project, mock_project / "_agents", True, False)

        # Old content should be replaced
        assert "old content" not in old_cursorrules.read_text()


class TestSetupOpencode:
    """Tests for setup_opencode function."""

    def test_creates_agents_md_wrapper(self, mock_project):
        """Should create AGENTS.md wrapper file."""
        setup_opencode(mock_project, mock_project / "_agents", False, False)

        agents_md = mock_project / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text()
        assert "AgentRx Wrapper" in content
        assert "_agents/AGENTS.md" in content

    def test_creates_opencode_json(self, mock_project):
        """Should create opencode.json configuration."""
        setup_opencode(mock_project, mock_project / "_agents", False, False)

        opencode_json = mock_project / "opencode.json"
        assert opencode_json.exists()
        config = json.loads(opencode_json.read_text())
        assert "instructions" in config
        assert "_agents/AGENTS.md" in config["instructions"]

    def test_does_not_overwrite_non_wrapper_agents_md(self, mock_project):
        """Should not overwrite existing non-wrapper AGENTS.md."""
        existing_agents_md = mock_project / "AGENTS.md"
        existing_agents_md.write_text("# My Custom AGENTS.md")

        setup_opencode(mock_project, mock_project / "_agents", False, False)

        # Original should be preserved
        assert "My Custom AGENTS.md" in existing_agents_md.read_text()
        # Wrapper should be created with alternate name
        assert (mock_project / "AGENTS.md.agentrx").exists()

    def test_does_not_overwrite_existing_opencode_json(self, mock_project):
        """Should not overwrite existing opencode.json."""
        existing_opencode = mock_project / "opencode.json"
        existing_opencode.write_text('{"custom": "config"}')

        setup_opencode(mock_project, mock_project / "_agents", False, False)

        # Original should be preserved
        config = json.loads(existing_opencode.read_text())
        assert config.get("custom") == "config"


class TestSetupCommand:
    """Tests for the setup command via CLI."""

    def test_setup_all_providers(self, runner, mock_project):
        """setup with default --provider=all should set up all providers."""
        result = runner.invoke(
            cli,
            ["setup", "--workspace-root", str(mock_project)],
        )

        assert result.exit_code == 0
        assert (mock_project / ".claude").exists()
        assert (mock_project / ".cursorrules").exists()
        assert (mock_project / "AGENTS.md").exists()

    def test_setup_claude_only(self, runner, mock_project):
        """setup --provider claude should only set up Claude."""
        result = runner.invoke(
            cli,
            ["setup", "--provider", "claude", "--workspace-root", str(mock_project)],
        )

        assert result.exit_code == 0
        assert (mock_project / ".claude").exists()
        assert not (mock_project / ".cursorrules").exists()

    def test_setup_cursor_only(self, runner, mock_project):
        """setup --provider cursor should only set up Cursor."""
        result = runner.invoke(
            cli,
            ["setup", "--provider", "cursor", "--workspace-root", str(mock_project)],
        )

        assert result.exit_code == 0
        assert (mock_project / ".cursorrules").exists()
        assert not (mock_project / ".claude").exists()

    def test_setup_opencode_only(self, runner, mock_project):
        """setup --provider opencode should only set up OpenCode."""
        result = runner.invoke(
            cli,
            ["setup", "--provider", "opencode", "--workspace-root", str(mock_project)],
        )

        assert result.exit_code == 0
        assert (mock_project / "AGENTS.md").exists()
        assert not (mock_project / ".claude").exists()
        assert not (mock_project / ".cursorrules").exists()

    def test_setup_fails_without_agents_dir(self, runner, temp_dir):
        """setup should fail if _agents directory doesn't exist."""
        empty_project = temp_dir / "empty"
        empty_project.mkdir()

        result = runner.invoke(
            cli,
            ["setup", "--workspace-root", str(empty_project)],
        )

        assert result.exit_code == 1
        assert "_agents" in result.output or "not found" in result.output.lower()

    def test_setup_verbose_output(self, runner, mock_project):
        """--verbose should show detailed output."""
        result = runner.invoke(
            cli,
            ["setup", "--verbose", "--workspace-root", str(mock_project)],
        )

        assert result.exit_code == 0
        # Verbose should show individual commands/skills
        assert "/" in result.output or "agentrx" in result.output.lower()

    def test_setup_clean_flag(self, runner, mock_project):
        """--clean should remove existing files before creating new ones."""
        # First setup
        result1 = runner.invoke(
            cli,
            ["setup", "--workspace-root", str(mock_project)],
        )
        assert result1.exit_code == 0

        # Create extra file
        extra_file = mock_project / ".cursor" / "rules" / "extra.mdc"
        extra_file.parent.mkdir(parents=True, exist_ok=True)
        extra_file.write_text("extra content")

        # Second setup with clean
        result2 = runner.invoke(
            cli,
            ["setup", "--clean", "--workspace-root", str(mock_project)],
        )

        assert result2.exit_code == 0
        # .cursor/rules should be recreated without extra file
        # (clean removes the entire rules directory)
        assert not extra_file.exists()

    def test_setup_shows_summary(self, runner, mock_project):
        """setup should show a summary of created files."""
        result = runner.invoke(
            cli,
            ["setup", "--workspace-root", str(mock_project)],
        )

        assert result.exit_code == 0
        assert "complete" in result.output.lower()
        assert ".claude" in result.output or "Provider-specific" in result.output
