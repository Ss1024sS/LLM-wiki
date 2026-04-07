# Release Notes — v1.0.1

Date: 2026-04-07

This is a cleanup release. No new philosophy, no new hand-wavy claims. Just sharper behavior.

## What changed

### 1. Bootstrap docs now match reality

The project scaffolder creates `22` files. Earlier docs still said `20` or `21` in a few places. That kind of mismatch makes a repo feel fake fast.

Now the docs and the script agree.

### 2. Session pages no longer fake provenance hashes

`source: session` pages used to carry a placeholder hash:

```yaml
source_hash: 0000000000000000
```

That worked mechanically, but the model was wrong. Session-derived pages are not compiled from a stable source file, so pretending they have a file hash was dirty.

Now the rule is:

- `source: session` → `source_hash` is optional
- file-backed pages → `source_hash` is required

`provenance_check.py` enforces that split directly.

### 3. Provenance output is clearer

The checker now reports:

- `checked`
- `fresh`
- `session-exempt`
- `without hash`
- `stale`

So you can actually tell whether missing hashes are expected or a bug.

### 4. Demo project now matches the real rules

The demo was updated so it no longer teaches the fake-hash pattern for session pages.

That matters more than it sounds. Example repos are where bad habits become cargo cult.

## What was verified

The patch was tested by bootstrapping a fresh project and running:

```bash
python3 scripts/wiki_check.py
python3 scripts/raw_manifest_check.py
python3 scripts/untracked_raw_check.py
python3 scripts/provenance_check.py
```

Expected provenance result on a fresh bootstrap:

```text
provenance_check: OK (0 checked, 0 fresh, 4 session-exempt, 0 without hash)
```

## Who this release is for

- Anyone bootstrapping a new repo from `LLM-wiki`
- Anyone who noticed the old file counts were inconsistent
- Anyone who hates fake metadata pretending to be design

## What did not change

- The core model is still the same:
  - compile-first
  - writeback mandatory
  - wiki before heavy RAG
  - raw outside Git
- Bootstrap still generates `22` files
- Root wrapper is still the entry point:

```bash
python3 scripts/bootstrap_knowledge_system.py /path/to/repo "Project Name"
```

Never call the skill-internal bootstrap script directly unless you're inside the Codex skill flow.
