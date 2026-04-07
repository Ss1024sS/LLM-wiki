# LLM Wiki — Universal Setup Guide

> Send this URL to any AI coding assistant. It will know what to do.
>
> https://github.com/Ss1024sS/LLM-wiki

---

## The Problem

- New session starts, AI remembers nothing
- Last week's decision? Buried in 3 hours of chat history
- Docs scattered across 10 places, nobody knows which version is current
- You keep re-explaining the same context every single time

## The Fix

Stop treating AI sessions as Q&A. Treat them as **compilation cycles**.

```
raw/ (source documents, immutable)
  |
  v  [LLM compiles]
  |
wiki/ (current consensus, continuously updated)
  |
  v  [LLM generates]
  |
code/ (compiled output, not the source of truth)
```

Every session: read wiki -> do work -> write back to wiki. Knowledge compounds. Nothing is lost.

---

## 5 Rules (Non-Negotiable)

1. **Compile-first** — Don't just answer questions. Compile raw docs into wiki pages.
2. **Writeback is mandatory** — Every conclusion, decision, or discovery goes back into the wiki. No exceptions.
3. **Wiki before RAG** — Under ~100 documents, direct LLM reading beats vector search. Less infra, better results.
4. **Obsidian is replaceable, the paradigm is not** — The real engine is LLM + filesystem + markdown. Tools come and go.
5. **Ideas outrank Code** — Your wiki (decisions, formulas, constraints) is more valuable than the code it generates.

---

## Setup for Any AI Platform

### Step 1: Create the wiki structure

In your project root, create these files:

```
your-project/
├── docs/wiki/
│   ├── index.md          # Links to all wiki pages
│   ├── log.md            # One line per session (date, topic, outcome)
│   ├── current-status.md # What's done, what's next, what's blocked
│   ├── project-overview.md
│   └── sources-and-data.md
├── manifests/
│   └── raw_sources.csv   # Index of raw docs (not the docs themselves)
└── [your platform config file]
```

Raw files (PDFs, Excel, images) stay **outside Git** in a local `raw/` directory. Only the compiled wiki goes into the repo.

### Step 2: Add the session protocol to your AI config

Copy the protocol below into your platform's config file. This is what makes the AI maintain the wiki automatically.

### Step 3: Start working

That's it. The AI will read the wiki at session start, update it during work, and write a log entry at session end. Knowledge compounds automatically.

When a batch of new raw files arrives, don't hand-edit the manifest like a martyr. Run:

```bash
python3 scripts/ingest_raw.py
python3 scripts/stale_report.py
```

The first updates the raw index and low-cost structural metadata. The second tells you what has gone stale.

---

## Platform-Specific Config Templates

### Claude Code (`CLAUDE.md`)

Create `CLAUDE.md` in your project root:

````markdown
# [Project Name] — Claude Rules

## Knowledge System
This project uses a wiki-first knowledge system. Knowledge lives in `docs/wiki/`, not in chat history.

## Session Protocol (mandatory)

