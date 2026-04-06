# Knowledge System Playbook

这份文档不是某个单一项目的业务说明，而是一套可以复制到别的项目里的知识工程打法。

目标很直接：

- 不再靠聊天上下文硬撑“记忆”
- 不再把 GitHub 私有仓搞成二进制垃圾场
- 让每个新 session 一进项目就知道怎么干

## 一句话范式

默认范式就是这 5 条：

- `compile-first`，不是问答
- `writeback` 必做
- 中等规模先 `wiki`，不先上重 `RAG`
- Obsidian 可替换，范式不可替换
- `Idea / Intent` 优先于 `Code`

## 核心分层

任何项目都按这三层来：

### 1. raw

原始资料层，放这些：

- PDF
- XLSX / XLS
- RAR / ZIP
- 截图
- 客户原件
- 访谈纪要原件

raw 是证据，不乱改。

### 2. wiki

编译后的项目知识层，放这些：

- 项目总览
- 当前状态
- 数据来源
- 规则边界
- 运维方式
- 风险
- 时间线

wiki 是当前共识，必须持续回写。

### 3. code

最终执行层，放这些：

- 业务代码
- 规则
- 测试
- 部署脚本

code 是编译产物，不是唯一真相。

## 为什么不是先上 RAG

因为大多数中等规模项目根本没到“先建检索系统”的门槛。

典型更值钱的顺序是：

1. 先把 raw 收好
2. 再把 raw 编译成 wiki
3. 再把 wiki 里的稳定结论落到 code

如果 raw 还是乱的，直接上 RAG 只是在高级检索垃圾。

## GitHub private repo 应该放什么

放这些：

- code
- wiki
- manifests
- verified cases
- 轻量知识文件
- 规则
- 测试

不该放这些：

- 全量 PDF 仓库
- 全量 workbook 原件
- 大量图片稿
- 一堆 zip/rar 历史包

## 本地 raw 仓应该放什么

本地 raw 仓就是原始资料主仓，推荐放在 repo 外面，比如：

```text
../my_project_raw/
```

结构建议：

```text
my_project_raw/
├── inbox/
├── internal_sources/
├── competitor_sources/
├── customer_answers/
├── screenshots/
├── extracted_text/
└── archive/
```

## manifests 是干嘛的

manifest 是 raw 的目录卡，不是 raw 本体。

它至少要记录：

- `source_id`
- `company`
- `vendor`
- `kind`
- `filename`
- `raw_rel_path`
- `status`
- `compiled_into`
- `notes`

这样 GitHub 里就能知道：

- 这份 raw 在不在
- 它属于什么
- 它有没有被编译
- 它现在到了哪一层

## 每个新 session 的默认行为

只要不是纯闲聊，默认先读：

1. `docs/wiki/index.md`
2. `docs/wiki/current-status.md`
3. `docs/wiki/log.md`

如果任务涉及具体领域，再继续读对应页面。

这条必须写进 repo 级 `AGENTS.md`，不靠口头提醒。

## writeback 为什么必须做

没有 writeback，LLM 就永远在重复浪费 token。

每次做完有长期价值的事，必须至少回写一处：

- 新 raw 进来：记 manifest
- 新结论确定：更 wiki
- 新规则落地：更 wiki + 测试
- 新样本确认：进 verified cases

## 对外部工具的态度

- Obsidian 可以用，但它只是 `.md` 的前端
- 以后换别的也无所谓
- 真正不可替换的是：
  - `LLM + 文件系统 + markdown + manifests + writeback`

## 如何快速复用到新项目

这仓库里已经给了脚手架：

- `scripts/bootstrap_knowledge_system.py`

示例：

```bash
python3 scripts/bootstrap_knowledge_system.py /path/to/new-repo "My New Project"
```

它会生成：

- `AGENTS.md`
- `docs/wiki/*`
- `manifests/*`
- `scripts/wiki_check.py`
- `scripts/raw_manifest_check.py`
- `scripts/init_raw_root.py`
- `scripts/export_memory_repo.py`

如果你想一把梭复用，不想手动拷这些文件，这套逻辑已经被打成全局 skill：

- `knowledge-system-bootstrap`

它本质上就是把这份 playbook 和脚手架装箱，方便别的项目直接照抄，不必再从旧项目里挖脚本。

## 什么时候这套打法最合适

特别适合这种项目：

- 文档多
- 规则多
- 原始资料多
- 业务口径会变
- 多个 session / 多个工程师接手

也就是绝大多数“真业务项目”。

## 什么时候别硬套

如果项目只是：

- 一个超小 demo
- 单人两天内做完
- 没什么原始资料
- 没什么业务知识沉淀

