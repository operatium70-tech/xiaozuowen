#!/usr/bin/env python3
"""Generate word-count statistics for source chapters.

The report is for project management only. It is written to 7_长期记忆/
and must not be copied into publish outputs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from clean_markdown import clean_markdown
from export import VOLUMES, chapter_sort_key, is_publishable_chapter


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "7_长期记忆" / "字数统计.md"
CHAPTER_TITLE_RE = re.compile(r"^第\d+章[^\n]*(?:\n|$)")


@dataclass(frozen=True)
class ChapterCount:
    volume: str
    chapter: str
    title: str
    source: Path
    count: int


@dataclass(frozen=True)
class VolumeCount:
    volume: str
    count: int
    chapters: list[ChapterCount]


def count_visible_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def chapter_body(cleaned_text: str) -> str:
    return CHAPTER_TITLE_RE.sub("", cleaned_text, count=1).strip()


def split_chapter_name(path: Path) -> tuple[str, str]:
    stem = path.stem
    match = re.match(r"^(第\d+章)[_\s]*(.+)$", stem)
    if match:
        return match.group(1), match.group(2)
    return stem, ""


def count_chapter(volume_label: str, chapter_path: Path) -> ChapterCount:
    cleaned = clean_markdown(chapter_path.read_text(encoding="utf-8"))
    chapter, title = split_chapter_name(chapter_path)
    return ChapterCount(
        volume=volume_label,
        chapter=chapter,
        title=title,
        source=chapter_path.relative_to(ROOT),
        count=count_visible_chars(chapter_body(cleaned)),
    )


def collect_counts() -> list[VolumeCount]:
    volume_counts: list[VolumeCount] = []
    for volume in VOLUMES:
        if not volume.source_dir.exists():
            continue
        chapters = [
            count_chapter(volume.label, chapter)
            for chapter in sorted(
                (path for path in volume.source_dir.glob("第*.md") if is_publishable_chapter(path)),
                key=chapter_sort_key,
            )
        ]
        if not chapters:
            continue
        volume_counts.append(
            VolumeCount(
                volume=volume.name,
                count=sum(chapter.count for chapter in chapters),
                chapters=chapters,
            )
        )
    return volume_counts


def render_report(volume_counts: list[VolumeCount]) -> str:
    total_count = sum(volume.count for volume in volume_counts)
    total_chapters = sum(len(volume.chapters) for volume in volume_counts)
    lines = [
        "# 字数统计",
        "",
        "## 统计口径",
        "",
        "- 本文件由 `python3 tools/word_count.py` 生成，用于创作管理。",
        "- 统计基于 `tools/clean_markdown.py` 清理后的发布正文。",
        "- 章节标题、YAML frontmatter、Obsidian 双链、批注、关联索引和 AI 工程尾注不计入字数。",
        "- 字数按正文非空白可见字符估算，标点计入；平台实际统计可能存在轻微差异。",
        "- 本文件属于长期记忆与工程管理层，禁止进入 `9_发布版本/`。",
        "",
        "## 总览",
        "",
        "| 项目 | 数量 |",
        "| --- | ---: |",
        f"| 全书已写字数 | {total_count} |",
        f"| 已写章节数 | {total_chapters} |",
        f"| 已写卷数 | {len(volume_counts)} |",
        "",
        "## 分卷统计",
        "",
        "| 卷 | 章节数 | 字数 |",
        "| --- | ---: | ---: |",
    ]
    for volume in volume_counts:
        lines.append(f"| {volume.volume} | {len(volume.chapters)} | {volume.count} |")

    lines.extend(["", "## 章节明细", "", "| 卷 | 章节 | 标题 | 字数 | 源文件 |", "| --- | --- | --- | ---: | --- |"])
    for volume in volume_counts:
        for chapter in volume.chapters:
            lines.append(
                f"| {volume.volume} | {chapter.chapter} | {chapter.title} | {chapter.count} | `{chapter.source}` |"
            )

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    REPORT_PATH.write_text(render_report(collect_counts()), encoding="utf-8")
    print(f"已生成 {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