### Session Start (auto, no confirmation needed)
0. Run `python3 scripts/version_check.py` — checks for updates, silent if current, prints notice if outdated
1. Read `docs/wiki/index.md` — get the full page list
2. Read `docs/wiki/current-status.md` — know where things stand
3. Read `docs/wiki/log.md` — understand recent session history
4. Read additional wiki pages **only as needed** for the current task (don't read everything)

### During Work
- New decision made → update the relevant wiki page immediately
- **Any file mentioned, received, referenced, or saved — including screenshots, customer attachments, chat images, debug captures, PDFs, Excel, CAD files, archives → check `manifests/raw_sources.csv` first. Not listed → register it before proceeding.** For batches, run `python3 scripts/ingest_raw.py` instead of hand-editing rows one by one. This is the single most commonly skipped step.
- Task completed → update `docs/wiki/current-status.md`

### Session End
1. Append one line to `docs/wiki/log.md`: date, topic, key outcomes
2. Update `docs/wiki/current-status.md` with latest state
3. If context is running low → generate `CONTINUATION-SUMMARY.md`

### Consistency
- If `current-status.md` conflicts with other wiki pages → trust the more specific page, then fix `current-status.md`
- If `log.md` is missing entries from before your session → don't guess, only append your own
- If two wiki pages contradict each other → flag it to the user, resolve before proceeding

### Token Budget
Normal operations are cheap. The wiki is designed for incremental updates, not bulk reads.
- **Session start**: read 3 files (index, status, log). ~2K tokens.
- **During work**: read specific pages one at a time, only when needed.
- **Structural checks**: `wiki_check.py`, `raw_manifest_check.py`, `untracked_raw_check.py`, `provenance_check.py`, and `stale_report.py` are Python scripts. Zero LLM tokens.
- **Never read all wiki pages upfront.** If the protocol is followed, you never need to.

Full audit and recompilation are **disaster recovery**, not normal workflow:
- Full wiki audit: only if the wiki was neglected for months and you suspect widespread contradictions.
- Full raw recompilation: only if source files were silently replaced outside the normal flow.
- If every session does its incremental writeback correctly, neither of these ever happens.

### Frontmatter
Every wiki page (except index.md and log.md) must start with YAML frontmatter:
```yaml
---
title: Page Title
source: where this info came from (raw file path, URL, or "session")
created: 2026-04-06
tags: [relevant, tags]
status: current
---
```
This lets the AI know the provenance of each page without reading any external index. Obsidian renders it natively. `wiki_check.py` validates it automatically.

### Rules
- compile-first: don't just answer, write conclusions into wiki pages
- writeback is mandatory: if you learned something durable, it goes in the wiki
- raw files stay outside Git, only manifests go in
- all non-code files are "raw" — PDFs, spreadsheets, images, screenshots, customer attachments, archives, CAD files, audio, video
- every wiki page must have frontmatter (title + source + created)
````

### Codex (`AGENTS.md`)

Create `AGENTS.md` in your project root:

```markdown
# [Project Name] Agent Rules

## Session Protocol

Only tasks that are not pure chat require reading the wiki first:

1. `docs/wiki/index.md`
2. `docs/wiki/current-status.md`
3. `docs/wiki/log.md`

## Default Stance

- `compile-first`
- `writeback` is mandatory
- Wiki before heavy RAG
- Obsidian is optional, markdown is not
- `Idea / Intent` outranks `Code`

## Knowledge Layers

- raw: source documents (outside Git)
- wiki: compiled consensus (in Git)
- code: execution layer (in Git)

Changing code without updating wiki = incomplete work.
```

### Cursor (`.cursorrules`)

Create `.cursorrules` in your project root:

```
This project uses a wiki-first knowledge system.

Before starting any non-trivial task:
1. Read docs/wiki/index.md for the wiki page list
2. Read docs/wiki/current-status.md for project state
3. Read docs/wiki/log.md for recent session history

After completing work:
- Update docs/wiki/current-status.md with new state
- Append a log entry to docs/wiki/log.md (date | topic | outcome)
- If a durable decision was made, write it into the relevant wiki page

Rules:
- Compile raw documents into wiki pages, don't just reference them
- Every conclusion goes back into the wiki (writeback is mandatory)
- Raw files (PDF/XLSX) stay outside Git, only manifests/ indexes go in
```

### Windsurf (`.windsurfrules`)

Same content as `.cursorrules` above. Create `.windsurfrules` in project root.

### ChatGPT / Other (manual)

If your AI doesn't have filesystem access:
1. Paste the contents of `docs/wiki/current-status.md` at the start of each conversation
2. At the end of each conversation, ask the AI to generate updated wiki content
3. Manually copy the updates back into your wiki files

This is slower but still works. The paradigm matters more than the tool.

---

## Migrating an Existing Project

If your project already has docs, a CLAUDE.md, or scattered markdown:

1. **Don't delete anything.** Run bootstrap with default settings — it skips existing files.
2. Preview first: `python3 bootstrap_knowledge_system.py /your/project "Name" --dry-run`
3. Move existing docs into `docs/wiki/` manually
4. Register existing raw files (PDFs, Excel) in `manifests/raw_sources.csv`
5. Merge your existing CLAUDE.md rules with the generated session protocol
6. Run `python3 scripts/wiki_check.py` to verify the structure

The bootstrap never overwrites unless you pass `--force`. Your existing work is safe.

---

## FAQ

**Q: Why not just use an Obsidian AI plugin?**

An Obsidian plugin locks your knowledge into one tool. If the plugin dies, your workflow dies. LLM Wiki is a paradigm built on `.md` files and filesystem conventions. Switch from Claude to Codex to Cursor — your wiki stays. Obsidian is a great viewer, but the engine is LLM + filesystem, not any single app.

**Q: Why not RAG / vector search?**

Under ~100 documents, LLMs reading files directly outperforms vector retrieval. Less infra, fewer hallucinations, easier debugging. When your wiki grows past that, RAG becomes worth it. Start simple.

**Q: How does this handle stale knowledge?**

Current approach is two-layered:

- `provenance_check.py` validates page-level `source_hash` for source-backed wiki pages
- `stale_report.py` compares current raw hashes, manifest status, and wiki frontmatter to tell you what needs recompilation

Still local. Still deterministic. Still cheap.

**Q: What about multiple people / teams?**

Use a simple rule set, not vibes:

1. **One session, one primary page owner at a time.** Don't have two people freestyle-edit `current-status.md` and the same deep wiki page in parallel unless someone wants a stupid merge.
2. **Specific pages beat summary pages.** If `current-status.md` conflicts with `pricing.md`, keep the source-backed specific page, then rewrite the summary.
3. **`log.md` is append-only.** Never edit someone else's old line unless you're fixing a typo. Add your own entry and move on.
4. **Conflict resolution is manual, not "accept both".** If Git shows conflict markers in wiki pages, resolve them by keeping the version with clearer source backing, then rewrite the page into one clean narrative.
5. **After every merge, rerun checks.** `wiki_check.py` first, then any raw/provenance checks. If the wiki is broken after merge, the merge is not done.

Git stores versions. It does not think for you. The protocol still matters.

**Q: Won't the token cost get scary as the wiki grows?**

No. The protocol is incremental by design. Daily cost:
- Session start: 3 files, ~2K tokens — pennies
- During work: 1-3 pages on demand, ~5K tokens — normal
- Writeback: small diffs, not full rewrites

Structural checks (broken links, missing files, untracked raw) use Python scripts — zero LLM tokens.

"But what about full audits and recompilation?" Those are disaster recovery, not regular operations. If every session does its incremental writeback, contradictions don't accumulate and raw files don't go untracked. You never need to read the entire wiki. The design goal is that each session touches only what it needs — typically under 10K tokens for wiki maintenance, regardless of how large the wiki gets.

**Q: Does this run automatically or do I need to tell the AI each time?**

Fully automatic. The session protocol is written into your AI's config file (CLAUDE.md, AGENTS.md, .cursorrules, .windsurfrules). The AI reads it at session start and follows it without being asked. You install once, it works forever.

---

## The Bootstrap Script

For a faster setup, use the included Python script:

```bash
python3 scripts/bootstrap_knowledge_system.py /path/to/your-project "Your Project Name"
```

This generates the full wiki structure, manifest templates, and validation scripts in one command. See `docs/knowledge-system-playbook.md` for the complete rationale.

---

## Quick Test: Is It Working?

After 3 sessions, check:

- [ ] `docs/wiki/log.md` has 3 entries
- [ ] `docs/wiki/current-status.md` reflects the actual project state
- [ ] New session AI can answer "what did we do last time?" without you explaining
- [ ] Decisions from session 1 are still accessible in session 3

If yes, your knowledge system is compiling. If no, check that writeback is actually happening.

---

## Upgrading

Already bootstrapped a project and want the latest scripts?

```bash
cd /path/to/your-project
bash scripts/upgrade.sh
```

If you're running from the `LLM-wiki` repo clone itself instead:

```bash
bash scripts/upgrade.sh /path/to/your-project
```

This updates validation scripts and CI workflow only. Your wiki content, manifests, and customized configs (CLAUDE.md, AGENTS.md, etc.) are never touched. Template changes are printed for you to review and merge manually.

---

## Credits

Baseline paradigm from [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). This repo packages it into a reusable, platform-agnostic engineering practice.
