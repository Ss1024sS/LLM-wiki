from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "project"


WIKI_CHECK = """from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = ROOT / "docs" / "wiki"

REQUIRED_FILES = [
    "README.md",
    "SCHEMA.md",
    "index.md",
    "log.md",
    "project-overview.md",
    "current-status.md",
    "sources-and-data.md",
    "github-and-raw-strategy.md",
]

LINK_RE = re.compile(r"\\[[^\\]]+\\]\\(([^)]+)\\)")
LOG_HEADER_RE = re.compile(r"^## \\[\\d{4}-\\d{2}-\\d{2}\\] .+ \\| .+$")
FRONTMATTER_RE = re.compile(r"^---\\n(.*?)\\n---", re.DOTALL)
FRONTMATTER_EXEMPT = {"index.md", "log.md", "README.md", "SCHEMA.md"}
REQUIRED_FRONTMATTER_KEYS = {"title", "source", "created"}


def check_frontmatter(path: Path, text: str) -> list[str]:
    errs: list[str] = []
    rel = path.name
    if rel in FRONTMATTER_EXEMPT:
        return errs
    m = FRONTMATTER_RE.match(text)
    if not m:
        errs.append(f"missing frontmatter: {path.relative_to(ROOT)}")
        return errs
    body = m.group(1)
    found_keys: set[str] = set()
    for line in body.splitlines():
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            found_keys.add(key)
    missing = REQUIRED_FRONTMATTER_KEYS - found_keys
    if missing:
        errs.append(f"missing frontmatter keys in {path.relative_to(ROOT)}: {', '.join(sorted(missing))}")
    return errs


def resolve_link(source_file: Path, target: str) -> Path | None:
    if target.startswith(("http://", "https://", "mailto:")):
        return None
    if target.startswith("#"):
        return None
    target = target.split("#", 1)[0]
    if not target:
        return None
    return (source_file.parent / target).resolve()


def main() -> int:
    errors: list[str] = []
    if not WIKI_ROOT.exists():
        print("wiki_check: docs/wiki does not exist")
        return 1

    for rel in REQUIRED_FILES:
        path = WIKI_ROOT / rel
        if not path.exists():
            errors.append(f"missing required file: docs/wiki/{rel}")

    md_files = sorted(WIKI_ROOT.rglob("*.md"))
    index_text = (WIKI_ROOT / "index.md").read_text(encoding="utf-8") if (WIKI_ROOT / "index.md").exists() else ""

    fm_ok = 0
    for path in md_files:
        text = path.read_text(encoding="utf-8")

        # Frontmatter check
        fm_errors = check_frontmatter(path, text)
        errors.extend(fm_errors)
        if not fm_errors and path.name not in FRONTMATTER_EXEMPT:
            fm_ok += 1

        if path.name == "log.md":
            headers = [line for line in text.splitlines() if line.startswith("## ")]
            for header in headers:
                if not LOG_HEADER_RE.match(header):
                    errors.append(f"bad log header format in {path.relative_to(ROOT)}: {header}")

        rel = path.relative_to(WIKI_ROOT).as_posix()
        if path.name != "index.md" and rel not in {"README.md", "SCHEMA.md", "log.md"}:
            if rel not in index_text:
                errors.append(f"index.md does not reference docs/wiki/{rel}")

        for match in LINK_RE.finditer(text):
            raw_target = match.group(1).strip()
            resolved = resolve_link(path, raw_target)
            if resolved is None:
                continue
            if not resolved.exists():
                errors.append(f"broken link in {path.relative_to(ROOT)} -> {raw_target}")

    if errors:
        print("wiki_check: FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("wiki_check: OK")
    print(f"- markdown files: {len(md_files)}")
    print(f"- required files: {len(REQUIRED_FILES)}")
    print(f"- frontmatter valid: {fm_ok}")
    print(f"- wiki root: {WIKI_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""


RAW_MANIFEST_CHECK = """from __future__ import annotations

