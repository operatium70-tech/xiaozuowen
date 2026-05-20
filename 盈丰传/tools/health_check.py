#!/usr/bin/env python3
"""Run read-only structural checks for the Yingfeng Zhuan project."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

from story_config import ROOT, iter_source_chapters


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: list[str]


KEY_PATHS = [
    "README.md",
    "总控制大屏.md",
    "Obsidian工作台/README.md",
    "Obsidian工作台/Templater模板/README.md",
    "系统规则/README.md",
    "世界观/README.md",
    "人物设定/README.md",
    "剧情大纲/README.md",
    "正文源码/README.md",
    "文风控制/README.md",
    "参考资料/README.md",
    "长期记忆/README.md",
    "技能规则/README.md",
    "发布版本/README.md",
    "素材资源/README.md",
    "tools/README.md",
]

REQUIRED_DIRS = [
    "剧情大纲/定稿/全局",
    "剧情大纲/定稿/复盘/十章复盘",
    "剧情大纲/定稿/时间线/十章时间线",
    "剧情大纲/定稿/后续/十章细纲",
    "正文源码/正文章节/蓄水期",
    "长期记忆/当前状态",
    "发布版本/平台发布版/正文章节",
    "素材资源/版权与来源",
]


def git_file_list() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def check_key_paths() -> CheckResult:
    missing = [path for path in KEY_PATHS if not (ROOT / path).exists()]
    return CheckResult("关键入口文件", not missing, missing or ["全部存在"])


def check_required_dirs() -> CheckResult:
    missing = [path for path in REQUIRED_DIRS if not (ROOT / path).is_dir()]
    return CheckResult("关键目录", not missing, missing or ["全部存在"])


def check_no_root_loose_notes() -> CheckResult:
    allowed = {"README.md", "总控制大屏.md"}
    loose = []
    for item in ROOT.iterdir():
        if item.is_file() and item.suffix.lower() in {".md", ""} and item.name not in allowed:
            loose.append(item.name)
    return CheckResult("根目录散落文档", not loose, loose or ["未发现散落文档"])


def check_empty_files() -> CheckResult:
    empty = []
    for path in git_file_list():
        if path.exists() and path.is_file() and path.stat().st_size <= 1:
            empty.append(path.relative_to(ROOT).as_posix())
    return CheckResult("空文件", not empty, empty or ["未发现 0/1 字节文件"])


def check_python_compile() -> CheckResult:
    failures = []
    for script in sorted((ROOT / "tools").glob("*.py")):
        try:
            source = script.read_text(encoding="utf-8-sig")
            compile(source, str(script), "exec")
        except SyntaxError as exc:
            failures.append(f"{script.relative_to(ROOT).as_posix()}: {exc.msg}")
    return CheckResult("Python 语法", not failures, failures or ["tools/*.py 全部通过"])


def check_source_status() -> CheckResult:
    chapters = iter_source_chapters()
    if chapters:
        return CheckResult("正文源码状态", True, [f"已发现 {len(chapters)} 个正文源文件"])
    return CheckResult("正文源码状态", True, ["当前无正文源文件，符合本阶段边界"])


def render(result: CheckResult) -> str:
    mark = "OK" if result.ok else "FAIL"
    details = "\n".join(f"  - {line}" for line in result.details)
    return f"[{mark}] {result.name}\n{details}"


def main() -> int:
    checks = [
        check_key_paths(),
        check_required_dirs(),
        check_no_root_loose_notes(),
        check_empty_files(),
        check_source_status(),
        check_python_compile(),
    ]
    print("\n\n".join(render(check) for check in checks))
    return 0 if all(check.ok for check in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
