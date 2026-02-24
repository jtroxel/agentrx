"""Tests for the init command."""

import os
import pytest
from pathlib import Path
from click.testing import CliRunner

from agentrx.cli import cli
from agentrx.commands.init import (
    _run_init,
    _mkdir,
    _write_file,
    _make_symlink,
    _strip_arx_marker,
    _resolve_dirs,
    InitError,
    DEFAULT_AGENTS_DIR,
    DEFAULT_PROJECT_DIR,
    DEFAULT_WORK_DOCS,
    AGENTS_TEMPLATE_SUBDIR,
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
    """Create a mock AgentRx source directory with templates structure."""
    source = tmp_path / "agentrx_source"
    source.mkdir()

    # Create templates structure (matching the actual layout)
    templates = source / "templates"
    templates.mkdir()

    # Create _arx_agent_tools.arx structure
    agents_tmpl = templates / AGENTS_TEMPLATE_SUBDIR
    for subdir in ["commands", "skills", "scripts", "hooks", "agents"]:
        path = agents_tmpl / subdir / "agentrx"
        path.mkdir(parents=True)
        # Add a sample file
        (path / "sample.md").write_text(f"# Sample {subdir}")

    # Create root-level template files
    (templates / "AGENTS.ARX.md").write_text("# AGENTS Template")
    (templates / "AGENT_TOOLS.ARX.md").write_text("# Agent Tools Template")

    return source


class TestHelperFunctions:
    """Tests for low-level helper functions."""

    def test_mkdir_creates_directory(self, temp_dir):
        """Should create directory if it doesn't exist."""
        path = temp_dir / "new_dir"
        assert not path.exists()
        result = _mkdir(path)
        assert result is True
        assert path.exists()

    def test_mkdir_returns_false_for_existing(self, temp_dir):
        """Should return False for existing directory."""
        path = temp_dir / "existing"
        path.mkdir()
        result = _mkdir(path)
        assert result is False
        assert path.exists()

    def test_mkdir_creates_nested_directories(self, temp_dir):
        """Should create nested directories."""
        path = temp_dir / "a" / "b" / "c"
        result = _mkdir(path)
        assert result is True
        assert path.exists()

    def test_write_file_creates_file(self, temp_dir):
        """Should create file with content."""
        path = temp_dir / "test.txt"
        content = "Hello, World!"
        result = _write_file(path, content, skip_existing=False)
        assert result is True
        assert path.read_text() == content

    def test_write_file_skips_existing_by_default(self, temp_dir):
        """Should skip existing file when skip_existing=True."""
        path = temp_dir / "existing.txt"
        path.write_text("original")
        result = _write_file(path, "new content", skip_existing=True)
        assert result is False
        assert path.read_text() == "original"

    def test_write_file_overwrites_when_skip_false(self, temp_dir):
        """Should overwrite when skip_existing=False."""
        path = temp_dir / "existing.txt"
        path.write_text("original")
        result = _write_file(path, "new content", skip_existing=False)
        assert result is True
        assert path.read_text() == "new content"

    def test_make_symlink_creates_symlink(self, temp_dir):
        """Should create symbolic link."""
        target = temp_dir / "target"
        target.mkdir()
        link = temp_dir / "link"

        _make_symlink(link, target)
        assert link.is_symlink()
        assert link.resolve() == target

    def test_make_symlink_replaces_existing_symlink(self, temp_dir):
        """Should replace existing symlink."""
        target1 = temp_dir / "target1"
        target2 = temp_dir / "target2"
        target1.mkdir()
        target2.mkdir()
        link = temp_dir / "link"

        link.symlink_to(target1)
        _make_symlink(link, target2)
        assert link.resolve() == target2

    def test_strip_arx_marker(self):
        """Should strip .ARX. and .arx. markers from filenames."""
        assert _strip_arx_marker("AGENTS.ARX.md") == "AGENTS.md"
        assert _strip_arx_marker("context.arx.yaml") == "context.yaml"
        assert _strip_arx_marker("README.md") == "README.md"


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
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0, f"Failed with: {result.output}"

        # Check directories exist
        assert (target / "_agents" / "commands").exists()
        assert (target / "_agents" / "skills").exists()
        assert (target / "_agents" / "hooks").exists()
        assert (target / "_agents" / "scripts").exists()
        assert (target / "_project" / "src").exists()
        assert (target / "_project" / "docs" / "agentrx" / "vibes").exists()

    def test_init_creates_config_files(self, runner, temp_dir):
        """init should create configuration files."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        # AGENTS.md comes from templates if available, otherwise not created
        assert (target / "CLAUDE.md").exists()
        assert (target / "CHAT_START.md").exists()
        assert (target / ".env").exists()

    def test_init_env_file_content(self, runner, temp_dir):
        """init should create .env with correct variable names."""
        target = temp_dir / "project"

        runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir", "my_agents",
                "--target-proj", "my_project",
                "--proj-docs", "my_project/docs",
                "--work-docs", "my_project/docs/arx",
            ],
        )

        env_content = (target / ".env").read_text()
        assert "ARX_AGENT_TOOLS=" in env_content
        assert "ARX_TARGET_PROJ=" in env_content
        assert "ARX_PROJ_DOCS=" in env_content
        assert "ARX_WORK_DOCS=" in env_content
        assert "ARX_PROJECT_ROOT=" in env_content

    def test_init_link_mode_requires_source(self, runner, temp_dir):
        """--link-arx mode should require --agentrx-source."""
        target = temp_dir / "project"

        # Unset AGENTRX_SOURCE to ensure the test doesn't pick it up from env
        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--link-arx",
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
            env={"AGENTRX_SOURCE": ""},
        )

        assert result.exit_code == 1
        assert "requires" in result.output.lower() or "agentrx-source" in result.output.lower()

    def test_init_link_mode_creates_symlinks(self, runner, temp_dir, mock_source):
        """--link-arx mode should create symlinks to source."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--link-arx",
                "--agentrx-source", str(mock_source),
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0, f"Failed with: {result.output}"

        # Check symlinks exist
        commands_link = target / "_agents" / "commands" / "agentrx"
        assert commands_link.is_symlink()

    def test_init_copy_mode_with_source(self, runner, temp_dir, mock_source):
        """Copy mode with source should copy files."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agentrx-source", str(mock_source),
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0, f"Failed with: {result.output}"

        # Check files were copied (not symlinked)
        commands_dir = target / "_agents" / "commands" / "agentrx"
        assert commands_dir.exists()
        assert not commands_dir.is_symlink()
        assert (commands_dir / "sample.md").exists()

    def test_init_verbose_output(self, runner, temp_dir):
        """--verbose should show detailed output."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--verbose",
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        # Verbose mode shows [OK] markers
        assert "[OK]" in result.output or "mkdir" in result.output

    def test_init_dry_run(self, runner, temp_dir):
        """--dry-run should show actions without making changes."""
        target = temp_dir / "project"

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--dry-run",
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        # Directory should not be created in dry-run
        assert not (target / "_agents").exists()

    def test_init_preserves_existing_env_values(self, runner, temp_dir):
        """init should preserve existing .env values while adding new ones."""
        target = temp_dir / "project"
        target.mkdir(parents=True)

        # Create existing .env with custom value
        env_path = target / ".env"
        env_path.write_text("OTHER_VAR=value\n")

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir", "_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        env_content = env_path.read_text()
        assert "OTHER_VAR=value" in env_content
        assert "ARX_PROJECT_ROOT=" in env_content

    def test_init_updates_existing_arx_values(self, runner, temp_dir):
        """init should update existing ARX_* values in .env."""
        target = temp_dir / "project"
        target.mkdir(parents=True)

        # Create existing .env with old ARX value
        env_path = target / ".env"
        env_path.write_text("ARX_AGENT_TOOLS=old_value\n")

        result = runner.invoke(
            cli,
            [
                "init",
                str(target),
                "--agents-dir", "new_agents",
                "--target-proj", "_project",
                "--proj-docs", "_project/docs",
                "--work-docs", "_project/docs/agentrx",
            ],
        )

        assert result.exit_code == 0
        env_content = env_path.read_text()
        # Old value should be updated, not duplicated
        assert env_content.count("ARX_AGENT_TOOLS") == 1
        assert "new_agents" in env_content


class TestRunInit:
    """Tests for _run_init function directly."""

    def test_uses_default_dirs_when_not_specified(self, temp_dir):
        """Should use default directories when none specified."""
        target = temp_dir / "project"

        _run_init(
            target_dir=str(target),
            link_arx=False,
            verbose=False,
            dry_run=False,
            agentrx_source=None,
            agents_dir=None,
            target_proj=None,
            proj_docs=None,
            work_docs=None,
            data_path=None,
        )

        assert (target / DEFAULT_AGENTS_DIR).exists()
        assert (target / DEFAULT_PROJECT_DIR).exists()

    def test_raises_for_link_without_source(self, temp_dir):
        """Should raise InitError for link mode without source."""
        target = temp_dir / "project"

        with pytest.raises(InitError) as exc_info:
            _run_init(
                target_dir=str(target),
                link_arx=True,
                verbose=False,
                dry_run=False,
                agentrx_source=None,
                agents_dir="_agents",
                target_proj="_project",
                proj_docs="_project/docs",
                work_docs="_project/docs/agentrx",
                data_path=None,
            )

        assert "requires" in str(exc_info.value).lower()

    def test_creates_docs_subdirs(self, temp_dir):
        """Should create docs subdirectories (deltas, vibes, history)."""
        target = temp_dir / "project"

        _run_init(
            target_dir=str(target),
            link_arx=False,
            verbose=False,
            dry_run=False,
            agentrx_source=None,
            agents_dir="_agents",
            target_proj="_project",
            proj_docs="_project/docs",
            work_docs="_project/docs/agentrx",
            data_path=None,
        )

        docs_dir = target / "_project" / "docs" / "agentrx"
        assert (docs_dir / "deltas").exists()
        assert (docs_dir / "vibes").exists()
        assert (docs_dir / "history").exists()


class TestTildeExpansion:
    """Tests for ~ (tilde) path expansion in _resolve_dirs / _run_init."""

    def test_tilde_agents_dir_expanded(self, temp_dir):
        """Tilde in --agents-dir should be expanded to $HOME, not treated as relative."""
        target = temp_dir / "project"
        tilde_path = "~/some_agents_dir"

        _run_init(
            target_dir=str(target),
            link_arx=False,
            verbose=False,
            dry_run=True,
            agentrx_source=None,
            agents_dir=tilde_path,
            target_proj="_project",
            proj_docs="_project/docs",
            work_docs="_project/docs/agentrx",
            data_path=None,
        )

        # The key assertion: ~ should NOT appear as a literal directory name
        bogus_path = target / "~" / "some_agents_dir"
        assert not bogus_path.exists(), (
            f"Tilde was treated as relative — created {bogus_path}"
        )

    def test_tilde_resolves_to_home(self, temp_dir):
        """Path with ~ should resolve to an absolute path under $HOME."""
        from agentrx.commands.init import _resolve_dirs

        target = temp_dir / "project"
        target.mkdir(parents=True, exist_ok=True)
        home = os.path.expanduser("~")

        agents, _, _, _ = _resolve_dirs(
            root=target,
            agents_dir="~/my_agents",
            target_proj="_project",
            proj_docs="_project/docs",
            work_docs="_project/docs/agentrx",
            interactive=False,
        )

        assert str(agents) == os.path.join(home, "my_agents")
        assert not str(agents).startswith(str(target))
