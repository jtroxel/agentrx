"""Tests for the prompt commands."""

import json
import os
import pytest
from datetime import datetime
from pathlib import Path
from click.testing import CliRunner

from agentrx.cli import cli
from agentrx.commands.prompt import (
    get_prompts_dir,
    get_history_dir,
    find_most_recent_prompt,
    write_history_entry,
    PromptError,
    DEFAULT_PROMPTS_DIR,
)
from agentrx.render import build_context


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_prompts_dir(tmp_path, monkeypatch):
    """Create a temporary prompts directory and set env var."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    monkeypatch.setenv("ARX_PROMPTS", str(prompts_dir))
    return prompts_dir


@pytest.fixture
def sample_prompts(temp_prompts_dir):
    """Create sample prompt files with different modification times."""
    import time

    prompts = []
    for i, name in enumerate(["old_prompt", "middle_prompt", "newest_prompt"]):
        path = temp_prompts_dir / f"{name}.md"
        path.write_text(f"# Prompt: {name}\n\nThis is {name} content.")
        prompts.append(path)
        time.sleep(0.1)  # Ensure different modification times

    return prompts


class TestGetPromptsDir:
    """Tests for get_prompts_dir function."""

    def test_returns_env_var_when_set(self, monkeypatch):
        """Should return ARX_PROMPTS env var when set."""
        monkeypatch.setenv("ARX_PROMPTS", "/custom/prompts")
        result = get_prompts_dir()
        assert result == Path("/custom/prompts")

    def test_returns_default_when_not_set(self, monkeypatch):
        """Should return default when ARX_PROMPTS not set."""
        monkeypatch.delenv("ARX_PROMPTS", raising=False)
        result = get_prompts_dir()
        assert result == Path(DEFAULT_PROMPTS_DIR)


class TestGetHistoryDir:
    """Tests for get_history_dir function."""

    def test_returns_env_var_when_set(self, monkeypatch):
        """Should return ARX_HISTORY env var when set."""
        monkeypatch.setenv("ARX_HISTORY", "/custom/history")
        result = get_history_dir()
        assert result == Path("/custom/history")

    def test_returns_default_subdirectory(self, monkeypatch):
        """Should return history subdirectory of prompts dir."""
        monkeypatch.delenv("ARX_HISTORY", raising=False)
        monkeypatch.setenv("ARX_PROMPTS", "/prompts")
        result = get_history_dir()
        assert result == Path("/prompts/history")


class TestFindMostRecentPrompt:
    """Tests for find_most_recent_prompt function."""

    def test_returns_none_for_nonexistent_dir(self, tmp_path):
        """Should return None if directory doesn't exist."""
        result = find_most_recent_prompt(tmp_path / "nonexistent")
        assert result is None

    def test_returns_none_for_empty_dir(self, tmp_path):
        """Should return None if no .md files exist."""
        result = find_most_recent_prompt(tmp_path)
        assert result is None

    def test_returns_most_recent_file(self, sample_prompts, temp_prompts_dir):
        """Should return the most recently modified file."""
        result = find_most_recent_prompt(temp_prompts_dir)
        assert result is not None
        assert result.name == "newest_prompt.md"


class TestBuildContext:
    """Tests for render.build_context (replaces load_json_data)."""

    def test_loads_from_file(self, tmp_path):
        """Should load JSON from data_file."""
        data_file = tmp_path / "data.json"
        data_file.write_text('{"key": "value"}')
        result = build_context(data_file=str(data_file))
        assert result == {"key": "value"}

    def test_loads_from_inline_json(self):
        """Should load JSON from data_json inline string."""
        result = build_context(data_json='{"stdin": "data"}')
        assert result == {"stdin": "data"}

    def test_merges_file_and_inline_json(self, tmp_path):
        """Inline JSON takes precedence over file."""
        data_file = tmp_path / "data.json"
        data_file.write_text('{"key": "file", "other": "value"}')
        result = build_context(data_file=str(data_file), data_json='{"key": "inline"}')
        assert result == {"key": "inline", "other": "value"}

    def test_raises_for_missing_file(self, tmp_path):
        """Should raise ValueError for missing file."""
        with pytest.raises(ValueError) as exc_info:
            build_context(data_file=str(tmp_path / "nonexistent.json"))
        assert "not found" in str(exc_info.value)

    def test_raises_for_invalid_json_file(self, tmp_path):
        """Should raise ValueError for invalid JSON in file."""
        data_file = tmp_path / "invalid.json"
        data_file.write_text("not valid json")
        with pytest.raises(ValueError) as exc_info:
            build_context(data_file=str(data_file))
        assert "Invalid JSON" in str(exc_info.value)

    def test_raises_for_invalid_inline_json(self):
        """Should raise ValueError for invalid inline JSON."""
        with pytest.raises(ValueError) as exc_info:
            build_context(data_json="not valid json")
        assert "Invalid JSON" in str(exc_info.value)


