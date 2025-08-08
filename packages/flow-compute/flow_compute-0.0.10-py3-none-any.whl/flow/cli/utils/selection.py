"""Selection parser and model (core).

Parses index sets like :1, :1-3, :1-3,5,7.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


class SelectionParseError(Exception):
    pass


@dataclass
class Selection:
    indices: List[int]

    @staticmethod
    def parse(text: str) -> "Selection":
        s = text.strip()
        if not s.startswith(":"):
            raise SelectionParseError("Selection must start with ':'")
        body = s[1:]
        if not body:
            raise SelectionParseError("Empty selection")
        parts = [p.strip() for p in body.split(",") if p.strip()]
        indices: List[int] = []
        for p in parts:
            if "-" in p:
                a, b = p.split("-", 1)
                if not (a.isdigit() and b.isdigit()):
                    raise SelectionParseError(f"Invalid range: {p}")
                start = int(a)
                end = int(b)
                if end < start:
                    raise SelectionParseError(f"Invalid range: {p}")
                indices.extend(range(start, end + 1))
            else:
                if not p.isdigit():
                    raise SelectionParseError(f"Invalid index: {p}")
                indices.append(int(p))
        # De-duplicate while preserving order
        seen = set()
        uniq: List[int] = []
        for i in indices:
            if i not in seen:
                seen.add(i)
                uniq.append(i)
        return Selection(indices=uniq)
