# Release Notes — v1.2.0

Date: 2026-04-07

This is the release where `LLM-wiki` finally grows a pair of eyes.

Before this, the system had discipline:

- wiki-first
- writeback
- provenance
- upgrade flow

But it still had one dumb dependency: a human acting as the manifest intern.

`v1.2.0` fixes that.

## What changed

### 1. Raw intake is now a real script, not a moral aspiration

Bootstrapped projects now include:

```bash
python3 scripts/ingest_raw.py
```

It does the boring work locally:

- scans the raw root
- computes content hashes
- detects duplicates
- guesses file kind
- updates `manifests/raw_sources.csv`
- writes `manifests/raw_index.json`
- writes `manifests/intake_report.md`

No LLM call. No “please fill the manifest carefully.” No spreadsheet martyrdom.

### 2. Stale detection is now default behavior

Projects now also get:

```bash
python3 scripts/stale_report.py
```

It compares:

- wiki frontmatter
- `source_hash`
- manifest rows
- current raw hashes

And tells you:

- what is fresh
- what is stale
- what is missing `source_hash`
- what points to archived raw
- what is still sitting in the manifest as `new`

That means “is this wiki page still current?” is now a cheap local check, not a ritual.

### 3. Existing projects can upgrade into this instead of rebuilding from scratch

The upgrade path now carries the new scripts forward:

- `scripts/ingest_raw.py`
- `scripts/stale_report.py`
- `scripts/version_check.py`
- `scripts/upgrade.sh`

So this is not “nice for new users, shrug for everyone else.” Old projects can actually join the party.

### 4. Docs and CI now match the real toolchain

This release also cleans up the repo surface around the new workflow:

- bootstrap count is now **29 files**
- `README.md` reflects the new output
- `UNIVERSAL.md` treats intake + stale checks as default low-token operations
- the playbook explains why this matters
- CI smoke tests now verify the real ingest/stale path instead of waving vaguely in its direction

## Important behavior fix

One subtle bug got killed before release:

`stale_report.py` used to mark a page stale just because its manifest row was still `status=new`, even if the page already referenced the current source hash.

That was wrong.

Now the behavior is:

- referenced + matching hash = fresh
- unreferenced `new` raw = `manifest-new`
- changed source hash = stale
- archived referenced raw = archived reference alert

That distinction matters, because otherwise the tool punishes correct incremental compilation.

## What was verified

This release was not rubber-stamped.

We validated:

1. Fresh bootstrap project
   - `29` files generated
   - `wiki_check.py`
   - `raw_manifest_check.py`
   - `untracked_raw_check.py`
   - `provenance_check.py`

2. Upgrade path
   - bootstrapped a `v1.1.1` project from the tagged script
   - upgraded it using the current local snapshot
   - confirmed the new scripts landed correctly
   - reran the validators successfully

3. Ingest / stale edge cases
   - duplicate files
   - referenced `new` files
   - archived raw
   - archived wiki references
   - source hash changes producing a real stale result

4. CI contract
   - `raw_index.json` now exposes a stable `summary`
   - smoke tests now track an explicit source file for stale detection

## Why this version is worth shipping

Because it moves work from expensive tokens to cheap local computation.

That is the whole point.

LLMs should synthesize, judge, and write back conclusions.
They should not spend their life:

- registering filenames
- comparing raw hashes by hand
- figuring out whether the wiki is stale because nobody bothered to check

`v1.2.0` does not turn `LLM-wiki` into a graph platform.

Good.

It turns it into a better compiler.