class TestWriteHistoryEntry:
    """Tests for write_history_entry function."""

    def test_creates_history_file(self, tmp_path):
        """Should create history entry file."""
        history_dir = tmp_path / "history"
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("# Test")

        result = write_history_entry(
            history_dir=history_dir,
            prompt_file=prompt_file,
            data_source="test.json",
            data={"key": "value"},
            output_file=None,
        )

        assert result.exists()
        assert result.parent.name == datetime.now().strftime("%Y-%m-%d")

    def test_history_content_is_valid_json(self, tmp_path):
        """Should write valid JSON content."""
        history_dir = tmp_path / "history"
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("# Test")

        result = write_history_entry(
            history_dir=history_dir,
            prompt_file=prompt_file,
            data_source="stdin",
            data={"test": "data"},
            output_file=tmp_path / "output.md",
        )

        content = json.loads(result.read_text())
        assert "timestamp" in content
        assert content["prompt_file"] == str(prompt_file)
        assert content["data_source"] == "stdin"
        assert content["data"] == {"test": "data"}


class TestPromptDoCommand:
    """Tests for the prompt do command."""

    def test_do_with_explicit_prompt_file(self, runner, temp_prompts_dir):
        """Should execute specified prompt file."""
        prompt_file = temp_prompts_dir / "test.md"
        prompt_file.write_text("# Test Prompt\n\nThis is a test.")

        result = runner.invoke(cli, ["prompt", "do", str(prompt_file)])
        assert result.exit_code == 0
        assert "Test Prompt" in result.output

    def test_do_with_most_recent(self, runner, sample_prompts, temp_prompts_dir):
        """Should use most recent prompt when none specified."""
        result = runner.invoke(cli, ["prompt", "do"])
        assert result.exit_code == 0
        assert "newest_prompt" in result.output

    def test_do_with_data_file(self, runner, temp_prompts_dir, tmp_path):
        """Should render template with data from file."""
        prompt_file = temp_prompts_dir / "test.md"
        prompt_file.write_text("Hello <ARX [[user]] />!")

        data_file = tmp_path / "data.json"
        data_file.write_text('{"user": "alice"}')

        result = runner.invoke(cli, [
            "prompt", "do", str(prompt_file),
            "--data", str(data_file)
        ])
        assert result.exit_code == 0
        assert "alice" in result.output

    def test_do_dry_run(self, runner, temp_prompts_dir):
        """--dry-run should show execution plan without running."""
        prompt_file = temp_prompts_dir / "test.md"
        prompt_file.write_text("# Dry run test")

        result = runner.invoke(cli, [
            "prompt", "do", str(prompt_file), "--dry-run"
        ])
        assert result.exit_code == 0
        assert "Dry Run" in result.output
        assert str(prompt_file) in result.output

    def test_do_with_history(self, runner, temp_prompts_dir, monkeypatch):
        """--history should create history entry."""
        history_dir = temp_prompts_dir / "history"
        monkeypatch.setenv("ARX_HISTORY", str(history_dir))

        prompt_file = temp_prompts_dir / "test.md"
        prompt_file.write_text("# History test")

        result = runner.invoke(cli, [
            "prompt", "do", str(prompt_file), "--history", "-v"
        ])
        assert result.exit_code == 0
        assert history_dir.exists()
        # Check that history file was created
        history_files = list(history_dir.rglob("*.json"))
        assert len(history_files) == 1

    def test_do_with_output_file(self, runner, temp_prompts_dir, tmp_path):
        """--output should write to file."""
        prompt_file = temp_prompts_dir / "test.md"
        prompt_file.write_text("# Output test")

        output_file = tmp_path / "output.md"

        result = runner.invoke(cli, [
            "prompt", "do", str(prompt_file),
            "--output", str(output_file)
        ])
        assert result.exit_code == 0
        assert output_file.exists()
        assert "Output test" in output_file.read_text()

    def test_do_fails_for_missing_prompt(self, runner, tmp_path, monkeypatch):
        """Should fail if prompt file doesn't exist."""
        monkeypatch.setenv("ARX_PROMPTS", str(tmp_path))

        result = runner.invoke(cli, [
            "prompt", "do", "nonexistent.md"
        ])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_do_fails_for_empty_prompts_dir(self, runner, tmp_path, monkeypatch):
        """Should fail if prompts dir is empty and no file specified."""
        monkeypatch.setenv("ARX_PROMPTS", str(tmp_path))

        result = runner.invoke(cli, ["prompt", "do"])
        assert result.exit_code == 1
        assert "No prompt files" in result.output


