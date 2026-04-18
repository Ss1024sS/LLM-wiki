"""Sanity-check the Claude plugin manifests so a typo doesn't break install."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_plugin_json_parses_and_has_required_fields() -> None:
    data = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    for key in ("name", "version", "description"):
        assert key in data, f"plugin.json missing required key: {key}"
    assert data["name"] == "llm-wiki"
    for skill_path in data.get("skills", []):
        assert (REPO / skill_path / "SKILL.md").exists(), f"skill missing: {skill_path}/SKILL.md"


def test_marketplace_json_parses() -> None:
    data = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert data["name"] == "llm-wiki"
    assert data["plugins"][0]["name"] == "llm-wiki"


def test_plugin_commands_have_frontmatter() -> None:
    commands_dir = REPO / "commands"
    if not commands_dir.exists():
        pytest.skip("no commands dir")
    found = list(commands_dir.glob("*.md"))
    assert found, "expected at least one plugin command"
    for cmd in found:
        text = cmd.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{cmd.name} missing YAML frontmatter"
        assert "description:" in text.split("---")[1], f"{cmd.name} missing description in frontmatter"
