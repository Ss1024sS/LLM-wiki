---
title: Sources and Data
source: session
source_hash: 0000000000000000
created: 2026-04-01
tags: [data, raw]
status: current
---

# Sources and Data

## Raw Documents (outside Git)

Raw files live in `../acme_raw/` — never committed to Git.

| File | Type | Status | Compiled Into |
|------|------|--------|---------------|
| Quoting Template v3.xlsx | Excel | compiled | project-overview.md |
| Customer Price List.pdf | PDF | compiled | current-status.md |
| Factory Layout.dwg | CAD | new | — |

## Database
- PostgreSQL (pricing tables, customer data)
- ERP middleware at 192.168.28.17 (pending VPN)
