"""Tests for the init command."""

import os
import pytest
from pathlib import Path
from click.testing import CliRunner

from agentrx.cli import cli
from agentrx.commands.init import (
    _init_impl,
    InitError,
    resolve_mode,
    create_directory,
    create_file,
    create_symlink,
    check_link_target_exists,
    DEFAULT_AGENTS_DIR,
    DEFAULT_PROJECT_DIR,
    DEFAULT_DOCS_DIR,
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
def mock_source(tmp_path):
    """Create a mock AgentRx source directory."""
    source = tmp_path / "agentrx_source"
    source.mkdir()

    # Create _agents structure
    agents = source / "_agents"
    for subdir in ["commands", "skills", "scripts", "hooks", "agents"]:
        path = agents / subdir / "agentrx"
        path.mkdir(parents=True)
        # Add a sample file
        (path / "sample.md").write_text(f"# Sample {subdir}")

    return source


class TestResolveMode:
    """Tests for resolve_mode function."""

    def test_mode_option_takes_precedence(self):
        """--mode option should override flags."""
        assert resolve_mode("link", True, False) == "link"
        assert resolve_mode("copy", False, True) == "copy"

    def test_link_flag(self):
        """--link flag should return link mode."""
        assert resolve_mode(None, False, True) == "link"

    def test_copy_flag(self):
        """--copy flag should return copy mode."""
        assert resolve_mode(None, True, False) == "copy"

    def test_default_is_copy(self):
        """Default mode should be copy."""
        assert resolve_mode(None, False, False) == "copy"


class TestCreateDirectory:
    """Tests for create_directory function."""

    def test_creates_directory(self, temp_dir):
        """Should create directory if it doesn't exist."""
        path = temp_dir / "new_dir"
        assert not path.exists()
        result = create_directory(path)
        assert result is True
        assert path.exists()

    def test_does_not_recreate_existing(self, temp_dir):
        """Should not recreate existing directory."""
        path = temp_dir / "existing"
        path.mkdir()
        result = create_directory(path)
        assert result is False
        assert path.exists()

    def test_creates_nested_directories(self, temp_dir):
        """Should create nested directories."""
        path = temp_dir / "a" / "b" / "c"
        result = create_directory(path)
        assert result is True
        assert path.exists()


class TestCreateFile:
    """Tests for create_file function."""

    def test_creates_file(self, temp_dir):
        """Should create file with content."""
        path = temp_dir / "test.txt"
        content = "Hello, World!"
        result = create_file(path, content)
        assert result is True
        assert path.read_text() == content

    def test_does_not_overwrite_by_default(self, temp_dir):
        """Should not overwrite existing file by default."""
        path = temp_dir / "existing.txt"
        path.write_text("original")
        result = create_file(path, "new content")
        assert result is False
        assert path.read_text() == "original"

    def test_overwrites_when_requested(self, temp_dir):
        """Should overwrite when overwrite=True."""
        path = temp_dir / "existing.txt"
        path.write_text("original")
        result = create_file(path, "new content", overwrite=True)
        assert result is True
        assert path.read_text() == "new content"


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
        assert link.resolve() == target

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


class TestCheckLinkTargetExists:
    """Tests for check_link_target_exists function."""

    def test_raises_if_directory_exists(self, temp_dir):
        """Should raise InitError if directory exists."""
        path = temp_dir / "existing"
        path.mkdir()

        with pytest.raises(InitError) as exc_info:
            check_link_target_exists(path, "test")
        assert "already exists" in str(exc_info.value)

    def test_allows_symlink(self, temp_dir):
        """Should allow if path is a symlink."""
        target = temp_dir / "target"
        target.mkdir()
        link = temp_dir / "link"
        link.symlink_to(target)

        # Should not raise
        check_link_target_exists(link, "test")

    def test_allows_nonexistent(self, temp_dir):
        """Should allow if path doesn't exist."""
        path = temp_dir / "nonexistent"
        # Should not raise
        check_link_target_exists(path, "test")


class TestInitCommand:
    """Tests for the init command via CLI."""

    def test_init_creates_directory_structure(self, runner, temp_dir):
        """init should create the expected directory structure."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0, f"Failed with: {result.output}"

        # Check directories exist
        assert (target / "_agents" / "commands" / "agentrx").exists()
        assert (target / "_agents" / "skills" / "agentrx").exists()
        assert (target / "_agents" / "hooks" / "agentrx").exists()
        assert (target / "_agents" / "scripts" / "agentrx").exists()
        assert (target / "_project" / "src").exists()
        assert (target / "_project" / "docs" / "agentrx" / "vibes").exists()
        # .claude directory should NOT be created anymore
        assert not (target / ".claude").exists()

    def test_init_creates_config_files(self, runner, temp_dir):
        """init should create configuration files."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        assert (target / "AGENTS.md").exists()
        assert (target / "CLAUDE.md").exists()
        assert (target / "CHAT_START.md").exists()
        assert (target / ".env").exists()

    def test_init_env_file_content(self, runner, temp_dir):
        """init should create .env with correct content per README spec."""
        target = temp_dir / "project"

        runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir",
                "my_agents",
                "--project-dir",
                "my_project",
                "--docs-dir",
                "my_project/docs/arx",
            ],
        )

        env_content = (target / ".env").read_text()
        assert "ARX_TOOLS=my_agents" in env_content
        assert "ARX_TARGET_PROJ=my_project" in env_content
        assert "ARX_DOCS_OUT=my_project/docs/arx" in env_content
        assert "ARX_PROJECT_ROOT=" in env_content

    def test_init_link_mode_requires_source(self, runner, temp_dir):
        """--link mode should require --agentrx-source."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--link",
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 1
        assert "requires" in result.output.lower() or "agentrx-source" in result.output.lower()

    def test_init_link_mode_creates_symlinks(self, runner, temp_dir, mock_source):
        """--link mode should create symlinks to source."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--link",
                "--agentrx-source",
                str(mock_source),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0, f"Failed with: {result.output}"

        # Check symlinks exist
        commands_link = target / "_agents" / "commands" / "agentrx"
        assert commands_link.is_symlink()

    def test_init_link_mode_fails_if_target_exists(self, runner, temp_dir, mock_source):
        """--link mode should fail if target directory already exists."""
        target = temp_dir / "project"

        # Pre-create the target directory with content
        existing = target / "_agents" / "commands" / "agentrx"
        existing.mkdir(parents=True)
        (existing / "existing.md").write_text("existing content")

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--link",
                "--agentrx-source",
                str(mock_source),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_init_copy_mode_with_source(self, runner, temp_dir, mock_source):
        """--copy mode with source should copy files."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--copy",
                "--agentrx-source",
                str(mock_source),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0, f"Failed with: {result.output}"

        # Check files were copied (not symlinked)
        commands_dir = target / "_agents" / "commands" / "agentrx"
        assert commands_dir.exists()
        assert not commands_dir.is_symlink()
        assert (commands_dir / "sample.md").exists()

    def test_init_mode_option_overrides_flags(self, runner, temp_dir, mock_source):
        """--mode option should override --copy/--link flags."""
        target = temp_dir / "project"

        # Use --link flag but --mode copy
        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--link",  # This flag
                "--mode",
                "copy",  # Should be overridden by this
                "--agentrx-source",
                str(mock_source),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0

        # Should be copied, not linked
        commands_dir = target / "_agents" / "commands" / "agentrx"
        assert not commands_dir.is_symlink()

    def test_init_verbose_output(self, runner, temp_dir):
        """--verbose should show detailed output."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--verbose",
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        assert "[OK]" in result.output

    def test_init_does_not_overwrite_existing_env(self, runner, temp_dir):
        """init should not overwrite existing .env with ARX config."""
        target = temp_dir / "project"
        target.mkdir(parents=True)

        # Create existing .env with ARX config (using new var names)
        env_path = target / ".env"
        env_path.write_text("ARX_TOOLS=custom\n")

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        env_content = env_path.read_text()
        assert "ARX_TOOLS=custom" in env_content
        # Should not have duplicate
        assert env_content.count("ARX_TOOLS") == 1

    def test_init_appends_to_existing_env(self, runner, temp_dir):
        """init should append to existing .env without ARX config."""
        target = temp_dir / "project"
        target.mkdir(parents=True)

        # Create existing .env without ARX config
        env_path = target / ".env"
        env_path.write_text("OTHER_VAR=value\n")

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir",
                "_agents",
                "--project-dir",
                "_project",
                "--docs-dir",
                "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        env_content = env_path.read_text()
        assert "OTHER_VAR=value" in env_content
        assert "ARX_TOOLS=_agents" in env_content


class TestInitImpl:
    """Tests for _init_impl function directly."""

    def test_uses_default_dirs_when_not_specified(self, temp_dir):
        """Should use default directories when none specified."""
        target = temp_dir / "project"

        _init_impl(
            target_dir=str(target),
            copy_flag=False,
            link_flag=False,
            mode_option=None,
            custom=False,
            verbose=False,
            agentrx_source=None,
            agents_dir=None,
            project_dir=None,
            docs_dir=None,
            data_path=None,
        )

        assert (target / DEFAULT_AGENTS_DIR).exists()
        assert (target / DEFAULT_PROJECT_DIR).exists()

    def test_raises_for_link_without_source(self, temp_dir):
        """Should raise InitError for link mode without source."""
        target = temp_dir / "project"

        with pytest.raises(InitError) as exc_info:
            _init_impl(
                target_dir=str(target),
                copy_flag=False,
                link_flag=True,
                mode_option=None,
                custom=False,
                verbose=False,
                agentrx_source=None,
                agents_dir="_agents",
                project_dir="_project",
                docs_dir="_project/docs/agentrx",
                data_path=None,
            )

        assert "requires" in str(exc_info.value).lower()
