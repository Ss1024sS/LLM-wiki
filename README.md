# LLM Wiki

You've been here before:

- New session. AI remembers nothing. You spend 20 minutes re-explaining.
- "What did we decide about the pricing formula?" Buried in a 3-hour chat log.
- Five docs in Notion, three in Google Drive, two Excel files on desktop. Which one is current?

This repo fixes that. Not with another knowledge management theory post, but with a drop-in engineering practice that works across AI platforms.

---

## The Idea

Baseline from [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): the correct way to use LLMs is not Q&A, it's **compilation**.

```
raw/  (PDFs, Excel, client docs — immutable source material)
  ↓  LLM compiles
wiki/ (markdown — current consensus, continuously updated)
  ↓  LLM generates
code/ (the execution layer — a compiled artifact, not the truth)
```

Five rules:

1. **Compile-first** — Don't just answer. Write conclusions into wiki pages.
2. **Writeback is mandatory** — Every decision goes back to the wiki. Every single one.
3. **Wiki before RAG** — Under ~100 docs (or ~80k tokens, measured by `scripts/wiki_size_report.py`), LLM reads directly. No vector DB needed.
4. **Obsidian is replaceable, the paradigm is not** — The engine is LLM + filesystem + markdown.
5. **Ideas outrank Code** — Your wiki of decisions and formulas is worth more than the code it generates.

---

## Works With Any AI

| Platform | Config File | Status |
|----------|------------|--------|
| Claude Code | `CLAUDE.md` | **Native plugin** (`claude plugin install Ss1024sS/llm-wiki`) + template |
| Codex | `AGENTS.md` | Native skill + template |
| Cursor | `.cursorrules` | Template in UNIVERSAL.md |
| Windsurf | `.windsurfrules` | Template in UNIVERSAL.md |
| ChatGPT | Manual paste | Workflow in UNIVERSAL.md |

**Just send your AI this link and tell it to read `UNIVERSAL.md`:**

```text
Read https://github.com/Ss1024sS/LLM-wiki/blob/main/UNIVERSAL.md and set up the knowledge system for this project.
```

---

## What's In This Repo

```
LLM-wiki/
├── UNIVERSAL.md                    # Start here. Setup guide for any AI platform.
├── docs/
│   ├── knowledge-system-playbook.md  # Full rationale (Chinese + English), provenance roadmap
│   └── ingest-pipeline.md            # Low-token raw intake + stale detection flow
├── examples/
│   └── demo-project/               # What a bootstrapped project looks like after 3 sessions
│       ├── CLAUDE.md / AGENTS.md / .cursorrules / .windsurfrules
│       ├── docs/wiki/              # 5 wiki pages with realistic content
│       └── manifests/raw_sources.csv
├── .claude-plugin/                 # Claude Code plugin manifest (1.3.0+)
├── commands/                       # Plugin slash commands (/llm-wiki-bootstrap, /llm-wiki-status)
├── skills/
│   └── knowledge-system-bootstrap/
│       ├── scripts/bootstrap_knowledge_system.py  # 240-line renderer (was 2.6k LOC pre-1.3.0)
│       └── templates/              # 33 standalone files: scripts, configs, wiki pages
├── tests/                          # 35 pytest cases for bootstrap + every check
└── scripts/
    ├── bootstrap_knowledge_system.py   # Wrapper — always call this one
    └── install-codex-skill.sh
```

---

## Quick Start

### Option A: Tell your AI to do it

```text
Read https://github.com/Ss1024sS/LLM-wiki/blob/main/UNIVERSAL.md and set up the knowledge system for this project.
```

Works with Claude Code, Codex, Cursor, Windsurf.

### Option B: Run the bootstrap script

```bash
git clone https://github.com/Ss1024sS/LLM-wiki.git
cd LLM-wiki

# Preview what will be created (writes nothing)
python3 scripts/bootstrap_knowledge_system.py /path/to/your-project "My Project" --dry-run

# Run for real
python3 scripts/bootstrap_knowledge_system.py /path/to/your-project "My Project"
```

