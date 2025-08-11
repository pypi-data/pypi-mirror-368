"""Tests for the `quickstart` CLI command."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from rag_startups.cli import app

runner = CliRunner()


@pytest.fixture()
def tmp_workdir(tmp_path):
    """Change to a temporary working directory for the duration of a test."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield Path(tmp_path)
    finally:
        os.chdir(cwd)


def _mock_download(*args, **kwargs):  # noqa: D401  (simple style acceptable for tests)
    """Return a fake path when `hf_hub_download` is invoked during tests."""
    return "/fake/model/path"


@pytest.fixture()
def quickstart_env(monkeypatch):
    """Patch heavy external calls used by quickstart for fast, offline tests."""
    # Mock the model download to avoid network IO
    monkeypatch.setattr("rag_startups.cli.hf_hub_download", _mock_download)

    # Mock StartupIdeaGenerator.generate so we avoid actual model invocation
    with patch("rag_startups.cli.StartupIdeaGenerator") as mock_gen:
        instance = mock_gen.return_value
        instance.generate.return_value = (  # noqa: WPS442 (explicit tuple for clarity)
            "Example startup idea generated during quickstart.",
            {},
        )
        yield instance


def test_quickstart_creates_env_file(tmp_workdir, quickstart_env, monkeypatch):
    """Ensure the quickstart command exits successfully and creates `.env`."""
    # Provide a fake token via env to skip interactive prompt
    monkeypatch.setenv("HUGGINGFACE_TOKEN", "test123")

    result = runner.invoke(app, ["quickstart", "--no-input"])

    assert result.exit_code == 0, result.stdout
    env_path = tmp_workdir / ".env"
    assert env_path.exists(), "`.env` file should be created by quickstart"

    content = env_path.read_text()
    assert "HUGGINGFACE_TOKEN=test123" in content
    # Ensure our mocked generator was invoked to perform example query
    quickstart_env.generate.assert_called_once()
