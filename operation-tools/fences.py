"""Where a Markdown code fence opens and closes, read as CommonMark reads it.

Standard library only: validate.py and figures_check.py both import it, and
`make figures` runs without the validator's dependencies or its registry.
"""
from __future__ import annotations      # `str | None` on Python 3.9

import re

# Only spaces: a tab is four columns, which makes the line indented code rather
# than a fence. How many spaces a fence may carry is Fences' to say.
FENCE_RE = re.compile(r"^( *)(`{3,}|~{3,})(.*)$")
# A list item, and the column its content starts at. Past four spaces after the
# marker the content is indented code, which is not this reader's concern.
LIST_ITEM_RE = re.compile(r"^( *)([-*+]|\d{1,9}[.)])( {1,4})(?=\S)")
# `* * *` and `- - -` are thematic breaks, which end a list rather than open one.
BREAK_RE = re.compile(r"^ {0,3}([-*_])( *\1){2,} *$")


class Fences:
    """Line by line, which lines a fence holds.

    As CommonMark reads it: a fence closes only on a run of the same character,
    at least as long, with nothing after it. A ```` fence quoting a ``` example,
    or a ```bash line inside a ``` block, is content, not the end of the block.

    A fence is indented up to three spaces past the content of the list item
    holding it, so a ```bash under `1. ` at four spaces is a fence: reading it
    as prose left every command and heading inside it unread. A line indented
    less than the item's content leaves the item; a lazy continuation does too,
    which is the conservative side — it only reads as it did before lists counted.
    Leaving the item closes a fence it holds, unclosed or not: kept open, one
    missing ``` swallowed every heading and command to the end of the page.
    """

    def __init__(self) -> None:
        self.fence: str | None = None     # the open fence's run, or None
        self.info = ""                    # the open fence's info string
        self._content = 0                 # the enclosing list item's content column

    def step(self, line: str) -> bool:
        """Read `line`; whether it opened or closed a fence.

        A line that closes a fence by leaving its list item is not itself a fence
        line: it is read as the first line outside, and may open the next one.
        """
        if self.fence is not None and self._content and line.strip() \
                and len(line) - len(line.lstrip(" ")) < self._content:
            self.fence, self.info = None, ""
        if self.fence is None:
            self._content = self._list_content(line)
        m = FENCE_RE.match(line)
        if not m or len(m.group(1)) > self._content + 3:
            return False
        run, rest = m.group(2), m.group(3)
        if self.fence is None:
            if run[0] == "`" and "`" in rest:      # inline code, not a fence
                return False
            self.fence, self.info = run, rest.strip()
            return True
        if run[0] == self.fence[0] and len(run) >= len(self.fence) and not rest.strip():
            self.fence, self.info = None, ""
            return True
        return False

    def _list_content(self, line: str) -> int:
        if not line.strip():
            return self._content
        m = None if BREAK_RE.match(line) else LIST_ITEM_RE.match(line)
        if m:
            return len(m.group(1)) + len(m.group(2)) + len(m.group(3))
        indent = len(line) - len(line.lstrip(" "))
        return self._content if indent >= self._content else 0
