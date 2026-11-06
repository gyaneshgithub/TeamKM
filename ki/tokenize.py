from __future__ import annotations

import re
from collections import Counter

_WORD_RE = re.compile(r"[a-z0-9_]+", re.I)


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _WORD_RE.finditer(text or "")]


def term_freq(text: str) -> Counter[str]:
    return Counter(tokenize(text))
