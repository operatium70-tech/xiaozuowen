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
    "总控制大屏.md",
    "Obsidian工作台/工程设计理念.md",
    "系统规则/AI协作说明.md",
    "系统规则/开写白名单.md",
    "系统规则/最终设定硬规则.md",
    "系统规则/当前硬边界.md",
    "世界观/世界基础架构.md",
    "世界观/宇宙本源与场粒关系.md",
    "世界观/宇宙航行与场控穿梭.md",
    "世界观/生命形态与元素适配.md",
    "世界观/星球画风差异根源.md",
    "世界观/元能.md",
    "世界观/境界与元素熵变适配.md",
    "世界观/学院生态与筛选机制.md",
    "人物设定/人物索引.md",
    "人物设定/配角功能总表.md",
    "人物设定/赵盈丰前期旁门杂学.md",
    "人物设定/赵盈丰前期胜利方式.md",
    "剧情大纲/待确认问题.md",
    "剧情大纲/定稿/全局/总纲.md",
    "剧情大纲/定稿/全局/长篇结构补全草案.md",
    "剧情大纲/定稿/全局/伏笔候选投放表.md",
    "剧情大纲/定稿/全局/赵盈丰与赵倩倩关系阶段表.md",
    "剧情大纲/定稿/第一阶段白丁境/第一阶段剧情推进总表.md",
    "剧情大纲/定稿/第一阶段白丁境/配角功能与冲突网.md",
    "剧情大纲/定稿/第二阶段炼气境/阶段总纲.md",
    "剧情大纲/定稿/第二阶段炼气境/阶段功能定义.md",
    "剧情大纲/定稿/第二阶段炼气境/第二阶段剧情推进总表.md",
    "剧情大纲/定稿/第三阶段筑基境/阶段总纲.md",
    "剧情大纲/定稿/第三阶段筑基境/阶段功能定义.md",
    "剧情大纲/定稿/第三阶段筑基境/第三阶段剧情推进总表.md",
    "剧情大纲/定稿/第四阶段万象境/阶段总纲.md",
    "剧情大纲/定稿/后续/十章细纲/赛前铺垫与系内选拔起势细纲.md",
    "剧情大纲/定稿/后续/场景卡/前三章场景卡.md",
    "文风控制/小说定位.md",
    "参考资料/竞品与平台研究/沧元图结构读法.md",
    "参考资料/设定来源记录.md",
    "长期记忆/设定归档.md",
    "技能规则/Obsidian写作方法.md",
    "素材资源/素材索引.md",
    "tools/health_check.py",
]

REQUIRED_DIRS = [
    "剧情大纲/定稿/全局",
    "剧情大纲/定稿/第一阶段白丁境",
    "剧情大纲/定稿/第二阶段炼气境",
    "剧情大纲/定稿/第三阶段筑基境",
    "剧情大纲/定稿/第四阶段万象境",
    "剧情大纲/定稿/后续/场景卡",
    "剧情大纲/定稿/复盘/十章复盘",
    "剧情大纲/定稿/时间线/十章时间线",
    "剧情大纲/定稿/后续/十章细纲",
    "人物设定/学院配角",
    "人物设定/势力人物",
    "人物设定/组织观察者",
    "正文源码/正文章节/蓄水期",
    "长期记忆/当前状态",
    "发布版本/平台发布版/正文章节",
    "素材资源/版权与来源",
]

REQUIRED_PHASE_FILES = [
    "剧情大纲/定稿/第一阶段白丁境/阶段总纲.md",
    "剧情大纲/定稿/第一阶段白丁境/阶段功能定义.md",
    "剧情大纲/定稿/第一阶段白丁境/学院比赛篇规划.md",
    "剧情大纲/定稿/第一阶段白丁境/学院比赛赛制.md",
    "剧情大纲/定稿/第一阶段白丁境/学院比赛利益结构.md",
    "剧情大纲/定稿/第一阶段白丁境/学院比赛人物弧线.md",
    "剧情大纲/定稿/第一阶段白丁境/学院比赛名场面.md",
    "剧情大纲/定稿/第一阶段白丁境/比赛篇章节安排.md",
    "剧情大纲/定稿/第一阶段白丁境/第一阶段剧情推进总表.md",
    "剧情大纲/定稿/第一阶段白丁境/配角功能与冲突网.md",
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
    allowed = {"总控制大屏.md"}
    loose = []
    for item in ROOT.iterdir():
        if item.is_file() and item.suffix.lower() in {".md", ""} and item.name not in allowed:
            loose.append(item.name)
    return CheckResult("根目录散落文档", not loose, loose or ["未发现散落文档"])


def check_outline_root_structure() -> CheckResult:
    outline_dir = ROOT / "剧情大纲"
    allowed_files = {"待确认问题.md"}
    allowed_dirs = {"定稿"}
    unexpected = []
    if outline_dir.exists():
        for item in outline_dir.iterdir():
            if item.is_file() and item.name not in allowed_files:
                unexpected.append(item.relative_to(ROOT).as_posix())
            if item.is_dir() and item.name not in allowed_dirs:
                unexpected.append(item.relative_to(ROOT).as_posix())
    return CheckResult("剧情大纲根目录结构", not unexpected, unexpected or ["只保留待确认问题、定稿"])


def check_no_readme_files() -> CheckResult:
    readmes = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.rglob("README.md"))
    return CheckResult("README 文件", not readmes, readmes or ["未发现 README.md"])


def check_phase_outline_structure() -> CheckResult:
    missing = [path for path in REQUIRED_PHASE_FILES if not (ROOT / path).is_file()]
    global_dir = ROOT / "剧情大纲" / "定稿" / "全局"
    misplaced = []
    if global_dir.exists():
        for item in global_dir.iterdir():
            if item.is_file() and ("第一阶段" in item.name or "学院比赛" in item.name or "比赛篇" in item.name):
                misplaced.append(item.relative_to(ROOT).as_posix())
    details = []
    details.extend(f"缺失: {path}" for path in missing)
    details.extend(f"误放全局: {path}" for path in misplaced)
    return CheckResult("第一阶段目录结构", not details, details or ["第一阶段文件已归入阶段目录"])


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
        check_no_readme_files(),
        check_no_root_loose_notes(),
        check_outline_root_structure(),
        check_phase_outline_structure(),
        check_empty_files(),
        check_source_status(),
        check_python_compile(),
    ]
    print("\n\n".join(render(check) for check in checks))
    return 0 if all(check.ok for check in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
