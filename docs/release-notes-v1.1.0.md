# Release Notes — v1.1.0

Date: 2026-04-07

This release adds three things that v1.0.x was missing: automatic update notification, an upgrade path for existing projects, and slash commands for Claude Code.

## What changed

### 1. Auto update check at session start

Every bootstrapped project now runs `version_check.py` as Step 0 of the session protocol. It silently checks GitHub for a newer release. If your version is current, it says nothing. If there's an update, it prints:

```
[llm-wiki] Update available: v1.0.1 -> v1.1.0
[llm-wiki] Run: bash scripts/upgrade.sh
[llm-wiki] Release notes: https://github.com/Ss1024sS/LLM-wiki/releases/tag/v1.1.0
```

Timeout is 3 seconds. Offline or rate-limited? Silent skip. Zero disruption.

### 2. One-command upgrade

```bash
bash scripts/upgrade.sh
```

This pulls the latest LLM-wiki, updates validation scripts and CI workflow, and shows diffs for config templates. It never touches your wiki content, manifests, or customized platform configs (CLAUDE.md, AGENTS.md, etc.).

Every generated script now has a `# llm-wiki-version: X.Y.Z` header so the upgrade can detect what you're running.

### 3. Claude Code slash commands

Bootstrapped projects now include `.claude/commands/` with three commands:

| Command | What it does |
|---------|-------------|
| `/wiki-check` | Runs all 4 validation scripts and reports results |
| `/wiki-upgrade` | Checks for updates, offers to upgrade |
| `/wiki-status` | Shows wiki pages, last 3 log entries, current status summary |

These are `.md` files that Claude Code reads automatically. No installation needed.

### 4. Provenance cleanup (from v1.0.1)

- `source: session` pages are now exempt from `source_hash` requirements
- No more fake `0000000000000000` hashes
- `provenance_check.py` reports `session-exempt` explicitly

### 5. Community standards

- Security policy (SECURITY.md)
- Issue templates (bug report + feature request)
- Code of Conduct
- CONTRIBUTING.md with "where things live" guide
- CHANGELOG.md

### 6. Codex skill updated

`SKILL.md` now documents the full 27-file output, provenance tracking, upgrade path, and migration flow.

## File count

Bootstrap now generates **27 files** (was 22 in v1.0.0):
- +3 Claude Code commands (`.claude/commands/wiki-check.md`, `wiki-upgrade.md`, `wiki-status.md`)
- +1 `scripts/version_check.py`
- +1 `scripts/upgrade.sh`

## What was verified

```bash
python3 scripts/bootstrap_knowledge_system.py /tmp/test "Test" --dry-run
# Would create 27 files

python3 scripts/bootstrap_knowledge_system.py /tmp/test "Test"
cd /tmp/test
python3 scripts/wiki_check.py        # OK
python3 scripts/raw_manifest_check.py # OK
python3 scripts/untracked_raw_check.py # OK
python3 scripts/provenance_check.py   # OK
python3 scripts/version_check.py      # (silent = up to date)
ls .claude/commands/                  # wiki-check.md  wiki-status.md  wiki-upgrade.md
```

## Upgrade from v1.0.x

If you bootstrapped a project with v1.0.0 or v1.0.1:

```bash
git clone https://github.com/Ss1024sS/LLM-wiki.git
cd LLM-wiki
bash scripts/upgrade.sh /path/to/your-project
```

After that, future upgrades use `bash scripts/upgrade.sh` directly inside the bootstrapped project.

## What did not change

- Core model: compile-first, writeback mandatory, wiki before RAG, raw outside Git
- Session protocol: still reads 3 files at start, still writes back at end
- Token budget: still lazy loading, still under 10K tokens daily
- Provenance: still two-layer (manifest CSV for raw, frontmatter for wiki)
