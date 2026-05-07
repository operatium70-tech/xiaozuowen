#!/usr/bin/env python3
"""Clean source Markdown chapters into publish-ready text.

Conversion rules:
- Remove YAML frontmatter at the top of a chapter.
- Remove HTML comments used for Obsidian review annotations.
- Remove engineering-only level-2 sections:
  "关联索引", "本章推进", "新伏笔", "情绪节奏".
- Convert Obsidian wiki links to plain text:
  [[李阳]] -> 李阳, [[path|label]] -> label.
- Convert remaining Markdown headings to plain text for txt publishing.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


BLOCK_ONLY_SECTIONS = {"关联索引"}
DROP_TO_NEXT_HEADING_SECTIONS = {"本章推进", "新伏笔", "情绪节奏"}


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + len("\n---\n") :]


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def strip_engineering_sections(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    skipping = False
    skipping_block = False
    skip_level = 0

    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

    for line in lines:
        match = heading_re.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            if title in BLOCK_ONLY_SECTIONS and level == 2:
                skipping_block = True
                continue
            if title in DROP_TO_NEXT_HEADING_SECTIONS and level == 2:
                skipping = True
                skip_level = level
                continue
            if skipping and level <= skip_level:
                skipping = False

        if skipping_block:
            stripped = line.strip()
            if not stripped or stripped.startswith("- "):
                continue
            skipping_block = False

        if not skipping:
            kept.append(line)

    return "\n".join(kept)


def convert_wiki_links(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        if "|" in target:
            return target.split("|", 1)[1]
        return target.split("#", 1)[0]

    return re.sub(r"\[\[([^\]]+)\]\]", replace, text)


def convert_markdown_headings(text: str) -> str:
    return re.sub(r"^#{1,6}\s+(.+?)\s*$", r"\1", text, flags=re.MULTILINE)


def normalize_blank_lines(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    return text + "\n"


def clean_markdown(text: str) -> str:
    text = strip_frontmatter(text)
    text = strip_html_comments(text)
    text = strip_engineering_sections(text)
    text = convert_wiki_links(text)
    text = convert_markdown_headings(text)
    return normalize_blank_lines(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a Markdown chapter for publishing.")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source_text = args.source.read_text(encoding="utf-8")
    cleaned = clean_markdown(source_text)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(cleaned, encoding="utf-8")


if __name__ == "__main__":
    main()
