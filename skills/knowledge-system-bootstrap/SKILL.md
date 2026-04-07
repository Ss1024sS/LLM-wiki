---
name: knowledge-system-bootstrap
description: Bootstrap a compile-first project knowledge system with repo-local wiki, raw manifests, provenance tracking, auto-update checks, and platform configs for Claude Code / Codex / Cursor / Windsurf. Use when a user wants durable project context, wiki-first rules, or to replicate this model into another repo.
---

# Knowledge System Bootstrap

Use this when the user wants a project to stop relying on chat memory and start behaving like a sane system.

## What this skill does

Scaffolds a complete wiki-first knowledge system (27 files):

- `docs/wiki/` — 8 wiki pages with YAML frontmatter (title, source, created, tags, status)
- `manifests/raw_sources.csv` — raw file index (never raw files themselves)
- `scripts/` — 8 validation and utility scripts:
  - `wiki_check.py` — structure + broken links + frontmatter enforcement
  - `raw_manifest_check.py` — manifest integrity
  - `untracked_raw_check.py` — finds orphan PDFs/Excel/images not in manifest
  - `provenance_check.py` — content hash freshness (source_hash in frontmatter)
  - `version_check.py` — auto-checks GitHub for new LLM-wiki releases
  - `upgrade.sh` — one-command upgrade (scripts only, never touches wiki content)
  - `init_raw_root.py` — create local raw directory structure
  - `export_memory_repo.py` — export wiki to separate memory repo
- Platform configs: `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.windsurfrules`
- `.claude/commands/` — Claude Code slash commands: `/wiki-check`, `/wiki-upgrade`, `/wiki-status`
- `.github/workflows/wiki-lint.yml` — CI smoke test

## Default stance

- `compile-first`
- `writeback` is mandatory
- medium-sized projects use `wiki` before heavy `RAG`
- Obsidian is optional, markdown is not
- `Idea / Intent` outranks `Code`
- full audit = disaster recovery, not normal ops

## When to use it

- set up a durable project memory layer
- stop losing context between sessions
- separate GitHub knowledge from raw binary junk
- create a repeatable wiki/raw/manifests structure for a new repo
- migrate an existing repo toward this model

Do not use it for tiny throwaway demos.

## Workflow

1. Identify the target repo root and project name.
2. Preview: `python3 scripts/bootstrap_knowledge_system.py /path/to/repo "Name" --dry-run`
3. Run: `python3 scripts/bootstrap_knowledge_system.py /path/to/repo "Project Name"`
4. Initialize local raw root: `python3 scripts/init_raw_root.py`
5. Validate: `python3 scripts/wiki_check.py && python3 scripts/raw_manifest_check.py`

## Existing repo migration

If the repo already has docs or a CLAUDE.md:

- Run bootstrap with default settings (skips existing files)
- Move existing docs into `docs/wiki/` manually
- Register raw files in `manifests/raw_sources.csv`
- Merge customized config rules with generated templates

## Upgrade

Existing bootstrapped projects can upgrade in place:

```bash
bash scripts/upgrade.sh
```

If the project predates `scripts/upgrade.sh`, use the public repo wrapper once:

```bash
git clone https://github.com/Ss1024sS/LLM-wiki.git
cd LLM-wiki
bash scripts/upgrade.sh /path/to/your-project
```

Updates validation scripts and CI only. Wiki content and customized configs are never touched.

## Bundled resources

- Script: `scripts/bootstrap_knowledge_system.py`
- Reference: `references/playbook.md` (points to `docs/knowledge-system-playbook.md`)
