#!/usr/bin/env python3
"""Build a publish-ready volume text file from source Markdown chapters."""

from __future__ import annotations

import argparse
from pathlib import Path

from clean_markdown import clean_markdown


def chapter_sort_key(path: Path) -> str:
    return path.name


def build_volume(source_dir: Path) -> str:
    chapters = sorted(source_dir.glob("第*.md"), key=chapter_sort_key)
    cleaned_chapters = []
    for chapter in chapters:
        if "开头方案" in chapter.name:
            continue
        cleaned_chapters.append(clean_markdown(chapter.read_text(encoding="utf-8")).strip())
    return "\n\n".join(cleaned_chapters).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a publish-ready volume from chapters.")
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    text = build_volume(args.source_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
