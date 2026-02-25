"""Tests for the prompt commands."""

import json
import os
import stat
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner

from agentrx.cli import cli
from agentrx.commands.prompt import (
    get_prompts_dir,
    get_history_dir,
    find_most_recent_prompt,
    write_history_entry,
    PromptError,
    DEFAULT_PROMPTS_DIR,
    _find_template,
    _resolve_template_arg,
    _derive_short_name,
    _build_output_path,
    _run_context_script,
    _render_template_stage,
    _template_search_dirs,
    _DEFAULT_SUBDIR,
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


# ===================================================================
# prompt new — unit tests for helper functions
# ===================================================================


class TestDeriveShortName:
    """Tests for _derive_short_name helper."""

    def test_three_words(self):
        """Takes first three words, lowercased, joined with underscore."""
        assert _derive_short_name("Fix the Auth bug") == "fix_the_auth"

    def test_fewer_than_three_words(self):
        """Works with fewer than three words."""
        assert _derive_short_name("Refactor") == "refactor"
        assert _derive_short_name("Fix bugs") == "fix_bugs"

    def test_strips_non_alphanumeric(self):
        """Non-alphanumeric chars are stripped from each word."""
        assert _derive_short_name("Fix: the, bug!") == "fix_the_bug"

    def test_empty_string(self):
        """Empty string falls back to 'prompt'."""
        assert _derive_short_name("") == "prompt"

    def test_special_chars_only(self):
        """Words of only special chars produce empty tokens → underscores."""
        # Each word becomes "" after stripping, joined with "_"
        result = _derive_short_name("!!! ??? ###")
        assert result == "__"


class TestBuildOutputPath:
    """Tests for _build_output_path helper."""

    def test_structure(self, tmp_path):
        """Output path has work_docs/subdir/name_timestamp.md structure."""
        result = _build_output_path(tmp_path, "vibes", "my_name")
        assert result.parent.parent == tmp_path
        assert result.parent.name == "vibes"
        assert result.name.startswith("my_name_")
        assert result.suffix == ".md"

    def test_timestamp_format(self, tmp_path):
        """Filename ends with YY-MM-DD-HH timestamp."""
        result = _build_output_path(tmp_path, "deltas", "test")
        ts_part = result.stem.split("_", 1)[1]  # everything after "test_"
        # Validate it matches YY-MM-DD-HH
        assert len(ts_part) == 11  # e.g., "25-06-15-14"

    def test_custom_subdir(self, tmp_path):
        """Subdir is used as intermediate directory name."""
        result = _build_output_path(tmp_path, "custom/nested", "test")
        assert "custom" in str(result)


class TestTemplateSearchDirs:
    """Tests for _template_search_dirs helper."""

    def test_returns_empty_when_no_env(self, monkeypatch):
        """No env vars → empty list."""
        monkeypatch.delenv("ARX_AGENT_TOOLS", raising=False)
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        assert _template_search_dirs() == []

    def test_includes_agent_tools(self, monkeypatch):
        """ARX_AGENT_TOOLS set → includes templates subdir."""
        monkeypatch.setenv("ARX_AGENT_TOOLS", "/tools")
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        dirs = _template_search_dirs()
        assert len(dirs) == 1
        assert dirs[0] == Path("/tools/templates")

    def test_includes_agentrx_source(self, monkeypatch):
        """AGENTRX_SOURCE set → includes templates subdir."""
        monkeypatch.delenv("ARX_AGENT_TOOLS", raising=False)
        monkeypatch.setenv("AGENTRX_SOURCE", "/src")
        dirs = _template_search_dirs()
        assert len(dirs) == 1
        assert dirs[0] == Path("/src/templates")

    def test_order_agent_tools_first(self, monkeypatch):
        """ARX_AGENT_TOOLS searched before AGENTRX_SOURCE."""
        monkeypatch.setenv("ARX_AGENT_TOOLS", "/tools")
        monkeypatch.setenv("AGENTRX_SOURCE", "/src")
        dirs = _template_search_dirs()
        assert len(dirs) == 2
        assert dirs[0] == Path("/tools/templates")
        assert dirs[1] == Path("/src/templates")


class TestFindTemplate:
    """Tests for _find_template helper."""

    def test_direct_path(self, tmp_path):
        """Direct path to existing file resolves immediately."""
        f = tmp_path / "tmpl.md"
        f.write_text("hello")
        assert _find_template(str(f)) == f

    def test_direct_path_with_md_suffix(self, tmp_path, monkeypatch):
        """Path without .md suffix resolves when .md file exists."""
        f = tmp_path / "tmpl.md"
        f.write_text("hello")
        monkeypatch.chdir(tmp_path)
        result = _find_template("tmpl")
        # Returns relative path from cwd; resolve to compare
        assert result is not None
        assert result.resolve() == f.resolve()

    def test_search_agent_tools_dir(self, tmp_path, monkeypatch):
        """Named template found in ARX_AGENT_TOOLS/templates/."""
        tmpl_dir = tmp_path / "tools" / "templates"
        tmpl_dir.mkdir(parents=True)
        f = tmpl_dir / "vibes.md"
        f.write_text("template")
        monkeypatch.setenv("ARX_AGENT_TOOLS", str(tmp_path / "tools"))
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        assert _find_template("vibes") == f

    def test_search_agentrx_source_dir(self, tmp_path, monkeypatch):
        """Named template found in AGENTRX_SOURCE/templates/."""
        tmpl_dir = tmp_path / "src" / "templates"
        tmpl_dir.mkdir(parents=True)
        f = tmpl_dir / "delta.md"
        f.write_text("template")
        monkeypatch.delenv("ARX_AGENT_TOOLS", raising=False)
        monkeypatch.setenv("AGENTRX_SOURCE", str(tmp_path / "src"))
        assert _find_template("delta") == f

    def test_agent_tools_searched_before_source(self, tmp_path, monkeypatch):
        """When both dirs have a match, ARX_AGENT_TOOLS wins."""
        tools_tmpl = tmp_path / "tools" / "templates" / "shared.md"
        tools_tmpl.parent.mkdir(parents=True)
        tools_tmpl.write_text("from tools")
        src_tmpl = tmp_path / "src" / "templates" / "shared.md"
        src_tmpl.parent.mkdir(parents=True)
        src_tmpl.write_text("from src")
        monkeypatch.setenv("ARX_AGENT_TOOLS", str(tmp_path / "tools"))
        monkeypatch.setenv("AGENTRX_SOURCE", str(tmp_path / "src"))
        assert _find_template("shared") == tools_tmpl

    def test_returns_none_when_not_found(self, tmp_path, monkeypatch):
        """Returns None when template cannot be resolved anywhere."""
        monkeypatch.delenv("ARX_AGENT_TOOLS", raising=False)
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        monkeypatch.chdir(tmp_path)
        assert _find_template("nonexistent_template") is None

    def test_exact_name_with_extension(self, tmp_path, monkeypatch):
        """Named template with explicit .md extension in search dirs."""
        tmpl_dir = tmp_path / "tools" / "templates"
        tmpl_dir.mkdir(parents=True)
        f = tmpl_dir / "vibes.md"
        f.write_text("template")
        monkeypatch.setenv("ARX_AGENT_TOOLS", str(tmp_path / "tools"))
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        # Passing "vibes.md" should match directly
        assert _find_template("vibes.md") == f


class TestResolveTemplateArg:
    """Tests for _resolve_template_arg helper."""

    def test_no_template(self):
        """No template arg → (None, prompt_text)."""
        result = _resolve_template_arg(None, "hello")
        assert result == (None, "hello")

    def test_no_template_no_text(self):
        """Both None → (None, None)."""
        result = _resolve_template_arg(None, None)
        assert result == (None, None)

    def test_valid_template_resolves(self, tmp_path):
        """Existing file template → (path, prompt_text)."""
        f = tmp_path / "tmpl.md"
        f.write_text("template")
        path, text = _resolve_template_arg(str(f), "some text")
        assert path == f
        assert text == "some text"

    def test_template_not_found_no_text_fallback(self, monkeypatch, tmp_path):
        """Template doesn't resolve + no prompt_text → treat as plain text."""
        monkeypatch.delenv("ARX_AGENT_TOOLS", raising=False)
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        monkeypatch.chdir(tmp_path)
        path, text = _resolve_template_arg("not_a_template", None)
        assert path is None
        assert text == "not_a_template"

    def test_template_not_found_with_text_raises(self, monkeypatch, tmp_path):
        """Template doesn't resolve + prompt_text given → ambiguous, raises."""
        monkeypatch.delenv("ARX_AGENT_TOOLS", raising=False)
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        monkeypatch.chdir(tmp_path)
        with pytest.raises(PromptError, match="Template not found"):
            _resolve_template_arg("bad_template", "some text")


class TestRunContextScript:
    """Tests for _run_context_script helper."""

    def test_merges_script_output(self, tmp_path):
        """Script stdout JSON is returned as dict."""
        script = tmp_path / "ctx.sh"
        script.write_text('#!/bin/sh\necho \'{"extra": "data"}\'\n')
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

        result = _run_context_script(str(script), {"existing": "val"})
        assert result == {"extra": "data"}

    def test_receives_context_on_stdin(self, tmp_path):
        """Script receives current context as JSON on stdin."""
        script = tmp_path / "echo.sh"
        # Script reads stdin and echoes it back
        script.write_text('#!/bin/sh\ncat\n')
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

        result = _run_context_script(str(script), {"key": "value"})
        assert result == {"key": "value"}

    def test_raises_on_script_not_found(self):
        """Missing script raises PromptError."""
        with pytest.raises(PromptError, match="not found"):
            _run_context_script("/nonexistent/script.sh", {})

    def test_raises_on_nonzero_exit(self, tmp_path):
        """Non-zero exit code raises PromptError."""
        script = tmp_path / "fail.sh"
        script.write_text('#!/bin/sh\necho "oops" >&2\nexit 1\n')
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

        with pytest.raises(PromptError, match="exited 1"):
            _run_context_script(str(script), {})

    def test_raises_on_non_json_output(self, tmp_path):
        """Non-JSON stdout raises PromptError."""
        script = tmp_path / "badjson.sh"
        script.write_text('#!/bin/sh\necho "not json"\n')
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

        with pytest.raises(PromptError, match="non-JSON"):
            _run_context_script(str(script), {})


class TestRenderTemplateStage:
    """Tests for _render_template_stage helper."""

    def test_renders_new_phase_tags(self, tmp_path):
        """ARX :new tags are resolved during render."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text("---\narx: template\n---\nHello <ARX [[user]] :new />!")
        fm, body = _render_template_stage(tmpl, {"user": "Alice"}, verbose=False)
        assert "Hello Alice!" in body
        assert fm is not None
        assert fm.get("arx") == "template"

    def test_preserves_do_phase_tags(self, tmp_path):
        """:do tags survive the :new render pass."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\n---\n"
            "<ARX [[name]] :new /> and <ARX [[later]] :do />"
        )
        fm, body = _render_template_stage(
            tmpl, {"name": "Bob"}, verbose=False
        )
        assert "Bob" in body
        assert "<ARX [[later]] :do />" in body

    def test_unphased_tags_resolved(self, tmp_path):
        """Tags without a phase marker are always resolved."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text("---\narx: template\n---\nGreet: <ARX [[greeting]] />")
        _fm, body = _render_template_stage(
            tmpl, {"greeting": "hi"}, verbose=False
        )
        assert "Greet: hi" in body

    def test_missing_template_raises(self, tmp_path):
        """Non-existent template file raises PromptError."""
        with pytest.raises(PromptError, match="Failed to read template"):
            _render_template_stage(
                tmp_path / "nope.md", {}, verbose=False
            )

    def test_context_script_runs_and_re_renders(self, tmp_path):
        """Front-matter script: field triggers context script then re-render."""
        script = tmp_path / "inject.sh"
        script.write_text('#!/bin/sh\necho \'{"injected": "yes"}\'\n')
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            f"---\narx: template\nscript: {script}\n---\n"
            "Val: <ARX [[injected]] :new />"
        )
        _fm, body = _render_template_stage(tmpl, {}, verbose=False)
        assert "Val: yes" in body


# ===================================================================
# prompt new — integration / CLI tests
# ===================================================================


class TestPromptNewIntegration:
    """Integration tests for `arx prompt new` CLI command."""

    @pytest.fixture(autouse=True)
    def setup_work_docs(self, tmp_path, monkeypatch):
        """Set ARX_WORK_DOCS so output goes to tmp_path."""
        self.work_docs = tmp_path / "docs"
        self.work_docs.mkdir()
        monkeypatch.setenv("ARX_WORK_DOCS", str(self.work_docs))
        # Ensure search dirs don't leak from real env
        monkeypatch.delenv("ARX_AGENT_TOOLS", raising=False)
        monkeypatch.delenv("AGENTRX_SOURCE", raising=False)
        monkeypatch.delenv("ARX_PROMPTS", raising=False)
        self.runner = CliRunner()

    def test_plain_text_creates_file(self):
        """Plain text prompt creates file in vibes subdir."""
        result = self.runner.invoke(cli, ["prompt", "new", "Implement user auth"])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.exists()
        assert out_path.parent.name == "vibes"
        assert out_path.read_text() == "Implement user auth"

    def test_plain_text_derives_name(self):
        """Output filename is derived from first three words."""
        result = self.runner.invoke(cli, ["prompt", "new", "Fix the cache bug"])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.name.startswith("fix_the_cache_")

    def test_name_option_overrides(self):
        """--name overrides derived short name."""
        result = self.runner.invoke(cli, [
            "prompt", "new", "Do something", "--name", "custom"
        ])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.name.startswith("custom_")

    def test_subdir_option_overrides(self):
        """--subdir overrides default vibes subdir."""
        result = self.runner.invoke(cli, [
            "prompt", "new", "Delta prompt", "--subdir", "deltas"
        ])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.parent.name == "deltas"

    def test_template_with_prompt_text(self, tmp_path):
        """Template file with [[prompt]] :new tag substitutes user text."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\nsubdir: vibes\n---\n"
            "## Task\n<ARX [[prompt]] :new />\n"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "Fix the auth bug"
        ])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        content = out_path.read_text()
        assert "Fix the auth bug" in content
        assert "## Task" in content

    def test_template_front_matter_subdir(self, tmp_path):
        """Template front-matter subdir field controls output location."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\nsubdir: deltas\n---\nContent"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "test"
        ])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.parent.name == "deltas"

    def test_template_front_matter_short_name(self, tmp_path):
        """Template front-matter short_name field controls filename."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\nshort_name: my_delta\n---\nContent"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "test"
        ])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.name.startswith("my_delta_")

    def test_do_phase_tags_preserved_in_output(self, tmp_path):
        """:do phase tags survive through to the written file."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\n---\n"
            "<ARX [[prompt]] :new />\n"
            "<ARX [[runtime_var]] :do />\n"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "my task"
        ])
        assert result.exit_code == 0
        content = Path(result.output.strip()).read_text()
        assert "my task" in content
        assert "<ARX [[runtime_var]] :do />" in content

    def test_data_json_merged_into_context(self, tmp_path):
        """--data JSON values are available in template rendering."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\n---\n"
            "Ticket: <ARX [[ticket]] :new />"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "Fix it",
            "--data", '{"ticket": "ENG-42"}'
        ])
        assert result.exit_code == 0
        content = Path(result.output.strip()).read_text()
        assert "Ticket: ENG-42" in content

    def test_dry_run_no_file_created(self):
        """--dry-run shows plan but does not write any file."""
        result = self.runner.invoke(cli, [
            "prompt", "new", "Check this out", "--dry-run"
        ])
        assert result.exit_code == 0
        assert "Dry Run" in result.output
        # No vibes subdir created
        vibes = self.work_docs / "vibes"
        assert not vibes.exists() or len(list(vibes.glob("*.md"))) == 0

    def test_dry_run_shows_output_path(self):
        """--dry-run output includes the would-be output path."""
        result = self.runner.invoke(cli, [
            "prompt", "new", "Preview me", "--dry-run"
        ])
        assert result.exit_code == 0
        assert "Output:" in result.output
        assert "vibes" in result.output

    def test_verbose_shows_created_message(self):
        """-v flag shows 'Created:' message."""
        result = self.runner.invoke(cli, [
            "prompt", "new", "Verbose test", "-v"
        ])
        assert result.exit_code == 0
        assert "Created:" in result.output

    def test_no_args_raises_error(self):
        """No template and no prompt text → error."""
        result = self.runner.invoke(cli, ["prompt", "new"])
        assert result.exit_code == 1
        assert "Provide" in result.output or "Error" in result.output

    def test_ambiguous_template_raises_error(self, tmp_path, monkeypatch):
        """Non-resolving template + prompt text → ambiguous error."""
        monkeypatch.chdir(tmp_path)
        result = self.runner.invoke(cli, [
            "prompt", "new", "nonexistent_template", "some prompt text"
        ])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_first_arg_fallback_to_prompt_text(self):
        """If first arg doesn't resolve as template, treat as prompt text."""
        result = self.runner.invoke(cli, ["prompt", "new", "Just a prompt"])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.exists()

    def test_template_from_search_dir(self, tmp_path, monkeypatch):
        """Named template resolved from AGENTRX_SOURCE/templates/."""
        tmpl_dir = tmp_path / "source" / "templates"
        tmpl_dir.mkdir(parents=True)
        tmpl = tmpl_dir / "vibes.md"
        tmpl.write_text(
            "---\narx: template\nsubdir: vibes\n---\n"
            "## <ARX [[prompt]] :new />"
        )
        monkeypatch.setenv("AGENTRX_SOURCE", str(tmp_path / "source"))
        result = self.runner.invoke(cli, [
            "prompt", "new", "vibes", "Build the feature"
        ])
        assert result.exit_code == 0
        content = Path(result.output.strip()).read_text()
        assert "Build the feature" in content

    def test_subdir_option_overrides_front_matter(self, tmp_path):
        """--subdir CLI option takes precedence over template front-matter."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\nsubdir: fm_subdir\n---\nContent"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "test",
            "--subdir", "cli_subdir"
        ])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.parent.name == "cli_subdir"

    def test_name_option_overrides_front_matter(self, tmp_path):
        """--name CLI option takes precedence over template short_name."""
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            "---\narx: template\nshort_name: fm_name\n---\nContent"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "test",
            "--name", "cli_name"
        ])
        assert result.exit_code == 0
        out_path = Path(result.output.strip())
        assert out_path.name.startswith("cli_name_")

    def test_template_with_context_script(self, tmp_path):
        """Template with front-matter script: runs context script."""
        script = tmp_path / "ctx.sh"
        script.write_text('#!/bin/sh\necho \'{"injected": "from_script"}\'\n')
        script.chmod(script.stat().st_mode | stat.S_IEXEC)

        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text(
            f"---\narx: template\nscript: {script}\n---\n"
            "Val: <ARX [[injected]] :new />"
        )
        result = self.runner.invoke(cli, [
            "prompt", "new", str(tmpl), "test"
        ])
        assert result.exit_code == 0
        content = Path(result.output.strip()).read_text()
        assert "Val: from_script" in content
