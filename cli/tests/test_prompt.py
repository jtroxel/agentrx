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
    load_json_data,
    write_history_entry,
    PromptError,
    DEFAULT_PROMPTS_DIR,
)


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


class TestLoadJsonData:
    """Tests for load_json_data function."""

    def test_loads_from_file(self, tmp_path):
        """Should load JSON from file."""
        data_file = tmp_path / "data.json"
        data_file.write_text('{"key": "value"}')
        result = load_json_data(data_file, None)
        assert result == {"key": "value"}

    def test_loads_from_stdin(self):
        """Should load JSON from stdin."""
        result = load_json_data(None, '{"stdin": "data"}')
        assert result == {"stdin": "data"}

    def test_merges_file_and_stdin(self, tmp_path):
        """Should merge file and stdin data, stdin takes precedence."""
        data_file = tmp_path / "data.json"
        data_file.write_text('{"key": "file", "other": "value"}')
        result = load_json_data(data_file, '{"key": "stdin"}')
        assert result == {"key": "stdin", "other": "value"}

    def test_raises_for_missing_file(self, tmp_path):
        """Should raise PromptError for missing file."""
        with pytest.raises(PromptError) as exc_info:
            load_json_data(tmp_path / "nonexistent.json", None)
        assert "not found" in str(exc_info.value)

    def test_raises_for_invalid_json_file(self, tmp_path):
        """Should raise PromptError for invalid JSON in file."""
        data_file = tmp_path / "invalid.json"
        data_file.write_text("not valid json")
        with pytest.raises(PromptError) as exc_info:
            load_json_data(data_file, None)
        assert "Invalid JSON" in str(exc_info.value)

    def test_raises_for_invalid_json_stdin(self):
        """Should raise PromptError for invalid JSON from stdin."""
        with pytest.raises(PromptError) as exc_info:
            load_json_data(None, "not valid json")
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
        """Should include data from file."""
        prompt_file = temp_prompts_dir / "test.md"
        prompt_file.write_text("# Test with data")

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

    def test_new_creates_file(self, runner, temp_prompts_dir):
        """Should create prompt file."""
        result = runner.invoke(cli, [
            "prompt", "new", "Test prompt content"
        ])
        assert result.exit_code == 0

        # Check file was created
        md_files = list(temp_prompts_dir.glob("*.md"))
        assert len(md_files) == 1

    def test_new_with_custom_name(self, runner, temp_prompts_dir):
        """Should use provided short name."""
        result = runner.invoke(cli, [
            "prompt", "new", "Test content", "my_custom_name"
        ])
        assert result.exit_code == 0

        md_files = list(temp_prompts_dir.glob("my_custom_name_*.md"))
        assert len(md_files) == 1

    def test_new_with_custom_dir(self, runner, tmp_path):
        """--dir should create in specified directory."""
        custom_dir = tmp_path / "custom"

        result = runner.invoke(cli, [
            "prompt", "new", "Test", "--dir", str(custom_dir)
        ])
        assert result.exit_code == 0
        assert custom_dir.exists()
        md_files = list(custom_dir.glob("*.md"))
        assert len(md_files) == 1

    def test_new_file_content(self, runner, temp_prompts_dir):
        """Should create file with correct content structure."""
        result = runner.invoke(cli, [
            "prompt", "new", "My test prompt content", "test"
        ])
        assert result.exit_code == 0

        md_files = list(temp_prompts_dir.glob("test_*.md"))
        content = md_files[0].read_text()
        assert "# Prompt: test" in content
        assert "My test prompt content" in content
        assert "Created:" in content


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
