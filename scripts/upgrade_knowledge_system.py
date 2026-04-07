"""
Upgrade an existing LLM-wiki project to the latest version.

Updates scripts and CI workflow without touching wiki content or user configs.

Usage:
  python3 scripts/upgrade_knowledge_system.py /path/to/your-project

What gets UPDATED (safe to overwrite):
  - scripts/wiki_check.py
  - scripts/raw_manifest_check.py
  - scripts/untracked_raw_check.py
  - scripts/provenance_check.py
  - scripts/init_raw_root.py
  - scripts/export_memory_repo.py
  - .github/workflows/wiki-lint.yml

What gets SKIPPED (user content, never touched):
  - docs/wiki/*.md (your wiki pages)
  - manifests/*.csv (your raw index)
  - AGENTS.md / CLAUDE.md / .cursorrules / .windsurfrules (your customized configs)

What gets SHOWN as diff (you decide):
  - Template changes to platform configs (printed, not applied)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_URL = "https://github.com/Ss1024sS/LLM-wiki.git"
VERSION_RE = re.compile(r"# llm-wiki-version:\s*(\S+)")


def detect_local_version(project: Path) -> str:
    for script in ["wiki_check.py", "raw_manifest_check.py", "provenance_check.py"]:
        path = project / "scripts" / script
        if path.exists():
            text = path.read_text(encoding="utf-8")
            m = VERSION_RE.search(text)
            if m:
                return m.group(1)
    return "unknown"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/upgrade_knowledge_system.py /path/to/your-project")
        return 1

    project = Path(sys.argv[1]).expanduser().resolve()
    if not (project / "docs" / "wiki").exists():
        print(f"Error: {project} does not look like an LLM-wiki project (no docs/wiki/)")
        return 1

    local_version = detect_local_version(project)
    print(f"Current version: {local_version}")

    # Clone latest LLM-wiki to temp dir
    print("Fetching latest LLM-wiki...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(tmp / "repo")],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"Error cloning: {result.stderr}")
            return 1

        bootstrap = tmp / "repo" / "skills" / "knowledge-system-bootstrap" / "scripts" / "bootstrap_knowledge_system.py"
        if not bootstrap.exists():
            print("Error: bootstrap script not found in cloned repo")
            return 1

        # Bootstrap to a temp project to get the latest generated files
        temp_project = tmp / "generated"
        result = subprocess.run(
            [sys.executable, str(bootstrap), str(temp_project), "Upgrade"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"Error running bootstrap: {result.stderr}")
            return 1

        new_version = detect_local_version(temp_project)
        print(f"Latest version:  {new_version}")

        if local_version == new_version:
            print("\nAlready up to date!")
            return 0

        # Update scripts (safe to overwrite)
        updated = []
        safe_files = [
            "scripts/wiki_check.py",
            "scripts/raw_manifest_check.py",
            "scripts/untracked_raw_check.py",
            "scripts/provenance_check.py",
            "scripts/init_raw_root.py",
            "scripts/export_memory_repo.py",
            ".github/workflows/wiki-lint.yml",
        ]

        for rel in safe_files:
            src = temp_project / rel
            dst = project / rel
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                updated.append(rel)

        print(f"\nUpdated {len(updated)} files:")
        for f in updated:
            print(f"  + {f}")

        # Show config diffs (not applied)
        config_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules", ".windsurfrules"]
        diffs = []
        for rel in config_files:
            src = temp_project / rel
            dst = project / rel
            if src.exists() and dst.exists():
                old = dst.read_text(encoding="utf-8")
                new = src.read_text(encoding="utf-8")
                if old != new:
                    diffs.append(rel)

        if diffs:
            print(f"\nConfig templates have changed ({len(diffs)} files):")
            for f in diffs:
                print(f"  ~ {f}")
            print("\nThese are NOT auto-updated (you may have customized them).")
            print("Review the latest templates and merge manually if needed:")
            print(f"  Latest templates: {temp_project}")
            # Actually let's print the new template content for easy copy
            for f in diffs:
                src = temp_project / f
                print(f"\n--- NEW {f} ---")
                print(src.read_text(encoding="utf-8"))
                print(f"--- END {f} ---")
        else:
            print("\nConfig templates: no changes.")

        # Check for new scripts that don't exist yet
        new_scripts = []
        for path in (temp_project / "scripts").iterdir():
            if path.is_file() and not (project / "scripts" / path.name).exists():
                dst = project / "scripts" / path.name
                dst.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
                new_scripts.append(f"scripts/{path.name}")

        if new_scripts:
            print(f"\nNew scripts added:")
            for f in new_scripts:
                print(f"  + {f}")

        print(f"\nUpgrade complete: {local_version} -> {new_version}")
        print("Wiki content and manifests were NOT touched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