import csv
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "raw_sources.csv"
EXPECTED_COLUMNS = [
    "source_id",
    "company",
    "vendor",
    "kind",
    "filename",
    "raw_rel_path",
    "status",
    "compiled_into",
    "notes",
]
ALLOWED_STATUS = {"new", "compiled", "archived"}


def main() -> int:
    errors: list[str] = []
    if not MANIFEST.exists():
        print(f"raw_manifest_check: missing {MANIFEST}")
        return 1

    raw_root_env = os.environ.get("PROJECT_RAW_ROOT")
    raw_root = Path(raw_root_env).expanduser().resolve() if raw_root_env else None

    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_COLUMNS:
            errors.append(f"manifest columns mismatch: expected {EXPECTED_COLUMNS}, got {reader.fieldnames}")
        seen_ids: set[str] = set()
        for idx, row in enumerate(reader, start=2):
            source_id = (row.get("source_id") or "").strip()
            filename = (row.get("filename") or "").strip()
            raw_rel_path = (row.get("raw_rel_path") or "").strip()
            status = (row.get("status") or "").strip()
            compiled_into = (row.get("compiled_into") or "").strip()

            if not source_id:
                errors.append(f"row {idx}: empty source_id")
            elif source_id in seen_ids:
                errors.append(f"row {idx}: duplicate source_id {source_id}")
            else:
                seen_ids.add(source_id)

            if not filename:
                errors.append(f"row {idx}: empty filename")
            if not raw_rel_path:
                errors.append(f"row {idx}: empty raw_rel_path")
            if status not in ALLOWED_STATUS:
                errors.append(f"row {idx}: bad status {status}")

            if raw_root and raw_rel_path:
                candidate = (raw_root / raw_rel_path).resolve()
                if not candidate.exists():
                    errors.append(f"row {idx}: missing local raw file {candidate}")

            if status == "compiled" and not compiled_into:
                errors.append(f"row {idx}: status {status} requires compiled_into")

    if errors:
        print("raw_manifest_check: FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("raw_manifest_check: OK")
    print(f"- manifest: {MANIFEST}")
    if raw_root:
        print(f"- PROJECT_RAW_ROOT: {raw_root}")
    else:
        print("- PROJECT_RAW_ROOT: not set, existence checks skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""


UNTRACKED_RAW_CHECK = """from __future__ import annotations

import csv
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "raw_sources.csv"

# File extensions that should be tracked in the manifest
RAW_EXTENSIONS = {
    ".pdf", ".xlsx", ".xls", ".xlsm", ".csv", ".tsv",
    ".doc", ".docx", ".ppt", ".pptx",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".mp3", ".mp4", ".wav", ".mov",
}

# Directories to skip entirely
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".obsidian", ".next", "dist", "build",
    "manifests",  # manifest CSVs are the index, not raw data
}


def load_manifest_filenames() -> set[str]:
    if not MANIFEST.exists():
        return set()
    names: set[str] = set()
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            fn = (row.get("filename") or "").strip()
            if fn:
                names.add(fn.lower())
    return names


def main() -> int:
    known = load_manifest_filenames()
    scan_roots = [ROOT]

    raw_root_env = os.environ.get("PROJECT_RAW_ROOT")
    if raw_root_env:
        raw_root = Path(raw_root_env).expanduser().resolve()
        if raw_root.exists():
            scan_roots.append(raw_root)

    untracked: list[tuple[str, Path]] = []

    for scan_root in scan_roots:
        for dirpath, dirnames, filenames in os.walk(scan_root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                ext = Path(fn).suffix.lower()
                if ext in RAW_EXTENSIONS and fn.lower() not in known:
                    full = Path(dirpath) / fn
                    rel = full.relative_to(scan_root) if full.is_relative_to(scan_root) else full
                    untracked.append((fn, rel))

    if untracked:
        print(f"untracked_raw_check: FOUND {len(untracked)} untracked raw file(s)")
        print("These files exist in the project but are NOT registered in manifests/raw_sources.csv:")
        print()
        for fn, rel in sorted(untracked, key=lambda x: str(x[1])):
            print(f"  {rel}")
        print()
        print("To fix: add each file to manifests/raw_sources.csv with status 'new',")
        print("then compile its key information into the relevant wiki page.")
        return 1

    print("untracked_raw_check: OK (no untracked raw files found)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""


INIT_RAW_ROOT = """from __future__ import annotations

import argparse
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_ROOT = (ROOT.parent / "{raw_root_name}").resolve()

DIRS = [
    "inbox",
    "internal_sources",
    "external_sources",
    "customer_answers",
    "screenshots",
    "extracted_text",
    "archive",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize the local raw root directory.")
    parser.add_argument(
        "path",
        nargs="?",
        default=os.environ.get("PROJECT_RAW_ROOT", str(DEFAULT_RAW_ROOT)),
        help="Absolute or relative path for the local raw root",
    )
    args = parser.parse_args()

    raw_root = Path(args.path).expanduser().resolve()
    raw_root.mkdir(parents=True, exist_ok=True)

    for rel in DIRS:
        (raw_root / rel).mkdir(parents=True, exist_ok=True)

    print(f"Initialized raw root: {{raw_root}}")
    for rel in DIRS:
        print(f"- {{raw_root / rel}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


EXPORT_MEMORY_REPO = """from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COPY_FILES = [
    "AGENTS.md",
    "scripts/wiki_check.py",
    "scripts/raw_manifest_check.py",
    "scripts/init_raw_root.py",
]

COPY_DIRS = [
    ("docs/wiki", "docs/wiki"),
    ("manifests", "manifests"),
]

OPTIONAL_COPY_DIRS = [
    ("verified_cases", "verified_cases"),
    ("backend/verified_cases", "verified_cases"),
]


def wipe_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_dir(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the repo memory surface into a dedicated GitHub/wiki repo checkout.")
    parser.add_argument("target_dir", help="Target memory repo checkout directory")
    args = parser.parse_args()

    target = Path(args.target_dir).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    managed_paths = [
        target / "AGENTS.md",
        target / "README.md",
        target / "docs",
        target / "manifests",
        target / "verified_cases",
        target / "scripts",
    ]
    for path in managed_paths:
        wipe_path(path)

    exported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme = f\"\"\"# Memory Repo

This repo is the exported long-term memory surface for a project.

## What belongs here

- `docs/wiki/`
- `manifests/`
- `verified_cases/`
- repo-level operating rules such as `AGENTS.md`

## What does not belong here

- raw PDFs / XLSX / XLS / ZIP / RAR files
- main application runtime code
- build artifacts

## Export time

`{exported_at}`

## Source repo

`{ROOT}`

## Refresh

Run from the source repo:

```bash
python3 scripts/export_memory_repo.py /path/to/memory-repo-checkout
```
\"\"\"
    (target / "README.md").write_text(readme, encoding="utf-8")

    for rel in COPY_FILES:
        src = ROOT / rel
        if src.exists():
            copy_file(src, target / rel)

    for src_rel, dest_rel in COPY_DIRS:
        src = ROOT / src_rel
        if src.exists():
            copy_dir(src, target / dest_rel)

    for src_rel, dest_rel in OPTIONAL_COPY_DIRS:
        src = ROOT / src_rel
        if src.exists():
            copy_dir(src, target / dest_rel)
            break

    print(f"Exported memory repo snapshot to: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a compile-first knowledge system into another repo.")
    parser.add_argument("target_dir", help="Target repository root")
    parser.add_argument("project_name", help="Human-readable project name")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing anything")
    parser.add_argument("--raw-root-name", help="Folder name to use for the default local raw root")
    args = parser.parse_args()

    target = Path(args.target_dir).expanduser().resolve()
    project_name = args.project_name.strip()
    slug = slugify(project_name)
    raw_root_name = args.raw_root_name or f"{slug}_raw"
    today = date.today().isoformat()

    files: dict[Path, str] = {
        target / "AGENTS.md": f"""# {project_name} Agent Rules

这仓库默认走 `wiki-first`，不是 `chat-first`。

## 1. 每个新 session 默认先干嘛

只要任务不是纯闲聊，默认先读：

1. `docs/wiki/index.md`
2. `docs/wiki/current-status.md`
3. `docs/wiki/log.md`

别一上来就靠 session 硬猜。

## 1.5 文档文件自动归档

凡是提到、收到、引用、保存的任何非代码文件 → 第一件事查 `manifests/raw_sources.csv`。
包括但不限于：PDF、Excel、截图、客户发来的附件、聊天图片、CAD图纸、压缩包。
不在里面 → 先登记再用。这步最容易漏。

定期跑 `python3 scripts/untracked_raw_check.py` 找遗漏。

## 2. 默认范式

- `compile-first`
- `writeback` 必做
- 中等规模先 `wiki`，不先上重 `RAG`
- Obsidian 可替换，范式不可替换
- `Idea / Intent` 优先于 `Code`

## 3. 知识分层

- raw：原始资料
- wiki：编译后的当前共识
- code：执行层

只改代码不回写 wiki，算没做完。

## 4. 一致性规则

- `current-status.md` 和其他 wiki 页面冲突时 → 以更具体的页面为准，然后修正 `current-status.md`
- `log.md` 缺少之前 session 的记录 → 不猜，只追加自己的
- 两个 wiki 页面矛盾 → 标记给用户，解决后再继续
""",
        target / "CLAUDE.md": f"""# {project_name} — Claude Rules

## Knowledge System
This project uses a wiki-first knowledge system. Knowledge lives in `docs/wiki/`, not in chat history.

## Session Protocol (mandatory)

### Session Start
1. Read `docs/wiki/index.md` — get the full page list
2. Read `docs/wiki/current-status.md` — know where things stand
3. Read `docs/wiki/log.md` — understand recent session history
4. Read additional wiki pages as needed for the current task

### During Work
- New decision made → update the relevant wiki page immediately
- **Any non-code file mentioned, received, referenced, or saved → check `manifests/raw_sources.csv` first. If not listed, register it before proceeding.** This includes PDFs, spreadsheets, screenshots, customer attachments, chat images, debug captures, CAD files, archives. This is the most commonly skipped step.
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
Normal operations are cheap. Full audit/recompilation are disaster recovery, not regular workflow.
- Session start: read 3 files (index, status, log). ~2K tokens. Never read all pages upfront.
- During work: read specific pages one at a time, only when needed.
- Structural checks: Python scripts (wiki_check.py, untracked_raw_check.py) — zero LLM tokens.
- If every session does incremental writeback, you never need full audit or recompilation.

### Rules
- compile-first: don't just answer, write conclusions into wiki pages
- writeback is mandatory: if you learned something durable, it goes in the wiki
- all non-code files are raw — PDFs, spreadsheets, images, screenshots, customer files, archives
- raw files stay outside Git, only manifests go in
- every wiki page (except index.md and log.md) must have YAML frontmatter with at least: title, source, created
""",
        target / "docs" / "wiki" / "README.md": f"""# {project_name} Wiki

这套 wiki 解决三个问题：

1. 新 session 老失忆
2. 资料散在各处，没人知道先看哪
3. 新结论只活在聊天里

默认范式：

- `compile-first`
- `writeback` 必做
- 中等规模先 `wiki`
- Obsidian 可替换，范式不可替换
- `Idea / Intent` 优先于 `Code`

自检：

```bash
python3 scripts/wiki_check.py
python3 scripts/raw_manifest_check.py
```
""",
        target / "docs" / "wiki" / "SCHEMA.md": f"""# Wiki Schema

## Frontmatter（每个 wiki 页面必须有）

每个 `.md` 文件的头部用 YAML frontmatter 标注来源和状态：

```yaml
---
title: 页面标题
source: 编译来源（raw 文件路径、URL、或 "session" 表示来自对话）
created: 创建日期 (YYYY-MM-DD)
updated: 最后更新日期 (YYYY-MM-DD)
tags: [标签1, 标签2]
status: current / draft / stale
---
```

### 必填字段
- `title` — 页面标题
- `source` — 信息来源。让每个事实可追溯。
- `created` — 创建日期

### 可选字段
- `updated` — 最后更新日期（不填则等于 created）
- `tags` — 分类标签，Obsidian 可直接用
- `status` — `current`（默认）/ `draft`（未确认）/ `stale`（可能过期）

### 为什么这样设计
- AI 读一个页面就知道信息从哪来，不用额外查 manifest
- Obsidian 原生支持 frontmatter 属性面板
- 比在正文里写"来源：xxx"更结构化，脚本可以校验
- 零额外 token 开销（frontmatter 是页面自身的一部分）

## 页面

- `index.md`（免 frontmatter，纯索引）
- `log.md`（免 frontmatter，纯日志）
- `project-overview.md`
- `current-status.md`
- `sources-and-data.md`
- `github-and-raw-strategy.md`

## 规则

1. 新 raw 进来，先登记 manifest
2. 新结论，必须回写 wiki（带 frontmatter）
3. 新规则，必须同时补测试
4. 没证据，不要写成结论
5. memory repo 只放编译结果，不放 raw 本体
""",
        target / "docs" / "wiki" / "index.md": """# Wiki Index

- [README.md](./README.md)
- [SCHEMA.md](./SCHEMA.md)
- [project-overview.md](./project-overview.md)
- [current-status.md](./current-status.md)
- [sources-and-data.md](./sources-and-data.md)
- [github-and-raw-strategy.md](./github-and-raw-strategy.md)
- [log.md](./log.md)
""",
        target / "docs" / "wiki" / "log.md": f"""# Wiki Log

## [{today}] bootstrap | 初始化知识系统

- 建立 wiki、manifest、检查脚本和 repo 级默认规则。
""",
        target / "docs" / "wiki" / "project-overview.md": f"""---
title: {project_name} Overview
source: session
created: {today}
tags: [overview]
status: draft
---

# {project_name} Overview

这里写项目的一句话定义、主线目标、交付边界。
""",
        target / "docs" / "wiki" / "current-status.md": f"""---
title: {project_name} Current Status
source: session
created: {today}
tags: [status]
status: current
---

# {project_name} Current Status

这里写当前已支持、未支持、线上状态、最近风险。
""",
        target / "docs" / "wiki" / "sources-and-data.md": f"""---
title: Sources and Data
source: session
created: {today}
tags: [data, raw]
status: current
---

# {project_name} Sources and Data

原始资料默认放在本地 raw 根目录，不直接进 Git。

raw 根目录建议：

```text
../{raw_root_name}/
```

GitHub 里只保留 manifest 和编译结果。
""",
        target / "docs" / "wiki" / "github-and-raw-strategy.md": f"""---
title: GitHub and Raw Strategy
source: session
created: {today}
tags: [strategy, git]
status: current
---

# GitHub and Raw Strategy

## 结论

- GitHub private repo 放：`code + wiki + manifests + verified_cases`
- 本地 raw 仓放：`pdf/xlsx/xls/rar/图片/客户原件`
- memory repo 放：编译后的长期记忆，不放 raw 本体

## 为什么

把全量 raw 塞进 Git，只会让仓库越来越肥，diff 也基本没用。

真正该版本化的是：

- 结论
- 规则
- 答案表
- 清晰的索引

不是一堆二进制原件。
""",
        target / "manifests" / "README.md": """# Manifests

这里放 raw 的索引，不放 raw 本体。
""",
        target / "manifests" / "raw_sources.csv": "source_id,company,vendor,kind,filename,raw_rel_path,status,compiled_into,notes\n",
        target / "scripts" / "wiki_check.py": WIKI_CHECK,
        target / "scripts" / "raw_manifest_check.py": RAW_MANIFEST_CHECK,
        target / "scripts" / "untracked_raw_check.py": UNTRACKED_RAW_CHECK,
        target / "scripts" / "init_raw_root.py": INIT_RAW_ROOT.format(raw_root_name=raw_root_name),
        target / "scripts" / "export_memory_repo.py": EXPORT_MEMORY_REPO,
        target / ".cursorrules": f"""This project ({project_name}) uses a wiki-first knowledge system.

Before starting any non-trivial task:
1. Read docs/wiki/index.md for the wiki page list
2. Read docs/wiki/current-status.md for project state
3. Read docs/wiki/log.md for recent session history

During work:
- Any non-code file mentioned, received, or saved (PDF, Excel, screenshots, customer attachments,
  chat images, CAD files, archives) → check manifests/raw_sources.csv first
- Not listed → register it before proceeding. This step is most commonly skipped.

After completing work:
- Update docs/wiki/current-status.md with new state
- Append a log entry to docs/wiki/log.md (date | topic | outcome)
- If a durable decision was made, write it into the relevant wiki page

Consistency:
- If current-status.md conflicts with other wiki pages, trust the specific page and fix current-status.md
- If log.md is missing prior entries, don't guess — only append your own
- If two wiki pages contradict, flag it to the user before proceeding

Rules:
- Compile raw documents into wiki pages, don't just reference them
- Every conclusion goes back into the wiki (writeback is mandatory)
- Raw files (PDF/XLSX) stay outside Git, only manifests/ indexes go in
""",
        target / ".windsurfrules": f"""This project ({project_name}) uses a wiki-first knowledge system.

Before starting any non-trivial task:
1. Read docs/wiki/index.md for the wiki page list
2. Read docs/wiki/current-status.md for project state
3. Read docs/wiki/log.md for recent session history

After completing work:
- Update docs/wiki/current-status.md with new state
- Append a log entry to docs/wiki/log.md (date | topic | outcome)
- If a durable decision was made, write it into the relevant wiki page

Consistency:
- If current-status.md conflicts with other wiki pages, trust the specific page and fix current-status.md
- If log.md is missing prior entries, don't guess — only append your own
- If two wiki pages contradict, flag it to the user before proceeding

Rules:
- Compile raw documents into wiki pages, don't just reference them
- Every conclusion goes back into the wiki (writeback is mandatory)
- Raw files (PDF/XLSX) stay outside Git, only manifests/ indexes go in
""",
        target / ".github" / "workflows" / "wiki-lint.yml": """name: Wiki Lint
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check wiki structure
        run: python3 scripts/wiki_check.py
      - name: Check raw manifest
        run: python3 scripts/raw_manifest_check.py
      - name: Check for untracked raw files
        run: python3 scripts/untracked_raw_check.py
""",
        target / ".gitignore": ".obsidian/\\nraw/\\nraw_local/\\nraw_vault/\\n",
    }

    created: list[Path] = []
    skipped: list[Path] = []
    for path, content in files.items():
        if path.exists() and not args.force:
            skipped.append(path)
            continue
        if not args.dry_run:
            write(path, content)
        created.append(path)

    if args.dry_run:
        print(f"[DRY RUN] Would bootstrap: {project_name}")
        print(f"Target repo: {target}")
        print(f"Default raw root name: {raw_root_name}")
        print(f"\\nWould create {len(created)} files:")
        for path in created:
            print(f"  + {path.relative_to(target)}")
        if skipped:
            print(f"\\nWould skip {len(skipped)} existing files (use --force to overwrite):")
            for path in skipped:
                print(f"  ~ {path.relative_to(target)}")
        return 0

    print(f"Bootstrapped knowledge system for: {project_name}")
    print(f"Target repo: {target}")
    print(f"Default raw root name: {raw_root_name}")
    print(f"\\nFiles created: {len(created)}")
    for path in created:
        print(f"  + {path.relative_to(target)}")
    if skipped:
        print(f"\\nSkipped (already exist): {len(skipped)}")
        for path in skipped:
            print(f"  ~ {path.relative_to(target)}")

    print("\\nNext steps:")
    print(f"1. cd {target}")
    print("2. python3 scripts/init_raw_root.py")
    print("3. python3 scripts/wiki_check.py")
    print("4. python3 scripts/raw_manifest_check.py")
    print("5. python3 scripts/export_memory_repo.py /path/to/memory-repo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