**Always use `scripts/bootstrap_knowledge_system.py`** (the root wrapper). Never call the one inside `skills/` directly — that's the skill's internal copy.

Generates 33 files: wiki structure (8 pages with frontmatter), manifests + schema, raw intake + stale reporting scripts, manual delta-compile scaffolds, validation scripts (including `wiki_size_report.py` for quantitative RAG-threshold triage and `provenance_check.py --ci` for raw-free CI), Claude Code commands, CI workflow, and configs for 4 AI platforms.

`--force` re-runs back up existing files to `<file>.bak.<timestamp>` before overwriting (pass `--no-backup` to opt out).

### Option C: Install as a Claude Code plugin (1.3.0+)

```text
claude plugin install Ss1024sS/llm-wiki
```

Then use `/llm-wiki-bootstrap` to scaffold a project, or `/llm-wiki-status` to inspect an existing one.

### Option D: Install as a Codex skill

```text
Use $skill-installer to install https://github.com/Ss1024sS/LLM-wiki/tree/main/skills/knowledge-system-bootstrap
```

Or manually:

```bash
bash scripts/install-codex-skill.sh
```

---

## How Do I Know It's Working?

After 3 sessions, check:

- [ ] `docs/wiki/log.md` has 3 entries
- [ ] `docs/wiki/current-status.md` reflects actual project state
- [ ] AI can answer "what did we do last time?" without you re-explaining
- [ ] Decisions from session 1 are still accessible in session 3
- [ ] `python3 scripts/ingest_raw.py` can register new raw files without manual manifest grunt work
- [ ] `python3 scripts/stale_report.py` can tell you what needs recompilation
- [ ] `python3 scripts/delta_compile.py --write-drafts` can generate draft stubs instead of silently overwriting wiki pages
- [ ] `python3 scripts/wiki_size_report.py` shows GREEN — your wiki still fits in a single read
- [ ] CI workflow (`wiki-lint`) passes on push without needing raw files mounted (see `docs/wiki/runtime-profile.md`)

See `examples/demo-project/` for what a healthy wiki looks like after a few sessions.

---

## Upgrading Existing Projects

Already using LLM-wiki and want the latest scripts?

If you're inside an already-bootstrapped project:

```bash
cd /path/to/your-project
bash scripts/upgrade.sh
```

Updates validation scripts and CI only. Wiki content and customized configs are never touched.

If you're standing in this public repo clone instead:

```bash
bash scripts/upgrade.sh /path/to/your-project
```

---

## Don't Do These Things

- Don't put raw PDFs/XLSX into Git. That's a binary junk pile, not version control.
- Don't treat chat history as memory. It evaporates.
- Don't build a RAG pipeline before your raw docs are even organized.
- Don't change code without updating the wiki. That's incomplete work.

---

## Read More

- [UNIVERSAL.md](./UNIVERSAL.md) — Setup guide + migration path + FAQ + templates for every AI
- [docs/knowledge-system-playbook.md](./docs/knowledge-system-playbook.md) — Full rationale (CN+EN), GitHub/raw split, provenance roadmap
- [docs/ingest-pipeline.md](./docs/ingest-pipeline.md) — How local raw intake, dedupe, parsing, and stale detection work
- [docs/release-notes-v1.3.0.md](./docs/release-notes-v1.3.0.md) — **Latest**: 2.6k→240 LOC bootstrap refactor, Claude plugin packaging, `wiki_size_report` with RAG thresholds, manifest schema versioning, `.bak` on `--force`, runtime profile per script
- [docs/release-notes-v1.2.2.md](./docs/release-notes-v1.2.2.md) — Previous: structured table diffs, manual delta-compile drafts, stricter provenance
- [examples/demo-project/](./examples/demo-project/) — What a bootstrapped project looks like after 3 sessions

---

## License

MIT. Use it, fork it, adapt it.

## Credits

Paradigm from [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Engineering practice by [Ss1024sS](https://github.com/Ss1024sS).
