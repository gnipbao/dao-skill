"""Shared helpers for deterministic Markdown validation."""

from __future__ import annotations

import re


def strip_nonsemantic_markdown(text: str) -> str:
    """Remove HTML comments and fenced code before checking semantic markers."""

    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    output: list[str] = []
    fence_char: str | None = None
    fence_length = 0

    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence_char is None and match:
            marker = match.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            output.append("\n" if line.endswith("\n") else "")
            continue
        if fence_char is not None:
            closing = re.match(
                r"^\s{0,3}([`~]{3,})\s*$", line.rstrip("\r\n")
            )
            if (
                closing
                and closing.group(1)[0] == fence_char
                and len(closing.group(1)) >= fence_length
            ):
                fence_char = None
                fence_length = 0
            output.append("\n" if line.endswith("\n") else "")
        else:
            output.append(line)

    return "".join(output)
