# Changelog

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
