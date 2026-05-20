#!/usr/bin/env python3
"""Shared paths for the Yingfeng Zhuan novel project."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK_TITLE = "盈丰传"

SOURCE_DIR = ROOT / "正文源码" / "正文章节"
PUBLISH_DIR = ROOT / "发布版本" / "章节"
PLATFORM_DIR = ROOT / "发布版本" / "平台发布版" / "正文章节"
MANUSCRIPT_DIR = ROOT / "发布版本" / "全文整合版"
MANUSCRIPT_OUTPUT = MANUSCRIPT_DIR / "当前全文整合.txt"
CHAPTER_RE = re.compile(r"^第(\d+)章[_\s]*(.+)$")


@dataclass(frozen=True)
class PhaseConfig:
    name: str
    start: int
    end: int | None

    def contains(self, chapter_number: int) -> bool:
        if chapter_number < self.start:
            return False
        return self.end is None or chapter_number <= self.end


PHASES = [
    PhaseConfig("蓄水期", 1, 80),
]


def phase_for_chapter(chapter_number: int) -> PhaseConfig:
    for phase in PHASES:
        if phase.contains(chapter_number):
            return phase
    return PhaseConfig("阶段未规划", chapter_number, chapter_number)


def chapter_sort_key(path: Path) -> tuple[int, str]:
    match = CHAPTER_RE.match(path.stem)
    if match:
        return int(match.group(1)), path.name
    return 999999, path.name


def iter_source_chapters(source_dir: Path = SOURCE_DIR) -> list[Path]:
    if not source_dir.exists():
        return []
    return sorted(source_dir.rglob("第*.md"), key=chapter_sort_key)

