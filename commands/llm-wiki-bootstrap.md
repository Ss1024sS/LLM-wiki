---
description: Bootstrap a compile-first knowledge system into the current project
argument-hint: [project name]
---

Bootstrap a wiki-first knowledge system into the current working directory.

If the user has not provided a project name as an argument, ask them for one.
Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap_knowledge_system.py . "<project-name>" --dry-run
```

Show the dry-run preview to the user. If they confirm, run again without
`--dry-run`. Existing files are skipped unless the user passes `--force`.

After bootstrap, suggest the user run:
- `python3 scripts/init_raw_root.py` — set up the local raw directory
- `python3 scripts/wiki_check.py` — sanity-check the new wiki
