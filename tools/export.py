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


def main() -> None:
    for chapter in sorted(FIRST_VOLUME_SOURCE.glob("第*.md")):
        if "开头方案" in chapter.name:
            continue
        output_name = chapter.with_suffix(".txt").name
        run(["python3", "tools/clean_markdown.py", str(chapter), str(FIRST_VOLUME_DIR / output_name)])
        run(["python3", "tools/clean_markdown.py", str(chapter), str(PLATFORM_DIR / output_name)])

    run(
        [
            "python3",
            "tools/build_volume.py",
            str(FIRST_VOLUME_SOURCE),
            str(MERGED_DIR / "第一卷_灾变降临_当前整合.txt"),
        ]
    )


if __name__ == "__main__":
    main()