那上整套知识系统就是给自己加戏。

## Roadmap: Source Provenance（下一步进化）

当前的 wiki 模式解决了"知识不丢失"的问题。但还有一层没解决：**知识会过期**。

wiki 页面说"PCBA 成本是 2.55 元"，这个数字来自哪份 Excel？那份 Excel 现在还是这个值吗？

Source provenance 是解决方案：

### 核心思路

1. **每个编译结论记录来源** — wiki 页面里的每个事实，标注它编译自哪份 raw 文件
2. **Content hash 追踪** — 编译时记录源文件的 hash。查询时比对当前 hash，不一致则标记为 stale
3. **Query-time delta compilation** — 查询时不是重新编译全量，而是找出"源文件关于这个问题说了什么 wiki 还没收录的"，只编译增量
4. **Git branching 天然兼容** — 切分支，文件变了，不同的 propositions 自动标记为 valid/stale。合并分支，知识也合并

### 技术方案（未实现，规划中）

```python
# manifest 增加 content_hash 列
source_id,filename,raw_rel_path,status,compiled_into,content_hash
src_001,报价模板.xlsx,internal/报价模板.xlsx,compiled,project-overview.md,sha256:a1b2c3...

# wiki 页面增加 provenance 标注
<!-- provenance: src_001@sha256:a1b2c3 -->
PCBA 材料成本 = 2.55 元（5W 人工制费）

# 查询时校验
if current_hash(src_001) != stored_hash:
    mark_as_stale("PCBA 材料成本 = 2.55 元")
    suggest_recompile(src_001, "project-overview.md")
```

### 什么时候该上 provenance

- wiki 超过 20 页
- raw 源文件会频繁更新（价格表、客户资料）
- 多人协作，需要知道"这个结论还对不对"
- 已经被 stale 知识坑过

当前阶段不需要。先把 raw → wiki → code 的基础流程跑顺。

## 结论

这套东西本质上不是文档模板，而是知识生产线：

- raw 是原料
- wiki 是编译产物
- code 是执行层

顺序别反。

---

# Knowledge System Playbook (English)

This document is a reusable knowledge engineering playbook, not a single-project spec.

## One-Line Paradigm

5 rules:

- `compile-first`, not Q&A
- `writeback` is mandatory
- Medium-sized projects use `wiki` before heavy `RAG`
- Obsidian is replaceable, the paradigm is not
- `Idea / Intent` outranks `Code`

## Core Layers

### 1. raw

Source materials: PDFs, XLSX, screenshots, client originals, interview transcripts.

Raw is evidence. Don't modify it.

### 2. wiki

Compiled project knowledge: overview, current status, data sources, rules, risks, timeline.

Wiki is current consensus. Must be continuously written back to.

### 3. code

Execution layer: business logic, rules, tests, deploy scripts.

Code is a compiled artifact, not the single source of truth.

## Why Not RAG First

Most medium-sized projects haven't reached the threshold where a retrieval system is worth building.

The more valuable sequence:

1. Collect raw
2. Compile raw into wiki
3. Drop stable wiki conclusions into code

If raw is still a mess, RAG is just fancy searching through garbage.

## GitHub vs Local Raw

**GitHub private repo should contain:** code, wiki, manifests, verified cases, lightweight knowledge files, rules, tests.

**Should NOT contain:** bulk PDFs, full Excel workbooks, image archives, zip/rar history packs.

**Local raw root** lives outside the repo, e.g. `../my_project_raw/`.

## Manifests

A manifest is the raw file index, not the raw files themselves.

Required columns: `source_id, company, vendor, kind, filename, raw_rel_path, status, compiled_into, notes`

Status values: `new` → `compiled` → `archived`

## Session Default Behavior

Every non-trivial session starts by reading:

1. `docs/wiki/index.md`
2. `docs/wiki/current-status.md`
3. `docs/wiki/log.md`

This must be written into the repo-level agent config (CLAUDE.md / AGENTS.md / .cursorrules), not relied on verbally.

## Why Writeback Is Non-Negotiable

Without writeback, the LLM wastes tokens re-deriving the same conclusions.

After every durable outcome:

- New raw arrives → register in manifest
- New conclusion → update wiki
- New rule → update wiki + add test
- New verified sample → add to verified cases

## Roadmap: Source Provenance

The next evolution: every compiled fact records which source file produced it and its content hash at compilation time. Queries validate freshness by checking if sources still match. Knowledge grows with every query but never serves silently stale information.

See the Chinese section above for the full technical design.

## When NOT to Use This

- Tiny throwaway demo
- One person, two days, done
- No source materials
- No business knowledge to accumulate

Don't add ceremony to projects that don't need it.