class TestPromptNewCommand:
    """Tests for the prompt new command."""

    def test_new_plain_text(self, runner, temp_prompts_dir):
        """Plain text (no template) should create a file in ARX_WORK_DOCS/vibes/."""
        result = runner.invoke(cli, ["prompt", "new", "Test prompt content"])
        assert result.exit_code == 0
        # Output path is printed; file must exist
        out_path = result.output.strip()
        assert out_path.endswith(".md")

    def test_new_with_custom_name(self, runner, temp_prompts_dir):
        """--name should set the base filename."""
        result = runner.invoke(cli, [
            "prompt", "new", "Test content", "--name", "my_custom_name"
        ])
        assert result.exit_code == 0
        out_path = result.output.strip()
        assert "my_custom_name" in out_path

    def test_new_with_custom_subdir(self, runner, temp_prompts_dir, tmp_path):
        """--subdir should write into that subdir of ARX_WORK_DOCS."""
        result = runner.invoke(cli, [
            "prompt", "new", "Test", "--subdir", "deltas"
        ])
        assert result.exit_code == 0
        out_path = result.output.strip()
        assert "deltas" in out_path

    def test_new_from_template_file(self, runner, temp_prompts_dir, tmp_path):
        """Template file: [[prompt]] :new tag should be substituted."""
        tmpl = tmp_path / "my_tmpl.md"
        tmpl.write_text("---\narx: template\nsubdir: vibes\n---\n# <ARX [[prompt]] :new />\n")
        result = runner.invoke(cli, [
            "prompt", "new", str(tmpl), "Fix the auth bug"
        ])
        assert result.exit_code == 0
        out_path = result.output.strip()
        content = Path(out_path).read_text()
        assert "Fix the auth bug" in content

    def test_new_phase_do_tag_preserved(self, runner, temp_prompts_dir, tmp_path):
        """:do tags in a template must survive the :new render pass."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text("---\narx: template\n---\n<ARX [[user.name]] :do />\n")
        result = runner.invoke(cli, [
            "prompt", "new", str(tmpl), "Some prompt"
        ])
        assert result.exit_code == 0
        out_path = result.output.strip()
        content = Path(out_path).read_text()
        # :do tag must still be in the saved file
        assert "<ARX [[user.name]] :do />" in content

    def test_new_dry_run(self, runner, temp_prompts_dir, tmp_path):
        """--dry-run should not create a file."""
        result = runner.invoke(cli, [
            "prompt", "new", "Check this out", "--dry-run"
        ])
        assert result.exit_code == 0
        assert "Dry Run" in result.output
        # No files written
        vibes = temp_prompts_dir / "vibes"
        assert not vibes.exists() or len(list(vibes.glob("*.md"))) == 0

    def test_new_first_arg_fallback_to_prompt_text(self, runner, temp_prompts_dir):
        """If first arg doesn't resolve as a template, treat it as prompt text."""
        result = runner.invoke(cli, ["prompt", "new", "Implement user auth"])
        assert result.exit_code == 0
        out_path = result.output.strip()
        assert out_path.endswith(".md")


class TestPromptListCommand:
    """Tests for the prompt list command."""

    def test_list_shows_prompts(self, runner, sample_prompts, temp_prompts_dir):
        """Should list prompt files."""
        result = runner.invoke(cli, ["prompt", "list"])
        assert result.exit_code == 0
        assert "newest_prompt.md" in result.output
        assert "old_prompt.md" in result.output

    def test_list_respects_limit(self, runner, sample_prompts, temp_prompts_dir):
        """Should respect -n limit."""
        result = runner.invoke(cli, ["prompt", "list", "-n", "1"])
        assert result.exit_code == 0
        assert "newest_prompt.md" in result.output
        # Should show "and X more"
        assert "more" in result.output

    def test_list_empty_dir(self, runner, temp_prompts_dir):
        """Should handle empty directory."""
        result = runner.invoke(cli, ["prompt", "list"])
        assert result.exit_code == 0
        assert "No prompt files" in result.output

    def test_list_with_custom_dir(self, runner, tmp_path):
        """--dir should list from specified directory."""
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        (custom_dir / "custom_prompt.md").write_text("# Custom")

        result = runner.invoke(cli, [
            "prompt", "list", "--dir", str(custom_dir)
        ])
        assert result.exit_code == 0
        assert "custom_prompt.md" in result.output
