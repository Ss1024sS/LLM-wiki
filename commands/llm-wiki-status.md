---
description: Show the wiki status of the current project
---

Show the user the current state of this project's wiki.

If `docs/wiki/index.md` does not exist, tell the user this project hasn't
been bootstrapped yet and suggest running `/llm-wiki-bootstrap`.

Otherwise:
1. Read `docs/wiki/index.md` and list the wiki pages
2. Read the last 5 entries of `docs/wiki/log.md`
3. Read `docs/wiki/current-status.md` and summarize
4. Run `python3 scripts/wiki_check.py` and report any failures
5. If `scripts/stale_report.py` exists, run it and report stale pages
