---
title: Acme Widget Factory — Overview
source: raw/internal_sources/Quoting Template v3.xlsx
source_hash: a1b2c3d4e5f60708
created: 2026-04-01
updated: 2026-04-03
tags: [overview, formula]
status: current
---

# Acme Widget Factory — Overview

Acme makes industrial widgets. This system automates their quoting process.

## Goal
Replace the 11-step manual quoting process (Excel + email + phone) with a 3-step digital flow.

## Key Formula
```
material_cost = housing + cable + PCB
total_cost = material_cost + packaging(5%) + management(5% domestic / 15% export)
min_price = total_cost * (1 + customer_profit_margin%)
```
