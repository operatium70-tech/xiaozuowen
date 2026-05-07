#!/usr/bin/env python3
"""Export current publish-ready files for the novel project."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRST_VOLUME_SOURCE = ROOT / "4_正文源码" / "第一卷_灾变降临"
FIRST_VOLUME_DIR = ROOT / "9_发布版本" / "第一卷"
PLATFORM_DIR = ROOT / "9_发布版本" / "平台发布版"
MERGED_DIR = ROOT / "9_发布版本" / "全卷整合版"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def md_preview_name(txt_name: str) -> str:
    return txt_name.removesuffix(".txt") + "_md.md"


def export_clean(source: Path, txt_output: Path) -> None:
    md_output = txt_output.with_name(md_preview_name(txt_output.name))
    run(["python3", "tools/clean_markdown.py", str(source), str(txt_output)])
    md_output.write_text(txt_output.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> None:
    for chapter in sorted(FIRST_VOLUME_SOURCE.glob("第*.md")):
        if "开头方案" in chapter.name or "批注处理记录" in chapter.name:
            continue
        output_name = chapter.with_suffix(".txt").name
        export_clean(chapter, FIRST_VOLUME_DIR / output_name)
        export_clean(chapter, PLATFORM_DIR / output_name)

    merged_output = MERGED_DIR / "第一卷_灾变降临_当前整合.txt"
    run(["python3", "tools/build_volume.py", str(FIRST_VOLUME_SOURCE), str(merged_output)])
    merged_output.with_name(md_preview_name(merged_output.name)).write_text(
        merged_output.read_text(encoding="utf-8"), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
