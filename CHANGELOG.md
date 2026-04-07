# Changelog

## v1.2.0 (2026-04-07)

Raw intake and stale detection are now first-class instead of hand-wavy future tense.

### Added
- `scripts/ingest_raw.py` bootstraps and upgrades into every project. It scans a local raw root, computes content hashes, detects duplicates, guesses file kind, updates `manifests/raw_sources.csv`, writes `manifests/raw_index.json`, and emits `manifests/intake_report.md`.
- `scripts/stale_report.py` is now part of the generated toolchain. It compares wiki frontmatter, manifest status, and current raw hashes to report fresh pages, stale pages, missing hashes, unresolved sources, archived references, and still-uncompiled raw.
- New doc: `docs/ingest-pipeline.md` explains the local-first ingest flow without pretending this is a graph database startup pitch.

### Changed
- Bootstrap output is now **29 files** instead of 27.
- Upgrade flow now carries the new scripts forward for existing projects: `ingest_raw.py`, `stale_report.py`, `version_check.py`, and `upgrade.sh` are all updated in place.
- `README.md`, `UNIVERSAL.md`, the playbook, and the Codex skill docs now treat intake + stale detection as the default low-token workflow, not optional trivia.
- `raw_index.json` now includes a stable `summary` block so CI and downstream tooling can inspect ingest results without spelunking every file entry.
- `stale_report.py` no longer falsely marks a page stale just because its manifest row is still `new`; if the page references the current hash, it is fresh. Unreferenced `new` rows stay visible as `manifest-new`, which is the sane behavior.

### Verified
- Bootstrap a fresh project: `29` files generated, validators green.
- Upgrade a `v1.1.1` project with the current local snapshot: new scripts installed, validators still green.
- Ingest/stale edge cases: duplicate files, referenced `new` files, archived files, and archived wiki references all behave correctly.
- CI smoke flow now tracks an explicit source file for stale detection instead of mutating the wrong file and hoping for the best.

### Why it matters
- Less manual manifest grunt work
- Fewer tokens burned on clerical raw registration
- Faster “what changed?” checks without rereading raw by hand
- Better odds that the wiki stays current instead of becoming a polished fossil

## v1.1.1 (2026-04-07)

### Fixed
- `UNIVERSAL.md` no longer nests a triple-backtick YAML block inside a triple-backtick Markdown block; the Claude template now renders cleanly in stricter Markdown parsers.
- Team collaboration guidance now includes an actual merge-conflict strategy instead of hand-waving with “Git handles conflicts”.
- `README.md`, `SKILL.md`, and `release-notes-v1.1.0.md` now agree on the real bootstrap output count: `27 files`.
- Upgrade docs no longer send users down the old `curl /tmp/upgrade.py` path; the documented flow is now the root `scripts/upgrade.sh` wrapper.

### Why it matters
- Less doc drift
- Fewer copy-paste footguns
- Better odds that teams won't turn wiki merge conflicts into modern art

## v1.1.0 (2026-04-07)

Auto-update + community hardening.

### Added
- **Auto update check**: `version_check.py` runs at session start, silently checks GitHub for new releases. Prints notice only when outdated. Zero noise when current.
- **Upgrade path**: `scripts/upgrade.sh` — one command to pull latest scripts without touching wiki content or customized configs
- **Version markers**: every generated script has `# llm-wiki-version: X.Y.Z` header for version detection
- **Security policy**: SECURITY.md with scope, reporting channel, and what counts
- **Issue templates**: bug report + feature request templates
- **Code of Conduct**: Contributor Covenant

### Changed
- Session protocol Step 0: version check before reading wiki (all 5 platform templates)
- Bootstrap now generates 27 files (was 22: +upgrade.sh, +version_check.py, +3 Claude Code commands)
- Codex SKILL.md updated with full 27-file output, provenance, upgrade path

---

## v1.0.1 (2026-04-07)

Patch release. This one fixes the parts that looked finished but still had sharp edges.

### Fixed
- Root docs now consistently say bootstrap generates `22` files, not `20` or `21`
- `source: session` pages are now provenance-exempt instead of using fake `0000000000000000` hashes
- `provenance_check.py` now reports `session-exempt` pages explicitly and only requires `source_hash` for non-session sources
- Demo project was aligned with the real provenance model

### Improved
- Root wrapper path is now the only documented entry point: `scripts/bootstrap_knowledge_system.py`
- Smoke-tested bootstrap output still creates `22` files and passes all validators
- README + CHANGELOG + bootstrap behavior are back in sync instead of drifting apart

### Why it matters
- Less path confusion
- Cleaner provenance semantics
- Fewer “docs say one thing, script does another” footguns

## v1.0.0 (2026-04-06)

First stable release. Everything below was built in one day.

### Core
- Bootstrap script generates 22 files in one command (`--dry-run` to preview)
- 5 platform configs auto-generated: AGENTS.md, CLAUDE.md, .cursorrules, .windsurfrules, + ChatGPT manual workflow
- YAML frontmatter on all wiki pages (title, source, created, tags, status)
- Two-layer provenance: manifest CSV tracks raw files, frontmatter tracks wiki pages
- Content hash provenance for staleness detection (provenance_check.py)

### Validation
- `wiki_check.py` — structure + broken links + frontmatter enforcement
- `raw_manifest_check.py` — manifest integrity + status values
- `untracked_raw_check.py` — finds orphan PDFs/Excel/images not in manifest
- `provenance_check.py` — content hash freshness check on compiled wiki pages
- GitHub Actions smoke test (9 checks on every push)

### Documentation
- UNIVERSAL.md — platform-agnostic setup guide, migration path, FAQ (6 questions), token budget
- Playbook — full rationale in Chinese + English, provenance roadmap
- Demo project — realistic 3-session example with all platform configs
- CONTRIBUTING.md — where things live, how to test, commit style

### Design Decisions
- compile-first, not Q&A
- writeback is mandatory
- wiki before RAG (under ~100 docs)
- Obsidian is replaceable, the paradigm is not
- Ideas outrank Code
- Full audit = disaster recovery, not normal ops
- Status enum simplified: new / compiled / archived
- Session protocol runs automatically via config files, no per-session confirmation
