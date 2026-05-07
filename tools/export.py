#!/usr/bin/env python3
"""Export current publish-ready files for the novel project."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM_DIR = ROOT / "9_发布版本" / "平台发布版"
MERGED_DIR = ROOT / "9_发布版本" / "全卷整合版"
CHAPTER_RE = re.compile(r"^第(\d+)章[_\s]*(.+)$")
MAX_CHAPTER_PER_VOLUME = 999
SKIP_MARKERS = ("开头方案", "批注处理记录")


@dataclass(frozen=True)
class VolumeConfig:
    label: str
    name: str
    source_dir: Path
    publish_dir: Path
    platform_dir: Path
    merged_output: Path | None = None


VOLUMES = [
    VolumeConfig(
        label="第一卷",
        name="第一卷_灾变降临",
        source_dir=ROOT / "4_正文源码" / "第一卷_灾变降临",
        publish_dir=ROOT / "9_发布版本" / "第一卷",
        platform_dir=PLATFORM_DIR / "第一卷_灾变降临",
        merged_output=MERGED_DIR / "第一卷_灾变降临_当前整合.txt",
    ),
    VolumeConfig(
        label="第二卷",
        name="第二卷",
        source_dir=ROOT / "4_正文源码" / "第二卷",
        publish_dir=ROOT / "9_发布版本" / "第二卷",
        platform_dir=PLATFORM_DIR / "第二卷",
    ),
]


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def md_preview_name(txt_name: str) -> str:
    return txt_name.removesuffix(".txt") + "_md.md"


def export_clean(source: Path, txt_output: Path) -> None:
    md_output = txt_output.with_name(md_preview_name(txt_output.name))
    txt_output.parent.mkdir(parents=True, exist_ok=True)
    run(["python3", "tools/clean_markdown.py", str(source), str(txt_output)])
    md_output.write_text(txt_output.read_text(encoding="utf-8"), encoding="utf-8")


def chapter_sort_key(path: Path) -> tuple[int, str]:
    match = CHAPTER_RE.match(path.stem)
    if match:
        return int(match.group(1)), path.name
    return 999999, path.name


def is_publishable_chapter(path: Path) -> bool:
    return path.is_file() and not any(marker in path.name for marker in SKIP_MARKERS)


def platform_output_name(volume: VolumeConfig, chapter: Path) -> str:
    match = CHAPTER_RE.match(chapter.stem)
    if not match:
        return f"{volume.label}_{chapter.with_suffix('.txt').name}"
    chapter_number = int(match.group(1))
    if chapter_number > MAX_CHAPTER_PER_VOLUME:
        raise ValueError(f"{volume.name} 的章节号超过 999：{chapter.name}。请拆分到新卷后再导出。")
    title = match.group(2)
    return f"{volume.label}_第{chapter_number:03d}章_{title}.txt"


def export_volume(volume: VolumeConfig) -> None:
    if not volume.source_dir.exists():
        return
    chapters = sorted(
        (chapter for chapter in volume.source_dir.glob("第*.md") if is_publishable_chapter(chapter)),
        key=chapter_sort_key,
    )
    if not chapters:
        return
    for chapter in chapters:
        export_clean(chapter, volume.publish_dir / chapter.with_suffix(".txt").name)
        export_clean(chapter, volume.platform_dir / platform_output_name(volume, chapter))

    if volume.merged_output:
        run(["python3", "tools/build_volume.py", str(volume.source_dir), str(volume.merged_output)])
        volume.merged_output.with_name(md_preview_name(volume.merged_output.name)).write_text(
            volume.merged_output.read_text(encoding="utf-8"), encoding="utf-8"
        )


def main() -> None:
    for volume in VOLUMES:
        export_volume(volume)


if __name__ == "__main__":
    main()
